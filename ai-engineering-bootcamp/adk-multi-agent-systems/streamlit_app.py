"""
ADK Multi-Agent Systems -- Interactive Classroom Demo

Run:
    uvicorn shipping_agent:app --port 8001   # Terminal 1
    streamlit run streamlit_app.py            # Terminal 2
"""

import streamlit as st
import asyncio
import concurrent.futures
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

MODEL = "gemini-2.5-flash"

# --- Tools ---

def lookup_invoice(customer_email: str) -> dict:
    """Look up the most recent invoice for a customer by email."""
    invoices = {
        "bob@example.com": {"invoice_id": "INV-2024-002", "customer": "Bob Smith", "amount": "$299.00", "status": "overdue", "plan": "Enterprise Annual"},
        "jane@example.com": {"invoice_id": "INV-2024-001", "customer": "Jane Doe", "amount": "$99.00", "status": "paid", "plan": "Pro Monthly"},
        "alice@example.com": {"invoice_id": "INV-2024-003", "customer": "Alice Johnson", "amount": "$49.00", "status": "paid", "plan": "Starter Monthly"},
    }
    return invoices.get(customer_email.lower(), {"error": f"No invoice found for {customer_email}"})

def process_refund(invoice_id: str, reason: str) -> dict:
    """Process a refund for a specific invoice."""
    return {"refund_id": f"REF-{invoice_id[-3:]}", "status": "approved", "message": f"Refund for {invoice_id} approved. 5-7 business days."}

def search_knowledge_base(query: str) -> dict:
    """Search the knowledge base for technical solutions."""
    articles = {
        "login": {"title": "Login Issues", "solution": "1. Clear cache. 2. Try incognito. 3. Reset password."},
        "crash": {"title": "App Crashing", "solution": "1. Update to v3.2.1. 2. Clear app data. 3. Check OS requirements."},
        "slow": {"title": "Performance Issues", "solution": "1. Check internet. 2. Close other apps. 3. Enable hardware acceleration."},
    }
    for keyword, article in articles.items():
        if keyword in query.lower():
            return article
    return {"title": "General Support", "solution": "No specific article found."}

def check_system_status() -> dict:
    """Check current status of all platform services."""
    return {"overall": "operational", "auth_service": "degraded", "last_incident": "2026-02-08"}

def create_escalation_ticket(customer_email: str, issue_summary: str, priority: str) -> dict:
    """Create an escalation ticket for issues needing human review."""
    times = {"low": "48 hours", "medium": "24 hours", "high": "4 hours", "critical": "1 hour"}
    return {"ticket_id": "ESC-2026-0042", "priority": priority, "estimated_response": times.get(priority, "24 hours")}

# --- Demo 1 Agents ---

billing_agent = Agent(
    name="billing_agent", model=MODEL,
    description="Handles billing: invoices, payments, refunds.",
    instruction="You are a billing specialist. Use lookup_invoice and process_refund.",
    tools=[lookup_invoice, process_refund],
)
technical_agent = Agent(
    name="technical_agent", model=MODEL,
    description="Handles technical issues: bugs, crashes, performance.",
    instruction="You are a technical specialist. Use search_knowledge_base and check_system_status.",
    tools=[search_knowledge_base, check_system_status],
)
escalation_agent = Agent(
    name="escalation_agent", model=MODEL,
    description="Handles complaints, disputes, security concerns.",
    instruction="You are an escalation specialist. Use create_escalation_ticket.",
    tools=[create_escalation_ticket],
)
router_agent = Agent(
    name="customer_support_router", model=MODEL,
    instruction="Route to billing_agent, technical_agent, or escalation_agent. Never answer directly.",
    sub_agents=[billing_agent, technical_agent, escalation_agent],
)

# --- Demo 2 & 3 Agent Factories ---

def create_mcp_billing_agent():
    from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
    from mcp.client.stdio import StdioServerParameters
    token = os.getenv("SUPABASE_ACCESS_TOKEN", "")
    ref = os.getenv("SUPABASE_PROJECT_REF", "")
    if not token:
        return None, "SUPABASE_ACCESS_TOKEN not set in .env"
    mcp_args = ["-y", "@supabase/mcp-server-supabase@latest", "--access-token", token]
    if ref:
        mcp_args += ["--project-ref", ref]
    mcp = McpToolset(connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(command="npx", args=mcp_args), timeout=30.0))
    agent = Agent(
        name="billing_agent_mcp", model=MODEL,
        description="Billing agent with real Supabase database access via MCP.",
        instruction="You are a billing specialist with database access. Use MCP tools to query customers, orders, support_tickets.",
        tools=[mcp])
    return agent, None

