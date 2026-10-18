# Stage 1: build your first tool

Paste everything below into Claude (desktop app or claude.ai) in a **new chat**. Fill in the two parts in **[brackets]** first.

Using Claude Code instead? Use [`claude-code.md`](claude-code.md).

---

> Build a small MCP server in Python with me, step by step. Explain each step in one or two sentences and give me every command ready to copy.
>
> **What it does:** it's called "shop-data". It lets Claude answer questions about the sales of a fictional online homeware store, Northwind Home. The data is in a SQLite file at `data/shop.db` in my project folder, and my server goes in `workshop/server.py`. Its tables are `categories(category_id, name)`, `products(product_id, name, category_id, price)`, `customers(customer_id, first_name, country, signup_date)`, `orders(order_id, order_date, customer_id, channel, status)`, `order_items(order_item_id, order_id, product_id, quantity, price)`, `returns(return_id, order_item_id, return_date, reason)` and `notes(note_id, created_at, title, text)`. Dates are text like `2026-07-14`. The categories are Kitchen, Bedding, Lighting, Decor and Bath. Orders with status `cancelled` must not count as sales.
>
> **Build only this one tool for now:** `sales_by_month(category: str | None = None, months: int = 6)`. It returns, for each of the most recent `months` months, the month (like `2026-07`), the revenue (quantity times price, summed over order items) and the number of orders, oldest first. If `category` is given, only products in that category count.
>
> **Rules the code must follow exactly:**
> 1. Use FastMCP version 4.1. The import is exactly `from fastmcp import FastMCP`. Then `mcp = FastMCP("shop-data")`, decorate the function with `@mcp.tool` (no brackets), and end the file with `if __name__ == "__main__": mcp.run()`. Do **not** use `mcp.server.fastmcp`, the `mcp` package's own FastMCP, or the word `MCPServer`. That is a different, older or newer library and will not import.
> 2. Use only Python's built-in `sqlite3` module. Never build SQL by joining strings: use fixed SQL with `?` placeholders. Do not add a tool that runs any SQL the user types.
> 3. Never use `print()`. Use `logging`, sent to stderr, if you need to log anything.
> 4. The database path must be absolute: `DB_PATH = Path(__file__).resolve().parents[1] / "data" / "shop.db"` (server.py is in `workshop/`, one folder below the project), because Claude Desktop does not start the server in my folder. Open it read-only for read tools.
> 5. The function's docstring is what Claude reads to decide when to use the tool. Write one or two short sentences, then one line per input with an example.
> 6. If something goes wrong (an unknown category, `months` out of range), raise `fastmcp.exceptions.ToolError` with a short, plain-English message that says what is allowed, for example "Unknown category 'Toys'. Use one of: Kitchen, Bedding, Lighting, Decor, Bath."
> 7. Put everything in one file, `workshop/server.py`, under 80 lines, and show me the whole file in one code block.
>
> My computer is a **[Mac / Windows]**. My project folder is `[paste the output of pwd]` and already has FastMCP installed with uv.
>
> After the code, tell me:
> (a) the one command to test it with the MCP Inspector,
> (b) the exact `claude_desktop_config.json` block, using the full path to uv (tell me how to find it) and my folder path,
> (c) how to fully quit and reopen Claude Desktop, and
> (d) three questions to ask Claude to try the tool.

---

**Done when** the MCP Inspector lists `sales_by_month`, and calling it with category `Lighting` returns six months of revenue.

If you fall behind, point Claude Desktop at the finished file for this stage instead of your `workshop/server.py`: change the path in your config to `workshop/stages/stage1.py`, then quit and reopen Claude Desktop.
