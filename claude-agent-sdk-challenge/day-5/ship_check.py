"""Is your agent ready for someone else to run? Run: uv run ship_check.py PATH/TO/YOUR/AGENT

Reads your agent's folder and runs the Day 5 checklist on it. Works for Python and
TypeScript agents. Nothing is sent anywhere and nothing calls a model, so it's free.
Each check returns a Result; a ✗ line tells you what to add.
"""
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ICONS = {True: "✓", False: "✗", None: "·"}  # None is a note, not a problem
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build", ".pytest_cache"}
CODE_SUFFIXES = {".py", ".ts", ".js", ".mjs", ".cjs"}
TEXT_SUFFIXES = CODE_SUFFIXES | {".md", ".txt", ".json", ".toml", ".yml", ".yaml", ".csv", ".env", ".example", ".cfg", ".ini"}
RUN_COMMAND = re.compile(r"\b(uv run|python3? \S+\.py|npx tsx|npm (run|start)|node \S+\.(js|mjs)|bun run)[^\n`]*")
REAL_KEY = re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}")


@dataclass(frozen=True)
class Result:
    ok: bool | None
    message: str
    fix: str = ""


@dataclass
class Project:
    """Everything the checks need, read once."""
    root: Path
    files: list[Path]
    code: str
    git_root: Path | None
    tracked: set[str]  # paths relative to git_root, empty if not a git repo

    @classmethod
    def read(cls, root: Path) -> "Project":
        files = [p for p in root.rglob("*") if p.is_file() and not SKIP_DIRS & set(p.relative_to(root).parts)]
        code = "\n".join(_text(p) for p in files if p.suffix in CODE_SUFFIXES)
        git_root = _git(root, "rev-parse", "--show-toplevel")
        tracked = set(_git(root, "ls-files").splitlines()) if git_root else set()
        return cls(root, files, code, Path(git_root) if git_root else None, tracked)

    def has(self, *words: str) -> list[str]:
        return [w for w in words if w in self.code]

    def up_to_repo(self) -> list[Path]:
        """This folder and each folder above it, stopping at the repo root."""
        top = self.git_root or self.root
        return [d for d in [self.root, *self.root.parents] if d == top or top in d.parents]


def _text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _git(root: Path, *args: str) -> str:
    try:
        out = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return out.stdout.strip() if out.returncode == 0 else ""


# ---- the checklist ----------------------------------------------------------------------

def readme(p: Project) -> Result:
    found = next((f for f in p.root.iterdir() if f.name.lower() == "readme.md"), None)
    if not found:
        return Result(False, "No README.md", "Add one that says what the agent does and the one command that runs it.")
    command = RUN_COMMAND.search(_text(found))
    return Result(True, f"README with a run command: {command.group(0).strip()[:70]}") if command else \
        Result(False, "README has no run command", "Add the exact command someone types, e.g. uv run my_agent.py examples/sample.md")


def sample_input(p: Project) -> Result:
    rel = [f.relative_to(p.root) for f in p.files if not any(part.startswith(".") for part in f.relative_to(p.root).parts)]
    samples = sorted((r for r in rel if re.search(r"sample|example", str(r), re.I)), key=lambda r: (len(r.parts), str(r)))
    return Result(True, f"Sample input: {samples[0]}") if samples else \
        Result(False, "No sample input", "Add one (e.g. examples/sample.md) so someone can try it without their own data.")


def env_example(p: Project) -> Result:
    found = next((d / ".env.example" for d in p.up_to_repo() if (d / ".env.example").is_file()), None)
    if not found:
        return Result(False, "No .env.example", "Add one with a placeholder: ANTHROPIC_API_KEY=sk-ant-...")
    if REAL_KEY.search(_text(found)):
        return Result(False, f"{found.name} holds a real-looking key", "Replace it with a placeholder (sk-ant-...) and rotate that key.")
    return Result(True, f".env.example with a placeholder ({found.relative_to(p.up_to_repo()[-1])})")


def env_kept_private(p: Project) -> Result:
    if not p.git_root:
        return Result(None, "Not a git repo yet, so nothing is shared. Add .env to a .gitignore before you push.")
    shared = sorted(t for t in p.tracked if Path(t).name == ".env")
    if shared:
        return Result(False, f"Your .env is in git: {', '.join(shared)}",
                      "Remove it (git rm --cached .env), add .env to .gitignore, and rotate the key.")
    ignored = subprocess.run(["git", "-C", str(p.root), "check-ignore", "-q", ".env"]).returncode == 0
    return Result(True, ".env is ignored by git") if ignored else \
        Result(False, ".env is not in .gitignore", "Add a line with .env to your .gitignore before your next commit.")


