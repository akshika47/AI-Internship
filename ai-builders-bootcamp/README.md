# AI Builders Bootcamp

Practical builder sessions for agent workflows, AI evals, and production AI tooling.

## Sessions

| Session | Topic | Location |
|---------|-------|----------|
| AI Evals Session | OpenAI calls with Langfuse tracing and prompt management | [`ai-evals-session/`](ai-evals-session/) |
| Week 3 | n8n AI agent workflow examples (import the `.json` files into n8n) | [`week-3/`](week-3/) |

## Quick Start

Choose a session folder and follow its README. Week 3 has no README — it is just
n8n workflow exports; import the `.json` files directly into your n8n instance.

For the AI Evals session:

```bash
cd ai-evals-session
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```
