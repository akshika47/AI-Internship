# LangGraph Multi-Agent Systems

LangGraph re-implementation of the `adk-multi-agent-systems` demos. Same three progressive demos, same concepts — different framework.

## ADK → LangGraph Mapping

| ADK | LangGraph |
|---|---|
| `Agent(sub_agents=[...])` | `StateGraph` + supervisor `Command` routing |
| `McpToolset(StdioConnectionParams(...))` | `MultiServerMCPClient` from `langchain-mcp-adapters` |
| `RemoteA2aAgent(agent_card=...)` | `httpx` HTTP POST to a FastAPI service |
| `Runner` + `InMemorySessionService` | `graph.invoke()` / `graph.ainvoke()` |
| `Agent(tools=[...])` | `create_react_agent(llm, tools=[...])` |

## Setup

```bash
pip install -e .
cp .env.example .env   # then fill in your keys (see Environment Variables below)
```

## Demos

### Demo 1: Multi-Agent Routing
```bash
python demo1_routing.py
```
**Pattern:** Supervisor node uses `llm.with_structured_output(Router)` to route to billing, technical, or escalation specialist via `Command(goto=...)`.

### Demo 2: MCP + Supabase
```bash
python demo2_mcp.py
```
**Pattern:** `MultiServerMCPClient` launches the Supabase MCP server as a subprocess and exposes its tools to a `create_react_agent`.

### Demo 3: Full System
```bash
# Terminal 1 — start the remote shipping agent
uvicorn shipping_agent:app --port 8001

# Terminal 2 — run the full system
python demo3_full_system.py
```
**Pattern:** Supervisor routes to billing (MCP), technical (local tools), or shipping (HTTP POST to FastAPI service).

### Streamlit UI (all demos)
```bash
uvicorn shipping_agent:app --port 8001   # Terminal 1
streamlit run streamlit_app.py            # Terminal 2
```

### Notebook

`week3_langgraph_notebook.ipynb` walks through the same three demos step by step
in notebook form — the LangGraph counterpart to `adk-multi-agent-systems/week3_notebook.ipynb`.

## Architecture

```
User Query
    |
    v
+-----------------------+
|    Supervisor Node    |   llm.with_structured_output(Router) -> Command
+---+-------+-------+--+
    |       |       |
    v       v       v
+------+ +------+ +--------+
|Billing| | Tech | |Shipping|
+---+--+ +--+---+ +---+----+
    |       |          |
    v       v          v
+------+ +------+ +--------+
| MCP  | |Local | |  HTTP  |
|Client| |Tools | | :8001  |
+------+ +------+ +--------+
```

## Environment Variables

```
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini   # optional
SUPABASE_ACCESS_TOKEN=...
SUPABASE_PROJECT_REF=...
LANGFUSE_SECRET_KEY=...
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```
