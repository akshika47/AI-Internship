/**
 * Hosted, read-only copy of the workshop server on Cloudflare Workers + D1.
 * Same three read-only tools, SQL and prompt as src/shop_data/server.py (FastMCP); only the
 * wiring differs: D1 instead of a sqlite3 file, and createMcpHandler instead of mcp.run().
 * Stateless (MCP 2026-07-28): one server per request, no session to keep.
 */
import { McpServer } from "@modelcontextprotocol/server";
import { createMcpHandler } from "agents/mcp/server";
import { z } from "zod";

// Env (DB, LIMITER) is generated from wrangler.jsonc by `npx wrangler types`.
type Row = Record<string, unknown>;

/** A mistake the model can fix: returned as an MCP tool error (isError: true), not a crash. */
class ToolError extends Error {}

const CATEGORY_HINT = 'Kitchen, Bedding, Lighting, Decor or Bath. Example: "Lighting".';
const QUARTER_HINT = 'year, dash, Q and 1 to 4. Example: "2026-Q3".';

const ok = (data: unknown) => ({ content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }] });
const fail = (message: string) => ({ content: [{ type: "text" as const, text: message }], isError: true });

/** Run a tool body; ToolError becomes a readable tool error, anything else is logged and hidden. */
async function guarded(name: string, body: () => Promise<unknown>) {
	try {
		return ok(await body());
	} catch (e) {
		if (e instanceof ToolError) return fail(e.message);
		console.error(`${name} failed`, e);
		return fail(`${name} hit an internal error. Try again, or tell the user the server is having trouble.`);
	}
}

async function checkCategory(db: D1Database, category: string): Promise<string> {
	const { results } = await db.prepare("SELECT name FROM categories ORDER BY category_id").all<{ name: string }>();
	const names = results.map((r) => r.name);
	const match = names.find((n) => n.toLowerCase() === category.trim().toLowerCase());
	if (!match) throw new ToolError(`Unknown category '${category}'. Use one of: ${names.join(", ")}.`);
	return match;
}

/** '2026-Q3' -> ['2026-07-01', '2026-10-01']: start and the day after the end. */
function quarterRange(quarter: string): [string, string] {
	const m = /^(\d{4})-Q([1-4])$/.exec(quarter.trim().toUpperCase());
	if (!m) throw new ToolError(`'${quarter}' is not a valid quarter. Use the form 2026-Q3 (year, dash, Q, 1 to 4).`);
	const year = Number(m[1]);
	const q = Number(m[2]);
	const pad = (n: number) => String(n).padStart(2, "0");
	const start = `${year}-${pad(3 * q - 2)}-01`;
	const end = q === 4 ? `${year + 1}-01-01` : `${year}-${pad(3 * q + 1)}-01`;
	return [start, end];
}

function previousQuarter(quarter: string): string {
	const year = Number(quarter.slice(0, 4));
	const q = Number(quarter.slice(-1));
	return q === 1 ? `${year - 1}-Q4` : `${year}-Q${q - 1}`;
}

const round1 = (x: number) => Math.round(x * 10) / 10;

interface CategoryReturns {
	items: number;
	returned: number;
	top_reason?: string;
	top_reason_count?: number;
}