def no_keys_in_files(p: Project) -> Result:
    candidates = [f for f in p.files if f.name != ".env" and (f.suffix in TEXT_SUFFIXES or f.name.startswith(".env."))]
    if p.git_root:  # only what you'd actually share
        candidates = [f for f in candidates if str(f.relative_to(p.git_root)) in p.tracked]
    hits = [f"{f.relative_to(p.root)}:{n}" for f in candidates
            for n, line in enumerate(_text(f).splitlines(), 1) if REAL_KEY.search(line)]
    return Result(False, f"A key is written in {', '.join(hits[:3])}", "Read it from .env instead, then rotate that key.") if hits else \
        Result(True, "No API keys written in your files")


def limits(p: Project) -> Result:
    missing = [name for name, words in {"max_turns": ("max_turns", "maxTurns"), "max_budget_usd": ("max_budget_usd", "maxBudgetUsd")}.items()
               if not p.has(*words)]
    return Result(False, f"No {' or '.join(missing)}", "Set both in your options. The SDK has no timeout of its own.") if missing else \
        Result(True, "Limits set: max_turns and max_budget_usd")


def tools_locked(p: Project) -> Result:
    if p.has("bypassPermissions", "bypass_permissions"):
        return Result(False, "bypassPermissions is on", "Remove it and list the tools the agent needs instead.")
    restricted = re.search(r"(?<![A-Za-z_])tools\s*[=:]\s*[\[A-Za-z_]", p.code)  # a list, or a name holding one
    return Result(True, "Tools restricted with tools=[...]") if restricted else \
        Result(False, "Tools not restricted", "Pass tools=[...] with only what it needs. allowed_tools only pre-approves; it doesn't restrict.")


def readable_errors(p: Project) -> Result:
    handled = p.has("ClaudeSDKError", "is_error", "isError", "subtype", "error_max_turns", "error_max_budget_usd")
    return Result(True, "Handles a stopped run") if handled else \
        Result(False, "A stopped run would end in a traceback", "Catch ClaudeSDKError and check result.subtype, then print a plain message.")


def shows_cost(p: Project) -> Result:
    return Result(True, "Prints what a run cost") if p.has("total_cost_usd", "totalCostUsd") else \
        Result(False, "Doesn't show the cost", "Print result.total_cost_usd and result.num_turns at the end of a run.")


def rerunnable_check(p: Project) -> Result:
    checks = [f for f in p.files if re.search(r"(^|/)(tests?|evals?)/|(^|/)test_\w+\.py$|_test\.py$|\.test\.[jt]s$|run_evals|check_judge",
                                                  str(f.relative_to(p.root)))]
    return Result(True, f"A check you can rerun: {checks[0].relative_to(p.root)}") if checks else \
        Result(False, "No test or eval to rerun", "Add one: a test with a known answer, or Day 3's run_evals with your scenarios.")


CHECKS = [readme, sample_input, env_example, env_kept_private, no_keys_in_files,
          limits, tools_locked, readable_errors, shows_cost, rerunnable_check]


def ship_check(root: Path) -> list[Result]:
    project = Project.read(root)
    return [check(project) for check in CHECKS]


if __name__ == "__main__":
    target = Path(sys.argv[1] if len(sys.argv) > 1 else ".").expanduser().resolve()
    if not target.is_dir():
        sys.exit(f"Can't find a folder at {target}. Usage: uv run ship_check.py PATH/TO/YOUR/AGENT")
    print(f"Ship check for {target.name}\n")
    results = ship_check(target)
    for result in results:
        print(f"  {ICONS[result.ok]} {result.message}")
        if result.ok is False:
            print(f"      → {result.fix}")
    todo = sum(result.ok is False for result in results)
    ready = sum(result.ok is True for result in results)
    if todo:
        print(f"\n{ready} of {len(CHECKS)} ready. Fix the ✗ line{'s' * (todo > 1)}, run this again, then record your demo.")
        sys.exit(1)
    print(f"\n{ready} of {len(CHECKS)} ready. Ready to ship: record your one-minute demo.")
