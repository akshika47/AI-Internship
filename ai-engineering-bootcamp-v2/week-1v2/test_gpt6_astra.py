"""Smoke test for OpenAI's GPT-6 Astra (model ID: gpt-6-astra).

Uses the Responses API. Note GPT-6 Astra constraints:
  - no custom temperature / top_p
  - no reasoning effort "none"
  - tool calling requires the Responses API

Run:
  python test_gpt6_astra.py
  python test_gpt6_astra.py --prompt "Explain RAG in one sentence"
"""

import argparse
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import APIError, APIStatusError, OpenAI

THIS_DIR = Path(__file__).resolve().parent
load_dotenv(THIS_DIR / ".env")
load_dotenv(THIS_DIR.parent / ".env")

MODEL = "gpt-6-astra"


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test the gpt-6-astra model.")
    parser.add_argument(
        "--prompt",
        default="Reply with exactly: GPT-6 Astra is working.",
        help="Prompt to send to the model.",
    )
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        print("FAIL: OPENAI_API_KEY is not set.")
        print(f"      Add it to {THIS_DIR / '.env'} (see .env.example).")
        return 1

    client = OpenAI()

    print(f"Testing model : {MODEL}")
    print(f"Prompt        : {args.prompt!r}\n")

    start = time.perf_counter()
    try:
        response = client.responses.create(
            model=MODEL,
            input=args.prompt,
        )
    except APIStatusError as e:
        elapsed = time.perf_counter() - start
        print(f"FAIL: API returned HTTP {e.status_code} after {elapsed:.1f}s")
        print(f"      {e.message}")
        if e.status_code == 401:
            print("      -> Invalid API key. Check OPENAI_API_KEY in your .env.")
        elif e.status_code in (403, 404):
            print("      -> Your account may not have GPT-6 Astra access yet.")
            print("         Astra rolled out to Trusted Access Program enterprises")
            print("         first; general API access follows in the coming days.")
        return 1
    except APIError as e:
        print(f"FAIL: {e}")
        return 1

    elapsed = time.perf_counter() - start

    print("PASS: model responded")
    print(f"  latency : {elapsed:.1f}s")
    print(f"  model   : {response.model}")
    if response.usage:
        print(
            f"  tokens  : {response.usage.input_tokens} in / "
            f"{response.usage.output_tokens} out"
        )
    print(f"  output  : {response.output_text.strip()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
