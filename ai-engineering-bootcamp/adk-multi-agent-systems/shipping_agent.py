"""
Shipping Agent -- Exposed via A2A Protocol
Run: uvicorn shipping_agent:app --port 8001
"""

import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

load_dotenv()

# --- Tools ---

def get_shipping_status(order_id: str) -> dict:
    """Get current shipping status for an order."""
    data = {
        "ORD-1001": {"carrier": "FedEx", "tracking": "FX-789456123", "status": "in_transit", "location": "Memphis, TN"},
        "ORD-1002": {"carrier": "UPS", "tracking": "1Z999AA10123456784", "status": "delivered", "location": "Customer doorstep"},
        "ORD-1003": {"carrier": "USPS", "tracking": "9400111899223100001234", "status": "processing", "location": "Warehouse"},
        "ORD-1004": {"carrier": "DHL", "tracking": "DHL-5678901234", "status": "out_for_delivery", "location": "Local facility"},
        "ORD-1005": {"carrier": "FedEx", "tracking": "FX-321654987", "status": "in_transit", "location": "Chicago, IL"},
    }
    return data.get(order_id, {"error": f"No shipping info for {order_id}"})

def get_estimated_delivery(order_id: str) -> dict:
    """Get estimated delivery date for an order."""
    estimates = {
        "ORD-1001": {"date": "2026-02-14", "window": "9 AM - 5 PM", "note": "Signature required"},
        "ORD-1002": {"date": "2026-02-11", "window": "Delivered", "note": "Left at front door"},
        "ORD-1003": {"date": "2026-02-18", "window": "TBD", "note": "Still processing"},
        "ORD-1004": {"date": "2026-02-13", "window": "12 - 4 PM", "note": "Out for delivery today"},
        "ORD-1005": {"date": "2026-02-15", "window": "10 AM - 6 PM", "note": "Standard delivery"},
    }
    return estimates.get(order_id, {"error": f"No estimate for {order_id}"})

# --- Agent ---

shipping_agent = Agent(
    name="shipping_status_agent",
    model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    description="Handles shipping and delivery questions.",
    instruction="You are a shipping specialist. Use get_shipping_status and get_estimated_delivery to help customers track packages.",
    tools=[get_shipping_status, get_estimated_delivery],
)

# --- A2A ---

app = to_a2a(shipping_agent, port=8001)

# Run with: uvicorn shipping_agent:app --port 8001
