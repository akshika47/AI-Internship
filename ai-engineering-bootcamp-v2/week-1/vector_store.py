"""Pinecone vector store for the Week 1 FastAPI app.

Ingest and query both call embed_texts(), so they always use the same model.
Secrets come from the environment, never from this file.

Required:
  PINECONE_API_KEY
  PINECONE_INDEX
Optional:
  PINECONE_HOST  index host from the Pinecone console; recommended on Render
"""

import os
from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI
from pinecone import Pinecone

# One name and one width for both ingest and query.
# text-embedding-3-small returns 1536-number vectors.
EMBED_MODEL = "text-embedding-3-small"
EMBED_DIMENSIONS = 1536

_client: Pinecone | None = None
_index: Any = None


def chunk_settings() -> tuple[int, int]:
    """Chunk size and overlap. Override with CHUNK_SIZE and CHUNK_OVERLAP."""

    try:
        size = int(os.getenv("CHUNK_SIZE", "800").strip() or "800")
        overlap = int(os.getenv("CHUNK_OVERLAP", "100").strip() or "100")
    except ValueError as exc:
        raise RuntimeError("CHUNK_SIZE and CHUNK_OVERLAP must be integers") from exc
    if size <= 0:
        raise RuntimeError("CHUNK_SIZE must be a positive integer")
    if overlap < 0 or overlap >= size:
        raise RuntimeError("CHUNK_OVERLAP must be zero or more and smaller than CHUNK_SIZE")
    return size, overlap


def chunk_text(text: str) -> list[str]:
    """Split text with RecursiveCharacterTextSplitter using the configured size and overlap."""

    size, overlap = chunk_settings()
    splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=overlap)
    return [part.strip() for part in splitter.split_text(text) if part.strip()]


def require_env(name: str) -> str:
    """Return a required setting, or raise if it is missing or blank."""

    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


def get_client() -> Pinecone:
    """Reuse one control-plane client. The key is read when this is first called."""

    global _client
    if _client is None:
        _client = Pinecone(api_key=require_env("PINECONE_API_KEY"))
    return _client


def get_index() -> Any:
    """Reuse one data-plane client for the configured index."""

    global _index
    if _index is None:
        host = os.getenv("PINECONE_HOST", "").strip()
        if host:
            _index = get_client().index(host=host)
        else:
            _index = get_client().index(name=require_env("PINECONE_INDEX"))
    return _index


def embed_texts(client: OpenAI, texts: list[str]) -> tuple[list[list[float]], int]:
    """Embed texts with text-embedding-3-small. Call this for both ingest and query."""

    if not texts:
        return [], 0

    vectors: list[list[float]] = []
    embed_tokens = 0
    # Keep each request under the embeddings input limit.
    batch_size = 64
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        response = client.embeddings.create(
            model=EMBED_MODEL,
            input=batch,
            dimensions=EMBED_DIMENSIONS,
        )
        ordered = sorted(response.data, key=lambda item: item.index)
        vectors.extend(item.embedding for item in ordered)
        embed_tokens += response.usage.total_tokens if response.usage else 0
    return vectors, embed_tokens


def upsert_texts(
    client: OpenAI,
    items: list[dict[str, Any]],
    namespace: str = "",
) -> int:
    """Embed and store items. Each item needs id and text, and may include metadata."""

    if not items:
        return 0

    vectors, _embed_tokens = embed_texts(client, [str(item["text"]) for item in items])
    payload: list[dict[str, Any]] = []
    for item, values in zip(items, vectors):
        metadata = dict(item.get("metadata") or {})
        metadata["text"] = str(item["text"])
        payload.append({"id": str(item["id"]), "values": values, "metadata": metadata})

    get_index().upsert(vectors=payload, namespace=namespace, batch_size=100, show_progress=False)
    return len(payload)


# text-embedding-3-small: $0.02 per 1M tokens.
EMBED_PRICE_PER_1K = 0.00002


def retrieve(
    client: OpenAI,
    text: str,
    top_k: int = 5,
    namespace: str = "",
) -> tuple[list[dict[str, Any]], int]:
    """Embed a query and return the nearest chunks plus the embedding token count."""

    vectors, embed_tokens = embed_texts(client, [text])
    result = get_index().query(
        vector=vectors[0],
        top_k=top_k,
        namespace=namespace,
        include_metadata=True,
    )

    matches: list[dict[str, Any]] = []
    for match in result.matches or []:
        metadata = dict(match.metadata or {})
        matches.append(
            {
                "id": match.id,
                "score": match.score,
                "text": metadata.get("text", ""),
                "metadata": metadata,
            }
        )
    return matches, embed_tokens


def query_similar(
    client: OpenAI,
    text: str,
    top_k: int = 5,
    namespace: str = "",
) -> list[dict[str, Any]]:
    """Embed a query with the same model used at ingest, then return nearest matches."""

    matches, _embed_tokens = retrieve(client, text, top_k=top_k, namespace=namespace)
    return matches


def ingest_document(
    client: OpenAI,
    document_id: str,
    text: str,
    source: str = "",
    metadata: dict[str, Any] | None = None,
) -> int:
    """Chunk, embed with text-embedding-3-small, and upsert one document."""

    chunks = chunk_text(text)
    if not chunks:
        raise ValueError("text produced no chunks")

    items: list[dict[str, Any]] = []
    for chunk_index, chunk in enumerate(chunks):
        record_metadata: dict[str, Any] = {}
        for key, value in (metadata or {}).items():
            if isinstance(value, (str, int, float, bool)):
                record_metadata[str(key)] = value
            elif isinstance(value, list) and all(isinstance(item, str) for item in value):
                record_metadata[str(key)] = value
        record_metadata["document_id"] = document_id
        record_metadata["chunk_index"] = chunk_index
        record_metadata["source"] = source
        items.append(
            {
                "id": f"{document_id}:{chunk_index}",
                "text": chunk,
                "metadata": record_metadata,
            }
        )
    return upsert_texts(client, items)


def _index_dimension(description: Any) -> int | None:
    try:
        dimension = description.dimension
    except AttributeError:
        return None
    return int(dimension) if dimension is not None else None


def _index_metric(description: Any) -> str | None:
    try:
        metric = description.metric
    except AttributeError:
        return None
    return str(metric) if metric else None


def check_pinecone() -> dict[str, Any]:
    """Call Pinecone and report whether the configured index is reachable.

    This does not spend OpenAI tokens. It describes the index, then reads stats.
    """

    index_name = require_env("PINECONE_INDEX")
    description = get_client().describe_index(index_name)
    stats = get_index().describe_index_stats()

    status = description.status
    dimension = _index_dimension(description)
    expected = EMBED_DIMENSIONS
    ready = bool(getattr(status, "ready", False))
    dimension_ok = dimension == expected

    return {
        "ok": ready and dimension_ok,
        "reachable": True,
        "index": index_name,
        "host": description.host,
        "ready": ready,
        "state": getattr(status, "state", None),
        "metric": _index_metric(description),
        "dimension": dimension,
        "expected_dimension": expected,
        "dimension_ok": dimension_ok,
        "embed_model": EMBED_MODEL,
        "vector_count": int(stats.total_vector_count or 0),
    }
