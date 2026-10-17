"""Hosted, read-only copy of the workshop server: no save_note. Northwind Home (a fictional store) - stage 3: a ready-made prompt, the weekly business review."""

import logging
import re
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
DB_PATH = Path(__file__).resolve().parent / "shop.db"

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


def quarter_range(quarter: str) -> tuple[str, str]:
    """'2026-Q3' -> ('2026-07-01', '2026-10-01'): start and the day after the end."""
    m = re.fullmatch(r"(\d{4})-Q([1-4])", quarter.strip().upper())
    if not m:
        raise ToolError(f"'{quarter}' is not a valid quarter. Use the form 2026-Q3 (year, dash, Q, 1 to 4).")
    year, q = int(m.group(1)), int(m.group(2))
    start = f"{year}-{3 * q - 2:02d}-01"
    end = f"{year + 1}-01-01" if q == 4 else f"{year}-{3 * q + 1:02d}-01"
    return start, end


def previous_quarter(quarter: str) -> str:
    year, q = int(quarter[:4]), int(quarter[-1])
    return f"{year - 1}-Q4" if q == 1 else f"{year}-Q{q - 1}"


def returns_by_category(db: sqlite3.Connection, quarter: str) -> dict[str, dict]:
    """Items sold, items returned and the most common reason, per category (cancelled orders ignored)."""
    start, end = quarter_range(quarter)
    rows = db.execute(
        """
        SELECT c.name AS category, COUNT(*) AS items, COUNT(r.return_id) AS returned
        FROM order_items i
        JOIN orders o ON o.order_id = i.order_id
        JOIN products p ON p.product_id = i.product_id
        JOIN categories c ON c.category_id = p.category_id
        LEFT JOIN returns r ON r.order_item_id = i.order_item_id
        WHERE o.status <> 'cancelled' AND o.order_date >= ? AND o.order_date < ?
        GROUP BY c.name
        """,
        (start, end),
    ).fetchall()
    out = {r["category"]: dict(r) for r in rows}
    reasons = db.execute(
        """
        SELECT c.name AS category, r.reason, COUNT(*) AS n
        FROM returns r
        JOIN order_items i ON i.order_item_id = r.order_item_id
        JOIN orders o ON o.order_id = i.order_id
        JOIN products p ON p.product_id = i.product_id
        JOIN categories c ON c.category_id = p.category_id
        WHERE o.status <> 'cancelled' AND o.order_date >= ? AND o.order_date < ?
        GROUP BY c.name, r.reason ORDER BY n DESC, r.reason
        """,
        (start, end),
    ).fetchall()
    for r in reasons:  # rows come biggest first, so the first one per category is the top reason
        out[r["category"]].setdefault("top_reason", r["reason"])
        out[r["category"]].setdefault("top_reason_count", r["n"])
    return out


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


@mcp.tool(annotations={"readOnlyHint": True})
def top_products(category: str, quarter: str) -> list[dict]:
    """The five products with most revenue in a category in one quarter, with how many were returned.

    category: Kitchen, Bedding, Lighting, Decor or Bath. Example: "Lighting".
    quarter: year, dash, Q and 1 to 4. Example: "2026-Q3".
    """
    start, end = quarter_range(quarter)
    with read_db() as db:
        category = check_category(db, category)
        rows = db.execute(
            """
            SELECT p.name AS product,
                   ROUND(SUM(i.quantity * i.price), 2) AS revenue,
                   SUM(i.quantity) AS units,
                   COUNT(r.return_id) AS returned_items,
                   ROUND(100.0 * COUNT(r.return_id) / COUNT(*), 1) AS return_rate_pct
            FROM order_items i
            JOIN orders o ON o.order_id = i.order_id
            JOIN products p ON p.product_id = i.product_id
            JOIN categories c ON c.category_id = p.category_id
            LEFT JOIN returns r ON r.order_item_id = i.order_item_id
            WHERE c.name = ? AND o.status <> 'cancelled' AND o.order_date >= ? AND o.order_date < ?
            GROUP BY p.product_id ORDER BY revenue DESC LIMIT 5
            """,
            (category, start, end),
        ).fetchall()
    if not rows:
        raise ToolError(f"No sales for {category} in {quarter}. The data covers 2025-Q3 to 2026-Q3.")
    log.info("top_products category=%s quarter=%s", category, quarter)
    return [dict(r) for r in rows]


@mcp.tool(annotations={"readOnlyHint": True})
def return_rates(quarter: str) -> list[dict]:
    """Each category's return rate against the quarter before it, biggest rise first.

    quarter: year, dash, Q and 1 to 4. Example: "2026-Q3". Needs the previous quarter in the data.
    Rate = items returned / items sold, by order date. Also shows the most common return reason.
    """
    quarter = quarter.strip().upper()
    quarter_range(quarter)  # checks the format
    before = previous_quarter(quarter)
    with read_db() as db:
        now, prev = returns_by_category(db, quarter), returns_by_category(db, before)
    if not now:
        raise ToolError(f"No orders in {quarter}. The data covers 2025-Q3 to 2026-Q3.")
    if not prev:
        raise ToolError(f"There is no data for the previous quarter ({before}), so nothing to compare with. Try 2025-Q4 or later.")
    result = []
    for category, n in now.items():
        p = prev.get(category)
        rate = round(100 * n["returned"] / n["items"], 1)
        prev_rate = round(100 * p["returned"] / p["items"], 1) if p else None
        result.append({
            "category": category,
            "previous_quarter": before,
            "previous_rate_pct": prev_rate,
            "rate_pct": rate,
            "change_pts": round(rate - prev_rate, 1) if prev_rate is not None else None,
            "items_sold": n["items"],
            "items_returned": n["returned"],
            "top_reason": n.get("top_reason"),
            "top_reason_share_pct": round(100 * n["top_reason_count"] / n["returned"], 1) if n["returned"] else None,
        })
    log.info("return_rates quarter=%s", quarter)
    return sorted(result, key=lambda r: -(r["change_pts"] if r["change_pts"] is not None else 0))


@mcp.prompt
def weekly_business_review(quarter: str) -> str:
    """Weekly business review: find the return spike, trace it to a product, save a 5-line note.

    quarter: year, dash, Q and 1 to 4. Example: "2026-Q3".
    """
    return f"""Run the weekly business review for Northwind Home (a fictional homeware store) for {quarter}.

1. Call sales_by_month for the last 6 months to see whether revenue is growing overall.
2. Call return_rates for {quarter} and identify the categories whose return rate rose the most.
3. For each category with a big rise, call top_products for that category in {quarter} and in the quarter before it. Find the product behind the rise and explain it in plain English: its return rate, its share of the category's returns, and the most common reason.
4. Draft a note of exactly 5 lines: the headline number, the category, the product, the reason, and one suggested next step.
5. Show me the draft. (This hosted copy is read-only, so it cannot save notes.)
Use only numbers returned by the tools. If a tool returns an error, tell me what it said instead of guessing."""


if __name__ == "__main__":
    # Hosted copy: read-only tools over Streamable HTTP. Render sets PORT.
    import os
    mcp.run(transport="http", host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
