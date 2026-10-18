# Stage 1: build your first tool

Using Claude Code instead? Use [`claude-code.md`](claude-code.md).

## Before you paste

You need your project folder's full path. Open a terminal in the `build-your-first-mcp` folder, type `pwd` and press Enter. On a Mac, copy the line it prints. On Windows, copy only the line that starts with `C:\` (not the `Path` and `----` lines above it). [`workshop/README.md`](../workshop/README.md) explains what a terminal is and how to open one in a folder.

## The prompt

1. Copy everything inside the box below. On GitHub, the copy button is at the top right of the box.
2. Paste it into Claude (desktop app or claude.ai) in a **new chat**.
3. Before you send it, fill in the two parts in square brackets on the last lines: delete `[Mac / Windows]` and type your system, and delete `[paste the output of pwd]` and paste your path. Remove the brackets too.

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

I will test it from my project folder with:
npx -y @modelcontextprotocol/inspector@2.11.0 --cli uv --directory . run workshop/server.py --method tools/list
and my Claude Desktop config already runs workshop/server.py with uv.

My computer is a [Mac / Windows]. My project folder is [paste the output of pwd] and already
has FastMCP installed with uv. After the code, give me three questions to ask Claude to try
the tool.
```

## Save the reply as `workshop/server.py`

1. Claude's reply has the code in a box with a copy button. Copy it.
2. Open the `workshop` folder and create a new file called `server.py` in it:
   - **VS Code** (any system): File, New File, paste, then Save As `server.py` inside `workshop`.
   - **Mac without VS Code:** open TextEdit, choose Format, then **Make Plain Text**, paste, and save as `server.py` inside `workshop`. If it asks, choose "Use .py".
   - **Windows without VS Code:** open Notepad, paste, choose File, Save As, set "Save as type" to **All files**, and name it `server.py`. Otherwise Windows saves it as `server.py.txt`.

## Test it

In the terminal, from the `build-your-first-mcp` folder (not from inside `workshop`):

```bash
npx -y @modelcontextprotocol/inspector@2.11.0 --cli uv --directory . run workshop/server.py --method tools/call --tool-name sales_by_month --tool-arg category=Lighting
```

It prints a FastMCP box and some log lines first. That is normal; the result is the list of six months at the end. If you also want to run the server on its own, `uv run workshop/server.py` prints the FastMCP box and then waits: that is correct, press Ctrl+C to stop it. Ignore any "Update available" box; the workshop pins FastMCP 4.1.0 on purpose.

Then connect it: in `claude_desktop_config.json`, change `workshop/hello_server.py` to `workshop/server.py`, save, and quit and reopen Claude Desktop (Mac: Cmd+Q; Windows: right-click the tray icon, then Quit).

**Done when** the test command lists six months of Lighting revenue, and Claude Desktop answers "How have Lighting sales changed over the last 6 months?" using `sales_by_month`.

Your file may differ from `workshop/stages/stage1.py`, for example the finished stage files also mark tools read-only with `@mcp.tool(annotations={"readOnlyHint": True})`. Both are fine.

## If you fall behind

Point Claude Desktop at the finished file for this stage: in your config, change `workshop/server.py` to `workshop/stages/stage1.py`, save, then quit and reopen Claude Desktop. Don't copy the stage file over your `server.py`: it only works from `workshop/stages/`, and a copy can't find the database.
