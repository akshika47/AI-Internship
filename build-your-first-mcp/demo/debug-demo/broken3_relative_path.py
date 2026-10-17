"""Northwind Home - BROKEN 3 (relative db path): one tool, sales by month."""

import logging
import sqlite3
import sys
from pathlib import Path

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

# Logs go to stderr. Never print(): stdout is the channel Claude reads.
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger("shop")

# Absolute path: Claude Desktop does not start the server in our folder.
# This file lives next to shop.db, so copy it to server.py in shop-data/.
# The 'file:...?mode=ro' form opens the database READ-ONLY.
DB_PATH = Path("shop.db")  # BUG: relative path

mcp = FastMCP("shop-data")


def read_db() -> sqlite3.Connection:
    db = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    return db


def check_category(db: sqlite3.Connection, category: str) -> str:
    names = [r["name"] for r in db.execute("SELECT name FROM categories ORDER BY category_id")]
    match = next((n for n in names if n.lower() == category.strip().lower()), None)
    if match is None:
        raise ToolError(f"Unknown category '{category}'. Use one of: {', '.join(names)}.")
    return match


@mcp.tool(annotations={"readOnlyHint": True})
def sales_by_month(category: str | None = None, months: int = 6) -> list[dict]:
    """Revenue and order count for each of the most recent months, newest last. Cancelled orders are left out.

    category: Kitchen, Bedding, Lighting, Decor or Bath. Leave empty for all. Example: "Lighting".
    months: how many months to show, from 1 to 15. Example: 6.
    """
    if not 1 <= months <= 15:
        raise ToolError("months must be a whole number from 1 to 15 (the data covers 15 months).")
    with read_db() as db:
        if category is not None:
            category = check_category(db, category)
        rows = db.execute(
            """
            SELECT substr(o.order_date, 1, 7) AS month,
                   ROUND(SUM(i.quantity * i.price), 2) AS revenue,
                   COUNT(DISTINCT o.order_id) AS orders
            FROM order_items i
            JOIN orders o ON o.order_id = i.order_id
            JOIN products p ON p.product_id = i.product_id
            JOIN categories c ON c.category_id = p.category_id
            WHERE o.status <> 'cancelled' AND (? IS NULL OR c.name = ?)
            GROUP BY month ORDER BY month DESC LIMIT ?
            """,
            (category, category, months),
        ).fetchall()
    log.info("sales_by_month category=%s months=%s -> %d rows", category, months, len(rows))
    return [dict(r) for r in reversed(rows)]


if __name__ == "__main__":
    mcp.run()
