"""Day 2: two tools we write ourselves, for an applications tracker in applications.csv.

A tool is a normal Python function plus a name, a description and the inputs it takes.
The agent reads the description to decide when to call it; your code does the work.
"""
import csv
from datetime import date
from pathlib import Path
from typing import Any

from claude_agent_sdk import ToolAnnotations, create_sdk_mcp_server, tool

TRACKER = Path("applications.csv")
COLUMNS = ["date", "role", "fit_score", "decision", "job_ad"]


def read_rows() -> list[dict[str, str]]:
    if not TRACKER.is_file():
        return []
    with TRACKER.open(newline="") as f:
        return list(csv.DictReader(f))


@tool(
    "check_tracker",
    "List every job already assessed: date, role, fit score, decision and where the ad came from. "
    "Call this before writing the report so you can compare this job with earlier ones.",
    {},
    annotations=ToolAnnotations(readOnlyHint=True),  # it only looks, so it's safe to run any time
)
async def check_tracker(args: dict[str, Any]) -> dict[str, Any]:
    rows = read_rows()
    if not rows:
        return {"content": [{"type": "text", "text": "The tracker is empty. This is the first job assessed."}]}
    lines = [f"{r['date']} | {r['role']} | {r['fit_score']}/10 | {r['decision']} | {r['job_ad']}" for r in rows]
    return {"content": [{"type": "text", "text": f"{len(rows)} jobs assessed so far:\n" + "\n".join(lines)}]}


@tool(
    "save_to_tracker",
    "Save this job's result to the applications tracker. Call it once, after you've decided, "
    "and only if you read the job ad in full. Saving the same job ad again updates its row.",
    {
        "type": "object",
        "properties": {
            "role": {"type": "string", "description": "Job title and company"},
            "fit_score": {"type": "integer", "minimum": 0, "maximum": 10},
            "decision": {"type": "string", "enum": ["Apply now", "Apply after closing a gap", "Skip this one"]},
            "job_ad": {"type": "string", "description": "The job ad's link, or its file name"},
        },
        "required": ["role", "fit_score", "decision", "job_ad"],
    },
)
async def save_to_tracker(args: dict[str, Any]) -> dict[str, Any]:
    row = {"date": date.today().isoformat(), **{k: args[k] for k in COLUMNS[1:]}}
    if not row["job_ad"].startswith(("http://", "https://")):
        row["job_ad"] = Path(row["job_ad"]).name  # a file name reads better than a full path
    rows = [r for r in read_rows() if r["job_ad"] != row["job_ad"]] + [row]
    with TRACKER.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return {"content": [{"type": "text", "text": f"Saved. The tracker now has {len(rows)} jobs."}]}


# The agent gets the tools through a small server that runs inside this script.
# Their full names are mcp__tracker__check_tracker and mcp__tracker__save_to_tracker.
tracker_server = create_sdk_mcp_server(name="tracker", tools=[check_tracker, save_to_tracker])
TRACKER_TOOLS = ["mcp__tracker__check_tracker", "mcp__tracker__save_to_tracker"]
