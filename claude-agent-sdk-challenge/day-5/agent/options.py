"""Everything the agent is allowed to do, in one place: prompt, tools, skills, guardrail, limits.

This is the Day 4 agent plus an optional step log (agent/debug_log.py). What happens after it finishes,
the evidence and support checks, lives in agent/verify.py.
"""
from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions, HookMatcher

from agent.debug_log import DebugLog
from agent.guard import Guard
from agent.hooks import show_tool_use
from agent.prompt import SKILL_PROMPT
from agent.schema import REPORT_SCHEMA
from tools import CORE_TOOLS, SKILL_TOOLS, jobfit_server, tool_names

DAY_FOLDER = Path(__file__).resolve().parent.parent  # skills load from .claude/skills/ here
SKILLS_FOLDER = DAY_FOLDER / ".claude" / "skills"
SKILLS = ["reviewing-cvs"]  # the only skills this agent may use
BUILT_IN = ["Read", "Skill"]


def build_options(guard: Guard, show_steps: bool = True, log: DebugLog | None = None) -> ClaudeAgentOptions:
    pre_tool = [show_tool_use, guard] if show_steps else [guard]  # the guard always runs; printing steps is optional
    return ClaudeAgentOptions(
        system_prompt=SKILL_PROMPT,
        cwd=DAY_FOLDER,
        setting_sources=["project"],               # this folder's skills only, never your personal ones
        skills=SKILLS,
        tools=BUILT_IN,
        mcp_servers={"jobfit": jobfit_server(True)},
        allowed_tools=BUILT_IN + tool_names(CORE_TOOLS + SKILL_TOOLS),
        output_format={"type": "json_schema", "schema": REPORT_SCHEMA},
        hooks=log.hooks(extra_pre_tool_hooks=pre_tool) if log else {"PreToolUse": [HookMatcher(hooks=pre_tool)]},
        model="sonnet",
        max_turns=25,          # two check-and-fix loops now
        max_budget_usd=1.00,   # a cap per run; a normal run costs a few cents
    )
