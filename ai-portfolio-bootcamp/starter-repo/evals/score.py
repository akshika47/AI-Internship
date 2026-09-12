#!/usr/bin/env python3
"""Score the system against the golden set.

    python evals/score.py
    python evals/score.py --golden evals/golden_set.jsonl --out runs/week2.json

Prints per-metric and per-slice numbers, and a failure list you can paste
straight into the taxonomy section of your eval report.

This is deliberately simple exact-match scoring. If your task needs a judge,
you have to add one, and report its agreement rate against your hand labels.
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from src.config import load_config  # noqa: E402
from src.logging_setup import setup_logging  # noqa: E402
from src.pipeline import Pipeline  # noqa: E402
from src.schema import TicketInput  # noqa: E402

SCORED_FIELDS = ("category", "priority", "needs_human")


def percentile(values, pct):
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(int(round((pct / 100.0) * (len(ordered) - 1))), len(ordered) - 1)
    return ordered[idx]


def load_golden(path):
    if not path.exists():
        raise SystemExit("Golden set not found: {}".format(path))
    cases = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            case = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit("{}:{} is not valid JSON: {}".format(path, lineno, exc)) from exc
        if "expected" not in case:
            raise SystemExit("{}:{} has no 'expected' block.".format(path, lineno))
        cases.append(case)
    if not cases:
        raise SystemExit(
            "{} is empty. Hand-label your cases before scoring - "
            "that is the assignment, not a prerequisite for it.".format(path)
        )
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--golden", default="evals/golden_set.jsonl")
    parser.add_argument("--out", default=None, help="Write full results as JSON.")
    args = parser.parse_args()

    config = load_config()
    setup_logging(config.log_level)

    if config.offline:
        print("WARNING: no API key - scoring the offline stub, not your system.\n", file=sys.stderr)

    cases = load_golden(pathlib.Path(args.golden))
    pipeline = Pipeline(config)

    hits = collections.Counter()
    totals = collections.Counter()
    slice_hits = collections.defaultdict(collections.Counter)
    slice_totals = collections.defaultdict(collections.Counter)
    p1_expected = 0
    p1_caught = 0
    failures = []
    latencies = []
    results = []

    for case in cases:
        record = TicketInput(id=case["id"], subject=case["subject"], body=case["body"])
        expected = case["expected"]
        slice_name = case.get("slice", "unsliced")

        started = time.perf_counter()
        actual = pipeline.run(record)
        latencies.append((time.perf_counter() - started) * 1000)

        actual_dict = actual.model_dump(mode="json")
        case_failures = []

        for field in SCORED_FIELDS:
            if field not in expected:
                continue
            totals[field] += 1
            slice_totals[slice_name][field] += 1
            if actual_dict[field] == expected[field]:
                hits[field] += 1
                slice_hits[slice_name][field] += 1
            else:
                case_failures.append(
                    {"field": field, "expected": expected[field], "actual": actual_dict[field]}
                )

        if expected.get("priority") == "P1":
            p1_expected += 1
            if actual_dict["priority"] == "P1":
                p1_caught += 1

        if case_failures:
            failures.append(
                {
                    "id": case["id"],
                    "slice": slice_name,
                    "subject": case["subject"],
                    "misses": case_failures,
                    "model_reason": actual_dict["reason"],
                }
            )

        results.append({"id": case["id"], "expected": expected, "actual": actual_dict})

    print("\nGolden set: {} cases from {}".format(len(cases), args.golden))
    print("Mode: {}\n".format("OFFLINE STUB" if config.offline else config.model))

    print("Overall")
    for field in SCORED_FIELDS:
        if totals[field]:
            rate = hits[field] / totals[field]
            print("  {:<12} {:>3}/{:<3} {:6.1%}".format(field, hits[field], totals[field], rate))
    if p1_expected:
        print(
            "  {:<12} {:>3}/{:<3} {:6.1%}   <- the expensive failure".format(
                "P1 recall", p1_caught, p1_expected, p1_caught / p1_expected
            )
        )

    if len(slice_totals) > 1:
        print("\nBy slice")
        for slice_name in sorted(slice_totals):
            print("  {}".format(slice_name))
            for field in SCORED_FIELDS:
                total = slice_totals[slice_name][field]
                if total:
                    rate = slice_hits[slice_name][field] / total
                    print(
                        "    {:<12} {:>3}/{:<3} {:6.1%}".format(
                            field, slice_hits[slice_name][field], total, rate
                        )
                    )

    print(
        "\nLatency  p50 {:.0f} ms   p95 {:.0f} ms".format(
            percentile(latencies, 50), percentile(latencies, 95)
        )
    )

    if failures:
        print("\nFailures ({}) - group these into named categories".format(len(failures)))
        for failure in failures:
            print("\n  {} [{}] {}".format(failure["id"], failure["slice"], failure["subject"]))
            for miss in failure["misses"]:
                print(
                    "    {}: expected {}, got {}".format(
                        miss["field"], miss["expected"], miss["actual"]
                    )
                )
            print("    model said: {}".format(failure["model_reason"]))
    else:
        print("\nNo failures. If the golden set is small, that means it is too easy.")

    if args.out:
        out_path = pathlib.Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(
                {
                    "model": "offline-stub" if config.offline else config.model,
                    "cases": len(cases),
                    "overall": {
                        f: {"hits": hits[f], "total": totals[f]} for f in SCORED_FIELDS
                    },
                    "p1_recall": {"caught": p1_caught, "expected": p1_expected},
                    "latency_ms": {
                        "p50": percentile(latencies, 50),
                        "p95": percentile(latencies, 95),
                    },
                    "results": results,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print("\nWrote {}".format(out_path))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
