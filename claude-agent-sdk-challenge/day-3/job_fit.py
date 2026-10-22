"""Job-fit agent, Day 3: reviews your CV against a job ad using your own know-how, from a skill.

Usage:
    uv run job_fit.py JOB_AD [CV] [--no-skill]

    JOB_AD      a link to the job ad, or a file you saved it in
    CV          your CV as a .md, .txt or .pdf file (defaults to cv.md)
    --no-skill  run Day 2's agent instead, to compare

Examples:
    uv run job_fit.py examples/jobs/fernhill-automation-analyst.md examples/cvs/career-changer.pdf
    uv run job_fit.py examples/jobs/fernhill-automation-analyst.md examples/cvs/career-changer.pdf --no-skill

Where things live:
    .claude/skills/reviewing-cvs/   the skill: SKILL.md plus reference/ files it reads when needed
    agent/                          prompt, answer shape, options, step log, run, report
    tools/                          fetch_job_ad, check_tracker, save_to_tracker, check_cv_bullets
    shortlist.py                    the same agent over a whole folder of job ads
    run_evals.py                    measures the skill: the same jobs with and without it
"""
import argparse
import asyncio
import sys

from dotenv import find_dotenv, load_dotenv

from agent.report import report_path, to_markdown
from agent.run import StopRun, run_agent

load_dotenv(find_dotenv())  # finds the .env in the claude-agent-sdk-challenge folder


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Review a CV against a job ad.", usage=__doc__)
    parser.add_argument("job_ad")
    parser.add_argument("cv", nargs="?", default="cv.md")
    parser.add_argument("--no-skill", action="store_true", help="run without the skill, to compare")
    return parser.parse_args()


async def main(args: argparse.Namespace) -> None:
    run = await run_agent(args.job_ad, args.cv, use_skill=not args.no_skill)
    path = report_path(run.report["role"], args.cv, suffix="no-skill" if args.no_skill else "")
    path.write_text(to_markdown(run.report))
    print(f"\nSaved {path} · {run.summary}\nYour tracker is in applications.csv")


if __name__ == "__main__":
    try:
        asyncio.run(main(parse_args()))
    except StopRun as stop:
        sys.exit(f"\n{stop}")
