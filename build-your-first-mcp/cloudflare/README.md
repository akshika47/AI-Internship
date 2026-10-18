# shop-data on Cloudflare Workers

The three read-only tools of `shop-data` (`sales_by_month`, `top_products`, `return_rates`) and the `weekly_business_review` prompt, as a TypeScript Worker. Same names, descriptions, SQL and error messages as `../src/shop_data/server.py`. There is no `save_note`: this copy is public and read-only.

- **Data:** Cloudflare D1 (SQLite), seeded from `../data/shop.db`.
- **MCP:** `createMcpHandler` from the Agents SDK, stateless Streamable HTTP at `/mcp`.
- **Abuse protection:** Workers Rate Limiting, 60 requests per minute per client IP (`wrangler.jsonc`, binding `LIMITER`).

## Files

| File | What it is |
|---|---|
| `src/index.ts` | The Worker: tools, prompt and rate limit. |
| `wrangler.jsonc` | Worker name `shop-data-mcp`, the D1 binding `DB` and the rate-limit binding `LIMITER`. |
| `scripts/export_d1.py` | Writes `seed.sql` from `../data/shop.db`. D1 cannot import a `.db` file, so it gets SQL. |
| `package.json`, `package-lock.json` | Pinned dependencies. |

`seed.sql` and `worker-configuration.d.ts` are generated, so they are not committed.

## Run it locally

Needs Node 22.19 or newer and uv (which provides Python). No Cloudflare account is needed for this part.

```bash
cd cloudflare
npm install
uv run scripts/export_d1.py                                    # writes seed.sql
npx wrangler d1 execute shop-data --local --file seed.sql      # loads it into a local D1
npx wrangler dev --port 8787
```

In another terminal:

```bash
npx -y @modelcontextprotocol/inspector@2.11.0 --cli http://localhost:8787/mcp --transport http --method tools/call --tool-name return_rates --tool-arg quarter=2026-Q3
```

Lighting should come first, at 28.9%. Type-check with `npm run type-check`.

## Deploy

```bash
cd cloudflare
npx wrangler login
npx wrangler d1 create shop-data
```

Copy the `database_id` it prints into `wrangler.jsonc`, replacing the existing id (that one is our deployment's database). Then:

```bash
uv run scripts/export_d1.py
npx wrangler d1 execute shop-data --remote --file seed.sql
npx wrangler deploy
```

`wrangler deploy` prints the Worker's URL, for example `https://shop-data-mcp.<your-subdomain>.workers.dev`. Test it with the Inspector:

```bash
npx -y @modelcontextprotocol/inspector@2.11.0 --cli https://shop-data-mcp.<your-subdomain>.workers.dev/mcp --transport http --method tools/call --tool-name return_rates --tool-arg quarter=2026-Q3
```

Or open the Inspector's web UI with `npx -y @modelcontextprotocol/inspector@2.11.0`, choose "Streamable HTTP" and paste the `/mcp` URL.

To connect it to claude.ai, add it as a custom connector with the same `/mcp` URL.

## Updating the data

If `../data/make_data.py` changes, rebuild and reseed: `uv run ../data/make_data.py`, then `uv run scripts/export_d1.py` and the `d1 execute` command again. The seed drops and recreates its tables, so running it twice is safe.
