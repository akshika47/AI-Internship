"""The final gate: every claim in the report has to pass two checks, or it's taken out.

1. Evidence (code): its quote is really in the CV, word for word.
2. Support (a judge model): the quote actually backs up what the claim says.

This runs after the agent finishes, in plain Python, so the agent can't skip it or talk its
way past it. It's "no evidence, no pass", enforced rather than requested.
"""
from dataclasses import dataclass

from agent.judge import JUDGE, judge
from tools.evidence import problem_with, source_text, whole_sentence


@dataclass(frozen=True)
class Claim:
    kind: str    # "strength" or "bullet"
    index: int   # its position in that list in the report
    claim: str
    quote: str

    @property
    def question(self) -> str:
        """What the judge checks: a strength must be shown by its quote; a bullet must say only what its quote says."""
        return {"strength": "shows", "bullet": "says only"}[self.kind]


@dataclass(frozen=True)
class Check:
    claim: Claim
    evidence: str | None  # None means the quote was found
    supported: bool
    reason: str

    @property
    def passed(self) -> bool:
        return self.evidence is None and self.supported


@dataclass(frozen=True)
class Verification:
    checks: list[Check]
    cost_usd: float

    @property
    def failed(self) -> list[Check]:
        return [c for c in self.checks if not c.passed]


def claims_in(report: dict) -> list[Claim]:
    strengths = [Claim("strength", i, s["requirement"], s["cv_quote"]) for i, s in enumerate(report["strengths"])]
    bullets = [Claim("bullet", i, b["rewritten"], b["from_cv"]) for i, b in enumerate(report["cv_bullets"])]
    return strengths + bullets


async def verify(report: dict, cv_path: str, judges: list[str] = JUDGE) -> Verification:
    cv = source_text(cv_path)
    claims = claims_in(report)
    evidence = [problem_with(c.quote, cv) for c in claims]
    # Only claims with real quotes go to the judge: there's no point asking about a quote that doesn't exist.
    to_judge = [c for c, problem in zip(claims, evidence) if problem is None]
    # The judge reads each quote finished to the end of its sentence (all real CV text), so a quote cut at a
    # line wrap can't make a true claim look unsupported. Found with the Day 5 step log.
    verdicts, cost = await judge([(c.question, c.claim, whole_sentence(c.quote, cv)) for c in to_judge], judges)
    by_claim = dict(zip(to_judge, verdicts))
    checks = [Check(c, problem, by_claim[c].supported if c in by_claim else False,
                    by_claim[c].reason if c in by_claim else "quote not in the CV")
              for c, problem in zip(claims, evidence)]
    return Verification(checks, cost)


def without_failures(report: dict, verification: Verification) -> dict:
    """The report with every failed claim taken out, and a record of what was removed and why."""
    dropped = {(c.claim.kind, c.claim.index) for c in verification.failed}
    keep = lambda kind, items: [item for i, item in enumerate(items) if (kind, i) not in dropped]
    return {
        **report,
        "strengths": keep("strength", report["strengths"]),
        "cv_bullets": keep("bullet", report["cv_bullets"]),
        "removed": [f"{c.claim.claim}: {c.evidence or c.reason}" for c in verification.failed],
    }
