# RAG Demo — Lightning Lesson

Instructor-run end-to-end RAG: index a tiny NovaDesk corpus → retrieve top-3 → answer grounded in those chunks.

## Setup

```bash
cd lightning-lesson-demos/rag-demo
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

`.env` is symlinked to `ai-engineering-bootcamp-v2/week-1v2/.env` (`OPENAI_API_KEY`). Or copy `.env.example` → `.env`.

## Run

```bash
cd lightning-lesson-demos/rag-demo
source .venv/bin/activate
uvicorn app:app --reload --port 8766
```

Open [http://127.0.0.1:8766](http://127.0.0.1:8766)

## Demo flow (~5–8 min)

1. Show the status line: **Indexed 6 chunks** (expand “Show indexed corpus” if useful).
2. Click sample **“How many days of PTO do new hires get?”** → point at retrieved PTO chunk + score → read the answer.
3. Optional second ask: **“What’s the refund window for defective items?”** → expect the January 2025 / 60-day chunk.

Spoken beat: *docs → embeddings → similarity search → LLM only sees retrieved context.*
