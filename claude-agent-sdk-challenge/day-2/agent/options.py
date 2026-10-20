"""Everything the agent is allowed to do, in one place: prompt, tools, answer shape, limits."""
from claude_agent_sdk import ClaudeAgentOptions, HookMatcher

from agent.hooks import show_tool_use
from agent.prompt import SYSTEM_PROMPT
from agent.schema import REPORT_SCHEMA
from tools import JOBFIT_TOOLS, jobfit_server

BUILT_IN_TOOLS = ["Read"]  # from the SDK: read a file (your CV, or a job ad you saved)

OPTIONS = ClaudeAgentOptions(
    system_prompt=SYSTEM_PROMPT,
    tools=BUILT_IN_TOOLS,                          # the only built-in tool it has
    mcp_servers={"jobfit": jobfit_server},         # plus the tools we wrote (see tools/)
    allowed_tools=BUILT_IN_TOOLS + JOBFIT_TOOLS,   # all of them run without asking you
    output_format={"type": "json_schema", "schema": REPORT_SCHEMA},
    hooks={"PreToolUse": [HookMatcher(hooks=[show_tool_use])]},
    model="sonnet",
    max_turns=15,
    max_budget_usd=1.00,  # a cap per run; a normal run costs a few cents
)
