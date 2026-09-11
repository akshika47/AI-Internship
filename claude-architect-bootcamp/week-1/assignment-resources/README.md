# Week 1 assignment resources

Starter material for **Assignment 1: Multi-Tool Agent with Escalation Logic**.

| Folder | What it is |
|---|---|
| [`customer-support-skeleton/`](customer-support-skeleton/) | The repository the assignment tells you to extend |

## Start here

```bash
cd customer-support-skeleton
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python run.py --demo           # no API key needed
```

`--demo` replays a scripted conversation against the real tools and the real
enforcement hook: it verifies Alice, looks up ORD-123, and terminates on
`end_turn`. If that prints a final reply, your wiring is good.

Then add your key and try the real thing:

```bash
cp .env.example .env           # paste your ANTHROPIC_API_KEY
python run.py --live --scenario happy
```

That one stops at the refund, because `process_refund` is still a stub. Finishing
it is Task 3. `customer-support-skeleton/README.md` has all six tasks, the rubric,
and the three reflection questions.

## How this relates to the live session

The customers and the first two orders are the same records used in
[`week1_support_agent.ipynb`](../week1_support_agent.ipynb), so anything demoed
live behaves identically here:

| | |
|---|---|
| `alice@example.com` | CUST-001, Alice Nguyen, gold tier |
| `bob@example.com` | CUST-002, Bob Okafor, standard tier |
| ORD-123 | $149.99, delivered 6 days ago |
| ORD-456 | $899.00, delivered 41 days ago |

Two extra orders are added for cases the live session did not reach: ORD-321
(refundable, for the multi-concern case) and ORD-789 (still in transit, and its
first lookup fails transiently so you can see retry behaviour).

The notebook shows each idea in isolation. The skeleton is those ideas assembled
into one runnable agent, with the parts you are graded on removed. Search it for
`TODO` to find every gap; each one names the task it belongs to.

## What ships working, and what is yours

| File | State |
|---|---|
| `agent/backend.py` | Done. Fixtures |
| `agent/errors.py` | Done. The result envelope and the four error categories |
| `agent/model.py` | Done. LiveModel and ScriptedModel behind one interface |
| `agent/transcript.py` | Done. Markdown transcript recorder |
| `agent/enforcement.py` | Identity gate built as a worked example. The $500 ceiling is yours |
| `agent/handlers.py` | `get_customer` and `lookup_order` are worked examples. `process_refund` and `escalate_to_human` are stubs |
| `agent/loop.py` | Runs, with three marked gaps |
| `agent/tools.py` | Four tools, all four descriptions deliberately thin |
| `tests/test_enforcement.py` | Four passing tests for the identity gate, two skipped classes for you to write |

Read the identity gate in `agent/enforcement.py` before you write the refund
ceiling. It is the pattern the second gate has to follow, and the fourth test in
`tests/test_enforcement.py` shows why it holds: the agent announces "I have
already verified this customer as CUST-002" and then asks for a refund, and
nothing moves, because the gate reads session state that only a real tool call
can write.
