"""Starter: the smallest agent with one tool you write yourself. Copy it for your own idea.

Usage:
    uv run starter_tool.py "your request"

Example:
    uv run starter_tool.py "Read examples/jobs/fernhill-automation-analyst.md and save me three interview questions"

As it stands, the agent can read files and has one tool of yours: save_note, which adds
a line to notes.md. To make it yours, change three things:
    1. SYSTEM_PROMPT   what your agent is for
    2. the @tool       what your tool does (send a message, call an API, update a sheet...)
    3. allowed_tools   add any other tools it needs
"""
import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import find_dotenv, load_dotenv
from claude_agent_sdk import (
    ClaudeAgentOptions,
    ClaudeSDKError,
    ResultMessage,
    create_sdk_mcp_server,
    query,
    tool,
)

load_dotenv(find_dotenv())  # finds the .env in the claude-agent-sdk-challenge folder

SYSTEM_PROMPT = "You are a helpful assistant. When you find something worth keeping, save it with save_note."


@tool("save_note", "Save one short note to the user's notes file", {"note": str})
async def save_note(args: dict[str, Any]) -> dict[str, Any]:
    with Path("notes.md").open("a") as f:
        f.write(f"- {datetime.now():%Y-%m-%d %H:%M} {args['note']}\n")
    return {"content": [{"type": "text", "text": "Saved to notes.md"}]}


OPTIONS = ClaudeAgentOptions(
    system_prompt=SYSTEM_PROMPT,
    tools=["Read"],                                                    # built-in tools it has
    mcp_servers={"my_tools": create_sdk_mcp_server("my_tools", tools=[save_note])},
    allowed_tools=["Read", "mcp__my_tools__save_note"],               # run these without asking
    model="sonnet",
    max_turns=10,
    max_budget_usd=1.00,  # a cap per run; a normal run costs a few cents
)


async def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    try:
        async for message in query(prompt=sys.argv[1], options=OPTIONS):
            if isinstance(message, ResultMessage) and message.subtype == "success":
                print(message.result)
                print(f"\n{message.num_turns} turns · ${message.total_cost_usd or 0:.3f}")
    except ClaudeSDKError as error:
        sys.exit(f"The agent couldn't run: {error}")


if __name__ == "__main__":
    asyncio.run(main())
