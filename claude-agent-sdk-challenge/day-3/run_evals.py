"""Measures the skill: runs each scenario with and without it and scores both the same way.

Usage:
    uv run run_evals.py [SCENARIOS]

    SCENARIOS   a JSON list of {"name", "job", "cv", "cv_text"}; defaults to examples/scenarios.json

The agent reads "cv" (a PDF, like a real one). "cv_text" is the same CV as plain text, used
only to check that every line the agent quotes is really in the CV.

Scores come from the same checks as the check_cv_bullets tool (tools/cv_check.py), plus one
honesty check: is every "from_cv" line really in the CV? Lower is better for problems.
Each scenario runs once per mode, so expect some variation between runs.
"""
import argparse
import asyncio
import logging
import json
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

from agent.run import Run, StopRun, run_agent
from tools.cv_check import missing_keywords, problems_in

load_dotenv(find_dotenv())
# Parallel runs make Python's asyncio log a harmless "exit status already read" warning. Hide it.
logging.getLogger("asyncio").setLevel(logging.ERROR)

AT_ONCE = 3


@dataclass(frozen=True)
class Measure:
    name: str
    score: Callable[[dict, str], float]  # (report, cv text) -> number
    better: str                          # "lower" or "higher"


def _count(kind: str) -> Callable[[dict, str], float]:
    """How many bullet problems of one kind the report has, e.g. 'duty phrase'."""
    return lambda report, cv: sum(p.startswith(kind) for b in report["cv_bullets"]
                                  for p in problems_in(b["from_cv"], b["rewritten"]))


def _not_quoted(report: dict, cv: str) -> float:
    """Honesty: a "from_cv" line that isn't really in the CV means the agent made it up."""
    normalise = lambda text: " ".join(text.lower().replace("*", "").split())
    return sum(normalise(b["from_cv"]).rstrip(".") not in normalise(cv) for b in report["cv_bullets"])


def _keyword_coverage(report: dict, cv: str) -> float:
    keywords = report["ad_keywords"]
    used = len(keywords) - len(missing_keywords([b["rewritten"] for b in report["cv_bullets"]], keywords))
    return round(100 * used / len(keywords)) if keywords else 0


MEASURES = [
    Measure("Duty phrases in bullets", _count("duty phrase"), "lower"),
    Measure("Weak openers in bullets", _count("weak opener"), "lower"),
    Measure("US spellings", _count("US spelling"), "lower"),
    Measure("Numbers not on the CV", _count("number"), "lower"),
    Measure("Bullets not quoted from the CV", _not_quoted, "lower"),
    Measure("Ad keywords used (%)", _keyword_coverage, "higher"),
]


@dataclass(frozen=True)
class Scenario:
    name: str
    job: str
    cv: str       # what the agent reads
    cv_text: str  # the same CV as text, for the honesty check


def load_scenarios(path: str) -> list[Scenario]:
    folder = Path(path).parent
    return [Scenario(s["name"], str(folder / s["job"]), str(folder / s["cv"]), str(folder / s.get("cv_text", s["cv"])))
            for s in json.loads(Path(path).read_text())]


async def run_one(scenario: Scenario, use_skill: bool, limit: asyncio.Semaphore) -> tuple[Scenario, bool, Run | None]:
    async with limit:
        try:
            run = await run_agent(scenario.job, scenario.cv, use_skill, show_steps=False)
        except StopRun:
            run = None
    print(f"  · {'with' if use_skill else 'without'} skill: {scenario.name}" + ("" if run else " (failed)"))
    return scenario, use_skill, run


def scores(run: Run | None, cv_path: str) -> list[float | None]:
    cv = Path(cv_path).read_text()
    return [m.score(run.report, cv) if run else None for m in MEASURES]


def table(results: list[tuple[Scenario, bool, Run | None]]) -> str:
    by_mode = {mode: [scores(run, s.cv_text) for s, m, run in results if m == mode] for mode in (False, True)}
    totals = {mode: [sum(row[i] or 0 for row in rows) for i in range(len(MEASURES))] for mode, rows in by_mode.items()}
    n = len(by_mode[True]) or 1
    rows = [f"| {m.name} | {fmt(m, totals[False][i], n)} | {fmt(m, totals[True][i], n)} | {m.better} is better |"
            for i, m in enumerate(MEASURES)]
    cost = {mode: sum(run.cost_usd for s, m, run in results if m == mode and run) for mode in (False, True)}
    return "\n".join([
        f"# Skill evaluation: {n} scenarios",
        "", "| Measure | Without skill | With skill | |", "|---|---|---|---|", *rows,
        f"| Cost | ${cost[False]:.2f} | ${cost[True]:.2f} | |", "",
    ])


def fmt(measure: Measure, total: float, n: int) -> str:
    """Percentages are averaged across scenarios; counts are added up."""
    return f"{total / n:.0f}%" if measure.name.endswith("(%)") else f"{total:g}"


async def main(path: str) -> None:
    scenarios = load_scenarios(path)
    print(f"Running {len(scenarios)} scenarios with and without the skill...")
    limit = asyncio.Semaphore(AT_ONCE)
    results = await asyncio.gather(*(run_one(s, mode, limit) for s in scenarios for mode in (False, True)))
    report = table(results)
    Path("eval-results.md").write_text(report)
    print("\n" + report + "\nSaved eval-results.md")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Measure the skill.", usage=__doc__)
    parser.add_argument("scenarios", nargs="?", default="examples/scenarios.json")
    try:
        asyncio.run(main(parser.parse_args().scenarios))
    except StopRun as stop:
        sys.exit(f"\n{stop}")
