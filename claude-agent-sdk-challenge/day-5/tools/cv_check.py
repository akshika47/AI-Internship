"""check_cv_bullets: finds the CV mistakes that have a clear right answer, with code, not opinion.

The skill tells the agent to draft bullets, run this, fix what it reports, and run it again.
The same checks score run_evals.py, so "better" is measured the same way twice.
"""
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from claude_agent_sdk import ToolAnnotations, tool

DUTY_PHRASES = ("responsible for", "duties included", "tasked with", "in charge of")
WEAK_OPENERS = ("helped", "assisted", "worked on", "tried", "attempted", "involved in", "participated")
US_SPELLINGS = {  # US stem -> UK stem, so "optimizing" and "organized" are caught too
    "optimiz": "optimis", "organiz": "organis", "analyz": "analys", "prioritiz": "prioritis",
    "utiliz": "utilis", "standardiz": "standardis", "behavior": "behaviour", "color": "colour",
    "center": "centre", "modeling": "modelling", "favorit": "favourit",
}
MAX_WORDS = 30  # a bullet longer than this stops being skimmable
NUMBER = re.compile(r"\d[\d,.]*")


@dataclass(frozen=True)
class Check:
    name: str
    finds: Callable[[str, str], list[str]]  # (original, rewritten) -> problems found


def _duty_phrases(original: str, rewritten: str) -> list[str]:
    return [f'duty phrase "{p}"' for p in DUTY_PHRASES if p in rewritten.lower()]


def _weak_opener(original: str, rewritten: str) -> list[str]:
    first_words = rewritten.lower().split(maxsplit=2)[:2]
    return [f'weak opener "{w}"' for w in WEAK_OPENERS if " ".join(first_words).startswith(w)]


def _us_spelling(original: str, rewritten: str) -> list[str]:
    words = re.findall(r"[a-z]+", rewritten.lower())
    return [f'US spelling "{w}" (use "{US_SPELLINGS[stem] + w[len(stem):]}")'
            for w in words for stem in US_SPELLINGS if w.startswith(stem)]


def _invented_numbers(original: str, rewritten: str) -> list[str]:
    on_cv = {n.strip(".,") for n in NUMBER.findall(original)}
    return [f'number "{n}" is not in the CV line' for n in {n.strip(".,") for n in NUMBER.findall(rewritten)} - on_cv]


def _too_long(original: str, rewritten: str) -> list[str]:
    words = len(rewritten.split())
    return [f"{words} words (keep it under {MAX_WORDS})"] if words > MAX_WORDS else []


CHECKS = [
    Check("duty phrases", _duty_phrases),
    Check("weak openers", _weak_opener),
    Check("US spellings", _us_spelling),
    Check("invented numbers", _invented_numbers),
    Check("too long", _too_long),
]


def problems_in(original: str, rewritten: str) -> list[str]:
    return [problem for check in CHECKS for problem in check.finds(original, rewritten)]


def missing_keywords(rewrites: list[str], keywords: list[str]) -> list[str]:
    text = " ".join(rewrites).lower()
    return [k for k in keywords if k.lower() not in text]


def review(bullets: list[dict[str, str]], keywords: list[str]) -> str:
    """The text the agent reads back: one line per bullet, then keyword coverage, then a verdict."""
    lines = [f"{i}. {', '.join(problems_in(b['from_cv'], b['rewritten'])) or 'OK'}"
             for i, b in enumerate(bullets, 1)]
    missing = missing_keywords([b["rewritten"] for b in bullets], keywords)
    covered = len(keywords) - len(missing)
    lines.append(f"Ad keywords used: {covered} of {len(keywords)}"
                 + (f" (not used: {', '.join(missing)}; fine if the CV can't honestly support them)" if missing else ""))
    clean = all(line.endswith("OK") for line in lines[:-1])
    lines.append("PASS" if clean else "FIX the issues above, then run check_cv_bullets again.")
    return "\n".join(lines)


@tool(
    "check_cv_bullets",
    "Check rewritten CV bullets for duty phrases, weak openers, US spellings, numbers that "
    "aren't in the original CV line, and length; and report which of the job ad's keywords "
    "they use. Run it after drafting bullets and again after every fix, until it says PASS.",
    {
        "type": "object",
        "properties": {
            "bullets": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "from_cv": {"type": "string", "description": "The original CV line, quoted exactly"},
                        "rewritten": {"type": "string", "description": "Your rewrite of that line"},
                    },
                    "required": ["from_cv", "rewritten"],
                },
            },
            "ad_keywords": {"type": "array", "items": {"type": "string"},
                            "description": "Short keywords from the ad's essential requirements, e.g. Python, Zapier"},
        },
        "required": ["bullets", "ad_keywords"],
    },
    annotations=ToolAnnotations(readOnlyHint=True),  # it only reads what you pass it
)
async def check_cv_bullets(args: dict[str, Any]) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": review(args["bullets"], args["ad_keywords"])}]}
