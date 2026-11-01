# Week 1 v2: Minimal `/ask` Demo

This folder is the simplified class version of the Week 1 AI Engineering bootcamp demo.
Students run one final API and one small Streamlit page. The `stages/` files are optional
teaching references that show how the endpoint grows step by step.

## What Students Will Build

A typed FastAPI endpoint that accepts a question and returns:

- `answer`: a structured answer object
- `tokens_used`: token usage returned by the model provider
- `model`: the model used for the request
- `latency_ms`: how long the request took
- `cost_usd`: an estimated request cost
- `attempts`: validation and retry details for the guardrail demo

The main idea: an LLM call becomes more useful in software when it has a predictable
request shape, a predictable response shape, and observable runtime metadata.

## Week 2: RAG on top of `/ask`

The Week 1 service is extended, not rebuilt: a vector store, ingest, and retrieval now sit in
front of the same `/ask` handler (structured output, validate + retry, cost tracking).

| Endpoint | What it does |
|----------|--------------|
| `POST /ingest` | `document_id` + `text` → chunk with overlap (800 / 120 chars) → embed (`text-embedding-3-small`) → upsert into Chroma with metadata. Re-ingesting a `document_id` replaces it. |
| `POST /retrieve` | Question → top-k chunks + cosine scores. No LLM, so you can check retrieval on its own. |
| `POST /ask` | Retrieve → refuse right away if the best score is below `RAG_MIN_SCORE` (0.25) → otherwise answer from the context only, cite chunk IDs, refuse when the answer isn't there. Citations that don't match a retrieved chunk fail validation and trigger the retry. |
| `GET /documents` | Documents and chunk counts currently in the store. |

Code: `rag.py` (chunk, embed, Chroma store, retrieval) and `main.py` (endpoints + grounding).
Sample doc: `sample_docs/northwind_handbook.md` (a fictional handbook, so the model can't
answer from its training data).

Prove it end to end with curl (saves `curl_demo_output.txt`):

```bash
./curl_demo.sh http://127.0.0.1:8000
./curl_demo.sh https://week1-ask-api.onrender.com   # live Render URL
```

The script ingests the handbook, runs retrieval, then asks one question the handbook answers
(cited answer) and one it doesn't (refusal).

**Storage on Render:** by default Chroma writes to `./chroma_db`. The free Render plan wipes
the disk on every deploy and restart, and after ~15 minutes idle, so ingest again before you ask
(the Streamlit Ingest tab or `curl_demo.sh` does this). For storage that persists, create a free
Chroma Cloud database and set `CHROMA_API_KEY`, `CHROMA_TENANT`, `CHROMA_DATABASE` on the API
service. `rag.py` switches to Chroma Cloud automatically when `CHROMA_API_KEY` is set.

## Quick Start

Run these commands from this `week-1v2` folder:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
test -f .env || cp .env.example .env
```

Open `.env` and add your key:

```bash
OPENAI_API_KEY=sk-...
```

## Terminal 1: Start the API

```bash
source .venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Check that the API is running without spending tokens:

```bash
curl http://127.0.0.1:8000/health
```

You can also open the generated API docs:

```text
http://127.0.0.1:8000/docs
```

## Terminal 2: Start the Demo Page

```bash
source .venv/bin/activate
streamlit run demo_page.py
```

Open:

```text
http://localhost:8501
```

Use the page to ask a question, switch models, inspect the JSON response, and copy the
equivalent `curl` request.

## Try the Guardrail Demo

Turn on **Force a bad first response to demo validation + retry** in the Streamlit page.
The API intentionally asks the model for malformed JSON on the first attempt, validates
that response with Pydantic, records the failure, and retries with structured output.

This is a small classroom-friendly example of a production habit: do not trust free-form
LLM output at the boundary of your application.

## Test With Curl

Ingest a document first (or run `./curl_demo.sh`), then a normal request:

```bash
curl -s -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the daily meal allowance when traveling internationally?", "model": "gpt-4o-mini"}'
```

Validation and retry demo:

```bash
curl -s -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How much is the home office stipend?", "model": "gpt-4o-mini", "force_bad": true}'
```

## Instructor Flow

Use `main.py` and `demo_page.py` for the live student demo. Open the stage files only when
you want to explain how each capability was introduced:

| Stage | File | Teaching point |
|-------|------|----------------|
| 1 | `stages/stage_1_bare_ask.py` | Smallest typed `/ask`: question in, string answer out. |
| 2 | `stages/stage_2_structured_output.py` | Add a Pydantic `Answer` schema and OpenAI structured output. |
| 3 | `stages/stage_3_guardrails_and_observability.py` | Add validation retry, model selection, latency, and cost. |

Run one stage at a time if you want to teach the build-up live:

```bash
uvicorn stages.stage_1_bare_ask:app --host 127.0.0.1 --port 8000 --reload
uvicorn stages.stage_2_structured_output:app --host 127.0.0.1 --port 8000 --reload
uvicorn stages.stage_3_guardrails_and_observability:app --host 127.0.0.1 --port 8000 --reload
```

## Smoke Test

This starts the final API, checks `/health` and `/docs`, and does not call OpenAI:

```bash
source .venv/bin/activate
python smoke_test.py
```

## File Map

```text
week-1v2/
├── README.md
├── main.py                         # API: /ingest, /retrieve, grounded /ask
├── rag.py                          # Chunking, embeddings, Chroma vector store
├── demo_page.py                    # Streamlit UI: Ingest / Retrieve / Ask tabs
├── curl_demo.sh                    # curl proof of ingest + cited answer + refusal
├── sample_docs/northwind_handbook.md
├── smoke_test.py                   # No-token API startup check
├── requirements.txt
├── .env.example
├── .gitignore
└── stages/
    ├── stage_1_bare_ask.py
    ├── stage_2_structured_output.py
    └── stage_3_guardrails_and_observability.py
```

## Troubleshooting

- `Cannot reach http://127.0.0.1:8000`: start the API server in another terminal.
- `OPENAI_API_KEY` error: make sure `.env` exists and contains a real key.
- `Address already in use`: another server is already using port `8000`; stop it or use a different port.
- Streamlit opens but requests fail: confirm the sidebar API base URL is `http://127.0.0.1:8000`.
