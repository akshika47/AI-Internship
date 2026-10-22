"""Runs the agent over a list of job ads, a few at a time, and ranks the results."""
import asyncio
from dataclasses import dataclass
from pathlib import Path

from agent.report import report_path, to_markdown
from agent.run import Run, StopRun, is_link, run_agent

AT_ONCE = 3  # parallel runs: fast enough, and gentle on rate limits and job sites


@dataclass(frozen=True)
class Outcome:
    job: str
    run: Run | None = None
    problem: str = ""


def read_job_list(path: str) -> list[str]:
    """jobs.txt: one link or file per line. Files are relative to the list; # lines are skipped."""
    folder = Path(path).parent
    lines = [line.strip() for line in Path(path).read_text().splitlines()]
    return [line if is_link(line) else str(folder / line) for line in lines if line and not line.startswith("#")]


async def assess(job: str, cv: str, checks: bool, limit: asyncio.Semaphore) -> Outcome:
    async with limit:
        try:
            run = await run_agent(job, cv, checks=checks, show_steps=False)
        except StopRun as stop:
            return Outcome(job, problem=str(stop).splitlines()[0])
    report_path(run.report["role"], cv).write_text(to_markdown(run.report))
    print(f"  · {run.report['fit_score']}/10  {run.report['role']}  ({run.summary})")
    return Outcome(job, run)


async def shortlist(jobs: list[str], cv: str, checks: bool = True) -> list[Outcome]:
    limit = asyncio.Semaphore(AT_ONCE)
    return await asyncio.gather(*(assess(job, cv, checks, limit) for job in jobs))


def to_markdown_table(outcomes: list[Outcome]) -> str:
    done = sorted((o for o in outcomes if o.run), key=lambda o: o.run.report["fit_score"], reverse=True)
    failed = [o for o in outcomes if not o.run]
    rows = [f"| {i} | {o.run.report['role']} | {o.run.report['fit_score']}/10 | {o.run.report['decision']} | "
            f"{o.run.report['verdict'].split('. ')[0].rstrip('.')}. |" for i, o in enumerate(done, 1)]
    lines = ["# Your job shortlist", "", "| # | Role | Fit | Decision | Why |", "|---|---|---|---|---|", *rows]
    lines += ["", "## Couldn't assess", "", *[f"- {o.job}: {o.problem}" for o in failed]] if failed else []
    cost = sum(o.run.cost_usd for o in done)
    return "\n".join(lines + ["", f"{len(done)} jobs assessed for ${cost:.2f}. Full reports are next to this file."]) + "\n"
