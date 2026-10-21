"""Runs the agent once and hands back its report, or a StopRun explaining what went wrong."""
from dataclasses import dataclass
from pathlib import Path

from claude_agent_sdk import ClaudeSDKError, ResultMessage, query

from agent.options import build_options


class StopRun(Exception):
    """Something the user can fix. job_fit.py prints the message and exits, with no traceback."""


@dataclass(frozen=True)
class Run:
    report: dict
    turns: int
    cost_usd: float

    @property
    def summary(self) -> str:
        return f"{self.turns} turns · ${self.cost_usd:.3f}"


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


async def final_message(prompt: str, use_skill: bool, show_steps: bool) -> ResultMessage | None:
    """The agent streams messages while it works; the last one carries the answer."""
    result = None
    try:
        async for message in query(prompt=prompt, options=build_options(use_skill, show_steps)):
            if isinstance(message, ResultMessage):
                result = message
    except ClaudeSDKError as error:
        raise StopRun(f"The agent couldn't run: {error}\nThe Stuck? table in README.md has the usual fixes.") from error
    return result


async def run_agent(job: str, cv: str, use_skill: bool = True, show_steps: bool = True) -> Run:
    check_inputs(job, cv)
    where = job if is_link(job) else Path(job).resolve()
    result = await final_message(f"My CV is the file {Path(cv).resolve()}. The job ad is at {where}. How well do I fit?", use_skill, show_steps)

    if result is None or result.structured_output is None:
        raise StopRun(f"The agent stopped without a report ({result.subtype if result else 'no result'}).")
    run = Run(result.structured_output, result.num_turns, result.total_cost_usd or 0)
    if not run.report["ad_was_read"]:
        raise StopRun(f"Couldn't read the job ad. {run.report['verdict']}\n"
                      f"Copy the ad's text into job.md and run: uv run job_fit.py job.md\n({run.summary})")
    return run