def create_full_system_agent():
    from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
    from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
    from mcp.client.stdio import StdioServerParameters
    token = os.getenv("SUPABASE_ACCESS_TOKEN", "")
    ref = os.getenv("SUPABASE_PROJECT_REF", "")
    if not token:
        return None, "SUPABASE_ACCESS_TOKEN not set in .env"
    mcp_args = ["-y", "@supabase/mcp-server-supabase@latest", "--access-token", token]
    if ref:
        mcp_args += ["--project-ref", ref]
    mcp = McpToolset(connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(command="npx", args=mcp_args), timeout=30.0))
    billing = Agent(name="billing_agent_mcp", model=MODEL,
        description="Billing with real Supabase DB via MCP.", instruction="Use MCP tools to query the database.", tools=[mcp])
    tech = Agent(name="technical_agent", model=MODEL,
        description="Technical issues: bugs, crashes, performance.", instruction="Use search_knowledge_base and check_system_status.",
        tools=[search_knowledge_base, check_system_status])
    shipping = RemoteA2aAgent(name="shipping_agent", agent_card="http://localhost:8001",
        description="Remote agent for shipping and delivery tracking.")
    root = Agent(name="full_support_system", model=MODEL,
        instruction="Route to billing_agent_mcp, technical_agent, or shipping_agent. Never answer directly.",
        sub_agents=[billing, tech, shipping])
    return root, None

# --- Runner ---

def run_agent_sync(agent, message, timeout=120):
    """Run an ADK agent synchronously with trace capture."""
    async def _run():
        service = InMemorySessionService()
        runner = Runner(agent=agent, app_name="demo", session_service=service)
        session = await service.create_session(app_name="demo", user_id="user1")
        content = types.Content(role="user", parts=[types.Part(text=message)])
        trace, final = [], "(no response)"
        async for event in runner.run_async(user_id="user1", session_id=session.id, new_message=content):
            author = getattr(event, "author", "unknown")
            if event.content and event.content.parts:
                for part in event.content.parts:
                    fc = getattr(part, "function_call", None)
                    fr = getattr(part, "function_response", None)
                    text = getattr(part, "text", None)
                    if fc:
                        trace.append({"author": author, "type": "tool_call", "tool": fc.name, "args": dict(fc.args) if fc.args else {}})
                    elif fr:
                        trace.append({"author": author, "type": "tool_response", "tool": fr.name, "result": str(fr.response)[:800] if fr.response else ""})
                    elif text:
                        trace.append({"author": author, "type": "text", "text": text})
                        if event.is_final_response():
                            final = text
        return final, trace
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, _run()).result(timeout=timeout)

# --- Helpers ---

def check_shipping_agent(url="http://localhost:8001"):
    try:
        import urllib.request
        with urllib.request.urlopen(f"{url}/.well-known/agent-card.json", timeout=2) as r:
            return r.status == 200
    except Exception:
        return False

def render_trace(trace):
    if not trace:
        return
    seen = []
    for i, step in enumerate(trace):
        author = step.get("author", "unknown")
        if author not in seen:
            seen.append(author)
            if len(seen) > 1:
                st.info(f"Routed to **{author}**")
        if step["type"] == "tool_call":
            args = ", ".join(f"{k}={v!r}" for k, v in step.get("args", {}).items())
            st.warning(f"**{i+1}.** `{author}` called **{step['tool']}**({args[:200]})")
        elif step["type"] == "tool_response":
            st.success(f"**{i+1}.** `{author}` got result from **{step['tool']}**")
            if step.get("result"):
                st.code(step["result"][:500], language="json")
        elif step["type"] == "text" and step.get("text", "").strip():
            st.markdown(f"**{i+1}.** `{author}`: {step['text'][:300]}")

# --- Page Config ---

st.set_page_config(page_title="ADK Multi-Agent Systems", layout="wide")
st.markdown("<style>.block-container{padding-top:1.5rem;}</style>", unsafe_allow_html=True)

api_key = os.getenv("GOOGLE_API_KEY")
supa_token = os.getenv("SUPABASE_ACCESS_TOKEN")
supa_ref = os.getenv("SUPABASE_PROJECT_REF")
shipping_ok = check_shipping_agent()

# --- Sidebar ---

