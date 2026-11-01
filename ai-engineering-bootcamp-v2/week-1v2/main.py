"""Week 2 RAG API: the Week 1 `/ask` endpoint with retrieval + grounding in front of it.

Endpoints:
  POST /ingest    text + document_id -> chunk (with overlap) -> embed -> upsert with metadata
  POST /retrieve  question -> top-k chunks + scores (no LLM, for testing retrieval alone)
  POST /ask       retrieve -> ground (context only, cite chunk IDs, refuse if missing) -> generate
  GET  /documents what is in the vector store

Run:
  uvicorn main:app --host 127.0.0.1 --port 8000 --reload
"""

import os
import time
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

THIS_DIR = Path(__file__).resolve().parent
load_dotenv(THIS_DIR / ".env")
load_dotenv(THIS_DIR.parent / ".env")

import rag  # noqa: E402  (reads CHROMA_* settings, so load .env first)

app = FastAPI(title="Week 2 RAG /ask Demo")
_client: OpenAI | None = None

ModelName = Literal["gpt-4o-mini", "gpt-4o", "o3-mini"]
DEFAULT_MODEL: ModelName = "gpt-4o-mini"
MODEL_PRICES_PER_1K: dict[str, tuple[float, float]] = {
    "gpt-4o": (0.0025, 0.01),
    "gpt-4o-mini": (0.00015, 0.0006),
    "o3-mini": (0.0011, 0.0044),
}

# Below this cosine similarity the best chunk is treated as "not about the question",
# so /ask refuses without spending an LLM call.
MIN_RELEVANCE_SCORE = float(os.getenv("RAG_MIN_SCORE", "0.25"))
REFUSAL_TEXT = "I don't know. The ingested documents don't contain the answer to that question."

GROUNDING_PROMPT = """You answer questions using ONLY the context chunks below.

Rules:
- Use only facts stated in the context. Do not use outside knowledge.
- Every factual sentence must be supported by at least one chunk. Put the IDs of the
  chunks you used in `citations`, and cite them inline like [doc::chunk-000].
- If the context does not contain the answer, set refused=true, citations=[], and
  answer exactly: "{refusal}"
- Do not partially guess. A missing answer is a refusal.

Context:
{context}"""


class Answer(BaseModel):
    """The grounded output shape we want every caller to receive."""

    answer: str = Field(min_length=1)
    citations: list[str]
    refused: bool
    confidence: float = Field(ge=0.0, le=1.0)


class IngestRequest(BaseModel):
    document_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9._-]+$")
    text: str = Field(min_length=1)
    chunk_size: int = Field(default=rag.DEFAULT_CHUNK_SIZE, ge=100, le=4000)
    chunk_overlap: int = Field(default=rag.DEFAULT_CHUNK_OVERLAP, ge=0, le=1000)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)


class IngestResponse(BaseModel):
    document_id: str
    chunks_upserted: int
    chunk_ids: list[str]
    chunk_size: int
    chunk_overlap: int
    embedding_model: str
    embedding_tokens: int
    latency_ms: int
    cost_usd: float


class RetrieveRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=4, ge=1, le=20)
    document_id: str | None = None


class RetrievedChunk(BaseModel):
    chunk_id: str
    document_id: str
    score: float
    text: str
    metadata: dict


class RetrieveResponse(BaseModel):
    question: str
    top_k: int
    chunks: list[RetrievedChunk]
    latency_ms: int


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    model: ModelName | None = None
    force_bad: bool = False
    top_k: int = Field(default=4, ge=1, le=20)
    document_id: str | None = None


class AttemptResult(BaseModel):
    attempt: int
    step: str
    ok: bool
    message: str
    raw_output: str | None = None
    validation_error: str | None = None


