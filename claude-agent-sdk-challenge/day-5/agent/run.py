"""Runs the agent once, checks its report, and hands back both, or a StopRun explaining what went wrong."""
from dataclasses import dataclass
from pathlib import Path

from claude_agent_sdk import AssistantMessage, ClaudeSDKError, ResultMessage, query

from agent.debug_log import DebugLog
from agent.guard import Guard
from agent.judge import JUDGE
from agent.options import SKILLS_FOLDER, build_options
from agent.verify import Verification, verify, without_failures


class StopRun(Exception):
    """Something the user can fix. job_fit.py prints the message and exits, with no traceback."""


@dataclass(frozen=True)
class Run:
    report: dict                       # after the checks: failed claims removed
    raw_report: dict                   # exactly what the agent wrote
    steps: list[str]                   # every tool it called, in order: its trajectory
    blocked: list[str]                 # what the guardrail stopped
    verification: Verification | None  # None when the checks are turned off
    turns: int
    cost_usd: float                    # the agent plus the judge

    @property
    def summary(self) -> str:
        removed = f" · {len(self.verification.failed)} claims removed" if self.verification else ""
        return f"{self.turns} turns · ${self.cost_usd:.3f}{removed}"


def is_link(job: str) -> bool:
    return job.startswith(("http://", "https://"))


def require_file(path: str, what: str, hint: str) -> None:
    if not Path(path).is_file():
        raise StopRun(f"Can't find {what} at '{path}'. {hint}")


def check_inputs(job: str, cv: str) -> None:
    """Stop before spending anything if a file isn't where you said it was."""
    require_file(cv, "your CV", "Check the name, or save it as cv.md in this folder.")
    if not is_link(job):
        require_file(job, "the job ad", "Use a link that starts with https://, or a file that exists.")


def guard_for(job: str, cv: str) -> Guard:
    files = {Path(cv).resolve()} | (set() if is_link(job) else {Path(job).resolve()})
    return Guard(files=files, links={job} if is_link(job) else set(), skills_folder=SKILLS_FOLDER)


async def agent_result(prompt: str, guard: Guard, show_steps: bool,
                       log: DebugLog | None = None) -> tuple[ResultMessage | None, list[str]]:
    """The agent streams messages while it works; the last one carries the answer."""
    result, steps = None, []
    try:
        async for message in query(prompt=prompt, options=build_options(guard, show_steps, log)):
            if isinstance(message, AssistantMessage):
                steps += [block.name for block in message.content if hasattr(block, "name")]
            elif isinstance(message, ResultMessage):
                result = message
    except ClaudeSDKError as error:
        raise StopRun(f"The agent couldn't run: {error}\nThe Stuck? table in README.md has the usual fixes.") from error
    return result, steps


async def run_agent(job: str, cv: str, checks: bool = True, judges: list[str] = JUDGE, show_steps: bool = True,
                    log_path: str | None = None) -> Run:
    check_inputs(job, cv)
    guard = guard_for(job, cv)
    log = DebugLog(log_path) if log_path else None
    where = job if is_link(job) else Path(job).resolve()
    result, steps = await agent_result(
        f"My CV is the file {Path(cv).resolve()}. The job ad is at {where}. How well do I fit?", guard, show_steps, log)

    if result is None or result.structured_output is None:
        raise StopRun(f"The agent stopped without a report ({result.subtype if result else 'no result'}).")
    raw = result.structured_output
    if not raw["ad_was_read"]:
        raise StopRun(f"Couldn't read the job ad. {raw['verdict']}\n"
                      f"Copy the ad's text into job.md and run: uv run job_fit.py job.md")

    verification = await verify(raw, cv, judges) if checks else None
    report = without_failures(raw, verification) if verification else raw
    cost = (result.total_cost_usd or 0) + (verification.cost_usd if verification else 0)
    if log:
        log.write("end", turns=result.num_turns, cost_usd=round(cost, 4), blocked=guard.blocked,
                  taken_out=[{"claim": c.claim.claim, "why": c.evidence or c.reason} for c in verification.failed] if verification else [])
    return Run(report, raw, steps, guard.blocked, verification, result.num_turns, cost)
