"""Turns the agent's answer into the Markdown report you open."""
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Section:
    heading: str
    lines: Callable[[dict], list[str]]  # an empty list leaves the section out


SECTIONS = [
    Section("Where you're strong", lambda r: [f"- **{s['requirement']}**: {s['evidence_from_cv']}" for s in r["strengths"]]),
    Section("Gaps", lambda r: [f"- **{g['requirement']}**: {g['how_to_close_it']}" for g in r["gaps"]]),
    Section("CV bullets for this role", lambda r: [f"- {b}" for b in r["cv_bullets"]]),
    Section("Cover note opener", lambda r: [f"> {line}" for line in [r["opening_line"]] if line]),
    Section("Compared with your tracker", lambda r: [r["tracker_note"]]),
]


def to_markdown(report: dict) -> str:
    header = f"# {report['role']}\n\n**{report['decision']} · fit {report['fit_score']}/10.** {report['verdict']}\n"
    sections = [(s.heading, s.lines(report)) for s in SECTIONS]
    body = [f"## {heading}\n\n" + "\n".join(lines) + "\n" for heading, lines in sections if lines]
    return "\n".join([header, *body])


def report_path(role: str, cv: str) -> Path:
    """job-fit-fernhill-health-junior-ai-automation-analyst-cv.md: one report per job and CV."""
    slug = re.sub(r"[^a-z0-9]+", "-", f"{role} {Path(cv).stem}".lower()).strip("-")[:80]
    return Path(f"job-fit-{slug or 'report'}.md")
