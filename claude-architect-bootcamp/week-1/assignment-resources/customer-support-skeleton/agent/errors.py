"""Structured tool results. GIVEN TO YOU. You should not need to change this file.

Every tool returns one of two shapes. Claude never sees a Python exception, a
stack trace, or a raw HTTP body.

    success   {"ok": true, ...only the fields the agent needs next}
    failure   {"ok": false, "errorCategory": str, "isRetryable": bool, "message": str}

The four categories, and what you want the agent to DO with each:

    transient   downstream flake, timeout, 503. isRetryable=True.
                Correct behaviour: call the same tool again with the same args.

    validation  the arguments are wrong (bad order-ID format, negative amount).
                Correct behaviour: fix the argument, or ask the customer.
                Retrying unchanged will fail forever.

    business    well-formed and authorised, but the business says no (outside the
                return window, over the refund ceiling). Carries a customer-facing
                `message`. Correct behaviour: explain, then take the other route.

    permission  not allowed yet or at all (identity not verified, someone else's
                order). Correct behaviour: satisfy the precondition, then retry.

Retryability is derived from the category rather than passed in, so nobody can
mark a business rule "retryable" by accident.
"""

from __future__ import annotations

TRANSIENT = "transient"
VALIDATION = "validation"
BUSINESS = "business"
PERMISSION = "permission"

RETRYABLE_BY_CATEGORY = {
    TRANSIENT: True,
    VALIDATION: False,
    BUSINESS: False,
    PERMISSION: False,
}


def ok(**fields) -> dict:
    """A successful tool result.

    Keep `fields` lean. Every tool_result is re-sent to the model on every later
    turn of the conversation, so a field nobody reads is a field you pay for N
    times. Reflection question 3 is about exactly this.
    """
    return {"ok": True, **fields}


def fail(category: str, message: str, **fields) -> dict:
    """A failed tool result. `message` is written for Claude, and for the business
    category it should be safe to relay to the customer nearly verbatim."""
    if category not in RETRYABLE_BY_CATEGORY:
        raise ValueError(f"unknown errorCategory: {category!r}")
    return {
        "ok": False,
        "errorCategory": category,
        "isRetryable": RETRYABLE_BY_CATEGORY[category],
        "message": message,
        **fields,
    }
