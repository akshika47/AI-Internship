# <Project name>

> The README is the first thing a hiring manager opens and often the only thing
> they read. Lead with the problem, not the stack.

**<One or two sentences: the problem, and who has it.>**

## Demo

<A GIF, a screenshot, or a link to the 3-minute video. Put it above the fold.>

## Architecture

<One diagram or a five-line description. Say what each component does and why
it exists. Name the thing you deliberately did not build.>

```
ticket -> structured-output call -> schema validation -> confidence gate -> queue
                                                              |
                                                       below threshold
                                                              v
                                                        human review
```

## Results

| Metric | Before (v1) | After | Target |
| --- | --- | --- | --- |
| Category accuracy | 78% | 93% | >= 90% |
| P1 recall | 81% | 97% | >= 95% |
| p95 latency | 3.1s | 1.4s | < 2s |
| Cost per record | $0.014 | $0.006 | < $0.01 |

Measured on <N> hand-labelled cases. Full method in
[`evals/report.md`](../evals/report.md).

## How to run

```bash
git clone <your repo>
cd <your repo>
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                 # add your ANTHROPIC_API_KEY
python scripts/run_samples.py
```

## What I would do next

<Three things, with the reason each is next rather than done. This section is
where interviewers find out whether you know the limits of your own system.>

## What this does not do

<The out-of-scope list from your brief, restated honestly.>
