"""Your weekly job shortlist: run the job-fit agent over a list of job ads and rank them.

Usage:
    uv run shortlist.py JOBS_LIST [CV] [--no-checks]

    JOBS_LIST   a text file with one job ad per line: a link, or a saved file
    CV          your CV (defaults to cv.md)

Example:
    uv run shortlist.py examples/jobs/this-week.txt examples/cvs/ops-coordinator.pdf

It writes shortlist.md (ranked), one report per job, and updates applications.csv.
"""
import argparse
import asyncio
import logging
import sys
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

from agent.run import StopRun, check_inputs
from agent.shortlist import read_job_list, shortlist, to_markdown_table

load_dotenv(find_dotenv())
# Parallel runs make Python's asyncio log a harmless "exit status already read" warning. Hide it.
logging.getLogger("asyncio").setLevel(logging.ERROR)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rank a list of job ads against your CV.", usage=__doc__)
    parser.add_argument("jobs_list")
    parser.add_argument("cv", nargs="?", default="cv.md")
    parser.add_argument("--no-checks", action="store_true", help="skip the final evidence and support checks")
    return parser.parse_args()


async def main(args: argparse.Namespace) -> None:
    if not Path(args.jobs_list).is_file():
        raise StopRun(f"Can't find your list at '{args.jobs_list}'. Make a text file with one job link per line.")
    jobs = read_job_list(args.jobs_list)
    for job in jobs:
        check_inputs(job, args.cv)  # stop before spending anything if a file is missing
    print(f"Assessing {len(jobs)} jobs, a few at a time...")
    outcomes = await shortlist(jobs, args.cv, checks=not args.no_checks)
    Path("shortlist.md").write_text(to_markdown_table(outcomes))
    print("\nSaved shortlist.md · your tracker is in applications.csv")


if __name__ == "__main__":
    try:
        asyncio.run(main(parse_args()))
    except StopRun as stop:
        sys.exit(f"\n{stop}")
