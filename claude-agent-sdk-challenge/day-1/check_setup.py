"""Checks your setup before you spend anything. Run: uv run check_setup.py

It doesn't test your API key against the API; your first real run does that.
"""
import os
import sys
from pathlib import Path

problems = 0


def check(passed: bool, good: str, fix: str) -> None:
    global problems
    print(f"  ✓ {good}" if passed else f"  ✗ {fix}")
    problems += not passed


print("Checking your Day 1 setup...\n")

check(sys.version_info >= (3, 10),
      f"Python {sys.version.split()[0]}",
      f"Python {sys.version.split()[0]} is too old. Run this with: uv run check_setup.py")

try:
    import claude_agent_sdk
    check(True, f"Claude Agent SDK {claude_agent_sdk.__version__} installed", "")
except ImportError:
    check(False, "", "Claude Agent SDK not found. Run this with: uv run check_setup.py")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

key = os.environ.get("ANTHROPIC_API_KEY", "")
if not Path(".env").is_file() and not key:
    check(False, "", "No .env file yet. Run: cp .env.example .env  then put your key in it.")
elif key in ("", "sk-ant-..."):
    check(False, "", ".env still has the placeholder. Open .env and replace sk-ant-... with your real key.")
else:
    check(key.startswith("sk-ant-"), "API key found",
          "That doesn't look like an Anthropic key (they start with sk-ant-). Copy it again.")

cvs = sorted(p.name for p in Path(".").glob("cv.*"))
print(f"  ✓ Your CV: {', '.join(cvs)}" if cvs
      else "  · No CV yet. Save yours here as cv.md or cv.pdf when you're ready.")

if problems:
    sys.exit(f"\nFix the ✗ line{'s' if problems > 1 else ''} above, then run this again.")
if Path("job_fit.py").is_file():
    print("\nAll set. Try: uv run job_fit.py examples/job.md examples/cv.md")
else:
    print("\nAll set. You're ready for tonight's code drop.")
