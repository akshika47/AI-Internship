"""
Demo 1: Multi-Agent Routing with ADK
Run: python demo1_routing.py
"""

import asyncio
import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

MODEL = "gemini-2.5-flash"

# --- Tools ---

def lookup_invoice(customer_email: str) -> dict:
    """Look up the most recent invoice for a customer by email."""
    invoices = {
        "bob@example.com": {"invoice_id": "INV-2024-002", "customer": "Bob Smith", "amount": "$299.00", "status": "overdue", "plan": "Enterprise Annual"},
        "jane@example.com": {"invoice_id": "INV-2024-001", "customer": "Jane Doe", "amount": "$99.00", "status": "paid", "plan": "Pro Monthly"},
        "alice@example.com": {"invoice_id": "INV-2024-003", "customer": "Alice Johnson", "amount": "$49.00", "status": "paid", "plan": "Starter Monthly"},
    }
    return invoices.get(customer_email.lower(), {"error": f"No invoice found for {customer_email}"})

def process_refund(invoice_id: str, reason: str) -> dict:
    """Process a refund for a specific invoice."""
    return {"refund_id": f"REF-{invoice_id[-3:]}", "status": "approved", "message": f"Refund for {invoice_id} approved. 5-7 business days."}

def search_knowledge_base(query: str) -> dict:
    """Search the knowledge base for technical solutions."""
    articles = {
        "login": {"title": "Login Issues", "solution": "1. Clear cache. 2. Try incognito. 3. Reset password. 4. 3 failed attempts = 30 min lockout."},
        "crash": {"title": "App Crashing", "solution": "1. Update to v3.2.1. 2. Clear app data. 3. Check OS: iOS 16+ / Android 13+."},
        "slow": {"title": "Performance Issues", "solution": "1. Check internet (min 5 Mbps). 2. Close other apps. 3. Enable hardware acceleration."},
    }
    for keyword, article in articles.items():
        if keyword in query.lower():
            return article
    return {"title": "General Support", "solution": "No specific article found. Contact support."}

def check_system_status() -> dict:
    """Check current status of all platform services."""
    return {
        "overall": "operational",
        "services": {"web_app": "operational", "api": "operational", "database": "operational", "auth_service": "degraded"},
        "last_incident": "2026-02-08 -- Auth service brief outage (resolved)",
    }

def create_escalation_ticket(customer_email: str, issue_summary: str, priority: str) -> dict:
    """Create an escalation ticket for issues needing human review."""
    times = {"low": "48 hours", "medium": "24 hours", "high": "4 hours", "critical": "1 hour"}
    return {"ticket_id": "ESC-2026-0042", "priority": priority, "estimated_response": times.get(priority, "24 hours")}

# --- Agents ---

billing_agent = Agent(
    name="billing_agent", model=MODEL,
    description="Handles billing: invoices, payments, refunds.",
    instruction="You are a billing specialist. Use lookup_invoice to find invoices. Use process_refund for refunds.",
    tools=[lookup_invoice, process_refund],
)

technical_agent = Agent(
    name="technical_agent", model=MODEL,
    description="Handles technical issues: bugs, crashes, performance.",
    instruction="You are a technical specialist. Use search_knowledge_base and check_system_status.",
    tools=[search_knowledge_base, check_system_status],
)

escalation_agent = Agent(
    name="escalation_agent", model=MODEL,
    description="Handles complaints, disputes, security concerns needing human review.",
    instruction="You are an escalation specialist. Use create_escalation_ticket to log cases.",
    tools=[create_escalation_ticket],
)

root_agent = Agent(
    name="customer_support_router", model=MODEL,
    instruction="Route to billing_agent, technical_agent, or escalation_agent. Never answer directly.",
    sub_agents=[billing_agent, technical_agent, escalation_agent],
)

# --- Runner ---

async def ask(agent, message):
    service = InMemorySessionService()
    runner = Runner(agent=agent, app_name="demo", session_service=service)
    session = await service.create_session(app_name="demo", user_id="user1")
    content = types.Content(role="user", parts=[types.Part(text=message)])
    async for event in runner.run_async(user_id="user1", session_id=session.id, new_message=content):
        if event.is_final_response() and event.content and event.content.parts:
            return event.content.parts[0].text
    return "(no response)"

async def main():
    tests = [
        ("BILLING", "I need to check my latest invoice. My email is bob@example.com. Can I get a refund?"),
        ("TECHNICAL", "My app keeps crashing every time I try to login. Is there an outage?"),
        ("ESCALATION", "Someone hacked my account! I see charges I didn't make. Email: jane@example.com. Urgent!"),
    ]
    for label, query in tests:
        print(f"\n--- {label} ---")
        print(f"User: {query}\n")
        print(f"Agent: {await ask(root_agent, query)}\n")

if __name__ == "__main__":
    asyncio.run(main())