/** Items sold, items returned and the most common reason, per category (cancelled orders ignored). */
async function returnsByCategory(db: D1Database, quarter: string): Promise<Map<string, CategoryReturns>> {
	const [start, end] = quarterRange(quarter);
	const [counts, reasons] = await db.batch<Row>([
		db
			.prepare(
				`SELECT c.name AS category, COUNT(*) AS items, COUNT(r.return_id) AS returned
				 FROM order_items i
				 JOIN orders o ON o.order_id = i.order_id
				 JOIN products p ON p.product_id = i.product_id
				 JOIN categories c ON c.category_id = p.category_id
				 LEFT JOIN returns r ON r.order_item_id = i.order_item_id
				 WHERE o.status <> 'cancelled' AND o.order_date >= ? AND o.order_date < ?
				 GROUP BY c.name`,
			)
			.bind(start, end),
		db
			.prepare(
				`SELECT c.name AS category, r.reason, COUNT(*) AS n
				 FROM returns r
				 JOIN order_items i ON i.order_item_id = r.order_item_id
				 JOIN orders o ON o.order_id = i.order_id
				 JOIN products p ON p.product_id = i.product_id
				 JOIN categories c ON c.category_id = p.category_id
				 WHERE o.status <> 'cancelled' AND o.order_date >= ? AND o.order_date < ?
				 GROUP BY c.name, r.reason ORDER BY n DESC, r.reason`,
			)
			.bind(start, end),
	]);
	const out = new Map<string, CategoryReturns>();
	for (const r of counts.results) out.set(String(r.category), { items: Number(r.items), returned: Number(r.returned) });
	// Rows come biggest first, so the first one per category is the top reason.
	for (const r of reasons.results) {
		const c = out.get(String(r.category));
		if (c && c.top_reason === undefined) {
			c.top_reason = String(r.reason);
			c.top_reason_count = Number(r.n);
		}
	}
	return out;
}

