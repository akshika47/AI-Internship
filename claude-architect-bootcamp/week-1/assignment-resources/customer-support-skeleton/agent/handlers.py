"""Tool implementations.

Two are written for you, as worked examples of the conventions. Two are stubs.

CONVENTIONS THE WORKED EXAMPLES FOLLOW, AND YOURS SHOULD TOO

1. No exceptions escape. A tool that raises hands Claude a stack trace, which is
   both a bad prompt and a leak. Everything comes back as an envelope from
   errors.py.

2. Results are lean. Every tool_result is re-sent on every later turn, so each
   field is paid for once per remaining turn. Return what the agent needs to
   decide what to do next, and nothing else. Notice that get_customer does not
   echo back the email it was just given.
"""

from __future__ import annotations

import re

from . import backend
from .errors import BUSINESS, PERMISSION, TRANSIENT, VALIDATION, fail, ok
from .session import Session
from .tools import REASON_CODES

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ORDER_ID_RE = re.compile(r"^ORD-\d{3,}$")
SETTLEMENT_DAYS = 5
ESCALATION_SLA_HOURS = 4


# ---------------------------------------------------------------------------
# WORKED EXAMPLE 1: identity verification
# ---------------------------------------------------------------------------
def get_customer(session: Session, email: str = "") -> dict:
    email = str(email or "").strip().lower()
    if not EMAIL_RE.match(email):
        return fail(
            VALIDATION,
            f"'{email}' is not a valid email address. Ask the customer for the address "
            "their order was placed under.",
        )
    customer = backend.find_customer_by_email(email)
    if customer is None:
        return fail(
            VALIDATION,
            f"No account found for {email}. Ask the customer whether they ordered under a "
            "different address.",
        )
    # This assignment is the identity gate's only key. Nothing the model SAYS can
    # set it; only this line, on a real match.
    session.verified_customer_id = customer["customer_id"]
    session.verified_customer_name = customer["name"]
    session.log(event="verified", customer_id=customer["customer_id"])

    return ok(
        customer_id=customer["customer_id"],
        name=customer["name"],
        tier=customer["tier"],
        verified=True,
    )


# ---------------------------------------------------------------------------
# WORKED EXAMPLE 2: an order lookup that shows all four error categories in use
# ---------------------------------------------------------------------------
def lookup_order(session: Session, order_id: str = "") -> dict:
    order_id = str(order_id or "").strip().upper()
    if not ORDER_ID_RE.match(order_id):
        return fail(
            VALIDATION,
            f"'{order_id}' is not a valid order ID. The format is 'ORD-' followed by at "
            "least three digits, e.g. 'ORD-123'. Ask the customer for the full ID rather "
            "than adding a prefix yourself.",
        )

    # Seeded flake: the first attempt at certain orders fails transiently, so your
    # agent's retry behaviour is observable rather than something you assert in prose.
    attempts = session.lookup_attempts.get(order_id, 0) + 1
    session.lookup_attempts[order_id] = attempts
    if order_id in backend.FLAKY_ORDERS and attempts == 1:
        return fail(
            TRANSIENT,
            "The order service did not respond in time (gateway timeout). This is a "
            "temporary fault - retry this call once with the same order ID.",
        )

    order = backend.get_order(order_id)
    if order is None:
        return fail(VALIDATION, f"No order {order_id} exists.")
    if order["customer_id"] != session.verified_customer_id:
        return fail(
            PERMISSION,
            f"Order {order_id} belongs to a different customer. Do not disclose anything "
            "about it.",
        )

    result = ok(
        order_id=order["order_id"],
        item=order["item"],
        total=order["total"],
        status=order["status"],
        days_since_delivery=order["days_since_delivery"],
        return_window_open=backend.return_window_open(order),
        already_refunded=order["already_refunded"],
    )
    if order.get("carrier_note"):
        result["carrier_note"] = order["carrier_note"]
    return result


# ---------------------------------------------------------------------------
# YOUR TURN
# ---------------------------------------------------------------------------
def process_refund(
    session: Session, order_id: str = "", amount_usd: float = 0.0, reason: str = ""
) -> dict:
    """TODO (Task 3): implement.

    By the time this function runs, enforcement.intercept() has already had its
    say, so identity and the ceiling are somebody else's problem. What is left is
    order-level business policy. At minimum:

      - unknown order                     -> validation
      - a `reason` too thin for finance   -> validation
      - order not delivered yet           -> business
      - return window closed              -> business (backend.RETURN_WINDOW_DAYS)
      - amount above what is still owed   -> business

    On success: record the refund against the session (see Session.refunded_by_order,
    your ceiling depends on it), mint an ID with session.next_refund_id(), log it
    with session.log(event="refund", ...), and return a LEAN result. Ask yourself
    which fields the agent will actually read out to the customer.
    """
    raise NotImplementedError("process_refund: see Task 3 in the README")


def escalate_to_human(
    session: Session,
    customer_id: str = "",
    reason_code: str = "",
    issue_summary: str = "",
    root_cause: str = "",
    recommended_action: str = "",
    order_id: str | None = None,
    amount_usd: float | None = None,
) -> dict:
    """TODO (Task 6): implement.

    Two things make this one interesting.

    First, it must NOT be identity-gated. "I want a human" has to be honoured
    immediately, including from a caller who never verified. Decide what you put
    in customer_id in that case, and say so in the tool description.

    Second, the human who opens this ticket cannot see the conversation. So the
    TICKET you store on session.tickets should be fat: customer, order, amount,
    what went wrong, why, what you recommend, and whether identity was verified.
    Reject a ticket whose summary is a stub, with a validation error.

    But the RESULT you hand back to the model does not need any of that. The agent
    is about to read the customer a ticket number and a response time. Think about
    what that means for how much of the ticket belongs in the return value, and
    keep the answer for reflection question 3.
    """
    raise NotImplementedError("escalate_to_human: see Task 6 in the README")


HANDLERS = {
    "get_customer": get_customer,
    "lookup_order": lookup_order,
    "process_refund": process_refund,
    "escalate_to_human": escalate_to_human,
}
