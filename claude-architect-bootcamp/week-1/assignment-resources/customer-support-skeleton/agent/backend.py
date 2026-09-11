"""Stand-in for the retailer's backend. GIVEN TO YOU.

The customers and the first two orders are the same records used in the Week 1
laboratory notebook (`week1_support_agent.ipynb`), so anything you saw demoed
live behaves identically here. Two extra orders are added for cases the live
session did not cover.

  ORD-123  Alice, $149.99, delivered 6 days ago    happy path, refundable
  ORD-456  Bob,   $899.00, delivered 41 days ago   over the ceiling AND outside
                                                   the window: the escalation case
  ORD-321  Bob,    $64.00, delivered 9 days ago    refundable, for multi-concern
  ORD-789  Alice,  $28.00, still in transit        first lookup fails transiently
"""

from __future__ import annotations

RETURN_WINDOW_DAYS = 30

CUSTOMERS = {
    "alice@example.com": {
        "customer_id": "CUST-001",
        "name": "Alice Nguyen",
        "email": "alice@example.com",
        "tier": "gold",
    },
    "bob@example.com": {
        "customer_id": "CUST-002",
        "name": "Bob Okafor",
        "email": "bob@example.com",
        "tier": "standard",
    },
}

ORDERS = {
    "ORD-123": {
        "order_id": "ORD-123",
        "customer_id": "CUST-001",
        "item": "Ceramic pour-over kettle, 1L",
        "status": "delivered",
        "total": 149.99,
        "days_since_delivery": 6,
        "already_refunded": 0.0,
    },
    "ORD-456": {
        "order_id": "ORD-456",
        "customer_id": "CUST-002",
        "item": "Professional stand mixer, 6qt",
        "status": "delivered",
        "total": 899.00,
        "days_since_delivery": 41,
        "already_refunded": 0.0,
        "carrier_note": "Consignment recorded as crushed corner at final-mile scan.",
    },
    "ORD-321": {
        "order_id": "ORD-321",
        "customer_id": "CUST-002",
        "item": "Cast iron skillet, 12in",
        "status": "delivered",
        "total": 64.00,
        "days_since_delivery": 9,
        "already_refunded": 0.0,
    },
    "ORD-789": {
        "order_id": "ORD-789",
        "customer_id": "CUST-001",
        "item": "Espresso tamper, 58mm",
        "status": "in_transit",
        "total": 28.00,
        "days_since_delivery": None,
        "already_refunded": 0.0,
    },
}

# Orders whose FIRST lookup in a session returns a transient failure, so your
# agent's retry behaviour is observable rather than something you assert in prose.
FLAKY_ORDERS = {"ORD-789"}


def find_customer_by_email(email: str) -> dict | None:
    return CUSTOMERS.get(str(email).strip().lower())


def get_order(order_id: str) -> dict | None:
    return ORDERS.get(str(order_id).strip().upper())


def return_window_open(order: dict) -> bool:
    """True when the order was delivered inside the return window."""
    days = order.get("days_since_delivery")
    return days is not None and days <= RETURN_WINDOW_DAYS
