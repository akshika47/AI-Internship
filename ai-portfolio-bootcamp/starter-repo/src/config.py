"""Configuration, loaded from the environment.

Every knob lives here so that no other module reads os.environ directly.
When you add a setting, add it to .env.example in the same commit.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    api_key: str | None
    model: str
    log_level: str
    review_threshold: float

    @property
    def offline(self) -> bool:
        """True when no API key is available.

        The harness still runs end to end in this mode using a deterministic
        stub, so you can verify your install before your billing is sorted.
        Never submit results produced offline.
        """
        return not self.api_key


def load_config() -> Config:
    raw_threshold = os.getenv("REVIEW_THRESHOLD", "0.75")
    try:
        threshold = float(raw_threshold)
    except ValueError as exc:
        raise ValueError(
            f"REVIEW_THRESHOLD must be a number between 0 and 1, got {raw_threshold!r}"
        ) from exc
    if not 0.0 <= threshold <= 1.0:
        raise ValueError(f"REVIEW_THRESHOLD must be between 0 and 1, got {threshold}")

    return Config(
        api_key=os.getenv("ANTHROPIC_API_KEY") or None,
        model=os.getenv("MODEL", "claude-opus-5"),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        review_threshold=threshold,
    )
