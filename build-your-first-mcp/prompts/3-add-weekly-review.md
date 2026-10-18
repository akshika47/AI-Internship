# Stage 3: a ready-made weekly review

Copy everything inside the box below (on GitHub, the copy button is at its top right) and paste it into the **same chat** again. There is nothing to fill in.

```text
Add a prompt (not a tool) with @mcp.prompt called weekly_business_review(quarter: str).
It returns text that tells Claude to:
(1) call sales_by_month for the last 6 months,
(2) call return_rates for the quarter and find the categories whose return rate rose most,
(3) for each, call top_products for that quarter and the one before, find the product behind
    the rise and explain it in plain English using only numbers the tools returned,
(4) draft a note of exactly 5 lines, and
(5) show me the draft, then save it with save_note.
Show me the whole updated file.
```

Replace your `workshop/server.py` with the new file and save. Check the prompt is there, from the `build-your-first-mcp` folder:

```bash
npx -y @modelcontextprotocol/inspector@2.11.0 --cli uv --directory . run workshop/server.py --method prompts/list
```

Then quit and reopen Claude Desktop. In a new chat, open **+**, choose `weekly_business_review` and type `2026-Q3`.

**Done when** Claude shows a five-line draft and asks before saving it.

If you fall behind, point Claude Desktop at the finished file for this stage: change `workshop/server.py` to `workshop/stages/stage3.py` in your config, save, then quit and reopen Claude Desktop. Don't copy the stage file over your `server.py`: it only works from `workshop/stages/`.
