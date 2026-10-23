"""A small eval for ANY agent: run it on a few inputs and check what comes back.

Usage:
    uv run starter_eval.py EVALS_JSON [--runs N]

You write the JSON (see evals/cases.json): the command that runs your agent, and a few cases.
Each case gives an input and what must be true afterwards:

    exit_code      what the command should exit with (0 = success)
    contains       text that must appear in the output (or in the file named by "file")
    not_contains   text that must NOT appear (e.g. "Traceback", a planted phrase)
    max_cost_usd   the most a run may cost; read from the last "$0.123" your agent prints
    max_number     {"pattern": "(\\d+) claims removed", "max": 1}: a number your agent prints must stay under a limit

Agents don't do the same thing every time, so --runs 3 runs each case three times: a case passes only if every
run passes. It runs your agent for real, so it costs what your runs cost. It exits 1 if any case fails, so you
can rerun it after every change.
"""
import argparse
import json
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

COST = re.compile(r"\$(\d+\.\d+)")
TIMEOUT_SECONDS = 300


@dataclass
class Case:
    name: str
    input: str
    exit_code: int = 0
    contains: list[str] = field(default_factory=list)
    not_contains: list[str] = field(default_factory=list)
    max_cost_usd: float | None = None
    max_number: dict | None = None  # {"pattern": regex with one (\d+) group, "max": int}
    file: str | None = None  # a glob: check the newest matching file's text instead of the printed output


@dataclass
class Outcome:
    case: Case
    problems: list[str]
    cost: float | None

    @property
    def passed(self) -> bool:
        return not self.problems


def run_case(case: Case, command: str, cwd: Path) -> Outcome:
    argv = [part.replace("{input}", case.input) for part in shlex.split(command)]
    try:
        done = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        return Outcome(case, [f"took longer than {TIMEOUT_SECONDS} s"], None)
    except FileNotFoundError:
        return Outcome(case, [f"can't start '{argv[0]}': is it installed?"], None)
    printed = done.stdout + done.stderr
    costs = COST.findall(printed)
    cost = float(costs[-1]) if costs else None
    text = printed
    if case.file:
        matches = sorted(cwd.glob(case.file), key=lambda p: p.stat().st_mtime)
        text = matches[-1].read_text(encoding="utf-8", errors="ignore") if matches else ""
    problems = [
        *([f"exited {done.returncode}, expected {case.exit_code}"] if done.returncode != case.exit_code else []),
        *([f"no file matches {case.file}"] if case.file and not text else []),
        *(f"missing: {want!r}" for want in case.contains if want not in text),
        *(f"should not contain: {bad!r}" for bad in case.not_contains if bad in text),
        *([f"cost ${cost:.3f}, over ${case.max_cost_usd:.2f}"] if cost is not None and case.max_cost_usd is not None and cost > case.max_cost_usd else []),
        *(["printed no cost to check"] if cost is None and case.max_cost_usd is not None else []),
        *number_problems(case, printed),
    ]
    return Outcome(case, problems, cost)


def number_problems(case: Case, printed: str) -> list[str]:
    if not case.max_number:
        return []
    found = re.findall(case.max_number["pattern"], printed)
    if not found:
        return [f"printed nothing matching {case.max_number['pattern']!r}"]
    value = int(found[-1])
    return [f"{value} is over the limit of {case.max_number['max']} ({case.max_number['pattern']})"] if value > case.max_number["max"] else []


def load(path: Path) -> tuple[str, Path, list[Case]]:
    spec = json.loads(path.read_text())
    cwd = (path.parent / spec.get("cwd", ".")).resolve()
    return spec["command"], cwd, [Case(**c) for c in spec["cases"]]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run your agent on a few cases and check the results.", usage=__doc__)
    parser.add_argument("evals_json")
    parser.add_argument("--runs", type=int, default=1, help="run each case this many times; all must pass")
    args = parser.parse_args()
    spec_path = Path(args.evals_json)
    if not spec_path.is_file():
        sys.exit(f"Can't find {spec_path}. Start from evals/cases.json.")
    command, cwd, cases = load(spec_path)
    print(f"{len(cases)} case{'s' * (len(cases) != 1)} × {args.runs} run{'s' * (args.runs != 1)} with: {command}\n")
    passed_cases, spent = 0, 0.0
    for case in cases:
        outcomes = [run_case(case, command, cwd) for _ in range(args.runs)]
        spent += sum(o.cost or 0 for o in outcomes)
        good = sum(o.passed for o in outcomes)
        passed_cases += good == len(outcomes)
        print(f"  {'✓' if good == len(outcomes) else '✗'} {good}/{len(outcomes)}  {case.name}")
        for i, outcome in enumerate(outcomes, 1):
            for problem in outcome.problems:
                print(f"      → run {i}: {problem}")
    print(f"\n{passed_cases} of {len(cases)} cases passed every run · ${spent:.2f} spent")
    sys.exit(0 if passed_cases == len(cases) else 1)
