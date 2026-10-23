# 5-Day Challenge: Build Your First AI Agent with the Claude Agent SDK

Code for the TAI Labs community challenge, 19 to 23 October 2026. Each day has its own
folder with code that runs as-is, a README you can follow step by step, and fixes for the
errors people usually hit.

The [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) gives your
code the same agent loop and tools that power Claude Code: you give it a goal and the
tools it's allowed to use, and it works out the steps.

## How it works

You build your own agent this week, for whatever you choose. Dr Aki builds one alongside
you and shares each day's step here: a **job-fit agent** that compares a CV with a job ad.
It's a working example to learn from or copy from, not the assignment.

## Who this is for

If you can copy a command into a terminal, you can do Day 1. Python is the main path and
uses [uv](https://docs.astral.sh/uv/), so you don't need to set up Python yourself. If you
already write TypeScript, every day has a `typescript/` folder with the same agent.

## The five days

| Day | Goal | You're done when | Folder |
|---|---|---|---|
| 1 | Set up and run your first agent | An agent runs on your machine: Dr Aki's, the official quickstart, or your own | [`day-1/`](day-1/) |
| 2 | Give it tools | Your agent calls one tool you wrote yourself | [`day-2/`](day-2/) |
| 3 | Make it useful for a real task of yours | It does one real task from your week, the way you like it done | [`day-3/`](day-3/) |
| 4 | Break it, fix it, add guardrails | You've found one way it goes wrong and stopped it | [`day-4/`](day-4/) |
| 5 | Debug it, test it, show us | You found a bug in its steps, turned it into a test, and posted a one-minute demo | [`day-5/`](day-5/) |

Each folder has Dr Aki's worked example and, from Day 2, a small starter you can copy.
Both are optional: any route that gets you to "done" counts.

## Before you start

- An API key from [platform.claude.com](https://platform.claude.com/) with a little credit.
  The SDK is billed through the API, so a Claude Pro or Max plan doesn't cover it.
- Put it in **one** `.env` file in this folder: `cp .env.example .env`, then paste your key.
  Every day's code finds it, so you set it once.
- Every agent here has a spending cap per run (`max_budget_usd`), so a mistake can't run up a bill.

## Tests

Every pull request that touches this folder runs free checks in GitHub Actions: each day's Python
compiles, Day 4's offline tests pass, and each day's TypeScript type-checks. Day 4's agent
evaluations run only when started by hand, because they call Claude. See the Day 4 README.

## Share your progress

Post a screenshot or a short Loom in the challenge thread each day. Messy is fine.
