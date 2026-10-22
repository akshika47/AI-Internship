"""Job-fit agent, Day 2: compares your CV with a job ad and keeps an applications tracker.

Usage:
    uv run job_fit.py JOB_AD [CV]

    JOB_AD  a link to the job ad, or a file you saved it in
    CV      your CV as a .md, .txt or .pdf file (optional, defaults to cv.md)

Examples:
    uv run job_fit.py examples/jobs/fernhill-automation-analyst.md examples/cvs/ops-coordinator.md
    uv run job_fit.py https://job-boards.greenhouse.io/company/jobs/123 cv.pdf

Where things live:
    agent/   what the agent is told (prompt.py), the shape of its answer (schema.py),
             what it may do (options.py), its step log (hooks.py), running it (run.py),
             and the report it writes (report.py)
    tools/   the three tools we wrote: fetch_job_ad, check_tracker, save_to_tracker
"""
import asyncio
import sys

from dotenv import find_dotenv, load_dotenv

from agent.report import report_path, to_markdown
from agent.run import StopRun, run_agent

load_dotenv(find_dotenv())  # finds the .env in the claude-agent-sdk-challenge folder


async def main(job: str, cv: str = "cv.md") -> None:
    run = await run_agent(job, cv)
    path = report_path(run.report["role"], cv)
    path.write_text(to_markdown(run.report))
    print(f"\nSaved {path} · {run.summary}\nYour tracker is in applications.csv")


if __name__ == "__main__":
    if not 2 <= len(sys.argv) <= 3:
        sys.exit(__doc__)
    try:
        asyncio.run(main(*sys.argv[1:]))
    except StopRun as stop:
        sys.exit(f"\n{stop}")
