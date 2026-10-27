// The MCP server itself: two tools and one UI resource. No Node-only code here, so the same
// server runs on your laptop (src/server.ts) and on Cloudflare Workers (worker/worker.ts).
//
//   returns_chart   the model calls it. Its result carries a sentence for the model AND a link to the view.
//   return_reasons  only the view calls it (when you click "Show the reasons").
//   ui://returns/view.html   the view itself: one HTML file, built by `npm run build` into dist/view/.

import { registerAppResource, registerAppTool, RESOURCE_MIME_TYPE } from "@modelcontextprotocol/ext-apps/server";
import { McpServer } from "@modelcontextprotocol/server";
import { z } from "zod";
import { listChoices, normaliseQuarter, readOrders, reasonsFor, returnsByProduct, summarise, type Order } from "./returns.js";

export const VIEW_URI = "ui://returns/view.html";

/** Where the data and the view come from: files on your laptop, or text bundled into the Worker. */
export interface Source {
  ordersCsv(): string;
  viewHtml(): string;
}

// A tool error the model can read and fix. isError tells the host the call failed.
function problem(text: string) {
  return { content: [{ type: "text" as const, text }], isError: true };
}

/** Match a category or quarter against what's really in the data, or explain what's allowed. */
function check(orders: () => Order[], category: string, quarter: string): { category: string; quarter: string } | string {
  const { categories, quarters } = listChoices(orders());
  const cat = categories.find((c) => c.toLowerCase() === category.trim().toLowerCase());
  if (!cat) return `Unknown category "${category}". Use one of: ${categories.join(", ")}.`;
  const q = normaliseQuarter(quarter);
  if (!q) return `"${quarter}" is not a quarter. Write it like 2026-Q3 (year, dash, Q, 1 to 4).`;
  if (!quarters.includes(q)) return `There is no data for ${q}. Use one of: ${quarters.join(", ")}.`;
  return { category: cat, quarter: q };
}

export function createServer(source: Source): McpServer {
  // Read the CSV once, the first time a tool needs it.
  let cache: Order[] | undefined;
  const orders = () => (cache ??= readOrders(source.ordersCsv()));

  const server = new McpServer({ name: "returns-app", version: "1.0.0" });

  // 1. The tool the model sees. _meta.ui.resourceUri says "show this view with my result".
  registerAppTool(
    server,
    "returns_chart",
    {
      title: "Returns chart",
      description:
        "Shows which products were returned most in one category and quarter, as an interactive bar chart. " +
        "Also returns a one-sentence summary. Categories: Kitchen, Bedding, Lighting, Decor, Bath. Quarters: 2025-Q3 to 2026-Q3.",
      inputSchema: z.object({
        category: z.string().max(60).default("Lighting").describe('A product category, e.g. "Lighting".'),
        quarter: z.string().max(20).default("2026-Q3").describe('Year, dash, Q and 1 to 4, e.g. "2026-Q3".'),
      }),
      annotations: { readOnlyHint: true },
      _meta: { ui: { resourceUri: VIEW_URI } },
    },
    async (input) => {
      const ok = check(orders, input.category, input.quarter);
      if (typeof ok === "string") return problem(ok);
      const result = returnsByProduct(orders(), ok.category, ok.quarter);
      const { total, rows } = result;
      return {
        // content: what the MODEL reads. Works even in an app that can't show the view.
        content: [{ type: "text", text: summarise(result) }],
        // structuredContent: the data the VIEW draws.
        structuredContent: { category: ok.category, quarter: ok.quarter, total, rows },
      };
    },
  );

  // 2. A tool only the view calls. visibility ["app"] asks the host to hide it from the model.
  //    It is still listed on the wire and anyone connected can call it: it is NOT a security boundary.
  registerAppTool(
    server,
    "return_reasons",
    {
      title: "Return reasons",
      description: "Why one product was returned, with a count per reason. Called by the returns chart view.",
      inputSchema: z.object({
        product: z.string().min(1, "Give a product name, e.g. Aurora Glass Pendant.").max(100).describe('A product name, e.g. "Aurora Glass Pendant".'),
        category: z.string().max(60).default("Lighting"),
        quarter: z.string().max(20).default("2026-Q3"),
      }),
      annotations: { readOnlyHint: true },
      _meta: { ui: { resourceUri: VIEW_URI, visibility: ["app"] } },
    },
    async (input) => {
      const ok = check(orders, input.category, input.quarter);
      if (typeof ok === "string") return problem(ok);
      const products = returnsByProduct(orders(), ok.category, ok.quarter).rows.map((r) => r.product);
      const product = products.find((p) => p.toLowerCase() === input.product.trim().toLowerCase());
      if (!product) {
        return problem(`No product "${input.product}" in ${ok.category} for ${ok.quarter}. Use one of: ${products.join(", ")}.`);
      }
      const result = reasonsFor(orders(), product, ok.category, ok.quarter);
      const list = result.reasons.map((r) => `${r.reason} ${r.count}`).join(", ");
      const text =
        result.total === 0
          ? `${product} had no returns in ${ok.quarter}.`
          : `${product} (${ok.category}, ${ok.quarter}): ${result.total} returns. ${list}.`;
      return { content: [{ type: "text", text }], structuredContent: result };
    },
  );

  // 3. The view. The host reads this resource and shows it in a sandboxed iframe.
  //    We declare no outside domains (no _meta.ui.csp), so the view can't load anything from the internet.
  registerAppResource(server, "Returns chart view", VIEW_URI, { mimeType: RESOURCE_MIME_TYPE }, async () => {
    return { contents: [{ uri: VIEW_URI, mimeType: RESOURCE_MIME_TYPE, text: source.viewHtml() }] };
  });

  return server;
}
