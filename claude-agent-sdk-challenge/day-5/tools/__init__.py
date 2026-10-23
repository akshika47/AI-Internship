"""The tools we wrote, handed to the agent through one small in-process server.

Each tool lives in its own file. To add one: write it with @tool, import it here, and add
it to a list. Its full name becomes mcp__jobfit__<tool name>.
"""
from claude_agent_sdk import create_sdk_mcp_server

from tools.cv_check import check_cv_bullets
from tools.evidence import check_evidence
from tools.job_ad import fetch_job_ad
from tools.tracker import check_tracker, save_to_tracker

CORE_TOOLS = [fetch_job_ad, check_tracker, save_to_tracker]  # Day 2's tools
SKILL_TOOLS = [check_cv_bullets, check_evidence]             # the checks the skill relies on


def tool_names(tools) -> list[str]:
    return [f"mcp__jobfit__{t.name}" for t in tools]


def jobfit_server(with_skill_tools: bool):
    return create_sdk_mcp_server(name="jobfit", tools=CORE_TOOLS + (SKILL_TOOLS if with_skill_tools else []))