class AskResponse(BaseModel):
    answer: Answer
    retrieved_chunks: list[RetrievedChunk]
    tokens_used: int
    model: str
    latency_ms: int
    cost_usd: float
    attempts: list[AttemptResult]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def compute_cost_usd(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    input_per_1k, output_per_1k = MODEL_PRICES_PER_1K.get(
        model, MODEL_PRICES_PER_1K[DEFAULT_MODEL]
    )
    return (prompt_tokens / 1000 * input_per_1k) + (
        completion_tokens / 1000 * output_per_1k
    )


def embedding_cost_usd(tokens: int) -> float:
    return tokens / 1000 * rag.EMBEDDING_PRICE_PER_1K


def usage_counts(completion) -> tuple[int, int, int]:
    usage = completion.usage
    if usage is None:
        return 0, 0, 0
    return usage.total_tokens, usage.prompt_tokens, usage.completion_tokens


def grounded_messages(question: str, chunks: list[RetrievedChunk]) -> list[dict]:
    context = "\n\n".join(f"[{c.chunk_id}]\n{c.text}" for c in chunks)
    return [
        {
            "role": "system",
            "content": GROUNDING_PROMPT.format(refusal=REFUSAL_TEXT, context=context),
        },
        {"role": "user", "content": question},
    ]


def check_citations(answer: Answer, chunks: list[RetrievedChunk]) -> Answer:
    """Keep only citations that point at chunks we actually retrieved."""

    retrieved_ids = {c.chunk_id for c in chunks}
    valid = [cid for cid in dict.fromkeys(answer.citations) if cid in retrieved_ids]
    if answer.refused:
        return answer.model_copy(update={"citations": []})
    if not valid:
        raise ValueError(
            f"Answer cited no retrieved chunk (cited {answer.citations}, "
            f"retrieved {sorted(retrieved_ids)})"
        )
    return answer.model_copy(update={"citations": valid})


def call_structured_model(
    messages: list[dict], model: ModelName
) -> tuple[Answer, int, int, int]:
    completion = get_client().chat.completions.parse(
        model=model,
        messages=messages,
        response_format=Answer,
    )

    parsed = completion.choices[0].message.parsed
    if parsed is None:
        raise ValueError("Model returned no parseable structured output")

    total_tokens, prompt_tokens, completion_tokens = usage_counts(completion)
    return parsed, total_tokens, prompt_tokens, completion_tokens


def call_malformed_json_once(
    messages: list[dict], model: ModelName
) -> tuple[str, int, int, int]:
    """Demo-only path: force one malformed response so students can see retry."""

    *context, question = messages
    completion = get_client().chat.completions.create(
        model=model,
        messages=[
            *context,
            {
                "role": "user",
                "content": (
                    f"{question['content']}\n\n"
                    "Reply with ONLY JSON using keys answer, citations, refused, confidence. "
                    "Set confidence to the string 'very high' instead of a number."
                ),
            },
        ],
    )

    raw = completion.choices[0].message.content or ""
    total_tokens, prompt_tokens, completion_tokens = usage_counts(completion)
    return raw, total_tokens, prompt_tokens, completion_tokens


@app.get("/documents")
def documents() -> dict:
    return {"documents": rag.list_documents()}


@app.post("/ingest")
def ingest(body: IngestRequest) -> IngestResponse:
    if body.chunk_overlap >= body.chunk_size:
        raise HTTPException(
            status_code=422, detail="chunk_overlap must be smaller than chunk_size"
        )

    start = time.perf_counter()
    chunk_ids, tokens = rag.ingest_document(
        get_client(),
        body.document_id,
        body.text,
        body.chunk_size,
        body.chunk_overlap,
        body.metadata,
    )
    return IngestResponse(
        document_id=body.document_id,
        chunks_upserted=len(chunk_ids),
        chunk_ids=chunk_ids,
        chunk_size=body.chunk_size,
        chunk_overlap=body.chunk_overlap,
        embedding_model=rag.EMBEDDING_MODEL,
        embedding_tokens=tokens,
        latency_ms=int((time.perf_counter() - start) * 1000),
        cost_usd=round(embedding_cost_usd(tokens), 6),
    )


@app.post("/retrieve")
def retrieve(body: RetrieveRequest) -> RetrieveResponse:
    start = time.perf_counter()
    chunks, _ = rag.retrieve(get_client(), body.question, body.top_k, body.document_id)
    return RetrieveResponse(
        question=body.question,
        top_k=body.top_k,
        chunks=[RetrievedChunk(**c) for c in chunks],
        latency_ms=int((time.perf_counter() - start) * 1000),
    )


@app.post("/ask")
def ask(body: AskRequest) -> AskResponse:
    model = body.model or DEFAULT_MODEL
    last_error: str | None = None
    attempts: list[AttemptResult] = []
    start = time.perf_counter()

    # 1. Retrieve
    raw_chunks, embedding_tokens = rag.retrieve(
        get_client(), body.question, body.top_k, body.document_id
    )
    chunks = [RetrievedChunk(**c) for c in raw_chunks]
    total_tokens_used = embedding_tokens
    total_prompt_tokens = 0
    total_completion_tokens = 0

    # 2. Refuse early when nothing relevant was found: no context, no LLM call.
    best_score = max((c.score for c in chunks), default=0.0)
    if best_score < MIN_RELEVANCE_SCORE:
        attempts.append(
            AttemptResult(
                attempt=0,
                step="retrieval_gate",
                ok=True,
                message=(
                    f"Best chunk score {best_score:.3f} < {MIN_RELEVANCE_SCORE}: "
                    "refused without calling the LLM."
                ),
            )
        )
        return AskResponse(
            answer=Answer(answer=REFUSAL_TEXT, citations=[], refused=True, confidence=1.0),
            retrieved_chunks=chunks,
            tokens_used=total_tokens_used,
            model=model,
            latency_ms=int((time.perf_counter() - start) * 1000),
            cost_usd=round(embedding_cost_usd(embedding_tokens), 6),
            attempts=attempts,
        )

    # 3. Ground + generate, with the Week 1 validate-and-retry loop.
    messages = grounded_messages(body.question, chunks)
    for attempt in range(2):
        try:
            if body.force_bad and attempt == 0:
                raw, tokens_used, prompt_tokens, completion_tokens = call_malformed_json_once(
                    messages, model
                )
                total_tokens_used += tokens_used
                total_prompt_tokens += prompt_tokens
                total_completion_tokens += completion_tokens

                try:
                    answer = check_citations(Answer.model_validate_json(raw), chunks)
                except (ValidationError, ValueError) as exc:
                    last_error = str(exc)
                    attempts.append(
                        AttemptResult(
                            attempt=attempt + 1,
                            step="forced_bad_json",
                            ok=False,
                            message="Validation failed, so the endpoint retries with structured output.",
                            raw_output=raw,
                            validation_error=str(exc),
                        )
                    )
                    continue

                attempts.append(
                    AttemptResult(
                        attempt=attempt + 1,
                        step="forced_bad_json",
                        ok=True,
                        message="Unexpectedly passed validation.",
                        raw_output=raw,
                    )
                )
            else:
                answer, tokens_used, prompt_tokens, completion_tokens = call_structured_model(
                    messages, model
                )
                total_tokens_used += tokens_used
                total_prompt_tokens += prompt_tokens
                total_completion_tokens += completion_tokens
                answer = check_citations(answer, chunks)
                attempts.append(
                    AttemptResult(
                        attempt=attempt + 1,
                        step="structured_output",
                        ok=True,
                        message=(
                            "Model refused: the retrieved context does not contain the answer."
                            if answer.refused
                            else f"Grounded answer citing {', '.join(answer.citations)}."
                        ),
                    )
                )

            latency_ms = int((time.perf_counter() - start) * 1000)
            cost_usd = compute_cost_usd(
                model, total_prompt_tokens, total_completion_tokens
            ) + embedding_cost_usd(embedding_tokens)
            return AskResponse(
                answer=answer,
                retrieved_chunks=chunks,
                tokens_used=total_tokens_used,
                model=model,
                latency_ms=latency_ms,
                cost_usd=round(cost_usd, 6),
                attempts=attempts,
            )
        except (ValidationError, ValueError) as exc:
            last_error = str(exc)
            attempts.append(
                AttemptResult(
                    attempt=attempt + 1,
                    step="structured_output",
                    ok=False,
                    message="Structured output or citation check failed.",
                    validation_error=str(exc),
                )
            )

    raise HTTPException(
        status_code=502,
        detail=f"Model response failed validation after retry: {last_error}",
    )
