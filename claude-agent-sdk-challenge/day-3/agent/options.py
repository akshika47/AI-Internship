"""Everything the agent is allowed to do, in one place: prompt, tools, skills, answer shape, limits.

build_options(use_skill=True) is the Day 3 agent. use_skill=False is Day 2's agent, so you
can run both on the same job and compare.
"""
from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions, HookMatcher

from agent.hooks import show_tool_use
from agent.prompt import BASE_PROMPT, SKILL_PROMPT
from agent.schema import REPORT_SCHEMA
from tools import CORE_TOOLS, SKILL_TOOLS, jobfit_server, tool_names

DAY_FOLDER = Path(__file__).resolve().parent.parent  # skills load from .claude/skills/ here
SKILLS = ["reviewing-cvs"]  # the only skills this agent may use


def build_options(use_skill: bool, show_steps: bool = True) -> ClaudeAgentOptions:
    built_in = ["Read", "Skill"] if use_skill else ["Read"]  # Skill is the tool that opens a skill
    ours = CORE_TOOLS + (SKILL_TOOLS if use_skill else [])
    return ClaudeAgentOptions(
        system_prompt=SKILL_PROMPT if use_skill else BASE_PROMPT,
        cwd=DAY_FOLDER,
        setting_sources=["project"],               # this folder's skills only, never your personal ones
        skills=SKILLS if use_skill else [],
        tools=built_in,
        mcp_servers={"jobfit": jobfit_server(use_skill)},
        allowed_tools=built_in + tool_names(ours),
        output_format={"type": "json_schema", "schema": REPORT_SCHEMA},
        hooks={"PreToolUse": [HookMatcher(hooks=[show_tool_use])]} if show_steps else {},  # off when runs overlap
        model="sonnet",
        max_turns=20,          # the check-and-fix loop adds a few turns
        max_budget_usd=1.00,   # a cap per run; a normal run costs a few cents
    )
