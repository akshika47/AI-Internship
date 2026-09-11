# customer-support-skeleton

Starter repository for **Claude Architect, Week 1, Assignment 1: Multi-Tool Agent with
Escalation Logic**.

You are building a customer support resolution agent for a mid-size e-commerce retailer.
It handles returns, billing disputes and account issues, and reaches the backend through
four tools. The business target is 80%+ first-contact resolution, with correct escalation
on the remainder, and three non-negotiables:

- No order operation may occur before customer identity is verified.
- Refunds above $500 require human approval.
- Explicit customer requests for a human are honoured immediately.

---

## Get it running first

```bash
python -m venv .venv
. .venv/Scripts/activate        # Windows.  macOS/Linux: . .venv/bin/activate
pip install -r requirements.txt

python run.py --demo            # no API key needed
```

You should see a scripted run that verifies Alice, looks up ORD-123, and terminates on
`end_turn`. That is the wiring check: two handlers work, the identity gate lets them
through, the loop turns over. Everything else is yours.

Then add your key and try the real thing:

```bash
cp .env.example .env            # put your ANTHROPIC_API_KEY in it
python run.py --live --scenario happy
```

It will not get far yet. `process_refund` raises `NotImplementedError`. That is Task 3.

---

## What is here

| File | State |
|---|---|
| `agent/backend.py` | **Done.** Fixtures: customers, orders, the return window |
| `agent/errors.py` | **Done.** The result envelope and the four error categories |
| `agent/model.py` | **Done.** LiveModel and ScriptedModel behind one interface |
| `agent/transcript.py` | **Done.** Markdown transcript recorder |
| `agent/session.py` | Mostly done. One field is yours |
| `agent/handlers.py` | Two worked examples, two stubs |
| `agent/enforcement.py` | One gate built as a worked example, one is yours |
| `agent/loop.py` | Runs, with three marked gaps |
| `agent/tools.py` | Four tools, all four descriptions deliberately thin |
| `tests/test_enforcement.py` | Four passing tests, two skipped classes to fill in |

Every gap is marked `TODO (Task N)` and names the task below. Search for `TODO` to find
all of them.

---

## The six tasks

**1. Tool descriptions** (`agent/tools.py`). Each description must state purpose, expected
inputs with formats, outputs, and explicit boundaries against similar tools. At least two
tools have genuinely overlapping surface area. Write descriptions that let the model
discriminate between them reliably despite that overlap. Fix it in the descriptions, not
with a routing layer in front of the model.

**2. The agentic loop** (`agent/loop.py`). Correct `stop_reason` handling: continue on
`tool_use`, terminate on `end_turn`, append tool results to conversation history between
iterations. You must not use natural-language parsing or an iteration cap as your primary
termination mechanism. A cap as a safety net is fine and expected: label it as such in a
comment. Three gaps are marked 2A, 2B and 2C.

**3. Structured errors** (`agent/handlers.py`). Every tool returns structured errors with
`errorCategory` (transient / validation / business / permission), `isRetryable`, and a
human-readable description. Business rule violations are not retryable and carry a
customer-facing explanation. The helpers are in `errors.py`; the two worked handlers show
the pattern. Demonstrate the agent behaving correctly against each category.

**4. Programmatic enforcement** (`agent/enforcement.py`). Two enforcement points, both in
code, neither in the system prompt:

- a prerequisite gate blocking `lookup_order` and `process_refund` until `get_customer`
  returns a verified customer ID (**built for you, read it**);
- a tool-call interception hook blocking refunds above $500 (**yours**).

Prove the enforcement holds with a test where the system prompt is deliberately weakened
or instructed to skip verification, and show the gate still blocks. That test carries
significant weight in the rubric. Scaffolding is in `tests/test_enforcement.py`.

**5. Multi-concern handling.** A single message containing two or more distinct issues:
decompose them, investigate in parallel against shared context, answer once. This mostly
falls out of Task 2B, and it will not work until you fix it.

**6. Structured handoff** (`agent/handlers.py`). Escalation produces a summary containing
customer ID, root cause, amounts and recommended action. Assume the human has no access to
the transcript.

---

## Fixtures

| Order | Customer | Amount | State |
|---|---|---|---|
| ORD-123 | Alice Nguyen, CUST-001 | $149.99 | Delivered 6 days ago, return window open |
| ORD-456 | Bob Okafor, CUST-002 | $899.00 | Delivered 41 days ago, housing crushed. Over the ceiling **and** outside the window |
| ORD-321 | Bob Okafor, CUST-002 | $64.00 | Delivered 9 days ago, refundable |
| ORD-789 | Alice Nguyen, CUST-001 | $28.00 | Still in transit. First lookup fails transiently |

Emails are `alice@example.com` and `bob@example.com`. These are the same records used in
the Week 1 laboratory notebook, so anything demoed live behaves identically here.

---

## Deliverables

1. **This repository, extended and runnable.**
2. **Two transcripts**, in `transcripts/`:
   - happy path: Alice, ORD-123
   - escalation: Bob, ORD-456, or an explicit "I want a human"

   Generate them with `python run.py --live --scenario happy` and
   `python run.py --live --scenario escalation`. `--scenario human` gives you the explicit
   request for a person, if you would rather use that one.
3. **This README, with the three reflection answers filled in below.**

---

## Reflection

Answer all three. Depth beats length, but a paragraph each is not depth. Restating the
brief scores nothing.

### 1. You put the refund ceiling in code. Argue the case for a system prompt instruction instead, then explain why it loses. Be specific about failure rate and money.

> Your answer here. Make the case for the prompt honestly and at its strongest before you
> knock it down: what does a prompt instruction genuinely do better than a hook? Then put
> numbers on the failure. Conversations per month, share of them over $500, compliance
> rate, average amount at risk. Work out what that costs per year, and say what the gate
> costs instead.

### 2. Your two similar tools: what did you write so Claude can tell them apart, and how would you notice misrouting in production?

> Your answer here. Quote the actual text you added. Then the harder half: the two
> directions of misroute do not look the same in production. One of them is loud and one
> of them is invisible. What would you put on a dashboard, and what would you alert on?

### 3. Every `tool_result` is resent on later turns. What did you strip from payloads, and what would break if a summary dropped the refund amount?

> Your answer here. List what you removed and why. Then trace the second question
> properly: if a compaction step dropped the refund amount from a tool result, what
> actually goes wrong, and does your $500 ceiling still hold? Where does the number your
> ceiling depends on actually live?

---

## Rubric

| Criterion | Points |
|---|---|
| Tool descriptions | 15 |
| Agentic loop | 20 |
| Error handling | 15 |
| Enforcement | 25 |
| Multi-concern and handoff | 15 |
| Reflection | 10 |

Weight: 20% of the course. Estimated 2 hours. Maps to exam Scenario 1, Customer Support
Resolution Agent, Domains 1 (primary), 2 and 5.

---

## Licence

MIT. See [LICENSE](LICENSE). Fork it, change it, keep your work.