function createServer(env: Env) {
	const server = new McpServer({ name: "shop-data", version: "1.0.0" });
	const db = env.DB;

	server.registerTool(
		"sales_by_month",
		{
			description:
				"Revenue and order count for each of the most recent months, newest last. Cancelled orders are left out.\n\n" +
				`category: ${CATEGORY_HINT} Leave empty for all.\nmonths: how many months to show, from 1 to 15. Example: 6.`,
			inputSchema: z.object({ category: z.string().optional(), months: z.number().int().default(6) }),
			annotations: { readOnlyHint: true },
		},
		({ category, months }) =>
			guarded("sales_by_month", async () => {
				if (months < 1 || months > 15)
					throw new ToolError("months must be a whole number from 1 to 15 (the data covers 15 months).");
				const cat = category === undefined ? null : await checkCategory(db, category);
				const { results } = await db
					.prepare(
						`SELECT substr(o.order_date, 1, 7) AS month,
						        ROUND(SUM(i.quantity * i.price), 2) AS revenue,
						        COUNT(DISTINCT o.order_id) AS orders
						 FROM order_items i
						 JOIN orders o ON o.order_id = i.order_id
						 JOIN products p ON p.product_id = i.product_id
						 JOIN categories c ON c.category_id = p.category_id
						 WHERE o.status <> 'cancelled' AND (?1 IS NULL OR c.name = ?1)
						 GROUP BY month ORDER BY month DESC LIMIT ?2`,
					)
					.bind(cat, months)
					.all();
				return results.reverse();
			}),
	);

	server.registerTool(
		"top_products",
		{
			description:
				"The five products with most revenue in a category in one quarter, with how many were returned.\n\n" +
				`category: ${CATEGORY_HINT}\nquarter: ${QUARTER_HINT}`,
			inputSchema: z.object({ category: z.string(), quarter: z.string() }),
			annotations: { readOnlyHint: true },
		},
		({ category, quarter }) =>
			guarded("top_products", async () => {
				const [start, end] = quarterRange(quarter);
				const cat = await checkCategory(db, category);
				const { results } = await db
					.prepare(
						`SELECT p.name AS product,
						        ROUND(SUM(i.quantity * i.price), 2) AS revenue,
						        SUM(i.quantity) AS units,
						        COUNT(r.return_id) AS returned_items,
						        ROUND(100.0 * COUNT(r.return_id) / COUNT(*), 1) AS return_rate_pct
						 FROM order_items i
						 JOIN orders o ON o.order_id = i.order_id
						 JOIN products p ON p.product_id = i.product_id
						 JOIN categories c ON c.category_id = p.category_id
						 LEFT JOIN returns r ON r.order_item_id = i.order_item_id
						 WHERE c.name = ? AND o.status <> 'cancelled' AND o.order_date >= ? AND o.order_date < ?
						 GROUP BY p.product_id ORDER BY revenue DESC LIMIT 5`,
					)
					.bind(cat, start, end)
					.all();
				if (results.length === 0)
					throw new ToolError(`No sales for ${cat} in ${quarter}. The data covers 2025-Q3 to 2026-Q3.`);
				return results;
			}),
	);

	server.registerTool(
		"return_rates",
		{
			description:
				"Each category's return rate against the quarter before it, biggest rise first.\n\n" +
				`quarter: ${QUARTER_HINT} Needs the previous quarter in the data.\n` +
				"Rate = items returned / items sold, by order date. Also shows the most common return reason.",
			inputSchema: z.object({ quarter: z.string() }),
			annotations: { readOnlyHint: true },
		},
		({ quarter }) =>
			guarded("return_rates", async () => {
				const q = quarter.trim().toUpperCase();
				quarterRange(q); // checks the format
				const before = previousQuarter(q);
				const [now, prev] = await Promise.all([returnsByCategory(db, q), returnsByCategory(db, before)]);
				if (now.size === 0) throw new ToolError(`No orders in ${q}. The data covers 2025-Q3 to 2026-Q3.`);
				if (prev.size === 0)
					throw new ToolError(
						`There is no data for the previous quarter (${before}), so nothing to compare with. Try 2025-Q4 or later.`,
					);
				const result = [...now].map(([category, n]) => {
					const p = prev.get(category);
					const rate = round1((100 * n.returned) / n.items);
					const prevRate = p ? round1((100 * p.returned) / p.items) : null;
					return {
						category,
						previous_quarter: before,
						previous_rate_pct: prevRate,
						rate_pct: rate,
						change_pts: prevRate !== null ? round1(rate - prevRate) : null,
						items_sold: n.items,
						items_returned: n.returned,
						top_reason: n.top_reason ?? null,
						top_reason_share_pct: n.returned ? round1((100 * (n.top_reason_count ?? 0)) / n.returned) : null,
					};
				});
				return result.sort((a, b) => (b.change_pts ?? 0) - (a.change_pts ?? 0));
			}),
	);

	server.registerPrompt(
		"weekly_business_review",
		{
			description: "Weekly business review: find the return spike, trace it to a product, draft a 5-line note.",
			argsSchema: z.object({ quarter: z.string().describe(QUARTER_HINT) }),
		},
		({ quarter }) => ({
			messages: [
				{
					role: "user" as const,
					content: {
						type: "text" as const,
						text: `Run the weekly business review for Northwind Home (a fictional homeware store) for ${quarter}.

1. Call sales_by_month for the last 6 months to see whether revenue is growing overall.
2. Call return_rates for ${quarter} and identify the categories whose return rate rose the most.
3. For each category with a big rise, call top_products for that category in ${quarter} and in the quarter before it. Find the product behind the rise and explain it in plain English: its return rate, its share of the category's returns, and the most common reason.
4. Draft a note of exactly 5 lines: the headline number, the category, the product, the reason, and one suggested next step.
5. Show me the draft. (This hosted copy is read-only, so it cannot save notes.)
Use only numbers returned by the tools. If a tool returns an error, tell me what it said instead of guessing.`,
					},
				},
			],
		}),
	);

	return server;
}

export default {
	async fetch(request: Request, env: Env, ctx: ExecutionContext) {
		const url = new URL(request.url);
		if (url.pathname === "/") return new Response("shop-data MCP server. Connect an MCP client to /mcp.\n");
		{
			// Authless server, so the caller's IP is the only key we have.
			const key = request.headers.get("cf-connecting-ip") ?? "local";
			const { success } = await env.LIMITER.limit({ key });
			if (!success) return new Response("Too many requests. Try again in a minute.", { status: 429 });
		}
		return createMcpHandler(() => createServer(env))(request, env, ctx);
	},
} satisfies ExportedHandler<Env>;
