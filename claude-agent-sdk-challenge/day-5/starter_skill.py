"""Starter: give any agent a skill, and compare it with and without. Copy it for your own idea.

Usage:
    uv run starter_skill.py SKILL "your request" [--no-skill]

    SKILL       a skill folder name in .claude/skills/, e.g. turning-notes-into-actions
    --no-skill  the same request without the skill, to compare

Examples:
    uv run starter_skill.py turning-notes-into-actions "Turn examples/documents/meeting-notes.md into actions"
    uv run starter_skill.py replying-to-emails "Draft a reply to examples/documents/email-thread.md" --no-skill

To make your own: copy skill-template/ into .claude/skills/, rename it, write your rules, and
run this with its name. No code changes needed.
"""
import argparse
import asyncio
import sys
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKError, ResultMessage, query

load_dotenv(find_dotenv())  # finds the .env in the claude-agent-sdk-challenge folder

HERE = Path(__file__).resolve().parent
SKILLS_FOLDER = HERE / ".claude" / "skills"


def options(skill: str, use_skill: bool) -> ClaudeAgentOptions:
    tools = ["Read", "Skill"] if use_skill else ["Read"]
    return ClaudeAgentOptions(
        system_prompt=f"You are a helpful assistant. Use the {skill} skill for this task." if use_skill
        else "You are a helpful assistant.",
        cwd=HERE,
        setting_sources=["project"],      # this folder's skills only, never your personal ones
        skills=[skill] if use_skill else [],
        tools=tools,
        allowed_tools=tools,
        model="sonnet",
        max_turns=10,
        max_budget_usd=1.00,  # a cap per run; a normal run costs a few cents
    )


async def main(args: argparse.Namespace) -> None:
    if not (SKILLS_FOLDER / args.skill / "SKILL.md").is_file():
        available = ", ".join(sorted(p.name for p in SKILLS_FOLDER.iterdir() if (p / "SKILL.md").is_file()))
        sys.exit(f"No skill called '{args.skill}'. Available: {available}")
    try:
        async for message in query(prompt=args.request, options=options(args.skill, not args.no_skill)):
            if isinstance(message, ResultMessage) and message.subtype == "success":
                print(message.result)
                print(f"\n{'without' if args.no_skill else 'with'} {args.skill} · "
                      f"{message.num_turns} turns · ${message.total_cost_usd or 0:.3f}")
    except ClaudeSDKError as error:
        sys.exit(f"The agent couldn't run: {error}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a request with or without a skill.", usage=__doc__)
    parser.add_argument("skill")
    parser.add_argument("request")
    parser.add_argument("--no-skill", action="store_true")
    asyncio.run(main(parser.parse_args()))
