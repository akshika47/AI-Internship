# Stage 1 for Claude Code users

Claude Code writes the file and tests it for you. Open a terminal in the `build-your-first-mcp` folder (the project folder, not `workshop`), run `claude`, and paste everything inside the box below. There is nothing to fill in.

```text
Build a small MCP server in Python with me, step by step. Explain each step in one or two
sentences and give me every command ready to copy.

What it does: it's called "shop-data". It lets Claude answer questions about the sales of a
fictional online homeware store, Northwind Home. The data is in a SQLite file at data/shop.db
in my project folder, and my server goes in workshop/server.py. Its tables are
categories(category_id, name), products(product_id, name, category_id, price),
customers(customer_id, first_name, country, signup_date),
orders(order_id, order_date, customer_id, channel, status),
order_items(order_item_id, order_id, product_id, quantity, price),
returns(return_id, order_item_id, return_date, reason) and notes(note_id, created_at, title, text).
Dates are text like 2026-07-14. The categories are Kitchen, Bedding, Lighting, Decor and Bath.
Orders with status 'cancelled' must not count as sales.

Build only this one tool for now: sales_by_month(category: str | None = None, months: int = 6).
It returns, for each of the most recent `months` months, the month (like 2026-07), the revenue
(quantity times price, summed over order items, rounded to 2 decimals) and the number of orders,
oldest first. If category is given, only products in that category count.

Rules the code must follow exactly:
1. Use FastMCP version 4.1. The import is exactly `from fastmcp import FastMCP`. Then
   mcp = FastMCP("shop-data"), decorate the function with @mcp.tool (no brackets), and end the
   file with:
       if __name__ == "__main__":
           mcp.run()
   Do NOT use mcp.server.fastmcp, the mcp package's own FastMCP, or the word MCPServer. That is
   a different, older or newer library and will not import.
2. Use only Python's built-in sqlite3 module. Never build SQL by joining strings: use fixed SQL
   with ? placeholders. Do not add a tool that runs any SQL the user types.
3. Never use print(). Use logging, sent to stderr, if you need to log anything.
4. The database path must be absolute:
   DB_PATH = Path(__file__).resolve().parents[1] / "data" / "shop.db"
   (server.py is in workshop/, one folder below the project), because Claude Desktop does not
   start the server in my folder. Open it read-only for read tools.
5. The function's docstring is what Claude reads to decide when to use the tool. Write one or
   two short sentences, then one line per input with an example.
6. If something goes wrong (an unknown category, or months outside 1 to 15, because the data
   covers 15 months), raise fastmcp.exceptions.ToolError with a short, plain-English message
   that says what is allowed, for example
   "Unknown category 'Toys'. Use one of: Kitchen, Bedding, Lighting, Decor, Bath."
7. Put everything in one file, workshop/server.py, under 80 lines, and show me the whole file
   in one code block.

Write workshop/server.py. Then prove it works from the project folder: run
npx -y @modelcontextprotocol/inspector@2.11.0 --cli uv --directory . run workshop/server.py --method tools/list
and call the tool with
npx -y @modelcontextprotocol/inspector@2.11.0 --cli uv --directory . run workshop/server.py --method tools/call --tool-name sales_by_month --tool-arg category=Lighting --tool-arg months=6
Show me the output and explain it in two sentences.
```

The Inspector prints a FastMCP box and log lines before the result. That is normal. Ignore any "Update available" box: the workshop pins FastMCP 4.1.0 on purpose.

For stages 2 and 3, paste the boxes from [`2-add-more-tools.md`](2-add-more-tools.md) and [`3-add-weekly-review.md`](3-add-weekly-review.md) into the same session.

If you fall behind, use the finished files in `workshop/stages/` from where they are (for example `uv --directory . run workshop/stages/stage2.py`). Don't copy one over your `server.py`: it only works from `workshop/stages/`.
