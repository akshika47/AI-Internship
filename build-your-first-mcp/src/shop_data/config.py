"""Settings, read from environment variables. Every one has a safe default.

SHOP_DB_PATH   path to the SQLite file. Default: <repo>/data/shop.db
MCP_TRANSPORT  "stdio" (a desktop app starts the server) or "http". Default: stdio
HOST           address to listen on in http mode. Default: 127.0.0.1 (use 0.0.0.0 in a container)
PORT           port to listen on in http mode. Default: 8000
ALLOW_WRITES   "true" registers save_note; "false" makes the server read-only. Default: true
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

# src/shop_data/config.py -> parents[2] is the repo folder, which holds data/.
REPO_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = REPO_DIR / "data" / "shop.db"

TRANSPORTS = ("stdio", "http")
_TRUE = {"1", "true", "yes", "on"}
_FALSE = {"0", "false", "no", "off"}


class ConfigError(ValueError):
    """A setting has a value we cannot use. The message says which one and why."""


@dataclass(frozen=True)
class Settings:
    db_path: Path
    transport: str = "stdio"
    host: str = "127.0.0.1"
    port: int = 8000
    allow_writes: bool = True


def _bool(name: str, raw: str) -> bool:
    value = raw.strip().lower()
    if value in _TRUE:
        return True
    if value in _FALSE:
        return False
    raise ConfigError(f"{name} must be true or false, not {raw!r}.")


def load_settings(env: dict[str, str] | None = None) -> Settings:
    env = dict(os.environ if env is None else env)

    raw_db = env.get("SHOP_DB_PATH", "").strip()
    # Always absolute: a desktop app does not start the server in this folder.
    db_path = Path(raw_db).expanduser().resolve() if raw_db else DEFAULT_DB_PATH

    transport = env.get("MCP_TRANSPORT", "stdio").strip().lower() or "stdio"
    if transport not in TRANSPORTS:
        raise ConfigError(f"MCP_TRANSPORT must be one of {', '.join(TRANSPORTS)}, not {transport!r}.")

    raw_port = env.get("PORT", "8000").strip() or "8000"
    try:
        port = int(raw_port)
    except ValueError:
        raise ConfigError(f"PORT must be a whole number, not {raw_port!r}.") from None
    if not 1 <= port <= 65535:
        raise ConfigError(f"PORT must be from 1 to 65535, not {port}.")

    return Settings(
        db_path=db_path,
        transport=transport,
        host=env.get("HOST", "127.0.0.1").strip() or "127.0.0.1",
        port=port,
        allow_writes=_bool("ALLOW_WRITES", env.get("ALLOW_WRITES", "true")),
    )
