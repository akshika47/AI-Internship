"""The contracts Filings Copilot returns. You fill these in during the guided build."""

from typing import Literal

from pydantic import BaseModel


class IngestRequest(BaseModel):
    filing_id: str
    tenant_id: str
    source_path: str  # e.g. data/filings/netbay-10q-q3-2026.md


class AskRequest(BaseModel):
    query: str
    tenant_id: str


class Citation(BaseModel):
    filing_id: str
    page: int


class Answer(BaseModel):
    evidence: Literal["enough", "missing", "conflicting", "stale"]
    citations: list[Citation]  # must be a subset of what was retrieved
    customer_message: str
    retrieved_chunk_ids: list[str]
