# Northwind Home: ask your shop data

By the end of the workshop, you can ask Claude plain-English questions about the sales and returns of a made-up online store. **Northwind Home is a fictional homeware store** (kitchen, bedding, lighting, decor and bath). Claude answers from a real database, through an MCP server that you built by directing an AI assistant. All names and numbers are invented, and no real shop or customer is in the data.

Everything below happens inside the `build-your-first-mcp` folder (the "project folder"). The data lives in `data/`; you work in `workshop/`.

> **No time for setup, or stuck?** Use the online copy instead: add `https://shop-data-mcp.empty-dream-9630.workers.dev/mcp` as a custom connector in claude.ai or ChatGPT. Steps are at the top of the [project README](../README.md#try-it-now-nothing-to-install-2-minutes).

## Before the workshop (20 minutes)

1. **Claude Desktop:** install it from https://claude.ai/download, sign in and update it.
2. **uv** (runs Python for you):
   - Mac: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Windows PowerShell: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
   - Reopen the terminal and check it with `uv --version`.
3. **Node.js 22.19 or newer** from https://nodejs.org. Check it with `node --version`. It is only needed for the MCP Inspector, the testing tool.
4. **Get the project folder:** download or clone it to `~/mcp-workshop/build-your-first-mcp` (Windows: `C:\Users\YOU\mcp-workshop\build-your-first-mcp`). In a terminal, go into that folder and run `uv sync`.
5. **Look at the data first:** open `data/orders.csv` in Excel, Numbers or Google Sheets. Each row is one item in one order, with a column saying whether it was returned. Can you tell which category has a returns problem? (Hard, isn't it? That is why we are building this.)
6. **Connect the test server:**
   - Find uv's full path: `which uv` (Mac) or `where.exe uv` (Windows).
   - In Claude Desktop open Settings, then Developer, then Edit Config. This opens `claude_desktop_config.json`.
   - Paste in the block from `workshop/config-mac.json` or `workshop/config-windows.json`, replace `YOU` with your user name, and change `workshop/server.py` to `workshop/hello_server.py` for now. If the file already has other content, add only the `"shop-data": { ... }` part inside `mcpServers`.
   - Quit Claude Desktop completely (Mac: Cmd+Q; Windows: tray icon, then Quit) and reopen it.
   - Ask: "Say hello to me using my workshop setup. My name is ...". Claude should use the `say_hello` tool and ask your permission first.

If a step fails, send us a screenshot of the terminal and tell us your operating system.

## What is in this folder

| File | What it is for |
|---|---|
| `hello_server.py` | The setup test: one tool. |
| `../prompts/` | The prompts you paste into your AI assistant, one file per stage (start with `1-build-first-tool.md`). |
| `config-mac.json`, `config-windows.json` | Templates for connecting your server to Claude Desktop. |
| `stages/stage1.py` to `stage3.py` | Working code for each stage, each one a single file. If you fall behind, point your Claude Desktop config at the current stage's file (for example `workshop/stages/stage2.py` instead of `workshop/server.py`) and restart Claude Desktop. |
| `debugging/` | Three deliberately broken servers for the debugging block. |
| `server.py` | Does not exist yet: this is the file you build during the workshop. |

The data is one folder up, in `data/`: `orders.csv` (to open in a spreadsheet), `shop.db` (the same data as a SQLite database, which the server reads) and `make_data.py` (rebuilds both exactly the same way: `uv run data/make_data.py`). `pyproject.toml` and `uv.lock` in the project folder pin FastMCP 4.1.0, so everyone has the same setup.

## The three stages

1. **One live tool:** `sales_by_month` shows revenue and orders for each month, for all categories or one.
2. **More tools:** `top_products`, `return_rates` (which category's returns rose against the previous quarter), and `save_note`, the only tool that writes. Claude asks your permission before it runs.
3. **The payoff:** a ready-made prompt, `weekly_business_review`, appears in Claude's "+" menu. It finds the return spike, traces it to a product and saves a note.

Test any stage without Claude, from the project folder:

```bash
npx -y @modelcontextprotocol/inspector@2.11.0 --cli uv --directory . run workshop/stages/stage2.py --method tools/list
```

## Things that break, and the fix

Each of the first three has a matching file in `debugging/` so you can see the error for yourself.

1. **`No module named 'mcp.server.fastmcp'`** (`debugging/broken1_old_import.py`): the AI wrote old code. Use `from fastmcp import FastMCP`.
2. **The Inspector says "Connection closed" and no error appears** (`debugging/broken2_no_run.py`): the file never calls `mcp.run()`, so it starts and immediately ends. Add `if __name__ == "__main__": mcp.run()` at the bottom.
3. **`unable to open database file` on the first tool call** (`debugging/broken3_relative_path.py`): the database path is relative, so it is looked up in whatever folder Claude Desktop started in. Build it from the file's own location: `Path(__file__).resolve().parents[1] / "data" / "shop.db"` for `workshop/server.py`.
4. **The server doesn't appear in Claude:** quit Claude Desktop fully, then reopen it.
5. **`uv` not found:** put the full path to uv in the config.
6. **A `print()` in the code:** it writes onto the channel Claude listens on. Use `logging` instead.
7. **A missing comma in the config file:** paste the file into a JSON checker.

## Stay safe

Only run servers you have read or trust. A tool can act as you. This server can only read the shop data, plus write short notes into its own `notes` table. There is deliberately no "run any SQL" tool.
