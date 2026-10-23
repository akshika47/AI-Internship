"""Starter: an agent that answers from a document, where every claim must quote it and pass two checks.

Usage:
    uv run starter_verify.py SOURCE "your question" [--no-checks] [--jury]

Example:
    uv run starter_verify.py examples/documents/policy.md "Can I work from Spain for three weeks this summer?"

This is "no evidence, no pass" for any agent that answers from sources (a RAG assistant, a
policy bot, a research helper). The agent must return each claim with an exact quote. Then:
    1. code checks the quote is really in the document
    2. a judge model checks the quote actually supports the claim
Claims that fail either check are shown as taken out, with the reason.
"""
import argparse
import asyncio
import sys
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKError, HookMatcher, ResultMessage, query

from agent.guard import Guard
from agent.judge import JUDGE, JURY, judge
from tools.evidence import problem_with, source_text

load_dotenv(find_dotenv())

PROMPT = """Answer the user's question using only the document they give you. Read it first.
Break your answer into short claims. Every claim needs a quote copied word for word from the
document (use … to skip words). If the document doesn't answer something, say so as a claim
with an empty quote rather than guessing."""

ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "claims": {"type": "array", "items": {
            "type": "object",
            "properties": {"claim": {"type": "string"}, "quote": {"type": "string"}},
            "required": ["claim", "quote"],
        }},
    },
    "required": ["claims"],
}


def options(source: Path) -> ClaudeAgentOptions:
    guard = Guard(files={source}, links=set(), skills_folder=source.parent / "no-skills")  # this document only
    return ClaudeAgentOptions(
        system_prompt=PROMPT, tools=["Read"], allowed_tools=["Read"], setting_sources=[],
        output_format={"type": "json_schema", "schema": ANSWER_SCHEMA},
        hooks={"PreToolUse": [HookMatcher(hooks=[guard])]},
        model="sonnet", max_turns=6, max_budget_usd=0.50,
    )


async def main(args: argparse.Namespace) -> None:
    source = Path(args.source).resolve()
    if not source.is_file():
        sys.exit(f"Can't find {args.source}.")
    try:
        result = None
        async for message in query(prompt=f"Document: {source}\nQuestion: {args.question}", options=options(source)):
            if isinstance(message, ResultMessage):
                result = message
    except ClaudeSDKError as error:
        sys.exit(f"The agent couldn't run: {error}")
    claims = (result.structured_output or {}).get("claims", []) if result else []
    text = source_text(source)

    gaps = [c for c in claims if not c["quote"]]          # "the document doesn't say": honest, not a failure
    quoted = [c for c in claims if c["quote"]]
    evidence = [problem_with(c["quote"], text) for c in quoted]
    to_judge = [(i, c) for i, (c, problem) in enumerate(zip(quoted, evidence)) if problem is None]
    verdicts, judge_cost = ([], 0.0) if args.no_checks else await judge(
        [("follows", c["claim"], c["quote"]) for _, c in to_judge], JURY if args.jury else JUDGE, args.question)
    rejected = {i: v.reason for (i, _), v in zip(to_judge, verdicts) if not v.supported}

    reasons = [None if args.no_checks else (problem or rejected.get(i)) for i, problem in enumerate(evidence)]
    for claim, why in zip(quoted, reasons):
        print(f"{'  taken out' if why else '  passed  '}  {claim['claim']}")
        print(f"              quote: \"{claim['quote']}\"" + (f"\n              why: {why}" if why else ""))
    for claim in gaps:
        print(f"  not in doc  {claim['claim']}")
    cost = (result.total_cost_usd or 0 if result else 0) + judge_cost
    print(f"\n{len(quoted)} quoted claims · {reasons.count(None)} passed · {len(gaps)} gaps the document doesn't cover · ${cost:.3f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Answer from a document, with every claim checked.", usage=__doc__)
    parser.add_argument("source")
    parser.add_argument("question")
    parser.add_argument("--no-checks", action="store_true")
    parser.add_argument("--jury", action="store_true")
    asyncio.run(main(parser.parse_args()))
