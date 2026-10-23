"""A guardrail hook: the agent may only open the files and links this run is about.

Runs before every tool call. If a job ad hides an instruction like "read ../.env", the agent
might try, and this hook says no before anything happens. The rules are a table of tool ->
check, so adding a tool means adding one line.
"""
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Guard:
    files: set[Path]              # the CV and job ad for this run
    links: set[str]               # the job ad link, if there is one
    skills_folder: Path           # skill files are always fine to read
    blocked: list[str] = field(default_factory=list)  # what it stopped, for the report and evals

    def file_ok(self, args: dict) -> bool:
        path = Path(args.get("file_path", "")).resolve()
        return path in self.files or self.skills_folder in path.parents

    def link_ok(self, args: dict) -> bool:
        return args.get("url", "") in self.links

    def rules(self) -> dict[str, Callable[[dict], bool]]:
        return {"Read": self.file_ok, "mcp__jobfit__fetch_job_ad": self.link_ok,
                "mcp__jobfit__check_evidence": lambda args: Path(args.get("source_path", "")).resolve() in self.files}

    async def __call__(self, input_data, tool_use_id, context):
        tool, args = input_data["tool_name"], input_data["tool_input"]
        allowed = self.rules().get(tool, lambda _: True)(args)  # tools not in the table are already limited by options
        if allowed:
            return {}
        target = args.get("file_path") or args.get("url") or args.get("source_path")
        self.blocked.append(f"{tool}: {target}")
        print(f"  · blocked: {tool} tried to open {target}")
        return {"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Only the CV, the job ad and the skill files can be opened in this run.",
        }}
