# Stage 2: more tools, and one that writes

Paste this into the **same chat** you used for stage 1, so Claude keeps the rules and the file.

---

> Now add three tools. Keep every rule from before (FastMCP 4.1 with `from fastmcp import FastMCP`, `@mcp.tool`, fixed parameterised SQL, no print, absolute database path, `ToolError` with plain-English messages, short docstrings with an example per input).
>
> 1. `top_products(category: str, quarter: str)`: the five products with the highest revenue in that category in that quarter, with revenue, units, how many items were returned and the return rate.  A quarter looks like `2026-Q3`. If the format is wrong, say so and show the right form. Mark it read-only with `@mcp.tool(annotations={"readOnlyHint": True})`.
> 2. `return_rates(quarter: str)`: for each category, the return rate (items returned divided by items sold, by order date, ignoring cancelled orders) in the quarter against the quarter before it, with the change in percentage points and the most common return reason, sorted with the biggest rise first. If the previous quarter has no data, say so. Mark it read-only too.
> 3. `save_note(title: str, text: str)`: inserts a row into the `notes` table. This is the only tool that writes, so open a separate read-write connection just for it, and start its docstring with "WRITES to the database". Refuse an empty title or text.
>
> Show me the whole updated file.

---

Save the new file, then quit and reopen Claude Desktop.

**Done when** Claude can answer "Which category had a returns problem in Q3 2026?", and asking it to save a note makes Claude ask your permission first.

If you fall behind, point Claude Desktop at the finished file for this stage instead of your `workshop/server.py`: change the path in your config to `workshop/stages/stage2.py`, then quit and reopen Claude Desktop.
