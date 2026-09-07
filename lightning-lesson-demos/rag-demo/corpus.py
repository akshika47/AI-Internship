"""Tiny hardcoded knowledge base for the lightning RAG demo."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    id: str
    title: str
    text: str


# Short passages with distinct facts so retrieval demos cleanly.
CORPUS: list[Chunk] = [
    Chunk(
        id="pto",
        title="Paid time off",
        text=(
            "NovaDesk employee handbook — Paid time off (PTO). "
            "Full-time employees receive 20 days of PTO per calendar year. "
            "New hires receive a prorated allotment in their first year: "
            "1.5 days of PTO for each full month remaining in the year after their start date. "
            "Unused PTO may roll over up to 5 days into the next year."
        ),
    ),
    Chunk(
        id="refund",
        title="Refund policy — defective items",
        text=(
            "NovaDesk customer policy — Refunds for defective items (effective January 2025). "
            "Customers may request a full refund for defective hardware within 60 days of delivery. "
            "Proof of purchase and a brief defect description are required. "
            "Approved refunds are issued to the original payment method within 5–7 business days."
        ),
    ),
    Chunk(
        id="onboarding",
        title="New hire onboarding",
        text=(
            "NovaDesk HR — New hire onboarding. "
            "All new hires complete a 2-day virtual orientation in their first week. "
            "Laptop and SSO access are provisioned on day 1. "
            "Managers schedule a 30-day check-in and a 90-day performance review."
        ),
    ),
    Chunk(
        id="support",
        title="Support hours",
        text=(
            "NovaDesk support — Hours of operation. "
            "Live chat and email support run Monday–Friday, 9:00–18:00 Eastern Time. "
            "Priority enterprise tickets receive a first response within 1 hour during business hours. "
            "There is no phone support for self-serve plans."
        ),
    ),
    Chunk(
        id="remote",
        title="Remote work",
        text=(
            "NovaDesk workplace policy — Remote work. "
            "Employees may work remotely up to 3 days per week. "
            "Core collaboration hours are 11:00–15:00 local time. "
            "International remote work longer than 14 consecutive days requires People Ops approval."
        ),
    ),
    Chunk(
        id="shipping",
        title="Shipping SLAs",
        text=(
            "NovaDesk fulfillment — Shipping. "
            "Standard shipping arrives in 3–5 business days within the contiguous US. "
            "Express shipping arrives in 1–2 business days. "
            "Orders placed after 2:00 PM Eastern ship the next business day."
        ),
    ),
]

# Reliable questions for the live lesson (answers live in the chunks above).
SAMPLE_QUESTIONS = [
    "How many days of PTO do new hires get?",
    "What’s the refund window for defective items?",
]
