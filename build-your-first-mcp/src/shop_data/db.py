"""SQLite connections. Read tools get a read-only connection; only save_note gets a writable one."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def read_only(db_path: Path) -> sqlite3.Connection:
    """Open the database READ-ONLY: 'mode=ro' makes SQLite itself refuse any write."""
    db = sqlite3.connect(f"{db_path.as_uri()}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    return db


def writable(db_path: Path) -> sqlite3.Connection:
    """The only read-write connection. Only save_note uses it."""
    return sqlite3.connect(f"{db_path.as_uri()}?mode=rw", uri=True)
