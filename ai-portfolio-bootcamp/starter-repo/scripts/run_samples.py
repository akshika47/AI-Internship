#!/usr/bin/env python3
"""Run the sample inputs end to end and print the outputs.

This is the one-command run. It is what the setup checklist asks you to get
working, and what a grader runs from a clean checkout.

    python scripts/run_samples.py
    python scripts/run_samples.py --limit 5 --input data/sample_inputs.jsonl
"""

from __future__ import annotations

import argparse
import json
import logging
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from src.config import load_config  # noqa: E402
from src.logging_setup import setup_logging  # noqa: E402
from src.pipeline import Pipeline  # noqa: E402
from src.schema import TicketInput  # noqa: E402

log = logging.getLogger("run_samples")


def read_records(path: pathlib.Path, limit: int) -> list[TicketInput]:
    if not path.exists():
        raise SystemExit(f"Input file not found: {path}")

    records: list[TicketInput] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            records.append(TicketInput(**json.loads(line)))
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            raise SystemExit(f"{path}:{lineno} is not a valid record: {exc}") from exc
        if len(records) >= limit:
            break

    if not records:
        raise SystemExit(f"No records found in {path}")
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="data/sample_inputs.jsonl")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--json", action="store_true", help="Print JSON only.")
    args = parser.parse_args()

    config = load_config()
    setup_logging(config.log_level)

    if config.offline:
        print(
            "No ANTHROPIC_API_KEY found - running the offline stub.\n"
            "The harness works, but these are not real predictions.\n"
            "Copy .env.example to .env and add your key for the real thing.\n",
            file=sys.stderr,
        )

    records = read_records(pathlib.Path(args.input), args.limit)
    pipeline = Pipeline(config)

    started = time.perf_counter()
    outputs = [pipeline.run(record) for record in records]
    total_ms = round((time.perf_counter() - started) * 1000)

    if args.json:
        print(json.dumps([o.model_dump(mode="json") for o in outputs], indent=2))
    else:
        for out in outputs:
            flag = "  <-- needs human" if out.needs_human else ""
            print(f"\n{out.id}  [{out.priority.value}] {out.category.value}{flag}")
            print(f"  summary    : {out.summary}")
            print(f"  confidence : {out.confidence:.2f}")
            print(f"  reason     : {out.reason}")

    escalated = sum(1 for o in outputs if o.needs_human)
    print(
        f"\n{len(outputs)} records in {total_ms} ms. "
        f"{escalated} flagged for human review.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
