"""Tool definitions. THESE DESCRIPTIONS ARE DELIBERATELY THIN. Fixing them is Task 1.

Four tools are wired up and the agent will call them. What is missing is the
prose. Every description below states roughly what the tool does and nothing
else: no input formats, no examples, no failure modes, and above all no
boundaries against the tool next to it.

THE OVERLAP YOU HAVE TO FIX
---------------------------
`process_refund` and `escalate_to_human` have genuinely overlapping surface
area. Both are answers to "I want my money back", and the customer turns that
produce them are nearly identical. "The mixer arrived smashed, $912, I want a
refund" and "the kettle arrived cracked, $84, I want a refund" differ in one
number.

With the descriptions as written, the model misroutes in both directions, and
the two directions cost you differently:

  - escalating a routine $40 refund      first-contact resolution falls, queue
                                         cost rises, and it is INVISIBLE, because
                                         the ticket looks perfectly fine;
  - refunding $899 without approval      caught by your ceiling hook once you
                                         build one. Until then it is a payout.

Fix this with description text, not with a routing layer in front of the model,
and not by deleting one of the tools. Reflection question 2 asks what you wrote
and how you would detect it failing in production, so keep notes as you go.

A second, softer overlap exists between `get_customer` and `lookup_order`: both
look like "fetch account information". Worth bounding too.

WHAT A GOOD DESCRIPTION COVERS
  - purpose, in one sentence
  - every input, with its format and a concrete example value
  - what comes back on success, and what does NOT come back
  - an explicit DO NOT USE WHEN clause naming the sibling tool
  - the failure modes, and what the agent should do about each
"""

from __future__ import annotations

REFUND_CEILING_USD = 500.00

REASON_CODES = [
    "over_refund_ceiling",
    "customer_requested_human",
    "policy_exception",
    "suspected_fraud",
    "unresolvable",
]

GET_CUSTOMER = {
    "name": "get_customer",
    # TODO (Task 1): expand. What format is the email? What comes back? What is
    # this tool NOT for? What happens when no account matches?
    "description": "Gets customer information.",
    "input_schema": {
        "type": "object",
        "properties": {
            "email": {"type": "string"},
        },
        "required": ["email"],
        "additionalProperties": False,
    },
}

LOOKUP_ORDER = {
    "name": "lookup_order",
    # TODO (Task 1): expand. Order ID format? What if the customer gives you a
    # bare number? Which failures are worth retrying and which are not?
    "description": "Looks up an order.",
    "input_schema": {
        "type": "object",
        "properties": {"order_id": {"type": "string"}},
        "required": ["order_id"],
        "additionalProperties": False,
    },
}

PROCESS_REFUND = {
    "name": "process_refund",
    # TODO (Task 1): this is half of the overlapping pair. Where does this tool
    # stop and escalate_to_human start? Say it in numbers, not in adjectives.
    "description": "Refunds an order.",
    "input_schema": {
        "type": "object",
        "properties": {
            "order_id": {"type": "string"},
            "amount_usd": {"type": "number"},
            "reason": {"type": "string"},
        },
        "required": ["order_id", "amount_usd", "reason"],
        "additionalProperties": False,
    },
}

ESCALATE_TO_HUMAN = {
    "name": "escalate_to_human",
    # TODO (Task 1): the other half of the pair. Also note that the human who
    # picks this ticket up CANNOT SEE THE CONVERSATION, so the description has to
    # make the model write fields that stand on their own. Right now it will
    # happily send "issue_summary": "refund".
    "description": "Sends the case to a human.",
    "input_schema": {
        "type": "object",
        "properties": {
            "customer_id": {"type": "string"},
            "order_id": {"type": "string"},
            "reason_code": {"type": "string", "enum": REASON_CODES},
            "issue_summary": {"type": "string"},
            "root_cause": {"type": "string"},
            "amount_usd": {"type": "number"},
            "recommended_action": {"type": "string"},
        },
        # TODO (Task 6): which of these should actually be required for a handoff
        # that works without the transcript?
        "required": ["customer_id", "reason_code", "issue_summary"],
        "additionalProperties": False,
    },
}

TOOLS = [GET_CUSTOMER, LOOKUP_ORDER, PROCESS_REFUND, ESCALATE_TO_HUMAN]
TOOLS_BY_NAME = {t["name"]: t for t in TOOLS}
