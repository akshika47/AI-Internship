# Stage 2: more tools, and one that writes

Copy everything inside the box below (on GitHub, the copy button is at its top right) and paste it into the **same chat** you used for stage 1, so Claude keeps the rules and the file. There is nothing to fill in.

```text
Now add three tools. Keep every rule from before (FastMCP 4.1 with `from fastmcp import FastMCP`,
@mcp.tool, fixed parameterised SQL, no print, absolute database path, ToolError with
plain-English messages, short docstrings with an example per input).

Definitions, so the numbers match the finished version exactly:
- A quarter looks like 2026-Q3. 2026-Q3 means orders with order_date from 2026-07-01 up to,
  but not including, 2026-10-01. If the format is wrong, raise ToolError with
  "'<what they typed>' is not a valid quarter. Use the form 2026-Q3 (year, dash, Q, 1 to 4)."
- Always ignore orders with status 'cancelled'. Count by the order's order_date, not the
  return date.
- An "item" is one row of order_items (one order line), whatever its quantity.
- Return rate = returned items / items, where a returned item is an order line that has a row
  in returns. As a percentage rounded to 1 decimal: round(100 * returned / items, 1).

1. top_products(category: str, quarter: str): the five products with the highest revenue in
   that category in that quarter, highest first. For each: product (its name), revenue
   (quantity times price, summed, rounded to 2 decimals), units (sum of quantity),
   returned_items (returned order lines) and return_rate_pct (returned order lines / order
   lines, rounded to 1 decimal, as defined above; not divided by units). Mark it read-only
   with @mcp.tool(annotations={"readOnlyHint": True}).
2. return_rates(quarter: str): one row per category with category, previous_quarter,
   previous_rate_pct, rate_pct, change_pts, items_sold, items_returned, top_reason and
   top_reason_share_pct. rate_pct and previous_rate_pct are rounded to 1 decimal first;
   change_pts = round(rate_pct - previous_rate_pct, 1), using the rounded rates. top_reason is
   the most common returns.reason in that category and quarter; if two reasons tie, pick the
   one that comes first alphabetically. top_reason_share_pct = round(100 * that reason's count
   / items_returned, 1). Sort with the biggest change_pts first. The quarter before 2026-Q1 is
   2025-Q4. If the previous quarter has no data, raise ToolError saying so. Mark it read-only
   too.
3. save_note(title: str, text: str): inserts a row into the notes table. This is the only tool
   that writes, so open a separate read-write connection just for it, and start its docstring
   with "WRITES to the database". Refuse an empty title or text.

Show me the whole updated file.
```

Replace your `workshop/server.py` with the new file (select all, paste, save), then quit and reopen Claude Desktop.

Test it from the `build-your-first-mcp` folder:

```bash
npx -y @modelcontextprotocol/inspector@2.11.0 --cli uv --directory . run workshop/server.py --method tools/call --tool-name return_rates --tool-arg quarter=2026-Q3
```

Lighting should come first: `previous_rate_pct` 5.2, `rate_pct` 28.9, `change_pts` 23.7, 92 of 318 items returned.

**Done when** Claude can answer "Which category had a returns problem in Q3 2026?", and asking it to save a note makes Claude ask your permission first.

Notes you save go into `data/shop.db`. To start again with a clean copy, run `uv run data/make_data.py`.

If you fall behind, point Claude Desktop at the finished file for this stage: change `workshop/server.py` to `workshop/stages/stage2.py` in your config, save, then quit and reopen Claude Desktop. Don't copy the stage file over your `server.py`: it only works from `workshop/stages/`.
