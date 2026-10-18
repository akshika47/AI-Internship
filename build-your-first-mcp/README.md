# Build Your First MCP in 3 Hours

An MCP server lets an AI app like Claude or ChatGPT use your own tools and data. This one, `shop-data`, lets your AI app answer questions about a shop's sales and returns.

The shop is **Northwind Home, a fictional homeware store**. All its data is made up, with one real-world problem hidden in it for you to find.

## Try it now, nothing to install (2 minutes)

A ready-made copy runs online. Add this address to your AI app:

```
https://shop-data-mcp.empty-dream-9630.workers.dev/mcp
```

**In claude.ai or Claude Desktop**
1. Open **Settings → Connectors** (it may be called **Customize → Connectors**).
2. Click **Add custom connector**, give it a name like `Northwind shop`, and paste the address above. Leave login and any other fields empty.
3. In a new chat, click **+**, open **Connectors**, and switch it on.

**In ChatGPT**
1. Open **Plugins**, click **+**, then **Add custom MCP server**.
2. Paste the address above and choose no authentication.
3. ChatGPT's Free plan can't add custom servers. Some paid plans can; check yours.

**Then ask:**
- "Which category had a problem with returns in Q3 2026?"
- "Which product is causing it?"
- "How have Lighting sales changed over the last 6 months?"

When the app asks permission to use a tool, click **Allow**. Every number in the answer comes from the server, not from the AI's memory.

Opening the address in a web browser shows "Method not allowed". That's normal: it only talks to AI apps.

## Build your own (the workshop)

1. **Set up your laptop:** follow [`workshop/README.md`](workshop/README.md). It takes about 20 minutes.
2. **Build it with your AI assistant:** open [`prompts/`](prompts/) and paste the files in order, starting with [`prompts/1-build-first-tool.md`](prompts/1-build-first-tool.md).
3. **Test it:** questions and the answers you should see are in [`prompts/ask-your-server.md`](prompts/ask-your-server.md).

Stuck on a stage? Each one has a finished version in [`workshop/stages/`](workshop/stages/).

---

# For developers

The rest of this page covers the code, settings, tests and deployment.

