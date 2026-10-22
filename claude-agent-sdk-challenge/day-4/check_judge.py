"""Checks the judge itself: runs it on cases where we know the right answer.

Usage:
    uv run check_judge.py [CASES] [--jury]

    CASES   a JSON list of {"question", "claim", "quote", "expected", "note", "user_question"?};
            defaults to evals/judge-cases.json

A judge you haven't tested is just another opinion. Add a case every time it gets one wrong,
and run this before you trust a change to its instructions. Costs about a cent.
"""
import argparse
import asyncio
import json
import sys
from itertools import groupby
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

from agent.judge import JUDGE, JURY, judge

load_dotenv(find_dotenv())


async def main(path: str, models: list[str]) -> bool:
    cases = json.loads(Path(path).read_text())
    by_question = lambda c: c.get("user_question", "")
    results, cost = [], 0.0
    # Cases that share a user question go to the judge together, with that question as context.
    for user_question, group in groupby(sorted(cases, key=by_question), key=by_question):
        group = list(group)
        verdicts, spent = await judge([(c["question"], c["claim"], c["quote"]) for c in group], models, user_question)
        results += zip(group, verdicts)
        cost += spent
    for case, verdict in results:
        mark = "right" if verdict.supported == case["expected"] else "WRONG"
        print(f"  {mark}  {'pass' if verdict.supported else 'fail'} ({verdict.votes})  {case['note']}")
    right = sum(v.supported == c["expected"] for c, v in results)
    print(f"\n{right} of {len(results)} right with {', '.join(models)} · ${cost:.3f}")
    return right == len(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check the judge on known cases.", usage=__doc__)
    parser.add_argument("cases", nargs="?", default="evals/judge-cases.json")
    parser.add_argument("--jury", action="store_true")
    args = parser.parse_args()
    sys.exit(0 if asyncio.run(main(args.cases, JURY if args.jury else JUDGE)) else 1)
