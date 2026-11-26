"""Filings Copilot at Northgate Capital: the Monday scaffold.

GET /health works today. POST /ingest and POST /ask return 501 until the
guided build fills them in.
"""

from fastapi import FastAPI, HTTPException

from src.config import settings
from src.schemas import AskRequest, IngestRequest

app = FastAPI(title="Filings Copilot")


@app.get("/health")
def health() -> dict:
    # Never call a model or the vector store here: health must stay fast.
    return {"ok": True}


@app.post("/ingest")
def ingest(req: IngestRequest) -> dict:
    # Guided build: read req.source_path, split on Item / section headings,
    # keep the printed page, embed, and upsert chunks with filing_id,
    # company_ticker, form_type, fiscal_period, section_id, page, tenant_id,
    # as_of, superseded_by. Index the same chunks for BM25.
    raise HTTPException(status_code=501, detail="Implemented in guided build")


@app.post("/ask")
def ask(req: AskRequest) -> dict:
    # Guided build: filter on req.tenant_id first, retrieve BM25 + dense,
    # fuse with RRF, rerank, then draft an Answer with citations or return
    # an evidence state (missing, conflicting, stale).
    _ = settings.model_name
    raise HTTPException(status_code=501, detail="Implemented in guided build")
