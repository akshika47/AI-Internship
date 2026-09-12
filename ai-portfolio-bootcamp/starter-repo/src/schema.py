"""Input and output schemas.

This is the file you change first. The reference task is support ticket triage,
chosen because it makes the two required fields obvious. Your brief describes a
different system: replace these models with yours and the rest of the harness
keeps working.

Two fields are required whatever you build, because the brief asks for them:

  confidence      - how sure the system is, 0 to 1
  needs_human     - whether a person has to look at this one

A system that is always confident and never escalates has not been designed,
it has just been written.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class Priority(str, Enum):
    P1 = "P1"  # production down, or money/data at risk
    P2 = "P2"  # broken for this user, workaround exists
    P3 = "P3"  # question, request, cosmetic


class Category(str, Enum):
    BILLING = "billing"
    BUG = "bug"
    HOW_TO = "how_to"
    ACCOUNT = "account"
    FEATURE_REQUEST = "feature_request"
    OTHER = "other"


class TicketInput(BaseModel):
    """One record in, exactly as it appears in data/sample_inputs.jsonl."""

    id: str
    subject: str
    body: str


class TicketOutput(BaseModel):
    """One record out. Every field is scored in evals/score.py."""

    id: str
    category: Category
    priority: Priority
    summary: str = Field(description="One sentence a human can act on.")
    confidence: float = Field(ge=0.0, le=1.0)
    needs_human: bool = Field(
        description="True when confidence is below the threshold, or the ticket "
        "involves a refund, a legal threat, or anything irreversible."
    )
    reason: str = Field(description="Why this category and priority. One sentence.")


class ExtractedFields(BaseModel):
    """What the model is asked to produce.

    Deliberately smaller than TicketOutput: `id` comes from the input and
    `needs_human` is decided in code, not by the model. Asking the model to
    echo an id it was given is a way to introduce errors for free.
    """

    category: Category
    priority: Priority
    summary: str
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    irreversible_action: bool = Field(
        description="True if acting on this ticket would move money, delete data, "
        "or create a legal commitment."
    )


RunStatus = Literal["ok", "error"]
