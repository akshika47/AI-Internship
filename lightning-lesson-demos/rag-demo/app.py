"""Lightning lesson demo: tiny end-to-end RAG (retrieve + answer).

Run:  uvicorn app:app --reload --port 8766
Open: http://127.0.0.1:8766
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import numpy as np
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel, Field

from corpus import CORPUS, SAMPLE_QUESTIONS, Chunk

load_dotenv(Path(__file__).resolve().parent / ".env")

app = FastAPI(title="RAG Demo — Lightning Lesson")
STATIC = Path(__file__).resolve().parent / "static"

EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
CHAT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TOP_K = 3

# Populated on startup: list of Chunk + (n, d) float32 matrix.
_chunks: list[Chunk] = []
_matrix: np.ndarray | None = None
_ready = False


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)


class RetrievedChunk(BaseModel):
    id: str
    title: str
    text: str
    score: float


class AskResponse(BaseModel):
    question: str
    chunks: list[RetrievedChunk]
    answer: str
    model: str
    embed_model: str


def _client() -> OpenAI:
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY missing. Symlink or copy a .env into this folder.",
        )
    return OpenAI()


def _embed(client: OpenAI, texts: list[str]) -> np.ndarray:
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    vectors = [item.embedding for item in sorted(resp.data, key=lambda x: x.index)]
    arr = np.asarray(vectors, dtype=np.float32)
    # Cosine via dot product on L2-normalized rows.
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms = np.clip(norms, 1e-12, None)
    return arr / norms


def _build_index() -> None:
    global _chunks, _matrix, _ready
    client = _client()
    _chunks = list(CORPUS)
    texts = [f"{c.title}. {c.text}" for c in _chunks]
    _matrix = _embed(client, texts)
    _ready = True


def _retrieve(client: OpenAI, question: str, k: int = TOP_K) -> list[RetrievedChunk]:
    if _matrix is None or not _chunks:
        raise HTTPException(status_code=503, detail="Index not ready. Restart the server.")
    q = _embed(client, [question])[0]
    scores = _matrix @ q
    top_idx = np.argsort(scores)[::-1][:k]
    results: list[RetrievedChunk] = []
    for i in top_idx:
        chunk = _chunks[int(i)]
        results.append(
            RetrievedChunk(
                id=chunk.id,
                title=chunk.title,
                text=chunk.text,
                score=float(scores[int(i)]),
            )
        )
    return results


def _answer(client: OpenAI, question: str, chunks: list[RetrievedChunk]) -> tuple[str, str]:
    context = "\n\n".join(
        f"[{i + 1}] {c.title}\n{c.text}" for i, c in enumerate(chunks)
    )
    messages = [
        {
            "role": "system",
            "content": (
                "You answer using only the retrieved context below. "
                "If the context does not contain the answer, say you do not know. "
                "Be concise (2–4 sentences). Mention which context numbers you used."
            ),
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}",
        },
    ]
    completion = client.chat.completions.create(
        model=CHAT_MODEL,
        temperature=0.2,
        max_tokens=220,
        messages=messages,
    )
    text = (completion.choices[0].message.content or "").strip()
    return text, completion.model


@app.on_event("startup")
def startup() -> None:
    try:
        _build_index()
        print(f"Indexed {len(_chunks)} chunks with {EMBED_MODEL}", flush=True)
    except Exception as exc:  # noqa: BLE001 — surface clearly in logs for live demo
        print(f"WARNING: index build failed: {exc}", flush=True)
        print("Fix OPENAI_API_KEY / network, then restart.", flush=True)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/api/demo")
def demo_payload() -> dict[str, Any]:
    return {
        "ready": _ready,
        "chunk_count": len(_chunks),
        "chunks": [{"id": c.id, "title": c.title, "text": c.text} for c in _chunks or CORPUS],
        "sample_questions": SAMPLE_QUESTIONS,
        "embed_model": EMBED_MODEL,
        "chat_model": CHAT_MODEL,
        "top_k": TOP_K,
    }


@app.post("/api/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    if not _ready:
        # Retry once in case startup failed before the key was available.
        try:
            _build_index()
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Index not ready: {exc}",
            ) from exc

    question = req.question.strip()
    client = _client()
    try:
        chunks = _retrieve(client, question)
        answer, model = _answer(client, question, chunks)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return AskResponse(
        question=question,
        chunks=chunks,
        answer=answer,
        model=model,
        embed_model=EMBED_MODEL,
    )


app.mount("/static", StaticFiles(directory=STATIC), name="static")
