"""Tests for the shop-data server, through FastMCP's in-memory Client (no subprocess, no network).

Every test runs against a temporary copy of data/shop.db, so save_note never touches the real file.
Expected numbers are the workshop's story: in 2026-Q3 Lighting returns jump to 28.9% (92 of 318
items), and the Aurora Glass Pendant accounts for 77 of those 92 returns.
"""

from __future__ import annotations

import shutil
import sqlite3
from pathlib import Path

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from shop_data.config import DEFAULT_DB_PATH, ConfigError, Settings, load_settings
from shop_data.server import create_server

ALL_TOOLS = {"sales_by_month", "top_products", "return_rates", "save_note"}
READ_TOOLS = ALL_TOOLS - {"save_note"}


@pytest.fixture
def db_copy(tmp_path: Path) -> Path:
    target = tmp_path / "shop.db"
    shutil.copyfile(DEFAULT_DB_PATH, target)
    return target


@pytest.fixture
def server(db_copy: Path):
    return create_server(Settings(db_path=db_copy, allow_writes=True))


@pytest.fixture
def read_only_server(db_copy: Path):
    return create_server(Settings(db_path=db_copy, allow_writes=False))


async def call(server, name: str, args: dict | None = None):
    async with Client(server) as client:
        return (await client.call_tool(name, args or {})).data


async def call_error(server, name: str, args: dict) -> str:
    async with Client(server) as client:
        with pytest.raises(ToolError) as exc:
            await client.call_tool(name, args)
    return str(exc.value)


# ---------- listing ----------


async def test_lists_four_tools_and_one_prompt(server):
    async with Client(server) as client:
        tools = {t.name: t for t in await client.list_tools()}
        prompts = [p.name for p in await client.list_prompts()]
    assert set(tools) == ALL_TOOLS
    assert prompts == ["weekly_business_review"]
    for name in READ_TOOLS:
        assert tools[name].annotations.read_only_hint is True
    assert tools["save_note"].annotations.read_only_hint is False
    assert tools["save_note"].description.startswith("WRITES to the database")


async def test_save_note_absent_when_writes_off(read_only_server):
    async with Client(read_only_server) as client:
        names = {t.name for t in await client.list_tools()}
        assert names == READ_TOOLS
        with pytest.raises(ToolError):
            await client.call_tool("save_note", {"title": "x", "text": "y"})


# ---------- sales_by_month ----------


