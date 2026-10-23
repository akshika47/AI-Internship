"""Week 1 live demo — five stages in one file, built up live in class."""

import os
import time
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

from vector_store import EMBED_PRICE_PER_1K, check_pinecone, ingest_document, retrieve

# Load .env from this folder so the key is found regardless of shell working directory.
_ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(_ENV_PATH)

# Reuse one client so TLS handshakes are not repeated on every request.
app = FastAPI()
client = OpenAI()  # Reads OPENAI_API_KEY from the environment; never hardcode keys.

# Stage 4 default — strong general model; swap at request time for the live demo.
DEFAULT_MODEL = "gpt-4o"
TOP_K = 5

# The model sees this text, not the raw question. Chunks are filled in at request time.
GROUNDING_PROMPT = """Answer using ONLY the context below.
If the context does not contain the answer, say:
"I don't have enough information to answer that."
Cite the document_id of each chunk you used.

Context:
{retrieved_chunks}

Question: {question}
"""

# Stage 5 — per-1K-token input/output USD (derived from OpenAI list prices).
MODEL_PRICES_PER_1K: dict[str, tuple[float, float]] = {
    "gpt-4o": (0.0025, 0.01),
    "gpt-4o-mini": (0.00015, 0.0006),
    "o3-mini": (0.0011, 0.0044),
}


class Answer(BaseModel):
    """Structured model output — this is what turns a chatbot into a component."""

    answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    sources_needed: bool


class AskRequest(BaseModel):
    """Typed request body so bad input is rejected before we spend tokens."""

    question: str
    force_bad: bool = False  # Stage 3 demo knob — first attempt breaks schema on purpose.
    model: str | None = None  # Stage 4 — optional override to swap models live.


class IngestRequest(BaseModel):
    """One document to chunk, embed, and store."""

    document_id: str
    text: str
    source: str | None = None  # Optional filename or other origin label.
    metadata: dict | None = None


class IngestResponse(BaseModel):
    """What callers get after a document is stored."""

    document_id: str
    chunks_indexed: int
    status: str


class AskResponse(BaseModel):
    """Typed response so callers always get the same shape back."""

    answer: Answer
    tokens_used: int
    model: str
    latency_ms: int
    cost_usd: float
    chunk_ids: list[str]


def build_grounding_prompt(question: str, chunks: list[dict]) -> str:
    """Fill the grounding template with retrieved chunks."""

    blocks: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        metadata = chunk.get("metadata") or {}
        blocks.append(
            f"[{index}] chunk_id={chunk['id']} document_id={metadata.get('document_id', '')}\n"
            f"{chunk.get('text', '')}"
        )
    retrieved_chunks = "\n\n".join(blocks) if blocks else "(no context retrieved)"
    return GROUNDING_PROMPT.replace("{retrieved_chunks}", retrieved_chunks).replace(
        "{question}", question
    )


