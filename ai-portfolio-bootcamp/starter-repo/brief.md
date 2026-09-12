# Problem brief

One page. Five sections. Due end of Week 0.

A brief gets sent back for: a persona that is a category rather than a person,
a success metric nobody can compute, a missing out-of-scope section, a
"workflow today" that is really a description of the system you want to build,
and scope that needs a diagram to explain.

---

## 1. Persona

Who specifically. A named role at a named kind of company, not a market segment.

> Replace: *"Priya, a support team lead at a 30-person B2B SaaS company. She
> owns first-response time and reports it to her VP weekly."*

Not: *"small businesses"*, *"enterprise teams"*.

## 2. Workflow today

What this person does right now, without your system. Include how long it takes
and where it goes wrong. If you cannot describe today's workflow, you do not
understand the problem yet.

> Replace: *"Every morning Priya reads the overnight queue - 40 to 60 tickets -
> and manually tags each with a category and priority. It takes 50 minutes.
> She misses roughly two urgent tickets a week because they arrive worded
> calmly."*

## 3. What the system does

Inputs, outputs, and what happens when the system is not confident. **Name the
fields.** If a human stays in the loop, say exactly where.

> Replace: *"In: ticket subject and body. Out: category (one of six), priority
> (P1/P2/P3), a one-sentence summary, a confidence score, and a needs_human
> flag. Below 0.75 confidence, or any ticket involving a refund, the record is
> flagged and Priya reviews it before it is actioned."*

## 4. Success metric

Numbers you will measure on a golden set, **decided now, before you build**. At
least one quality metric and one operational metric.

```
Success metric
- Category accuracy >= 90% on the 40-case golden set
- P1 recall >= 95% (a missed P1 is the expensive failure, a false P1 is cheap)
- p95 latency < 2s per ticket
- < $0.01 per ticket at current pricing

Measured on: 40 hand-labelled tickets, including 10 deliberately hard cases.
```

## 5. Out of scope

Three to five things you are deliberately **not** doing. This is what keeps a
three-week project three weeks long, and interviewers read it as judgment.

> Replace:
> - *No multi-language support. English tickets only.*
> - *No automatic replies. The system tags, a human still answers.*
> - *No integration with the live helpdesk. It reads an export.*
> - *No fine-tuning. Prompt and schema only.*

---

## Hand in with this

- Which role track: AI Engineer, FDE, or AI PM.
- Which problem: bank number, bring-your-own, or a live partner application.
- A one-line self-score on the "real problem" rubric dimension, with reasoning.
