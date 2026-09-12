# Eval report - <project name>

> The single most valuable artefact in your portfolio. Almost nobody has one.
> It generates more interview questions than your code does.
>
> A 3 needs a golden set, a pass rate, and a failure taxonomy.
> A 4 needs before/after with cost and latency, plus a regression suite.

## 1. Golden set

- **Cases:** <N>
- **Source:** <where they came from>
- **Labelling:** I labelled these by hand. <Say so plainly. Say who, and when.>
- **Slices:**

| Slice | Cases | Why this slice exists |
| --- | --- | --- |
| clear | 24 | The everyday case |
| ambiguous-category | 8 | Could reasonably be two categories |
| calm-urgent | 5 | P1 worded politely - the failure that costs money |
| non-english-fragment | 3 | Out of scope, included to prove it degrades safely |

## 2. Scoring method

| Field | How scored |
| --- | --- |
| category | Exact match against hand label |
| priority | Exact match |
| needs_human | Exact match |

<If you used an LLM judge: give its prompt, its model, and its agreement rate
against your hand labels. A judge you have not validated is not a measurement.>

## 3. Results, before and after

"Before" is your Week 1 v1. Do not quietly drop the slices that did badly.

| Metric | Before | After | Target | Met |
| --- | --- | --- | --- | --- |
| Category accuracy | | | | |
| P1 recall | | | | |
| p95 latency | | | | |
| Cost / record | | | | |

Per slice:

| Slice | Before | After |
| --- | --- | --- |
| clear | | |
| ambiguous-category | | |
| calm-urgent | | |

## 4. Failure taxonomy

Every remaining failure in a named category, with a count and one line on why.
**Include the ones you did not fix.**

| Category | Count | Why it fails | Fixed? |
| --- | --- | --- | --- |
| Politely-worded outage read as P2 | 4 | No urgency words in the text | Partly |
| Refund vs billing-question confusion | 3 | Both mention charges | No |

## 5. Cost and latency

| | p50 | p95 |
| --- | --- | --- |
| Latency | | |

- Input tokens / record: <avg>
- Output tokens / record: <avg>
- Cost / record: $<x>  ->  per 1,000: $<y>
- Retry rate: <n>%

## 6. Changelog

One entry per change, in order, each with the number it moved. This is what
proves you iterated rather than got lucky.

| # | Change | Metric moved | From -> To |
| --- | --- | --- | --- |
| 1 | Added explicit P1 definition to system prompt | P1 recall | 81% -> 91% |
| 2 | Moved needs_human out of the model into code | needs_human acc | 74% -> 99% |
| 3 | Added 5 calm-urgent cases to golden set | (found 4 new failures) | - |
