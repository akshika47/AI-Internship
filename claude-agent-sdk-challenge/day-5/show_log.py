"""Read a step log as a timeline, with the usual problems flagged.

Usage:
    uv run show_log.py logs/last-run.jsonl

Make a log with: uv run job_fit.py JOB_AD CV --log
Works on any agent's log in the same format (see agent/debug_log.py).
"""
import json
import sys
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
from itertools import groupby
from pathlib import Path

LOOP_LIMIT = 3      # more calls than this to one tool in a row: is it stuck?
SLOW_MS = 10_000    # a tool call slower than this is worth a look


@dataclass
class Step:
    n: int
    t: float
    tool: str
    input: str
    outcome: str = "none"   # "ok", "error" or "none" (no result came back)
    detail: str = ""
    ms: int | None = None


@dataclass
class Log:
    steps: list[Step] = field(default_factory=list)
    end: dict | None = None

    @classmethod
    def read(cls, path: Path) -> "Log":
        log, by_id = cls(), {}
        for line in path.read_text().splitlines():
            event = json.loads(line)
            kind = event["event"]
            if kind == "call":
                step = Step(len(log.steps) + 1, event["t"], event["tool"], event.get("input", ""))
                log.steps.append(step)
                by_id[event["id"]] = step
            elif kind in ("result", "error") and event.get("id") in by_id:
                step = by_id[event["id"]]
                step.outcome = "ok" if kind == "result" else "error"
                step.detail = event.get("output" if kind == "result" else "error", "")
                step.ms = event.get("ms")
            elif kind == "end":
                log.end = event
        return log


# ---- what to look at: each check returns lines to show, or nothing ------------------------

def loops(log: Log) -> list[str]:
    runs = [(tool, [s.n for s in group]) for tool, group in groupby(log.steps, key=lambda s: s.tool)]
    return [f"{tool} called {len(ns)} times in a row (steps {ns[0]}-{ns[-1]}): is it stuck?"
            for tool, ns in runs if len(ns) > LOOP_LIMIT]


def repeats(log: Log) -> list[str]:
    seen = Counter((s.tool, s.input) for s in log.steps)
    return [f"{tool} asked for the same thing {count} times: {inp[:60]}" for (tool, inp), count in seen.items() if count > 1]


def failures(log: Log) -> list[str]:
    return [f"step {s.n} {s.tool} failed: {s.detail[:120]}" for s in log.steps if s.outcome == "error"]


def no_result(log: Log) -> list[str]:
    return [f"step {s.n} {s.tool} got no result: a hook blocked it (your guard?) or the run stopped" for s in log.steps if s.outcome == "none"]


def slow(log: Log) -> list[str]:
    return [f"step {s.n} {s.tool} took {s.ms / 1000:.1f} s" for s in log.steps if s.ms and s.ms > SLOW_MS]


FLAGS: list[Callable[[Log], list[str]]] = [failures, no_result, loops, repeats, slow]
MARK = {"ok": "ok", "error": "ERROR", "none": "no result"}


def show(log: Log) -> str:
    lines = []
    for s in log.steps:
        took = f" ({s.ms} ms)" if s.ms is not None else ""
        lines.append(f"  {s.n:>2}  {s.t:6.1f}s  {s.tool}  {s.input[:90]}")
        lines.append(f"      → {MARK[s.outcome]}{took}  {s.detail[:90]}".rstrip())
    if log.end:
        e = log.end
        lines.append(f"\nRun ended: {e.get('turns')} turns · ${e.get('cost_usd', 0):.3f}")
        lines += [f"  blocked by the guard: {b}" for b in e.get("blocked", [])]
        lines += [f"  taken out by the checks: {c['claim']} ({c['why']})" for c in e.get("taken_out", [])]
    else:
        lines.append("\nNo end line: the run stopped before it finished. The last step above is where to look.")
    flagged = [line for flag in FLAGS for line in flag(log)]
    lines.append("\nWhat to look at:" if flagged else "\nNothing flagged. Still read the steps: did each one make sense?")
    lines += [f"  ! {line}" for line in flagged]
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) != 2 or not Path(sys.argv[1]).is_file():
        sys.exit(__doc__)
    log = Log.read(Path(sys.argv[1]))
    print(f"Step log: {sys.argv[1]} · {len(log.steps)} tool calls\n")
    print(show(log))
