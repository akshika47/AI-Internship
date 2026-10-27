// The same MCP server as src/server.ts, hosted on Cloudflare Workers so anyone can add it to Claude
// as a custom connector: https://<your-worker>.workers.dev/mcp
// The CSV and the built view are bundled into the Worker as text (see the rules in wrangler.jsonc).

import { createMcpHandler } from "@modelcontextprotocol/server";
import ordersCsv from "../data/orders.csv";
import viewHtml from "../dist/view/index.html";
import { createServer } from "../src/app.js";

const mcp = createMcpHandler(() => createServer({ ordersCsv: () => ordersCsv, viewHtml: () => viewHtml }));

export default {
  async fetch(request: Request): Promise<Response> {
    const { pathname } = new URL(request.url);
    if (pathname === "/mcp") return mcp.fetch(request);
    return new Response("Returns chart MCP App. Add https://<this host>/mcp to Claude as a custom connector.\n", {
      headers: { "content-type": "text/plain; charset=utf-8" },
    });
  },
};