def compute_cost_usd(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Turn real usage into dollars — same prompt, different model, different cost."""

    prices = MODEL_PRICES_PER_1K.get(model, MODEL_PRICES_PER_1K[DEFAULT_MODEL])
    input_per_1k, output_per_1k = prices
    return (prompt_tokens / 1000 * input_per_1k) + (completion_tokens / 1000 * output_per_1k)


def call_model_structured(question: str, model: str) -> tuple[Answer, int, int, int]:
    """
    Stage 2 center: OpenAI structured output forces exactly the Answer schema.
    Returns parsed answer plus token counts from billing metadata.
    """

    completion = client.chat.completions.parse(
        model=model,
        messages=[{"role": "user", "content": question}],
        response_format=Answer,
    )

    parsed = completion.choices[0].message.parsed
    if parsed is None:
        raise ValueError("Model returned no parseable structured output")

    usage = completion.usage
    total = usage.total_tokens if usage else 0
    prompt_tokens = usage.prompt_tokens if usage else 0
    completion_tokens = usage.completion_tokens if usage else 0
    return parsed, total, prompt_tokens, completion_tokens


def call_model_unsafe(question: str, model: str) -> tuple[Answer, int, int, int]:
    """
    Stage 3 demo path: free-form JSON call, then validate locally.
    The bad instruction makes confidence a string so Pydantic rejects it reliably.
    """

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": (
                    f"{question}\n\n"
                    "Reply with ONLY a JSON object using keys answer, confidence, sources_needed. "
                    "Set confidence to the string 'very high' (not a number)."
                ),
            }
        ],
    )

    raw = completion.choices[0].message.content or ""
    # Guardrail: refuse malformed output instead of passing it through to clients.
    answer = Answer.model_validate_json(raw)

    usage = completion.usage
    total = usage.total_tokens if usage else 0
    prompt_tokens = usage.prompt_tokens if usage else 0
    completion_tokens = usage.completion_tokens if usage else 0
    return answer, total, prompt_tokens, completion_tokens


# curl -s -X POST http://127.0.0.1:8000/ask \
#   -H "Content-Type: application/json" \
#   -d '{"question": "What is a Lang factor?"}'
@app.post("/ask")
def ask(body: AskRequest) -> AskResponse:
    """Retrieve chunks, then answer with the Session 1 structured generation path."""

    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="question must be non-empty")

    model = body.model or DEFAULT_MODEL
    start = time.perf_counter()
    try:
        chunks, embed_tokens = retrieve(client, question, top_k=TOP_K)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=_public_error(exc)) from exc

    prompt = build_grounding_prompt(question, chunks)
    chunk_ids = [str(chunk["id"]) for chunk in chunks]
    last_error: str | None = None

    # Stage 3: one retry keeps the logic legible while still protecting callers.
    for attempt in range(2):
        try:
            # First attempt with force_bad uses the unsafe path; retry uses structured output.
            use_bad_path = body.force_bad and attempt == 0
            if use_bad_path:
                answer, tokens_used, prompt_tokens, completion_tokens = call_model_unsafe(
                    prompt, model
                )
            else:
                answer, tokens_used, prompt_tokens, completion_tokens = call_model_structured(
                    prompt, model
                )

            latency_ms = int((time.perf_counter() - start) * 1000)
            cost_usd = compute_cost_usd(model, prompt_tokens, completion_tokens)
            cost_usd += embed_tokens / 1000 * EMBED_PRICE_PER_1K

            return AskResponse(
                answer=answer,
                tokens_used=tokens_used + embed_tokens,
                model=model,
                latency_ms=latency_ms,
                cost_usd=round(cost_usd, 6),
                chunk_ids=chunk_ids,
            )
        except (ValidationError, ValueError) as exc:
            last_error = str(exc)
            continue

    # Clean failure — never leak a half-parsed response to the client.
    raise HTTPException(
        status_code=502,
        detail=f"Model response failed schema validation after retry: {last_error}",
    )


def _public_error(exc: Exception) -> str:
    """Hide API keys if a provider echoes them back in an error."""

    message = f"{type(exc).__name__}: {exc}"
    for name in ("PINECONE_API_KEY", "OPENAI_API_KEY"):
        secret = os.getenv(name, "")
        if secret:
            message = message.replace(secret, "[redacted]")
    return message


def _source_from(body: IngestRequest) -> str:
    """Prefer an explicit source, then a filename stored in metadata."""

    if body.source and body.source.strip():
        return body.source.strip()
    extra = body.metadata or {}
    for key in ("source", "filename", "source_filename"):
        value = extra.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


# curl -s -X POST http://127.0.0.1:8000/ingest \
#   -H "Content-Type: application/json" \
#   -d '{"document_id":"notes-1","text":"Retrieval stores chunks as vectors.","source":"notes.txt"}'
@app.post("/ingest")
def ingest(body: IngestRequest) -> IngestResponse:
    """Chunk a document, embed each chunk, and upsert it into Pinecone."""

    document_id = body.document_id.strip()
    text = body.text.strip()
    if not document_id or not text:
        raise HTTPException(
            status_code=400,
            detail="document_id and text must be non-empty",
        )

    try:
        chunks_indexed = ingest_document(
            client,
            document_id,
            text,
            source=_source_from(body),
            metadata=body.metadata,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=_public_error(exc)) from exc

    return IngestResponse(
        document_id=document_id,
        chunks_indexed=chunks_indexed,
        status="indexed",
    )


@app.get("/health/pinecone")
def pinecone_health() -> dict:
    """Debug check: confirm the Pinecone key can reach the configured index."""

    try:
        return check_pinecone()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=_public_error(exc)) from exc
