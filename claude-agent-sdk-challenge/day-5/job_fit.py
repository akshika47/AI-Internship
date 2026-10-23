"""Job-fit agent, Day 4: reviews your CV against a job ad, then checks every claim before you see it.

Usage:
    uv run job_fit.py JOB_AD [CV] [--no-checks] [--jury] [--log [FILE]]

    JOB_AD       a link to the job ad, or a file you saved it in
    CV           your CV as a .md, .txt or .pdf file (defaults to cv.md)
    --no-checks  skip the final checks, to see what the agent wrote on its own
    --jury       three judge models vote on each claim, instead of one
    --log        write every step to a log (logs/last-run.jsonl). Read it: uv run show_log.py logs/last-run.jsonl

Examples:
    uv run job_fit.py examples/jobs/fernhill-automation-analyst.md examples/cvs/career-changer.pdf
    uv run job_fit.py examples/jobs/northgate-planted-instruction.md examples/cvs/ops-coordinator.pdf

Where things live:
    .claude/skills/reviewing-cvs/   the skill: SKILL.md plus reference/ files it reads when needed
    agent/                          prompt, answer shape, options, step log, guard, judge, verify, run, report
    tools/                          fetch_job_ad, check_tracker, save_to_tracker, check_cv_bullets, check_evidence
    shortlist.py                    the same agent over a whole folder of job ads
    run_evals.py                    evaluates the agent: evidence, support, steps followed, planted instructions
"""
import argparse
import asyncio
import sys

from dotenv import find_dotenv, load_dotenv

from agent.report import report_path, to_markdown
from agent.judge import JUDGE, JURY
from agent.run import StopRun, run_agent

load_dotenv(find_dotenv())  # finds the .env in the claude-agent-sdk-challenge folder


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Review a CV against a job ad.", usage=__doc__)
    parser.add_argument("job_ad")
    parser.add_argument("cv", nargs="?", default="cv.md")
    parser.add_argument("--no-checks", action="store_true", help="skip the final evidence and support checks")
    parser.add_argument("--jury", action="store_true", help="three judge models vote on each claim")
    parser.add_argument("--log", nargs="?", const="logs/last-run.jsonl", help="write every step to this log file")
    return parser.parse_args()


async def main(args: argparse.Namespace) -> None:
    run = await run_agent(args.job_ad, args.cv, checks=not args.no_checks, judges=JURY if args.jury else JUDGE,
                          log_path=args.log)
    path = report_path(run.report["role"], args.cv, suffix="no-checks" if args.no_checks else "")
    path.write_text(to_markdown(run.report))
    for line in run.report.get("removed", []):
        print(f"  · taken out: {line}")
    print(f"\nSaved {path} · {run.summary}\nYour tracker is in applications.csv")


if __name__ == "__main__":
    try:
        asyncio.run(main(parse_args()))
    except StopRun as stop:
        sys.exit(f"\n{stop}")
