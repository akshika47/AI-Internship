"""Code that runs at points in the agent's loop. Here: print each step as it happens."""
import json
from collections.abc import Callable
from pathlib import Path

# One line per tool: how to describe that step to a person.
STEP_LABELS: dict[str, Callable[[dict], str]] = {
    "Read": lambda args: f"reading {Path(args['file_path']).name}",
    "mcp__jobfit__fetch_job_ad": lambda args: "fetching the job ad",
    "mcp__jobfit__check_tracker": lambda args: "checking your tracker",
    "mcp__jobfit__save_to_tracker": lambda args: f"saving to your tracker: {args['role']}, {args['fit_score']}/10",
    "Skill": lambda args: f"opening your skill: {args.get('skill', '')}",
    "mcp__jobfit__check_cv_bullets": lambda args: f"checking {len(args['bullets'])} CV bullets",
    "mcp__jobfit__check_evidence": lambda args: f"checking {len(args['quotes'])} quotes are really in the CV",
    "StructuredOutput": lambda args: "writing up the report",
}


def _raw_label(tool: str) -> Callable[[dict], str]:
    """For a tool without a friendly label: show its name and the start of its input."""
    return lambda args: f"{tool} {json.dumps(args)[:60]}"


async def show_tool_use(input_data, tool_use_id, context):
    """Runs before every tool call, so you can watch the agent work."""
    tool = input_data["tool_name"]
    label = STEP_LABELS.get(tool, _raw_label(tool))
    print(f"  · {label(input_data['tool_input'])}")
    return {}
