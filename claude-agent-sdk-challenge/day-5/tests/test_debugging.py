"""Day 5's debugging tools, tested offline: no model, no key, no cost."""
import asyncio
import json
import sys
from pathlib import Path

import show_log
import starter_eval
from agent.debug_log import DebugLog
from tools.evidence import check_evidence, goes_on, problem_with, source_text, whole_sentence

CV = source_text(Path(__file__).parent.parent / "examples/cvs/ops-coordinator.md")


# ---- the bug Day 5 found, kept as a free test so it can't come back ----------------------

def test_a_quote_cut_at_a_line_wrap_is_flagged_with_the_rest_of_the_sentence():
    clipped = "Built a Google Sheets tracker for around 40 weekly deliveries, which cut missed driver"
    assert problem_with(clipped, CV) is None                       # the words are real...
    assert goes_on(clipped, CV).startswith("handovers from 9 a month to 2")  # ...but the sentence goes on


def test_a_whole_sentence_is_not_flagged():
    whole = "Built a Google Sheets tracker for around 40 weekly deliveries, which cut missed driver handovers from 9 a month to 2 within the first quarter."
    assert goes_on(whole, CV) is None


def test_the_judge_reads_the_whole_sentence_and_all_of_it_is_in_the_cv():
    clipped = "Built a Google Sheets tracker for around 40 weekly deliveries, which cut missed driver"
    finished = whole_sentence(clipped, CV)
    assert finished.endswith("within the first quarter.") and problem_with(finished, CV) is None


def test_check_evidence_makes_the_agent_fix_a_clipped_quote():
    cv_path = str(Path(__file__).parent.parent / "examples/cvs/ops-coordinator.md")
    clipped = "Built a Google Sheets tracker for around 40 weekly deliveries, which cut missed driver"
    reply = asyncio.run(check_evidence.handler({"source_path": cv_path, "quotes": [clipped]}))["content"][0]["text"]
    assert "stops mid-sentence" in reply and "handovers from 9 a month to 2" in reply and reply.endswith("check_evidence again.")


def test_goes_on_ignores_quotes_that_are_not_in_the_source():
    assert goes_on("Led a team of 20 for 5 years", CV) is None


# ---- the step log --------------------------------------------------------------------------

def logged_run(tmp_path: Path, events: list[tuple]) -> Path:
    """Drive the real hooks with fake inputs, as the SDK would."""
    log = DebugLog(tmp_path / "logs/run.jsonl")
    for kind, tool, tool_use_id, extra in events:
        hook = {"call": log.before, "result": log.after, "error": log.failed}[kind]
        asyncio.run(hook({"tool_name": tool, "tool_input": {"x": tool_use_id}, **extra}, tool_use_id, None))
    log.write("end", turns=3, cost_usd=0.05, blocked=["Read tried to open ../.env"], taken_out=[])
    return log.path


def test_the_hooks_write_one_line_per_event_in_order(tmp_path):
    path = logged_run(tmp_path, [("call", "Read", "a", {}), ("result", "Read", "a", {"tool_response": "hi", "duration_ms": 12})])
    events = [json.loads(line)["event"] for line in path.read_text().splitlines()]
    assert events == ["call", "result", "end"]


def test_long_results_are_cut_so_the_log_stays_readable(tmp_path):
    path = logged_run(tmp_path, [("call", "Read", "a", {}), ("result", "Read", "a", {"tool_response": "x" * 5000})])
    result = json.loads(path.read_text().splitlines()[1])
    assert len(result["output"]) < 500 and "more" not in result["output"] and "+4600 chars" in result["output"]


def test_hooks_put_the_log_before_your_own_guard(tmp_path):
    async def guard(*_):
        return {}
    hooks = DebugLog(tmp_path / "run.jsonl").hooks(extra_pre_tool_hooks=[guard])
    assert hooks["PreToolUse"][0].hooks[1] is guard and set(hooks) == {"PreToolUse", "PostToolUse", "PostToolUseFailure"}


def test_show_log_flags_a_failure_a_blocked_call_and_a_loop(tmp_path):
    events = [("call", "Read", "1", {}), ("error", "Read", "1", {"error": "File not found"}),  # a failure
              ("call", "Read", "2", {})]                                                     # no result: blocked
    events += [e for i in range(3, 8) for e in (("call", "Grep", str(i), {}), ("result", "Grep", str(i), {"tool_response": ""}))]  # 5 in a row
    text = show_log.show(show_log.Log.read(logged_run(tmp_path, events)))
    assert "Read failed: File not found" in text
    assert "step 2 Read got no result" in text
    assert "Grep called 5 times in a row" in text
    assert "blocked by the guard: Read tried to open ../.env" in text


def test_show_log_says_when_a_run_never_finished(tmp_path):
    path = tmp_path / "cut.jsonl"
    path.write_text(json.dumps({"t": 0, "event": "call", "id": "a", "tool": "Read", "input": "{}"}) + "\n")
    assert "the run stopped before it finished" in show_log.show(show_log.Log.read(path))


# ---- the eval runner -----------------------------------------------------------------------

def fake_agent(tmp_path: Path) -> str:
    """A stand-in 'agent' that prints a cost and a count, so evals can be tested for free."""
    script = tmp_path / "agent.py"
    script.write_text("import sys\n"
                      "if sys.argv[1] == 'missing':\n    sys.exit('Can\\'t find that file')\n"
                      "print(f'Saved report · 9 turns · $0.040 · {sys.argv[1]} claims removed')\n")
    return f"{sys.executable} {script} {{input}}"


def test_a_passing_case(tmp_path):
    case = starter_eval.Case("ok", "0", contains=["Saved"], not_contains=["Traceback"], max_cost_usd=0.10,
                             max_number={"pattern": r"(\d+) claims removed", "max": 1})
    outcome = starter_eval.run_case(case, fake_agent(tmp_path), tmp_path)
    assert outcome.passed and outcome.cost == 0.04


def test_each_kind_of_failure_is_explained(tmp_path):
    cmd = fake_agent(tmp_path)
    too_many = starter_eval.run_case(starter_eval.Case("n", "3", max_number={"pattern": r"(\d+) claims removed", "max": 1}), cmd, tmp_path)
    too_dear = starter_eval.run_case(starter_eval.Case("c", "0", max_cost_usd=0.01), cmd, tmp_path)
    wrong_exit = starter_eval.run_case(starter_eval.Case("e", "missing"), cmd, tmp_path)
    assert too_many.problems == ["3 is over the limit of 1 ((\\d+) claims removed)"]
    assert too_dear.problems == ["cost $0.040, over $0.01"]
    assert wrong_exit.problems == ["exited 1, expected 0"]


def test_an_expected_error_passes(tmp_path):
    case = starter_eval.Case("missing", "missing", exit_code=1, contains=["Can't find"])
    assert starter_eval.run_case(case, fake_agent(tmp_path), tmp_path).passed


def test_the_example_cases_file_loads():
    command, cwd, cases = starter_eval.load(Path(__file__).parent.parent / "evals/cases.json")
    assert "{input}" in command and cwd.name == "day-5" and len(cases) == 3