**Stack:** Python 3.11+, [uv](https://docs.astral.sh/uv/), [FastMCP](https://gofastmcp.com) 4.1.0 and SQLite. The hosted copy is a TypeScript Cloudflare Worker with D1.

**The story in the data:** in 2026-Q3, Lighting's return rate jumps to 28.9% (92 of 318 items), up from 5.2%. The Aurora Glass Pendant accounts for 77 of the 92 returns. `data/make_data.py` generates it with a fixed seed.

## Layout

| Path | What it is |
|---|---|
| `src/shop_data/` | The production server, as a package. `server.py` has the four tools and the prompt, `config.py` reads environment variables, `db.py` opens SQLite (read-only for reads, a separate writable connection only for `save_note`), `__main__.py` runs it over stdio or HTTP. |
| `data/` | The only copy of the data: `shop.db` (SQLite), `orders.csv` (the same data for a spreadsheet) and `make_data.py` (rebuilds both). |
| `tests/` | Pytest suite using FastMCP's in-memory client: every tool, the story numbers, the error messages, the prompt, and the read-only mode. |
| `cloudflare/` | The three read-only tools as a Cloudflare Worker on D1, with rate limiting. See [`cloudflare/README.md`](cloudflare/README.md). |
| `prompts/` | **Start here for the workshop.** The prompt pack: one file per stage to paste into your AI assistant, plus questions to ask your server. |
| `workshop/` | Teaching material: pre-work, prompts, single-file servers for each stage, and three broken servers for the debugging block. |
| `pyproject.toml`, `uv.lock` | One environment for everything, pinned to FastMCP 4.1.0. |
| `.env.example` | The settings, with their defaults. |

## Tools

| Name | What it does |
|---|---|
| `sales_by_month(category=None, months=6)` | Revenue and orders per month, for all categories or one. |
| `top_products(category, quarter)` | The five best-selling products in a category in a quarter, with returns. |
| `return_rates(quarter)` | Each category's return rate against the previous quarter, biggest rise first. |
| `save_note(title, text)` | The only tool that writes: adds a row to the `notes` table. Registered only when `ALLOW_WRITES=true`. |

Prompt: `weekly_business_review(quarter)` walks Claude through the review and ends with a five-line note.

## Quick start

```bash
cd build-your-first-mcp
uv sync
uv run shop-data          # stdio: waits silently for an app to connect, which is correct
```

Settings come from environment variables (see `.env.example`):

| Variable | Default | Meaning |
|---|---|---|
| `SHOP_DB_PATH` | `<this folder>/data/shop.db` | The SQLite file. Relative paths are made absolute. |
| `MCP_TRANSPORT` | `stdio` | `stdio` for desktop apps, `http` to serve `/mcp` over Streamable HTTP. |
| `HOST` | `127.0.0.1` | Listen address in HTTP mode. Use `0.0.0.0` in a container. |
| `PORT` | `8000` | Listen port in HTTP mode. |
| `ALLOW_WRITES` | `true` | `false` removes `save_note`, making the server read-only. |

To use a `.env` file: `cp .env.example .env`, edit it, then `uv run --env-file .env shop-data`.

HTTP mode, read-only, as you would run it for other people:

```bash
MCP_TRANSPORT=http PORT=8000 ALLOW_WRITES=false uv run shop-data
# MCP endpoint: http://127.0.0.1:8000/mcp
```

Claude Desktop (`claude_desktop_config.json`), using the full path to uv and to this folder:

```json
{
  "mcpServers": {
    "shop-data": {
      "command": "/Users/YOU/.local/bin/uv",
      "args": ["--directory", "/Users/YOU/mcp-workshop/build-your-first-mcp", "run", "shop-data"],
      "env": { "ALLOW_WRITES": "true" }
    }
  }
}
```

## Test

```bash
uv run pytest -q
```

The tests copy `data/shop.db` to a temporary folder, so `save_note` never changes the real file.

Check it end to end with the MCP Inspector (needs Node 22.19 or newer). The Inspector passes only a few environment variables to the server, so set them with `-e`:

```bash
npx -y @modelcontextprotocol/inspector@2.11.0 --cli uv --directory . run shop-data --method tools/list
npx -y @modelcontextprotocol/inspector@2.11.0 --cli -e ALLOW_WRITES=false uv --directory . run shop-data --method tools/list
npx -y @modelcontextprotocol/inspector@2.11.0 --cli uv --directory . run shop-data \
  --method tools/call --tool-name return_rates --tool-arg quarter=2026-Q3
```

Over HTTP, with the server from the HTTP example running:

```bash
npx -y @modelcontextprotocol/inspector@2.11.0 --cli http://127.0.0.1:8000/mcp --transport http \
  --method tools/call --tool-name return_rates --tool-arg quarter=2026-Q3
```

Lighting should come first, at 28.9%.

## Deploy

- **Python, anywhere that runs a container or a process** (Render, Fly.io, a VM): run `uv sync --no-dev` then `uv run shop-data` with `MCP_TRANSPORT=http`, `HOST=0.0.0.0`, the platform's `PORT`, and `ALLOW_WRITES=false`. The server has no authentication, so keep it read-only when it is public.
- **Cloudflare Workers:** the read-only tools on D1. Exact commands are in [`cloudflare/README.md`](cloudflare/README.md).

## Safety

Read tools open the database with SQLite's `mode=ro`, so SQLite itself refuses writes. Every query is fixed SQL with `?` placeholders, and there is deliberately no "run any SQL" tool. Errors a model can fix (an unknown category, a badly written quarter) come back as plain-English tool errors; anything else is logged and reported only as a generic error.
