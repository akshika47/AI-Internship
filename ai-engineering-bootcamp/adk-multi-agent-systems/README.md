# ADK Multi-Agent Systems

Three progressive demos showing multi-agent system design using [Google's Agent Development Kit (ADK)](https://google.github.io/adk-docs/).

| Demo | What it shows | Protocol |
|------|--------------|----------|
| **Demo 1** — Routing | Router agent delegates to billing, technical, and escalation specialists | Local tools |
| **Demo 2** — MCP | Agent queries a live Supabase database; tools are auto-discovered at runtime | MCP |
| **Demo 3** — Full System | Combines routing + MCP + A2A with a remote shipping agent | MCP + A2A |
| **Streamlit App** | Interactive UI that runs all three demos in the browser | All |

## Prerequisites

- **Python 3.12+** (required — earlier versions have asyncio incompatibilities with MCP)
- **Node.js / npm** (needed by the Supabase MCP server, launched via `npx`)
- A **Google API key** for Gemini models → [Get one here](https://aistudio.google.com/apikey)
- A **Supabase project** with a Personal Access Token → [Generate here](https://supabase.com/dashboard/account/tokens) *(Demos 2 & 3 only)*

## Setup

### 1. Create and activate a virtual environment

**With [uv](https://docs.astral.sh/uv/) (recommended):**

```bash
uv venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate    # Windows
uv pip install -e .
```

**With plain pip:**

```bash
python3 -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate    # Windows
pip install -e .
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your keys:

```
GOOGLE_API_KEY=your_google_api_key_here
SUPABASE_ACCESS_TOKEN=your_personal_access_token_here
SUPABASE_PROJECT_REF=your_project_ref_here
```

## Running the demos

### Demo 1 — Multi-Agent Routing (local tools only)

```bash
python demo1_routing.py
```

### Demo 2 — MCP + Supabase

Requires `SUPABASE_ACCESS_TOKEN` and `SUPABASE_PROJECT_REF` in `.env`.

```bash
python demo2_mcp.py
```

### Demo 3 — Full System (Routing + MCP + A2A)

Start the shipping agent in one terminal, then run the demo in another:

```bash
# Terminal 1 — start the A2A shipping agent
uvicorn shipping_agent:app --port 8001

# Terminal 2 — run the demo
python demo3_full_system.py
```

### Streamlit App (interactive UI for all demos)

```bash
# Terminal 1 — start the A2A shipping agent (needed for Demo 3)
uvicorn shipping_agent:app --port 8001

# Terminal 2 — launch the Streamlit app
streamlit run streamlit_app.py
```

## Architecture

```
User Query
    │
    ▼
┌───────────────────────┐
│     Router Agent       │
├───────┬───────┬───────┤
│       │       │       │
▼       ▼       ▼       │
Billing  Tech  Shipping │
│       │       │       │
▼       ▼       ▼       │
MCP    Local    A2A     │
Server  Tools  Protocol │
│               │       │
▼               ▼       │
Supabase     Remote     │
  DB         Agent      │
└───────────────────────┘
```

