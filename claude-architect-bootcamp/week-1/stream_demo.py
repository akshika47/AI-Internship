#!/usr/bin/env python3
"""Week 1 streaming demo — run outside Jupyter so deltas print in real time."""

from __future__ import annotations

import argparse
import json
import os
import sys

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-4-6"
DEFAULT_QUESTION = (
    "Explain in 3 sentences why streaming improves perceived latency."
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stream a Claude response to stdout (Week 1 live demo)."
    )
    parser.add_argument(
        "question",
        nargs="?",
        default=DEFAULT_QUESTION,
        help="User message to send (default: built-in demo question)",
    )
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Set ANTHROPIC_API_KEY in your environment or .env file.", file=sys.stderr)
        sys.exit(1)

    client = Anthropic(api_key=api_key)

    with client.messages.stream(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": args.question}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)

        message = stream.get_final_message()

    print("\n--- stream complete ---")
    print(f"stop_reason: {message.stop_reason}")
    print("usage:")
    print(json.dumps(message.usage.model_dump(), indent=2))


if __name__ == "__main__":
    main()
