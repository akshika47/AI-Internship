"""Offline tests: no API calls, no cost. CI runs these on every pull request.

Each failure we found while building becomes a test here, so it can't quietly come back.
"""
import asyncio
from pathlib import Path

import pytest

import agent.judge as judge_module
from agent.guard import Guard
from agent.verify import Check, Claim, Verification, without_failures
from run_evals import followed
from tools.cv_check import problems_in
from tools.evidence import problem_with, source_text

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


# --- check_cv_bullets ---------------------------------------------------------------------

@pytest.mark.parametrize("original, rewrite, expected", [
    ("Responsible for weekly reporting", "Responsible for optimizing weekly reporting", ["duty phrase", "US spelling"]),
    ("Wrote Python scripts", "Helped automate scripts, saving 40% of time", ["weak opener", "number"]),
    ("Cut handovers from 9 a month to 2", "Cut missed handovers from 9 a month to 2", []),
])
def test_bullet_checks(original, rewrite, expected):
    found = problems_in(original, rewrite)
    assert len(found) == len(expected)
    assert all(any(problem.startswith(kind) for problem in found) for kind in expected)


# --- evidence: is the quote really in the CV? --------------------------------------------

@pytest.fixture(scope="module")
def daniel_cv() -> str:
    return source_text(EXAMPLES / "cvs" / "career-changer.pdf")  # a two-column PDF, the hardest layout to read


def test_real_quote_passes_even_from_a_two_column_pdf(daniel_cv):
    assert problem_with("Rebuilt the marketing dashboard in Looker Studio on BigQuery", daniel_cv) is None


def test_quote_with_ellipsis_passes(daniel_cv):
    assert problem_with("Used the OpenAI API … to tag 6,000 product reviews by theme", daniel_cv) is None


def test_the_day_3_failure_is_not_in_the_cv(daniel_cv):
    problem = problem_with("turning marketing data into plain recommendations for non-specialists", daniel_cv)
    assert problem and problem.startswith("not in the source")


def test_one_word_quotes_prove_nothing(daniel_cv):
    assert "too short" in problem_with("Python", daniel_cv)


# --- the guardrail -------------------------------------------------------------------------

def guard(tmp: Path) -> Guard:
    return Guard(files={(tmp / "cv.pdf").resolve()}, links={"https://example.com/job"}, skills_folder=tmp / "skills")


def decision(g: Guard, tool: str, args: dict) -> str:
    out = asyncio.run(g(({"tool_name": tool, "tool_input": args}), None, None))
    return out.get("hookSpecificOutput", {}).get("permissionDecision", "allow")


def test_guard_allows_the_cv_and_skill_files(tmp_path):
    g = guard(tmp_path)
    assert decision(g, "Read", {"file_path": str(tmp_path / "cv.pdf")}) == "allow"
    assert decision(g, "Read", {"file_path": str(tmp_path / "skills" / "reviewing-cvs" / "SKILL.md")}) == "allow"


def test_guard_blocks_the_env_file_a_job_ad_asked_for(tmp_path):
    g = guard(tmp_path)
    assert decision(g, "Read", {"file_path": str(tmp_path / ".." / ".env")}) == "deny"
    assert g.blocked and ".env" in g.blocked[0]


def test_guard_blocks_other_links(tmp_path):
    g = guard(tmp_path)
    assert decision(g, "mcp__jobfit__fetch_job_ad", {"url": "https://example.com/job"}) == "allow"
    assert decision(g, "mcp__jobfit__fetch_job_ad", {"url": "https://attacker.example/collect"}) == "deny"


# --- trajectory ----------------------------------------------------------------------------

def test_workflow_in_order_scores_full_marks():
    steps = ["Skill", "Read", "Read", "mcp__jobfit__check_tracker", "mcp__jobfit__check_cv_bullets",
             "mcp__jobfit__check_cv_bullets", "mcp__jobfit__check_evidence", "mcp__jobfit__save_to_tracker", "StructuredOutput"]
    assert followed(steps) == 1.0


def test_skipping_the_checks_loses_marks():
    steps = ["Skill", "Read", "mcp__jobfit__check_tracker", "mcp__jobfit__save_to_tracker", "StructuredOutput"]
    assert followed(steps) == pytest.approx(5 / 7)


# --- the final gate and the jury -----------------------------------------------------------

def test_failed_claims_are_taken_out_and_explained():
    report = {"strengths": [{"requirement": "SQL", "cv_quote": "x"}, {"requirement": "Team lead", "cv_quote": "y"}],
              "cv_bullets": []}
    checks = [Check(Claim("strength", 0, "SQL", "x"), None, True, "ok"),
              Check(Claim("strength", 1, "Team lead", "y"), None, False, "quote doesn't show leading a team")]
    cleaned = without_failures(report, Verification(checks, 0.0))
    assert [s["requirement"] for s in cleaned["strengths"]] == ["SQL"]
    assert cleaned["removed"] == ["Team lead: quote doesn't show leading a team"]


def test_jury_majority_and_missing_votes_count_against(monkeypatch):
    ballots = {"a": {0: {"supported": True, "reason": "yes"}, 1: {"supported": True, "reason": "yes"}},
               "b": {0: {"supported": True, "reason": "yes"}, 1: {"supported": False, "reason": "no"}},
               "c": {0: {"supported": False, "reason": "no"}}}  # c returned nothing for item 1

    async def fake_judge(model, items):
        return ballots[model], 0.0

    monkeypatch.setattr(judge_module, "_one_judge", fake_judge)
    verdicts, _ = asyncio.run(judge_module.judge([("says only", "c1", "q1"), ("says only", "c2", "q2")], ["a", "b", "c"]))
    assert verdicts[0].supported is True      # 2 of 3 yes
    assert verdicts[1].supported is False     # 1 yes, 1 no, 1 missing: no majority