with st.sidebar:
    st.title("ADK Multi-Agent Systems")
    st.caption("Interactive Classroom Demo")
    page = st.radio("Navigate", ["Overview", "Demo 1: Routing", "Demo 2: MCP + Database", "Demo 3: Full System"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("### Status")
    if api_key:
        st.success("Google API Key")
    else:
        st.error("Google API Key -- not set")
    if supa_token and supa_ref:
        st.success("Supabase")
    else:
        st.warning("Supabase -- not configured")
    if shipping_ok:
        st.success("Shipping Agent (:8001)")
    else:
        st.warning("Shipping Agent -- not running")

# --- Overview ---

if page == "Overview":
    st.header("Building Multi-Agent AI Systems with ADK")
    st.markdown("Three progressive demos showing multi-agent system design using Google's Agent Development Kit.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Demo 1: Routing")
        st.markdown("Router agent delegates to billing, technical, and escalation specialists.\n\n**Pattern:** Router / Delegation")
    with col2:
        st.subheader("Demo 2: MCP")
        st.markdown("Agent connects to a live Supabase database via MCP. Tools are auto-discovered at runtime.\n\n**Pattern:** External tool discovery")
    with col3:
        st.subheader("Demo 3: Full System")
        st.markdown("Combines routing + MCP + A2A. Shipping agent runs as a separate process.\n\n**Pattern:** Cross-process communication")

    st.markdown("---")
    st.subheader("Architecture")
    st.code("""
    User Query
        |
        v
    +-----------------------+
    |     Router Agent      |
    +---+-------+-------+--+
        |       |       |
        v       v       v
    +------+ +------+ +--------+
    |Billing| | Tech | |Shipping|
    +---+--+ +--+---+ +---+----+
        |       |          |
        v       v          v
    +------+ +------+ +--------+
    | MCP  | |Local | |  A2A   |
    |Server| |Tools | |Protocol|
    +---+--+ +------+ +---+----+
        |                  |
        v                  v
    +------+          +--------+
    |Supa- |          | Remote |
    | base |          | Agent  |
    +------+          +--------+
    """, language=None)

    st.markdown("---")
    st.subheader("Multi-Agent Patterns")
    for name, desc in {
        "Router / Delegation": "Router inspects the query and delegates to the right specialist via `sub_agents`.",
        "Sequential Pipeline": "Agents run in order: Draft -> Review -> Polish. Use `SequentialAgent`.",
        "Parallel Fan-Out": "Multiple agents process input simultaneously. Use `ParallelAgent`.",
        "Loop / Iterative Refinement": "Agent refines output until quality criteria are met. Use `LoopAgent`.",
    }.items():
        with st.expander(name):
            st.markdown(desc)

    st.subheader("Why Multi-Agent?")
    st.markdown(
        "| Single Agent | Multi-Agent |\n|---|---|\n"
        "| One massive prompt | Focused, modular agents |\n"
        "| Hard to test | Each agent testable independently |\n"
        "| Fragile | Swap or update agents independently |\n"
        "| Can't scale | Add specialists without rewriting |"
    )

# --- Demo 1 ---

elif page == "Demo 1: Routing":
    st.header("Demo 1: Multi-Agent Routing")
    st.markdown("A **router agent** delegates to the right specialist based on the query.")

    with st.expander("Architecture"):
        st.code("""
    Router Agent
      |--- billing_agent   -> lookup_invoice, process_refund
      |--- technical_agent  -> search_knowledge_base, check_system_status
      |--- escalation_agent -> create_escalation_ticket
        """, language=None)

    if not api_key:
        st.error("Set GOOGLE_API_KEY in .env"); st.stop()

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    query = None
    with col1:
        if st.button("Billing Query", use_container_width=True):
            query = "I need to check my invoice. Email: bob@example.com. Can I get a refund?"
    with col2:
        if st.button("Technical Query", use_container_width=True):
            query = "My app keeps crashing when I login. Is there an outage?"
    with col3:
        if st.button("Escalation Query", use_container_width=True):
            query = "Someone hacked my account! Email: jane@example.com. Urgent!"
    custom = st.text_input("Or type your own:", placeholder="e.g. What's the status of my refund?")
    if st.button("Send", type="primary") and custom.strip():
        query = custom.strip()

    if query:
        st.markdown(f"**Query:** {query}")
        with st.spinner("Running..."):
            try:
                response, trace = run_agent_sync(router_agent, query)
                st.session_state["d1_resp"], st.session_state["d1_trace"], st.session_state["d1_q"] = response, trace, query
            except Exception as e:
                st.error(str(e))

    if st.session_state.get("d1_resp"):
        st.markdown("---")
        st.markdown(f"**Query:** {st.session_state.get('d1_q', '')}")
        st.subheader("Response")
        st.markdown(st.session_state["d1_resp"])
        with st.expander("Agent Trace", expanded=True):
            render_trace(st.session_state.get("d1_trace", []))

# --- Demo 2 ---

elif page == "Demo 2: MCP + Database":
    st.header("Demo 2: MCP -- Real Database Access")
    st.markdown("The agent connects to a **live Supabase database** via MCP. Tools are auto-discovered at runtime.")

    with st.expander("Architecture"):
        st.code("Agent -> MCP Protocol -> Supabase MCP Server (npx) -> Supabase DB", language=None)

    if not api_key:
        st.error("Set GOOGLE_API_KEY in .env"); st.stop()
    if not supa_token:
        st.error("Set SUPABASE_ACCESS_TOKEN and SUPABASE_PROJECT_REF in .env"); st.stop()

    st.markdown("---")
    col1, col2 = st.columns(2)
    query = None
    with col1:
        if st.button("Customer Lookup", use_container_width=True):
            query = "What orders does Bob Smith have? What's the total?"
    with col2:
        if st.button("Cross-Table Query", use_container_width=True):
            query = "Show all high-priority open support tickets with customer name."
    custom = st.text_input("Or type your own:", key="d2c", placeholder="e.g. How many customers are on the pro plan?")
    if st.button("Send", key="d2s", type="primary") and custom.strip():
        query = custom.strip()

    if query:
        st.markdown(f"**Query:** {query}")
        with st.spinner("Connecting to MCP + Supabase (may take 10-15s)..."):
            try:
                agent, err = create_mcp_billing_agent()
                if err:
                    st.error(err)
                else:
                    response, trace = run_agent_sync(agent, query, timeout=180)
                    st.session_state["d2_resp"], st.session_state["d2_trace"], st.session_state["d2_q"] = response, trace, query
            except Exception as e:
                st.error(str(e))

    if st.session_state.get("d2_resp"):
        st.markdown("---")
        st.markdown(f"**Query:** {st.session_state.get('d2_q', '')}")
        st.subheader("Response")
        st.markdown(st.session_state["d2_resp"])
        with st.expander("Agent Trace", expanded=True):
            render_trace(st.session_state.get("d2_trace", []))

# --- Demo 3 ---

elif page == "Demo 3: Full System":
    st.header("Demo 3: Full System -- Routing + MCP + A2A")
    st.markdown("Combines **routing** + **MCP** (Supabase) + **A2A** (remote shipping agent).")

    with st.expander("Architecture"):
        st.code("""
    Router -> billing_agent  (MCP -> Supabase)
           -> technical_agent (local tools)
           -> shipping_agent  (A2A -> localhost:8001)
        """, language=None)

    if not api_key:
        st.error("Set GOOGLE_API_KEY in .env"); st.stop()
    if not supa_token:
        st.warning("Supabase not configured -- billing won't work.")
    if not shipping_ok:
        st.warning("Shipping agent not running. Start: `uvicorn shipping_agent:app --port 8001`")

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    query = None
    with col1:
        if st.button("Billing (MCP)", use_container_width=True):
            query = "I'm Jane Doe (jane@example.com). What plan am I on?"
    with col2:
        if st.button("Technical (Local)", use_container_width=True):
            query = "My app is slow. Is something wrong with your servers?"
    with col3:
        if st.button("Shipping (A2A)", use_container_width=True):
            query = "Where is my package for order ORD-1004?"
    custom = st.text_input("Or type your own:", key="d3c", placeholder="e.g. Help with my order and a tech issue")
    if st.button("Send", key="d3s", type="primary") and custom.strip():
        query = custom.strip()

    if query:
        st.markdown(f"**Query:** {query}")
        with st.spinner("Running full system (15-20s)..."):
            try:
                agent, err = create_full_system_agent()
                if err:
                    st.error(err)
                else:
                    response, trace = run_agent_sync(agent, query, timeout=180)
                    st.session_state["d3_resp"], st.session_state["d3_trace"], st.session_state["d3_q"] = response, trace, query
            except Exception as e:
                st.error(str(e))

    if st.session_state.get("d3_resp"):
        st.markdown("---")
        st.markdown(f"**Query:** {st.session_state.get('d3_q', '')}")
        st.subheader("Response")
        st.markdown(st.session_state["d3_resp"])
        with st.expander("Agent Trace", expanded=True):
            render_trace(st.session_state.get("d3_trace", []))
