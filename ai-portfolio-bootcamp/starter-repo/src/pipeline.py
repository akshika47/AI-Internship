"""The one entry point: run(input) -> output.

Everything the system does for a single record happens here. Week 1's
architecture decision is that this is a single structured-output call, not an
agent loop and not a retrieval pipeline. If you change that, write down why in
docs/architecture-decision-record.md, because a grader will ask.
"""

from __future__ import annotations

import logging
import time

import anthropic
from pydantic import ValidationError

from src.config import Config, load_config
from src.schema import ExtractedFields, TicketInput, TicketOutput

log = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You triage inbound customer support tickets.

Categories:
  billing          - charges, invoices, refunds, plan changes
  bug              - something is broken that should work
  how_to           - the product works, the user does not know how to use it
  account          - login, access, permissions, deletion
  feature_request  - the product has never done this
  other            - none of the above

Priority:
  P1 - production is down, data is at risk, or money is moving incorrectly
  P2 - broken for this user, but a workaround exists
  P3 - a question, a request, or something cosmetic

Set confidence honestly. A ticket that could reasonably be two categories is
not a 0.95. Reserve confidence above 0.9 for tickets where the text states the
answer plainly.

Set irreversible_action to true when acting on the ticket would move money,
delete data, or create a legal commitment.

Base every field on the ticket text alone. Do not invent account details,
order numbers, or history that is not in front of you.\
"""


class Pipeline:
    """Holds the client so a batch run does not rebuild it per record."""

    def __init__(self, config: Config | None = None) -> None:
        self.config = config or load_config()
        self._client = None if self.config.offline else anthropic.Anthropic(
            api_key=self.config.api_key
        )

    def run(self, record: TicketInput) -> TicketOutput:
        """Process one record. Never raises for a model failure.

        On any failure the record comes back flagged for a human with
        confidence 0.0, because dropping a ticket is worse than escalating one.
        """
        started = time.perf_counter()

        try:
            fields = self._extract(record)
        except (anthropic.APIError, ValidationError, ValueError) as exc:
            log.error(
                "extraction failed",
                extra={"record_id": record.id, "error_type": type(exc).__name__},
                exc_info=True,
            )
            return TicketOutput(
                id=record.id,
                category="other",
                priority="P2",
                summary="Automatic triage failed for this ticket.",
                confidence=0.0,
                needs_human=True,
                reason=f"{type(exc).__name__} during extraction.",
            )

        needs_human = (
            fields.confidence < self.config.review_threshold
            or fields.irreversible_action
        )

        elapsed_ms = round((time.perf_counter() - started) * 1000)
        log.info(
            "record processed",
            extra={
                "record_id": record.id,
                "category": fields.category.value,
                "priority": fields.priority.value,
                "confidence": fields.confidence,
                "needs_human": needs_human,
                "latency_ms": elapsed_ms,
                "offline": self.config.offline,
            },
        )

        return TicketOutput(
            id=record.id,
            category=fields.category,
            priority=fields.priority,
            summary=fields.summary,
            confidence=fields.confidence,
            needs_human=needs_human,
            reason=fields.reason,
        )

    def _extract(self, record: TicketInput) -> ExtractedFields:
        if self.config.offline:
            return _stub_extract(record)

        user_content = f"Subject: {record.subject}\n\nBody: {record.body}"

        response = self._client.messages.parse(
            model=self.config.model,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
            output_format=ExtractedFields,
        )

        if response.stop_reason == "refusal":
            raise ValueError("Model declined to process this ticket.")

        parsed = response.parsed_output
        if parsed is None:
            raise ValueError("Model returned no parseable output.")

        usage = response.usage
        log.debug(
            "token usage",
            extra={
                "record_id": record.id,
                "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens,
            },
        )
        return parsed


def _stub_extract(record: TicketInput) -> ExtractedFields:
    """Deterministic offline stand-in, so the harness runs without a key.

    This is keyword matching, not a system. It exists so that `run_samples`
    proves your install works. Your Week 1 numbers must come from the real
    model, and this is the baseline your v1 has to beat.
    """
    text = f"{record.subject} {record.body}".lower()

    table = [
        (("refund", "charged", "invoice", "billing", "payment"), "billing"),
        (("error", "crash", "broken", "500", "fails", "bug"), "bug"),
        (("password", "log in", "login", "locked out", "access"), "account"),
        (("how do i", "how to", "where is", "can i"), "how_to"),
        (("would be great", "feature", "please add", "wish"), "feature_request"),
    ]
    category = "other"
    for needles, label in table:
        if any(n in text for n in needles):
            category = label
            break

    # Crude negation guard. "Not urgent at all" is not a P1, and a keyword
    # matcher that misses that is exactly the failure your v1 has to beat.
    downplayed = any(n in text for n in ("not urgent", "no rush", "low priority"))
    urgent_words = ("down", "outage", "cannot access", "urgent", "everyone")
    if not downplayed and any(n in text for n in urgent_words):
        priority = "P1"
    elif category in ("bug", "billing", "account"):
        priority = "P2"
    else:
        priority = "P3"

    irreversible = any(n in text for n in ("refund", "delete", "cancel", "legal", "lawyer"))

    return ExtractedFields(
        category=category,
        priority=priority,
        summary=record.subject.strip() or "No subject.",
        confidence=0.4,  # low on purpose: this is a stub, not a system
        reason="Offline stub: keyword match. Not a real prediction.",
        irreversible_action=irreversible,
    )


def run(record: TicketInput) -> TicketOutput:
    """Convenience wrapper for a one-off call."""
    return Pipeline().run(record)