async def test_sales_by_month_all_categories(server):
    rows = await call(server, "sales_by_month")
    assert [r["month"] for r in rows] == ["2026-04", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09"]
    assert rows[0] == {"month": "2026-04", "revenue": 23396.0, "orders": 242}
    assert rows[-1] == {"month": "2026-09", "revenue": 23810.0, "orders": 250}


async def test_sales_by_month_category_is_case_insensitive(server):
    rows = await call(server, "sales_by_month", {"category": "lighting", "months": 3})
    assert rows == [
        {"month": "2026-07", "revenue": 8351.0, "orders": 88},
        {"month": "2026-08", "revenue": 9771.0, "orders": 96},
        {"month": "2026-09", "revenue": 10444.0, "orders": 104},
    ]


async def test_sales_by_month_unknown_category(server):
    msg = await call_error(server, "sales_by_month", {"category": "Toys"})
    assert msg == "Unknown category 'Toys'. Use one of: Kitchen, Bedding, Lighting, Decor, Bath."


@pytest.mark.parametrize("months", [0, 16])
async def test_sales_by_month_months_out_of_range(server, months):
    msg = await call_error(server, "sales_by_month", {"months": months})
    assert msg == "months must be a whole number from 1 to 15 (the data covers 15 months)."


# ---------- top_products ----------


async def test_top_products_shows_the_pendant(server):
    rows = await call(server, "top_products", {"category": "Lighting", "quarter": "2026-Q3"})
    assert len(rows) == 5
    assert rows[0] == {
        "product": "Aurora Glass Pendant",
        "revenue": 14190.0,
        "units": 110,
        "returned_items": 77,
        "return_rate_pct": 80.2,
    }


async def test_top_products_quarter_before_was_normal(server):
    rows = await call(server, "top_products", {"category": "Lighting", "quarter": "2026-Q2"})
    assert rows[0]["product"] == "Aurora Glass Pendant"
    assert rows[0]["returned_items"] == 4
    assert rows[0]["return_rate_pct"] == 4.5


async def test_top_products_unknown_category(server):
    msg = await call_error(server, "top_products", {"category": "Toys", "quarter": "2026-Q3"})
    assert msg.startswith("Unknown category 'Toys'.")


async def test_top_products_bad_quarter(server):
    msg = await call_error(server, "top_products", {"category": "Lighting", "quarter": "2026-3"})
    assert msg == "'2026-3' is not a valid quarter. Use the form 2026-Q3 (year, dash, Q, 1 to 4)."


async def test_top_products_no_sales(server):
    msg = await call_error(server, "top_products", {"category": "Lighting", "quarter": "2027-Q1"})
    assert msg == "No sales for Lighting in 2027-Q1. The data covers 2025-Q3 to 2026-Q3."


# ---------- return_rates: the story ----------


async def test_return_rates_lighting_story(server):
    rows = await call(server, "return_rates", {"quarter": "2026-Q3"})
    lighting = rows[0]
    assert lighting == {
        "category": "Lighting",
        "previous_quarter": "2026-Q2",
        "previous_rate_pct": 5.2,
        "rate_pct": 28.9,
        "change_pts": 23.7,
        "items_sold": 318,
        "items_returned": 92,
        "top_reason": "damaged",
        "top_reason_share_pct": 85.9,
    }
    assert len(rows) == 5
    changes = [r["change_pts"] for r in rows]
    assert changes == sorted(changes, reverse=True)


async def test_pendant_is_77_of_the_92_lighting_returns(server):
    rates = await call(server, "return_rates", {"quarter": "2026-Q3"})
    products = await call(server, "top_products", {"category": "Lighting", "quarter": "2026-Q3"})
    assert products[0]["returned_items"] == 77
    assert rates[0]["items_returned"] == 92


async def test_return_rates_accepts_lower_case(server):
    rows = await call(server, "return_rates", {"quarter": " 2026-q3 "})
    assert rows[0]["rate_pct"] == 28.9


@pytest.mark.parametrize("quarter", ["2026-Q9", "Q3-2026"])
async def test_return_rates_bad_quarter(server, quarter):
    msg = await call_error(server, "return_rates", {"quarter": quarter})
    assert msg == f"'{quarter}' is not a valid quarter. Use the form 2026-Q3 (year, dash, Q, 1 to 4)."


async def test_return_rates_no_previous_quarter(server):
    msg = await call_error(server, "return_rates", {"quarter": "2025-Q3"})
    assert msg.startswith("There is no data for the previous quarter (2025-Q2)")


async def test_return_rates_no_orders(server):
    msg = await call_error(server, "return_rates", {"quarter": "2027-Q1"})
    assert msg == "No orders in 2027-Q1. The data covers 2025-Q3 to 2026-Q3."


# ---------- save_note ----------


async def test_save_note_writes_a_row(server, db_copy):
    msg = await call(server, "save_note", {"title": "Test note", "text": "Written by pytest"})
    assert msg.startswith("Saved note #")
    with sqlite3.connect(db_copy) as db:
        assert db.execute("SELECT title, text FROM notes").fetchall() == [("Test note", "Written by pytest")]


async def test_save_note_refuses_empty_title(server):
    msg = await call_error(server, "save_note", {"title": "   ", "text": "no title"})
    assert msg == "Both a title and some text are needed to save a note."


async def test_save_note_refuses_long_text(server):
    msg = await call_error(server, "save_note", {"title": "t", "text": "x" * 2001})
    assert msg.startswith("That note is too long")


async def test_read_tools_cannot_write(db_copy):
    from shop_data.db import read_only

    with read_only(db_copy) as db, pytest.raises(sqlite3.OperationalError):
        db.execute("INSERT INTO notes (title, text) VALUES ('x', 'y')")


# ---------- the prompt ----------


async def test_weekly_business_review_prompt(server):
    async with Client(server) as client:
        result = await client.get_prompt("weekly_business_review", {"quarter": "2026-Q3"})
    text = result.messages[0].content.text
    assert text.startswith("Run the weekly business review for Northwind Home (a fictional homeware store) for 2026-Q3.")
    for tool in ("sales_by_month", "return_rates", "top_products", "save_note"):
        assert tool in text
    assert "exactly 5 lines" in text


async def test_prompt_does_not_promise_saving_when_read_only(read_only_server):
    async with Client(read_only_server) as client:
        result = await client.get_prompt("weekly_business_review", {"quarter": "2026-Q3"})
    text = result.messages[0].content.text
    assert "save_note" not in text
    assert "read-only" in text


# ---------- config ----------


def test_config_defaults():
    s = load_settings({})
    assert s.db_path == DEFAULT_DB_PATH and s.db_path.is_absolute()
    assert (s.transport, s.host, s.port, s.allow_writes) == ("stdio", "127.0.0.1", 8000, True)


def test_config_from_env(tmp_path):
    s = load_settings({"SHOP_DB_PATH": str(tmp_path / "x.db"), "MCP_TRANSPORT": "HTTP", "PORT": "8765", "ALLOW_WRITES": "false"})
    assert (s.db_path, s.transport, s.port, s.allow_writes) == (tmp_path / "x.db", "http", 8765, False)


@pytest.mark.parametrize(
    "env",
    [{"MCP_TRANSPORT": "sse"}, {"PORT": "abc"}, {"PORT": "70000"}, {"ALLOW_WRITES": "maybe"}],
)
def test_config_rejects_bad_values(env):
    with pytest.raises(ConfigError):
        load_settings(env)
