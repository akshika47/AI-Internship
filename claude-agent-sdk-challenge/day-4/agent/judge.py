"""A judge: does each quote actually support the claim made from it?

Code can prove a quote is in the CV (tools/evidence.py). It can't tell whether the claim goes
further than the quote does: "Wrote a monthly summary" doesn't support "turned marketing data
into plain recommendations for non-specialists". That takes reading, so a separate model call,
with no tools and one narrow job, checks it.

A jury asks three different models and takes the majority, which agrees with people more
often and leans less on one model's quirks (Verga et al., 2024, "Replacing Judges with Juries").
"""
import asyncio
import json
from dataclasses import dataclass

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query

JUDGE = ["sonnet"]
JURY = ["haiku", "sonnet", "opus"]

INSTRUCTIONS = """You check claims against the exact source text they cite. Each item has a
"question" telling you which check it needs. Answer it from the quote alone.

"shows": does the quote show real evidence of the requirement? Level words in the requirement
("basic", "some", "nice to have", "essential") describe the job, not the candidate: ignore them.
Supported if the quote clearly demonstrates it; not supported if the quote only hints, or needs
an assumption to get there.

"says only": does the rewrite say only what the quote says? Rewording, reordering,
shortening and changing tense ("Write" to "Wrote", "Responsible for X" to "Ran X") are fine,
and so is linking two things the quote states side by side ("Rebuilt X; cut Y" to "Cut Y by
rebuilding X"). Not supported if it adds anything the quote doesn't say: a result,
number, audience, purpose, skill, scope or seniority, even if it sounds plausible.

"follows": does the claim follow from the quote, applied to the facts in the user's question?
Applying a stated rule to their situation (their country, their dates) and simple arithmetic
are fine. Not supported if it needs a fact that neither the quote nor the question gives.

Judge only the text given. Don't use outside knowledge, and don't give the benefit of the doubt."""

VERDICTS_SCHEMA = {
    "type": "object",
    "properties": {
        "verdicts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "supported": {"type": "boolean"},
                    "reason": {"type": "string", "description": "One short sentence"},
                },
                "required": ["id", "supported", "reason"],
            },
        }
    },
    "required": ["verdicts"],
}


@dataclass(frozen=True)
class Verdict:
    supported: bool
    reason: str
    votes: str  # e.g. "2 of 3" for a jury, "1 of 1" for one judge


async def _one_judge(model: str, items: list[dict]) -> tuple[dict[int, dict], float]:
    options = ClaudeAgentOptions(
        system_prompt=INSTRUCTIONS, model=model, tools=[], setting_sources=[],
        output_format={"type": "json_schema", "schema": VERDICTS_SCHEMA}, max_turns=3, max_budget_usd=0.25,
    )
    result = None
    async for message in query(prompt=json.dumps(items, indent=1), options=options):
        if isinstance(message, ResultMessage):
            result = message
    verdicts = (result.structured_output or {}).get("verdicts", []) if result else []
    return {v["id"]: v for v in verdicts}, (result.total_cost_usd or 0) if result else 0


async def judge(items_in: list[tuple[str, str, str]], models: list[str] = JUDGE,
                user_question: str = "") -> tuple[list[Verdict], float]:
    """items_in: (question, claim, quote), where question is "shows", "says only" or "follows".
    user_question gives the facts a "follows" claim may apply the quote to.
    Returns one verdict per item, by majority across the models, plus the cost."""
    if not items_in:
        return [], 0.0
    items = [{"id": i, "question": q, "claim": claim, "quote": quote} for i, (q, claim, quote) in enumerate(items_in)]
    items = [{**item, "user_question": user_question} for item in items] if user_question else items
    ballots = await asyncio.gather(*(_one_judge(model, items) for model in models))  # jury members vote in parallel
    cost = sum(c for _, c in ballots)
    verdicts = []
    for i in range(len(items)):
        votes = [b[i] for b, _ in ballots if i in b]
        yes = sum(v["supported"] for v in votes)
        majority = yes * 2 > len(models)  # a missing vote counts as a no: no evidence, no pass
        reason = next((v["reason"] for v in votes if v["supported"] == majority), "no verdict returned")
        verdicts.append(Verdict(majority, reason, f"{yes} of {len(models)}"))
    return verdicts, cost
