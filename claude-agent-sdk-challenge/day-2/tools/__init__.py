"""The tools we wrote, handed to the agent through one small in-process server.

Each tool lives in its own file. To add one: write it with @tool, import it here, and
add it to the list. Its full name becomes mcp__jobfit__<tool name>.
"""
from claude_agent_sdk import create_sdk_mcp_server

from tools.job_ad import fetch_job_ad
from tools.tracker import check_tracker, save_to_tracker

ALL_TOOLS = [fetch_job_ad, check_tracker, save_to_tracker]

jobfit_server = create_sdk_mcp_server(name="jobfit", tools=ALL_TOOLS)
JOBFIT_TOOLS = [f"mcp__jobfit__{t.name}" for t in ALL_TOOLS]
