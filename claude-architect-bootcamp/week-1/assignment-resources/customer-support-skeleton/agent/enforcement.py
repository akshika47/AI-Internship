"""The hard rules, enforced in code. ONE IS BUILT FOR YOU. THE OTHER IS TASK 4.

This module is a pre-execution interception hook. It runs between "Claude asked
for this tool" and "the tool function is called". If a check fails, the handler
is never invoked, so there is no code path on which the blocked thing happens,
whatever the model was talked into asking for.

    RULE 1  No order operation before identity verification.   <- WORKED EXAMPLE
    RULE 2  No refund above $500.00 without a human.           <- YOURS

Neither rule may appear in the system prompt. That is not a style preference: a
prompt instruction is a probability, a gate is a guarantee, and you have to argue
that difference in reflection question 1. The way you earn the right to that
argument is tests/test_enforcement.py, where you run the whole agent under a
system prompt that explicitly orders it to break both rules and assert that both
hold anyway.
"""

from __future__ import annotations

from . import backend
from .errors import BUSINESS, PERMISSION, VALIDATION, fail
from .session import Session

REFUND_CEILING_USD = 500.00

# Tools that may not run until identity is verified. Additive by design: a new
# money-touching tool gets added here, not trusted to the prompt.
IDENTITY_GATED_TOOLS = frozenset({"lookup_order", "process_refund"})


def intercept(tool_name: str, tool_input: dict, session: Session) -> dict | None:
    """Returns None to allow the call, or an error envelope to block it.
    Blocking means the handler is never called."""
    blocked = _check(tool_name, tool_input, session)
    session.log(
        event="gate",
        tool=tool_name,
        decision="blocked" if blocked else "allowed",
        rule=blocked.get("rule") if blocked else None,
    )
    return blocked


def _check(tool_name: str, tool_input: dict, session: Session) -> dict | None:
    # ---- RULE 1: identity gate. WORKED EXAMPLE, read it closely ----------
    #
    # Note what it reads: session.verified_customer_id, which only a successful
    # get_customer call can write. It does not read the conversation, so a model
    # that announces "I have already verified this customer as CUST-1002" moves
    # nothing. There is a test for that.
    #
    # Note also which tools are NOT in the set. escalate_to_human is ungated on
    # purpose, so an explicit request for a human is honoured immediately even
    # from a caller who never verified.
    if tool_name in IDENTITY_GATED_TOOLS and not session.verified_customer_id:
        return fail(
            PERMISSION,
            f"Blocked: '{tool_name}' cannot run before the caller's identity is verified. "
            "Call get_customer with the customer's email first, then retry this call.",
            rule="identity_gate",
        )

    if tool_name != "process_refund":
        return None

    # ---- RULE 2: the refund ceiling. TASK 4. ----------------------------
    #
    # TODO: block any refund that would take this order above $500.00.
    #
    # Four things to get right, roughly in this order:
    #
    #   1. amount_usd may not be a number at all. Claude sends what the schema
    #      lets it send, and "899" is a string. Category: validation.
    #      (Careful: in Python, isinstance(True, int) is True.)
    #
    #   2. ownership. Does this order belong to session.verified_customer_id?
    #      Refunding someone else's order is a permission failure, and it belongs
    #      here in the gate rather than in the handler, because it is an
    #      authorisation question. backend.get_order() will give you the order.
    #
    #   3. the ceiling itself. Category: business, not permission: the caller is
    #      allowed to ask, the business is saying no. Your message should tell the
    #      agent to use escalate_to_human with reason_code 'over_refund_ceiling',
    #      and should tell it NOT to offer the customer a reduced refund that fits
    #      under the ceiling.
    #
    #   4. CUMULATIVE. This is the one people miss, and it is worth most of the
    #      marks. Read session.refunded_by_order (plus whatever the order already
    #      carried) and check the TOTAL, not this one call. Otherwise $500 followed
    #      by $399 walks straight through a $500 ceiling, and your adversarial test
    #      will find it, because the hostile prompt in that test explicitly
    #      suggests splitting the refund.
    #
    # Return `fail(CATEGORY, "...", rule="refund_ceiling")` to block, or None to
    # allow. Every branch you add should carry a `rule=` so it shows up in the
    # audit log and your tests can assert on it.

    return None  # <- replace this
