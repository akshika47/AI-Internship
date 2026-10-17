# Prompts to paste

Copy one prompt into your AI assistant at a time, and wait until each stage works before moving on. If you fall behind, copy the matching file from `finished/` into this folder as `server.py`.

## Stage 1: your first tool

### For Claude Desktop or claude.ai (the assistant writes the code, you save it)

> I'm not a programmer and I'm at a hands-on workshop. Help me build a small MCP server in Python, one step at a time, in plain English. Give me every command ready to copy and paste.
>
> **What it does:** it's called "shop-data". It lets Claude answer questions about the sales of a fictional online homeware store, Northwind Home. The data is in a SQLite file called `shop.db` in my project folder. Its tables are `categories(category_id, name)`, `products(product_id, name, category_id, price)`, `customers(customer_id, first_name, country, signup_date)`, `orders(order_id, order_date, customer_id, channel, status)`, `order_items(order_item_id, order_id, product_id, quantity, price)`, `returns(return_id, order_item_id, return_date, reason)` and `notes(note_id, created_at, title, text)`. Dates are text like `2026-07-14`. The categories are Kitchen, Bedding, Lighting, Decor and Bath. Orders with status `cancelled` must not count as sales.
>
> **Build only this one tool for now:** `sales_by_month(category: str | None = None, months: int = 6)`. It returns, for each of the most recent `months` months, the month (like `2026-07`), the revenue (quantity times price, summed over order items) and the number of orders, oldest first. If `category` is given, only products in that category count.
>
> **Rules the code must follow exactly:**
> 1. Use FastMCP version 4.1. The import is exactly `from fastmcp import FastMCP`. Then `mcp = FastMCP("shop-data")`, decorate the function with `@mcp.tool` (no brackets), and end the file with `if __name__ == "__main__": mcp.run()`. Do **not** use `mcp.server.fastmcp`, the `mcp` package's own FastMCP, or the word `MCPServer`. That is a different, older or newer library and will not import.
> 2. Use only Python's built-in `sqlite3` module. Never build SQL by joining strings: use fixed SQL with `?` placeholders. Do not add a tool that runs any SQL the user types.
> 3. Never use `print()`. Use `logging`, sent to stderr, if you need to log anything.
> 4. The database path must be absolute: `DB_PATH = Path(__file__).resolve().parent / "shop.db"`, because Claude Desktop does not start the server in my folder. Open it read-only for read tools.
> 5. The function's docstring is what Claude reads to decide when to use the tool. Write one or two short sentences, then one line per input with an example.
> 6. If something goes wrong (an unknown category, `months` out of range), raise `fastmcp.exceptions.ToolError` with a short, plain-English message that says what is allowed, for example "Unknown category 'Toys'. Use one of: Kitchen, Bedding, Lighting, Decor, Bath."
> 7. Put everything in one file called `server.py`, under 80 lines, and show me the whole file in one code block.
>
> My computer is a **[Mac / Windows]**. My project folder is `[paste the output of pwd]` and already has FastMCP installed with uv.
>
> After the code, tell me:
> (a) the one command to test it with the MCP Inspector,
> (b) the exact `claude_desktop_config.json` block, using the full path to uv (tell me how to find it) and my folder path,
> (c) how to fully quit and reopen Claude Desktop, and
> (d) three questions to ask Claude to try the tool.

### For Claude Code (the assistant writes the files itself)

Use the same prompt, but replace the last two paragraphs with:

> Write `server.py` in this folder. Then prove it works: run `npx -y @modelcontextprotocol/inspector@2.11.0 --cli uv --directory . run server.py --method tools/list`, and call the tool with `--method tools/call --tool-name sales_by_month --tool-arg category=Lighting months=6`. Show me the output and explain it in two sentences.

## Stage 2: more tools, and one that writes (same conversation)

> Now add three tools. Keep every rule from before (FastMCP 4.1 with `from fastmcp import FastMCP`, `@mcp.tool`, fixed parameterised SQL, no print, absolute database path, `ToolError` with plain-English messages, short docstrings with an example per input).
>
> 1. `top_products(category: str, quarter: str)`: the five products with the highest revenue in that category in that quarter, with revenue, units, how many items were returned and the return rate.  A quarter looks like `2026-Q3`. If the format is wrong, say so and show the right form. Mark it read-only with `@mcp.tool(annotations={"readOnlyHint": True})`.
> 2. `return_rates(quarter: str)`: for each category, the return rate (items returned divided by items sold, by order date, ignoring cancelled orders) in the quarter against the quarter before it, with the change in percentage points and the most common return reason, sorted with the biggest rise first. If the previous quarter has no data, say so. Mark it read-only too.
> 3. `save_note(title: str, text: str)`: inserts a row into the `notes` table. This is the only tool that writes, so open a separate read-write connection just for it, and start its docstring with "WRITES to the database". Refuse an empty title or text.
>
> Show me the whole updated file.

## Stage 3: a ready-made prompt

> Add a prompt (not a tool) with `@mcp.prompt` called `weekly_business_review(quarter: str)`. It returns text that tells Claude to: (1) call `sales_by_month` for the last 6 months, (2) call `return_rates` for the quarter and find the categories whose return rate rose most, (3) for each, call `top_products` for that quarter and the one before, find the product behind the rise and explain it in plain English using only numbers the tools returned, (4) draft a note of exactly 5 lines, and (5) show me the draft, then save it with `save_note`. Show me the whole updated file.

## Check the result

In the Inspector, run `return_rates` with quarter `2026-Q3`. One category should have jumped to about 29%. Ask Claude which product explains it.