"""Settings for Filings Copilot, read from the environment (.env is loaded if present)."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    model_name: str = os.getenv("MODEL_NAME", "gpt-4o-mini")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    vector_store_url: str = os.getenv("VECTOR_STORE_URL", "")
    reranker_api_key: str = os.getenv("RERANKER_API_KEY", "")
    max_tokens: int = int(os.getenv("MAX_TOKENS", "800"))


settings = Settings()
