# Northwind Home: ask your shop data

**Live workshop: Sunday 18 October 2026, 21:00 UTC** (5 PM US Eastern; 2:30 AM Monday 19 October in India). Do the setup below before then.

By the end of the workshop, you can ask Claude plain-English questions about the sales and returns of a made-up online store. **Northwind Home is a fictional homeware store** (kitchen, bedding, lighting, decor and bath). Claude answers from a real database, through an MCP server that you built by directing an AI assistant. All names and numbers are invented, and no real shop or customer is in the data.

You always work in the **project folder**, `build-your-first-mcp` (the folder that contains `pyproject.toml`). Every command below is typed there. Your server will be the file `workshop/server.py`, and the data lives in `data/`.

> **No time for setup, or stuck?** Use the online copy instead: add `https://shop-data-mcp.empty-dream-9630.workers.dev/mcp` as a custom connector in claude.ai or ChatGPT. Steps are at the top of the [project README](../README.md#try-it-now-nothing-to-install-2-minutes).

## What is a terminal?

A terminal is the window where you type commands and press Enter. On a Mac it is the **Terminal** app (search for it with Cmd+Space). On Windows it is **PowerShell** or **Terminal** (search for it in the Start menu).

To open a terminal *in a folder*:
- **Mac:** open Terminal, type `cd ` (with a space after it), drag the folder from Finder onto the Terminal window, and press Enter.
- **Windows:** in File Explorer, right-click the folder and choose **Open in Terminal**.

## Before the workshop (20 minutes)

1. **Claude Desktop:** install it from https://claude.ai/download, sign in and update it.
2. **uv** (runs Python for you):
   - Mac: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Windows PowerShell: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
   - Close the terminal, open a new one, and check it with `uv --version`. You should see a version number.
3. **Node.js 22.19 or newer** from https://nodejs.org. Check it with `node --version`. It is only needed for the MCP Inspector, the testing tool.
4. **Get the project folder.** Choose one way:
   - **Option A, with git:** in a new terminal, run `git clone https://github.com/akshika47/AI-Internship.git`, then `cd AI-Internship/build-your-first-mcp`. (On a Mac, if it offers to install "command line developer tools", accept, then run the clone again.)
   - **Option B, no git:** on https://github.com/akshika47/AI-Internship click the green **Code** button, then **Download ZIP**. Unzip it, then open the `AI-Internship-main/build-your-first-mcp` folder in a terminal (see "What is a terminal?" above).

   Then, in that terminal, run `uv sync`. It prints many lines starting with `+`, one per package it installs. That is normal; only a line that says `error` is a problem.
5. **Write down your folder's full path.** In the same terminal, type `pwd` and press Enter.
   - Mac: it prints one line like `/Users/sam/AI-Internship/build-your-first-mcp`. Copy it.
   - Windows: it prints `Path`, a line of dashes, and then a line like `C:\Users\sam\AI-Internship\build-your-first-mcp`. Copy only the line that starts with `C:\`.

   You need this path in step 7 and in the first prompt.
6. **Look at the data first:** open `data/orders.csv` in Excel, Numbers or Google Sheets. Each row is one item in one order, with a column saying whether it was returned. Can you tell which category has a returns problem? (Hard, isn't it? That is why we are building this.)
7. **Connect the test server to Claude Desktop:**
   - Find uv's full path. Mac: `which uv`. Windows: `where.exe uv`. Copy the line it prints (on a Mac usually like `/Users/sam/.local/bin/uv`; on Windows usually like `C:\Users\sam\.local\bin\uv.exe`). Claude Desktop does not search for programs the way your terminal does, so it needs this full path.
   - In Claude Desktop open **Settings**, then **Developer**, then **Edit Config**. Depending on the version, this either opens `claude_desktop_config.json` in an editor or shows the file in Finder or File Explorer. If it only shows the file, right-click it and open it with TextEdit (Mac) or Notepad (Windows).
   - Copy the whole block from [`config-mac.json`](config-mac.json) or [`config-windows.json`](config-windows.json) into that file. Then:
     - replace the capitals that start `PASTE THE PATH THAT which uv` (Windows: `where.exe uv`) with uv's path,
     - replace the capitals that start `PASTE THE PATH THAT pwd` with the path from step 5,
     - and for now change `workshop/server.py` to `workshop/hello_server.py`, because you have not built your server yet.

     Keep the quote marks around each path. If the file already has other content, add only the `"shop-data": { ... }` part inside `mcpServers`.
   - **Windows only:** in this file every backslash must be doubled. `C:\Users\sam\AI-Internship\build-your-first-mcp` becomes `C:\\Users\\sam\\AI-Internship\\build-your-first-mcp`.
   - Save the file. Quit Claude Desktop completely (Mac: Cmd+Q; Windows: right-click the tray icon, then Quit) and reopen it. Closing the window is not enough.
   - Ask: "Say hello to me using my workshop setup. My name is ...". Claude should ask your permission, then use the `say_hello` tool.

If a step fails, send us a screenshot of the terminal and tell us your operating system.

## What you will see when a server runs

When you start a server by hand, for example `uv run workshop/hello_server.py`, it prints a large FastMCP box, a line saying `Starting MCP server ... with transport 'stdio'`, and then waits. That is correct: it is waiting for an app to talk to it. Press Ctrl+C to stop it.

It may also print an **"Update available"** box that tells you to run `pip install --upgrade fastmcp`. **Ignore it.** The project pins FastMCP 4.1.0 on purpose so everyone has the same setup; don't upgrade during the workshop.

## What is in this folder

| File | What it is for |
|---|---|
| `hello_server.py` | The setup test: one tool. |
| `../prompts/` | The prompts you paste into your AI assistant, one file per stage (start with `1-build-first-tool.md`). |
| `config-mac.json`, `config-windows.json` | Templates for connecting your server to Claude Desktop. |
| `stages/stage1.py` to `stage3.py` | Working code for each stage, each one a single file. |
| `debugging/` | Three deliberately broken servers for the debugging block. |
| `server.py` | Does not exist yet: this is the file you build during the workshop. |

The data is one folder up, in `data/`: `orders.csv` (to open in a spreadsheet), `shop.db` (the same data as a SQLite database, which the server reads) and `make_data.py` (rebuilds both exactly the same way). `pyproject.toml` and `uv.lock` in the project folder pin FastMCP 4.1.0, so everyone has the same setup.

Notes that your server saves go into `data/shop.db`. To start again with a clean copy, run `uv run data/make_data.py` from the project folder.

## If you fall behind

Point Claude Desktop at the finished file for your stage: in `claude_desktop_config.json`, change `workshop/server.py` to `workshop/stages/stage1.py` (or `stage2.py`, `stage3.py`), save, then quit and reopen Claude Desktop.

**Don't copy a stage file over your `server.py`.** The stage files find the database from `workshop/stages/`, so a copy in `workshop/` looks in the wrong folder and every tool call fails with `unable to open database file`.

## The three stages

1. **One live tool:** `sales_by_month` shows revenue and orders for each month, for all categories or one.
2. **More tools:** `top_products`, `return_rates` (which category's returns rose against the previous quarter), and `save_note`, the only tool that writes. Claude asks your permission before it runs.
3. **The payoff:** a ready-made prompt, `weekly_business_review`, appears in Claude's "+" menu. It finds the return spike, traces it to a product and saves a note.

## Test a server without Claude

The MCP Inspector is the official testing tool. It has two modes; run either one from the project folder.

**Terminal check.** It prints the result and finishes:

```bash
npx -y @modelcontextprotocol/inspector@2.11.0 --cli uv --directory . run workshop/server.py --method tools/list
```

**Browser view.** It opens a web page where you click through your tools. The terminal keeps running until you press Ctrl+C; that is expected, so leave it open while you use the page:

```bash
npx -y @modelcontextprotocol/inspector@2.11.0 uv --directory . run workshop/server.py
```

Before you have built `server.py`, try them with `workshop/hello_server.py` or `workshop/stages/stage2.py` in its place.

## Things that break, and the fix

Each of the first three has a matching file in `debugging/` so you can see the error for yourself.

1. **`No module named 'mcp.server.fastmcp'`** (`debugging/broken1_old_import.py`): the AI wrote old code. Use `from fastmcp import FastMCP`.
2. **The Inspector says "Connection closed" and no error appears** (`debugging/broken2_no_run.py`): the file never calls `mcp.run()`, so it starts and immediately ends. Add `if __name__ == "__main__": mcp.run()` at the bottom.
3. **`unable to open database file` on the first tool call** (`debugging/broken3_relative_path.py`): the database path is relative, so it is looked up in whatever folder Claude Desktop started in. Build it from the file's own location: `Path(__file__).resolve().parents[1] / "data" / "shop.db"` for `workshop/server.py`.
4. **The server doesn't appear in Claude:** quit Claude Desktop fully, then reopen it.
5. **`uv` not found:** put the full path to uv in the config (step 7 above).
6. **A `print()` in the code:** it writes onto the channel Claude listens on. Use `logging` instead.
7. **A missing comma or quote mark in the config file:** paste the file into a JSON checker. On Windows, check that every backslash is doubled.

## Stay safe

Only run servers you have read or trust. A tool can act as you. This server can only read the shop data, plus write short notes into its own `notes` table. There is deliberately no "run any SQL" tool.
