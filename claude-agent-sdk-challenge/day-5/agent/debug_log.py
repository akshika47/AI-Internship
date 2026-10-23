"""A step log: every tool call the agent makes, written to a file you can read after the run.

Agent bugs live in the steps, not in a traceback. This records each call (what the agent asked for), each
result (what came back, how long it took) and each failure, one JSON line per event, in order. Read it with:
    uv run show_log.py logs/<file>.jsonl

To add it to any Agent SDK agent:
    log = DebugLog("logs/run.jsonl")
    ClaudeAgentOptions(..., hooks=log.hooks())   # or log.hooks(extra_pre_tool_hooks=[your_guard])
"""
import json
import time
from pathlib import Path

from claude_agent_sdk import HookMatcher

KEEP_CHARS = 400  # long inputs and results are cut, so a log stays readable


def _short(value) -> str:
    text = value if isinstance(value, str) else json.dumps(value, default=str)
    return text if len(text) <= KEEP_CHARS else text[:KEEP_CHARS] + f"… (+{len(text) - KEEP_CHARS} chars)"


class DebugLog:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("")  # one run per file
        self.started = time.monotonic()

    def write(self, event: str, **fields) -> None:
        line = {"t": round(time.monotonic() - self.started, 2), "event": event, **fields}
        with self.path.open("a") as f:
            f.write(json.dumps(line, default=str) + "\n")

    async def before(self, input_data, tool_use_id, context):
        self.write("call", id=tool_use_id, tool=input_data["tool_name"], input=_short(input_data["tool_input"]))
        return {}

    async def after(self, input_data, tool_use_id, context):
        self.write("result", id=tool_use_id, tool=input_data["tool_name"],
                   output=_short(input_data.get("tool_response")), ms=input_data.get("duration_ms"))
        return {}

    async def failed(self, input_data, tool_use_id, context):
        self.write("error", id=tool_use_id, tool=input_data["tool_name"],
                   error=_short(input_data.get("error", "")), ms=input_data.get("duration_ms"))
        return {}

    def hooks(self, extra_pre_tool_hooks: list | None = None) -> dict:
        """The log runs first, so even a call your guard blocks is recorded."""
        return {
            "PreToolUse": [HookMatcher(hooks=[self.before, *(extra_pre_tool_hooks or [])])],
            "PostToolUse": [HookMatcher(hooks=[self.after])],
            "PostToolUseFailure": [HookMatcher(hooks=[self.failed])],
        }
