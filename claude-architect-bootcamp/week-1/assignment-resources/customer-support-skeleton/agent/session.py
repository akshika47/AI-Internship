"""Per-conversation state.

This is the object the enforcement layer reads, and it is deliberately NOT
derivable from the message history. That distinction is the whole point: a gate
must not be satisfiable by anything the model *says*, only by a tool it actually
called succeeding.
"""

from __future__ import annotations

from dataclasses import dataclass, field

FROZEN_NOW = "2026-09-10T09:15:00Z"


@dataclass
class Session:
    # Set ONLY by a successful get_customer call, in handlers.py.
    verified_customer_id: str | None = None
    verified_customer_name: str | None = None

    # TODO (Task 4): the $500 ceiling has to hold across the whole conversation,
    # not just one call. Track what has already been refunded per order here, and
    # read it from your ceiling check. Without this, 2 x $450 walks straight past
    # a $500 limit and your gate is decorative.
    refunded_by_order: dict[str, float] = field(default_factory=dict)

    # Escalation tickets raised in this session. Handed to a human who cannot see
    # the conversation, so whatever you put in here has to stand on its own.
    tickets: list[dict] = field(default_factory=list)

    # Deterministic IDs and clock, so your transcripts are reproducible.
    now: str = FROZEN_NOW
    _ticket_seq: int = 0
    _refund_seq: int = 0

    # Lets the seeded transient failure fire once per session instead of forever.
    lookup_attempts: dict[str, int] = field(default_factory=dict)

    # Every gate decision and tool call. Your transcripts and your tests both read
    # this, and in production it is what you would alert on.
    audit: list[dict] = field(default_factory=list)

    def next_ticket_id(self) -> str:
        self._ticket_seq += 1
        return f"TKT-{7000 + self._ticket_seq}"

    def next_refund_id(self) -> str:
        self._refund_seq += 1
        return f"RFND-{4400 + self._refund_seq}"

    def log(self, **entry) -> None:
        self.audit.append(entry)
