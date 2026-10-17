# Northwind Home: ask your shop data

By the end of the workshop, you can ask Claude plain-English questions about the sales and returns of a made-up online store. **Northwind Home is a fictional homeware store** (kitchen, bedding, lighting, decor and bath). Claude answers from a real database, through an MCP server that you built by directing an AI assistant. All names and numbers are invented, and no real shop or customer is in the data.

## Before the workshop (20 minutes)

1. **Claude Desktop:** install it from https://claude.ai/download, sign in and update it.
2. **uv** (runs Python for you):
   - Mac: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Windows PowerShell: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
   - Reopen the terminal and check it with `uv --version`.
3. **Node.js 22.19 or newer** from https://nodejs.org. Check it with `node --version`. It is only needed for the MCP Inspector, the testing tool.
4. **Install this folder:** unzip it to `~/mcp-workshop/shop-data` (Windows: `C:\Users\YOU\mcp-workshop\shop-data`). In a terminal, go into the folder and run `uv sync`.
5. **Look at the data first:** open `orders.csv` in Excel, Numbers or Google Sheets. Each row is one item in one order, with a column saying whether it was returned. Can you tell which category has a returns problem? (Hard, isn't it? That is why we are building this.)
6. **Connect the test server:**
   - Find uv's full path: `which uv` (Mac) or `where.exe uv` (Windows).
   - In Claude Desktop open Settings, then Developer, then Edit Config. This opens `claude_desktop_config.json`.
   - Paste in the block from `config-mac.json` or `config-windows.json`, replace `YOU` with your user name, and change `server.py` to `hello_server.py` for now. If the file already has other content, add only the `"shop-data": { ... }` part inside `mcpServers`.
   - Quit Claude Desktop completely (Mac: Cmd+Q; Windows: tray icon, then Quit) and reopen it.
   - Ask: "Say hello to me using my workshop setup. My name is ...". Claude should use the `say_hello` tool and ask your permission first.

If a step fails, send us a screenshot of the terminal and tell us your operating system.

## What is in this folder

| File | What it is for |
|---|---|
| `orders.csv` | The raw data, to open in a spreadsheet. |
| `shop.db` | The same data as a database (SQLite). This is what the server reads. |
| `make_data.py` | Rebuilds both data files exactly the same way: `uv run make_data.py`. |
| `hello_server.py` | The setup test: one tool. |
| `PROMPTS.md` | The prompts you paste into your AI assistant, one per stage. |
| `config-mac.json`, `config-windows.json` | Templates for connecting your server to Claude Desktop. |
| `finished/stage1_server.py` to `stage3_server.py` | Working code for each stage. If you fall behind, copy the current stage's file into this folder, name it `server.py`, and carry on. |
| `pyproject.toml`, `uv.lock` | They pin the FastMCP version (4.1.0), so everyone has the same setup. |

## The three stages

1. **One live tool:** `sales_by_month` shows revenue and orders for each month, for all categories or one.
2. **More tools:** `top_products`, `return_rates` (which category's returns rose against the previous quarter), and `save_note`, the only tool that writes. Claude asks your permission before it runs.
3. **The payoff:** a ready-made prompt, `weekly_business_review`, appears in Claude's "+" menu. It finds the return spike, traces it to a product and saves a note.

## Things that break, and the fix

1. **`No module named 'mcp.server.fastmcp'`:** the AI wrote old code. Use `from fastmcp import FastMCP`.
2. **The server doesn't appear in Claude:** quit Claude Desktop fully, then reopen it.
3. **`uv` not found:** put the full path to uv in the config.
4. **A `print()` in the code:** it writes onto the channel Claude listens on. Use `logging` instead.
5. **`unable to open database file`:** the database path is relative. It must be built from `Path(__file__).resolve().parent`.
6. **A missing comma in the config file:** paste the file into a JSON checker.

## Stay safe

Only run servers you have read or trust. A tool can act as you. This server can only read the shop data, plus write short notes into its own `notes` table. There is deliberately no "run any SQL" tool.
