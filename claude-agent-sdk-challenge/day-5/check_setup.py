"""Checks your setup before you spend anything. Run: uv run check_setup.py

Each check returns a Result. It doesn't test your API key against the API; your first
real run does that.
"""
import importlib.metadata
import os
import sys
from dataclasses import dataclass
from pathlib import Path

PLACEHOLDER = "sk-ant-..."
ICONS = {True: "✓", False: "✗", None: "·"}  # None is a note, not a problem


@dataclass(frozen=True)
class Result:
    ok: bool | None
    message: str


def python_version() -> Result:
    version = sys.version.split()[0]
    ok = sys.version_info >= (3, 10)
    return Result(ok, f"Python {version}" if ok else f"Python {version} is too old. Run this with: uv run check_setup.py")


def sdk_installed() -> Result:
    try:
        return Result(True, f"Claude Agent SDK {importlib.metadata.version('claude-agent-sdk')} installed")
    except importlib.metadata.PackageNotFoundError:
        return Result(False, "Claude Agent SDK not found. Run this with: uv run check_setup.py")


def api_key() -> Result:
    from dotenv import find_dotenv, load_dotenv

    env_file = find_dotenv(usecwd=True)  # looks here, then in each folder above
    load_dotenv(env_file)
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    old_env = next((f"{p.parent.name}/.env" for p in Path("..").glob("day-*/.env")), "")  # Day 1 used day-1/.env
    problems = [
        (not env_file and not key and bool(old_env),
         f"Your key is in {old_env}, but it now lives one folder up. "
         f"From claude-agent-sdk-challenge, run: mv {old_env} .env"),
        (not env_file and not key, "No .env file yet. In the claude-agent-sdk-challenge folder, run: "
                                   "cp .env.example .env  then put your key in it."),
        (key in ("", PLACEHOLDER), f".env still has the placeholder. Open {env_file} and replace {PLACEHOLDER} with your key."),
        (not key.startswith("sk-ant-"), "That doesn't look like an Anthropic key (they start with sk-ant-). Copy it again."),
    ]
    first_problem = next((message for failed, message in problems if failed), None)
    return Result(first_problem is None, first_problem or f"API key found in {env_file}")


def cv_found() -> Result:
    cvs = sorted(p.name for p in Path(".").glob("cv.*"))
    return Result(True, f"Your CV: {', '.join(cvs)}") if cvs else \
        Result(None, "No CV yet. Save yours here as cv.md or cv.pdf when you're ready.")


CHECKS = [python_version, sdk_installed, api_key, cv_found]

if __name__ == "__main__":
    print(f"Checking your setup in {Path.cwd().name}...\n")
    results = [check() for check in CHECKS]
    for result in results:
        print(f"  {ICONS[result.ok]} {result.message}")
    problems = sum(result.ok is False for result in results)
    if problems:
        sys.exit(f"\nFix the ✗ line{'s' * (problems > 1)} above, then run this again.")
    print("\nAll set. Try: uv run job_fit.py examples/jobs/fernhill-automation-analyst.md examples/cvs/ops-coordinator.md")
