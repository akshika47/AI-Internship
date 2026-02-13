"""
Demo 2: MCP -- Agent with Real Database Access (Supabase)
Run: python demo2_mcp.py
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from google.genai import types
from mcp.client.stdio import StdioServerParameters

MODEL = "gemini-2.5-flash"
TOKEN = os.getenv("SUPABASE_ACCESS_TOKEN", "")
PROJECT_REF = os.getenv("SUPABASE_PROJECT_REF", "")

if not TOKEN:
    sys.exit("Set SUPABASE_ACCESS_TOKEN in .env (https://supabase.com/dashboard/account/tokens)")

# --- MCP Toolset (launches Supabase MCP server as subprocess) ---

mcp_args = ["-y", "@supabase/mcp-server-supabase@latest", "--access-token", TOKEN]
if PROJECT_REF:
    mcp_args += ["--project-ref", PROJECT_REF]

supabase_mcp = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(command="npx", args=mcp_args),
        timeout=30.0,
    ),
)

# --- Agent ---

billing_agent = Agent(
    name="billing_agent_mcp", model=MODEL,
    instruction="You are a billing specialist with real database access. "
                "Use MCP tools to query customers, orders, and support_tickets tables. "
                "Always look up the customer first.",
    tools=[supabase_mcp],
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
    tests = [
        ("CUSTOMER LOOKUP", "What orders does Bob Smith have? What's the total amount?"),
        ("CROSS-TABLE QUERY", "Show me all high-priority open support tickets with customer name and email."),
    ]
    for label, query in tests:
        print(f"\n--- {label} ---")
        print(f"User: {query}\n")
        print(f"Agent: {await ask(billing_agent, query)}\n")

if __name__ == "__main__":
    asyncio.run(main())
