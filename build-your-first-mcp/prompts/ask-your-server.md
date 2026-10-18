# Questions to ask your server

Once your server is connected (in Claude Desktop, claude.ai or ChatGPT), try these. The answers come from the tools, so every number should match.

| Ask | Tool Claude should use | What you should see |
|---|---|---|
| "How have Lighting sales changed over the last 6 months?" | `sales_by_month` | Six months of revenue and orders. Sales look healthy. |
| "Which category had a problem with returns in Q3 2026?" | `return_rates` | Lighting: 5.2% in Q2, 28.9% in Q3. Most returns say "damaged". |
| "Which Lighting product is causing it?" | `top_products` | The Aurora Glass Pendant: 77 of the 92 Lighting returns. |
| "Save a five-line note about this for the team." | `save_note` | Claude asks your permission first, because this tool writes. Laptop version only. |
| Open **+**, pick `weekly_business_review`, type `2026-Q3` | the prompt | The whole chain, a five-line draft, then a request to save it. |

## Your own questions

- "Compare Kitchen and Bath return rates for Q3."
- "Which product would you stop selling, and why?"
- "Which tool did you use, and why did you pick it?" (A good way to see how tool descriptions steer Claude.)

## The hosted copy

No laptop setup? Add `https://shop-data-mcp.empty-dream-9630.workers.dev/mcp` as a custom connector in claude.ai or ChatGPT. It has the three read-only tools, so the first three questions work; saving notes and the weekly review prompt need the laptop version.

Northwind Home is a fictional store. Its data is generated with a fixed seed, with one problem hidden in it on purpose.
