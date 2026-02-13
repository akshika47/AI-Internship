"""
Demo 3: Full System -- Multi-Agent + MCP + A2A

Start shipping agent first:  uvicorn shipping_agent:app --port 8001
Then run:                     python demo3_full_system.py
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from google.genai import types
from mcp.client.stdio import StdioServerParameters

MODEL = "gemini-2.5-flash"

# --- Layer 1: Technical Agent (local tools) ---

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

technical_agent = Agent(
    name="technical_agent", model=MODEL,
    description="Handles technical issues: bugs, crashes, performance, system status.",
    instruction="You are a technical specialist. Use search_knowledge_base and check_system_status.",
    tools=[search_knowledge_base, check_system_status],
)

# --- Layer 2: Billing Agent (MCP -> Supabase) ---

TOKEN = os.getenv("SUPABASE_ACCESS_TOKEN", "")
PROJECT_REF = os.getenv("SUPABASE_PROJECT_REF", "")

if not TOKEN:
    print("WARNING: SUPABASE_ACCESS_TOKEN not set -- billing agent won't work.")

mcp_args = ["-y", "@supabase/mcp-server-supabase@latest", "--access-token", TOKEN]
if PROJECT_REF:
    mcp_args += ["--project-ref", PROJECT_REF]

supabase_mcp = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(command="npx", args=mcp_args),
        timeout=30.0,
    ),
)

billing_agent = Agent(
    name="billing_agent_mcp", model=MODEL,
    description="Billing agent with real Supabase database access via MCP.",
    instruction="You are a billing specialist. Use MCP tools to query customers, orders, support_tickets.",
    tools=[supabase_mcp],
)

# --- Layer 3: Shipping Agent (A2A -> remote service) ---

shipping_agent = RemoteA2aAgent(
    name="shipping_agent",
    agent_card="http://localhost:8001",
    description="Remote agent for shipping and delivery tracking via A2A protocol.",
)

# --- Root Router ---

root_agent = Agent(
    name="full_support_system", model=MODEL,
    instruction="Route to billing_agent_mcp (billing/invoices), technical_agent (bugs/crashes), "
                "or shipping_agent (package tracking). Never answer directly.",
    sub_agents=[billing_agent, technical_agent, shipping_agent],
)

# --- Runner ---

async def ask(agent, message):
    service = InMemorySessionService()
    runner = Runner(agent=agent, app_name="demo", session_service=service)
    session = await service.create_session(app_name="demo", user_id="user1")
    content = types.Content(role="user", parts=[types.Part(text=message)])
    async for event in runner.run_async(user_id="user1", session_id=session.id, new_message=content):
        if event.is_final_response() and event.content and event.content.parts:
            return event.content.parts[0].text
    return "(no response)"

async def main():
    scenarios = [
        ("BILLING (MCP)", "I'm Jane Doe (jane@example.com). What plan am I on? Show my recent orders."),
        ("TECHNICAL (Local)", "My app is really slow lately. Is something wrong with your servers?"),
        ("SHIPPING (A2A)", "Where is my package for order ORD-1004? When will it arrive?"),
    ]
    for label, query in scenarios:
        print(f"\n--- {label} ---")
        print(f"User: {query}\n")
        print(f"Agent: {await ask(root_agent, query)}\n")

if __name__ == "__main__":
    asyncio.run(main())
