# Stage 3: a ready-made weekly review

Paste this into the **same chat** again.

---

> Add a prompt (not a tool) with `@mcp.prompt` called `weekly_business_review(quarter: str)`. It returns text that tells Claude to: (1) call `sales_by_month` for the last 6 months, (2) call `return_rates` for the quarter and find the categories whose return rate rose most, (3) for each, call `top_products` for that quarter and the one before, find the product behind the rise and explain it in plain English using only numbers the tools returned, (4) draft a note of exactly 5 lines, and (5) show me the draft, then save it with `save_note`. Show me the whole updated file.

---

Save, then quit and reopen Claude Desktop. In a new chat, open **+**, choose `weekly_business_review` and type `2026-Q3`.

**Done when** Claude shows a five-line draft and asks before saving it.

If you fall behind, point Claude Desktop at the finished file for this stage instead of your `workshop/server.py`: change the path in your config to `workshop/stages/stage3.py`, then quit and reopen Claude Desktop.
