"""Week 2 RAG layer: chunk -> embed -> upsert, and question -> top-k chunks.

Sits in front of the Week 1 `/ask` handler in main.py. Uses the same building blocks as
the week-2 notebook: RecursiveCharacterTextSplitter, OpenAI text-embedding-3-small, Chroma.

Storage:
  - Default: a local persistent Chroma folder (CHROMA_DIR, default ./chroma_db).
  - If CHROMA_API_KEY is set: Chroma Cloud (CHROMA_TENANT, CHROMA_DATABASE), so data
    survives Render free-tier restarts, which wipe the local disk.
"""

import os
from pathlib import Path

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI

THIS_DIR = Path(__file__).resolve().parent

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_PRICE_PER_1K = 0.00002
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "week2_docs")
DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 120  # ~15%, inside the notebook's 10-20% guidance

_collection = None


def get_collection():
    global _collection
    if _collection is None:
        if os.getenv("CHROMA_API_KEY"):
            client = chromadb.CloudClient(
                api_key=os.environ["CHROMA_API_KEY"],
                tenant=os.getenv("CHROMA_TENANT"),
                database=os.getenv("CHROMA_DATABASE"),
            )
        else:
            client = chromadb.PersistentClient(
                path=os.getenv("CHROMA_DIR", str(THIS_DIR / "chroma_db"))
            )
        # We always pass our own OpenAI embeddings, so Chroma never embeds anything itself.
        _collection = client.get_or_create_collection(
            COLLECTION_NAME,
            configuration={"hnsw": {"space": "cosine"}},
            embedding_function=None,
        )
    return _collection


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_text(text)


def embed(client: OpenAI, texts: list[str]) -> tuple[list[list[float]], int]:
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    vectors = [item.embedding for item in sorted(response.data, key=lambda d: d.index)]
    return vectors, response.usage.total_tokens


def chunk_id(document_id: str, index: int) -> str:
    return f"{document_id}::chunk-{index:03d}"


def ingest_document(
    client: OpenAI,
    document_id: str,
    text: str,
    chunk_size: int,
    chunk_overlap: int,
    metadata: dict[str, str | int | float | bool],
) -> tuple[list[str], int]:
    """Replace any earlier version of the document, then upsert its chunks."""

    chunks = chunk_text(text, chunk_size, chunk_overlap)
    vectors, tokens = embed(client, chunks)

    collection = get_collection()
    # Re-ingesting a shorter version must not leave stale chunks from the old one behind.
    collection.delete(where={"document_id": document_id})

    ids = [chunk_id(document_id, i) for i in range(len(chunks))]
    collection.upsert(
        ids=ids,
        embeddings=vectors,
        documents=chunks,
        metadatas=[
            {
                **metadata,
                "document_id": document_id,
                "chunk_index": i,
                "chunk_count": len(chunks),
            }
            for i in range(len(chunks))
        ],
    )
    return ids, tokens


def retrieve(
    client: OpenAI, question: str, top_k: int, document_id: str | None = None
) -> tuple[list[dict], int]:
    """Return the top-k chunks for the question, best first, with cosine similarity scores."""

    collection = get_collection()
    if collection.count() == 0:
        return [], 0

    [query_vector], tokens = embed(client, [question])
    result = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        where={"document_id": document_id} if document_id else None,
        include=["documents", "metadatas", "distances"],
    )
    chunks = [
        {
            "chunk_id": cid,
            "document_id": meta.get("document_id"),
            "score": round(1 - distance, 4),
            "text": text,
            "metadata": meta,
        }
        for cid, text, meta, distance in zip(
            result["ids"][0],
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        )
    ]
    return chunks, tokens


def list_documents() -> list[dict]:
    metadatas = get_collection().get(include=["metadatas"])["metadatas"] or []
    counts: dict[str, int] = {}
    for meta in metadatas:
        counts[meta["document_id"]] = counts.get(meta["document_id"], 0) + 1
    return [{"document_id": doc, "chunks": n} for doc, n in sorted(counts.items())]
