# Claude Architect Bootcamp — Week 1

**Session 1: Claude API Beyond Chat**

Live demo materials for engineers and technical PMs. Raw Anthropic Python SDK only — no frameworks.

## Setup

```bash
cd claude-architect-bootcamp/week-1
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then paste your ANTHROPIC_API_KEY
```

## Run

**Notebook (main demo):**

```bash
jupyter notebook week1_demo.ipynb
```

Restart kernel & clear all outputs before going live.

**Streaming (Section 5 companion — notebooks buffer streamed output):**

```bash
python stream_demo.py "Explain in 3 sentences why streaming improves perceived latency."
```

## Files

| File | Purpose |
|------|---------|
| `week1_demo.ipynb` | Live session notebook — API basics, tool loop, structured output, caching |
| `demo-ui/` | **Next.js live demo UI** — best for projecting to an audience |
| `stream_demo.py` | Standalone streaming demo (terminal) |
| `.env.example` | API key template |

## Next.js demo UI (recommended for live teaching)

```bash
cd demo-ui
npm install
cp .env.local.example .env.local   # paste ANTHROPIC_API_KEY
npm run dev
```

Open http://localhost:3001 — sidebar walks through all 5 sections with large readable outputs, streaming, and one-click demos. The API key stays server-side in `.env.local`.

**Teaching split:** Use the notebook when you want attendees to see raw SDK calls and response objects. Use the UI when you want maximum watchability on a projector.
