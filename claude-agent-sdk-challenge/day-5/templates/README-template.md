# <Your agent's name>

<One sentence: who it's for and what it does.>

Built with the [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) during the TAI Labs
5-day challenge.

## Run it

You need [uv](https://docs.astral.sh/uv/) and an API key from [platform.claude.com](https://platform.claude.com/).

```bash
git clone <your repo link>
cd <your repo>
cp .env.example .env            # then paste your key into .env
uv run <your_agent>.py examples/<sample input>
```

## What it does

1. <step one, e.g. reads the file you give it>
2. <step two, e.g. checks it against your notes>
3. <what you get back, e.g. a report saved as report.md>

## What a run costs

About $<0.00> per run on the sample input. It stops after <N> turns or $<0.00>, whichever comes first.

## How I checked it

<One or two lines: the test or eval you can rerun, and what it caught. For example: "uv run run_evals.py
runs 4 scenarios; it caught the agent inventing a skill, so every claim now has to quote its source.">

## Safety

- It can only use these tools: <list>.
- <Your guardrail, e.g. it can only read files inside examples/.>

## What's next

<The one thing you'd add with another day.>
