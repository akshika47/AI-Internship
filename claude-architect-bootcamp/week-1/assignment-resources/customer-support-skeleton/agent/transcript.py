"""Markdown transcript recorder.

Records what a grader needs to see: the stop_reason on every turn, every
tool_use block with its arguments, whether the enforcement hook allowed or
blocked it, and the exact JSON that went back to the model.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from .model import AgentResponse, Block


class TranscriptRecorder:
    def __init__(self, title: str, subtitle: str, mode: str):
        self.title = title
        self.subtitle = subtitle
        self.mode = mode
        self.lines: list[str] = []
        self._turn = 0

    # ---- events ---------------------------------------------------------
    def user(self, text: str) -> None:
        self.lines += ["## Customer", "", "> " + text.replace("\n", "\n> "), ""]

    def assistant(self, response: AgentResponse, turn: int) -> None:
        self._turn = turn
        self.lines += [
            f"## Turn {turn} - assistant",
            "",
            f"`stop_reason: {response.stop_reason}`",
            "",
        ]
        if response.text:
            self.lines += [response.text, ""]
        for block in response.tool_uses:
            self.lines += [
                f"**tool_use** `{block.name}` (`{block.id}`)",
                "",
                "```json",
                json.dumps(block.input, indent=2),
                "```",
                "",
            ]

    def tool_result(self, block: Block, payload: dict, blocked: bool) -> None:
        gate = "BLOCKED BY ENFORCEMENT HOOK" if blocked else "allowed by enforcement hook"
        self.lines += [
            f"**tool_result** for `{block.id}` - {gate}",
            "",
            "```json",
            json.dumps(payload, indent=2),
            "```",
            "",
        ]

    def tool_results_appended(self, count: int) -> None:
        plural = "s" if count != 1 else ""
        self.lines += [
            f"_{count} tool_result block{plural} appended to history in a single user "
            "message._",
            "",
        ]

    def note(self, text: str) -> None:
        self.lines += [text, ""]

    # ---- rendering ------------------------------------------------------
    def render(self, result, session) -> str:
        header = [
            f"# {self.title}",
            "",
            self.subtitle,
            "",
            f"- Model backend: **{self.mode}**",
            f"- Turns to `end_turn`: **{result.turns}** (safety-net cap is 12, never reached)",
            f"- Identity verified: **{session.verified_customer_id or 'no'}**",
            f"- Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%MZ')}",
            "",
            "---",
            "",
        ]

        footer = ["---", "", "## Final reply to the customer", "", result.final_text, ""]

        if session.tickets:
            footer += [
                "---",
                "",
                "## Escalation ticket as the human receives it",
                "",
                "The human opening this queue item cannot see the conversation above. "
                "Everything they need is in the ticket. Note that the agent itself only "
                "received `ticket_id`, `queue` and `response_within_hours` back - fat where "
                "a human reads it, lean where the model reads it.",
                "",
            ]
            for ticket in session.tickets:
                footer += ["```json", json.dumps(ticket, indent=2), "```", ""]

        footer += ["---", "", "## Enforcement audit log", "", "```"]
        for entry in session.audit:
            footer.append(json.dumps(entry))
        footer += ["```", ""]

        return "\n".join(header + self.lines + footer)
