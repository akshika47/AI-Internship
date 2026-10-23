"""Offline tests for ship_check: small agent folders built in a temp dir, no model, no key."""
import subprocess
from pathlib import Path

import ship_check

FAKE_KEY = "sk-ant-" + "api03-" + "x" * 40  # built at runtime so no key-shaped string sits in this file

READY_AGENT = """
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKError, query
options = ClaudeAgentOptions(tools=["Read"], max_turns=10, max_budget_usd=0.50)
try:
    ...
except ClaudeSDKError as error:
    print(f"The agent stopped: {error}")
print(f"{result.num_turns} turns, ${result.total_cost_usd:.3f}")
"""


def make(root: Path, files: dict[str, str]) -> Path:
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return root


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def git_repo(root: Path) -> None:
    git(root, "init", "-q")
    git(root, "-c", "user.name=t", "-c", "user.email=t@t", "add", "-A")
    git(root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init")


def by_check(results):
    return dict(zip([c.__name__ for c in ship_check.CHECKS], results))


def ready(tmp_path: Path) -> Path:
    return make(tmp_path, {
        "README.md": "# My agent\n\nRun it: `uv run my_agent.py examples/sample.md`\n",
        "examples/sample.md": "a sample input",
        ".env.example": "ANTHROPIC_API_KEY=sk-ant-...\n",
        ".gitignore": ".env\n",
        "my_agent.py": READY_AGENT,
        "tests/test_agent.py": "def test_ok():\n    assert True\n",
    })


def test_a_ready_agent_passes_everything(tmp_path):
    git_repo(ready(tmp_path))
    results = ship_check.ship_check(tmp_path)
    assert all(r.ok for r in results), [r.message for r in results if not r.ok]


def test_a_bare_agent_gets_a_fix_for_every_gap(tmp_path):
    make(tmp_path, {"agent.py": "print('hello')\n"})
    results = by_check(ship_check.ship_check(tmp_path))
    for name in ["readme", "sample_input", "env_example", "limits", "tools_locked", "readable_errors", "shows_cost", "rerunnable_check"]:
        assert results[name].ok is False and results[name].fix, name
    assert results["env_kept_private"].ok is None  # not a git repo: a note, not a failure


def test_allowed_tools_alone_does_not_count_as_restricted(tmp_path):
    make(tmp_path, {"agent.py": 'ClaudeAgentOptions(allowed_tools=["Read"])\n'})
    assert by_check(ship_check.ship_check(tmp_path))["tools_locked"].ok is False


def test_bypass_permissions_is_flagged(tmp_path):
    make(tmp_path, {"agent.py": 'ClaudeAgentOptions(tools=["Read"], permission_mode="bypassPermissions")\n'})
    result = by_check(ship_check.ship_check(tmp_path))["tools_locked"]
    assert result.ok is False and "bypass" in result.message


def test_typescript_options_are_understood(tmp_path):
    make(tmp_path, {"agent.ts": "const options = { tools: ['Read'], maxTurns: 10, maxBudgetUsd: 0.5 };\n"
                                "if (message.subtype !== 'success') console.log(message.totalCostUsd);\n"})
    results = by_check(ship_check.ship_check(tmp_path))
    assert results["tools_locked"].ok and results["limits"].ok and results["readable_errors"].ok and results["shows_cost"].ok


def test_a_key_written_in_a_shared_file_is_caught(tmp_path):
    ready(tmp_path)
    (tmp_path / "config.py").write_text(f'KEY = "{FAKE_KEY}"\n')
    git_repo(tmp_path)
    result = by_check(ship_check.ship_check(tmp_path))["no_keys_in_files"]
    assert result.ok is False and "config.py:1" in result.message
    assert FAKE_KEY not in result.message  # never echo the key itself


def test_a_key_only_in_an_ignored_env_is_fine(tmp_path):
    ready(tmp_path)
    (tmp_path / ".env").write_text(f"ANTHROPIC_API_KEY={FAKE_KEY}\n")
    git_repo(tmp_path)
    results = by_check(ship_check.ship_check(tmp_path))
    assert results["no_keys_in_files"].ok and results["env_kept_private"].ok


def test_a_committed_env_is_caught(tmp_path):
    ready(tmp_path)
    (tmp_path / ".gitignore").write_text("")
    (tmp_path / ".env").write_text("ANTHROPIC_API_KEY=placeholder\n")
    git_repo(tmp_path)
    result = by_check(ship_check.ship_check(tmp_path))["env_kept_private"]
    assert result.ok is False and ".env" in result.message


def test_env_example_is_found_in_a_parent_folder(tmp_path):
    make(tmp_path, {".env.example": "ANTHROPIC_API_KEY=sk-ant-...\n", "agent/README.md": "uv run agent.py\n"})
    git_repo(tmp_path)
    assert by_check(ship_check.ship_check(tmp_path / "agent"))["env_example"].ok


def test_a_real_key_in_env_example_is_caught(tmp_path):
    make(tmp_path, {".env.example": f"ANTHROPIC_API_KEY={FAKE_KEY}\n"})
    assert by_check(ship_check.ship_check(tmp_path))["env_example"].ok is False
