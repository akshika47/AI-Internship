// Check a deployed server the way Claude would use it: npx tsx scripts/check-remote.ts https://<host>/mcp
import { Client, StreamableHTTPClientTransport, type CallToolResult } from "@modelcontextprotocol/client";

const url = new URL(process.argv[2] ?? "http://localhost:8787/mcp");
const client = new Client({ name: "check-remote", version: "1.0.0" });
await client.connect(new StreamableHTTPClientTransport(url));

const text = (r: CallToolResult) => (r.content[0]?.type === "text" ? r.content[0].text : "");
const { tools } = await client.listTools();
console.log("tools:", tools.map((t) => `${t.name} ${JSON.stringify(t._meta?.ui)}`).join(" | "));
console.log("chart:", text((await client.callTool({ name: "returns_chart", arguments: {} })) as CallToolResult));
const reasons = await client.callTool({ name: "return_reasons", arguments: { product: "Aurora Glass Pendant" } });
console.log("reasons:", text(reasons as CallToolResult));
const view = await client.readResource({ uri: "ui://returns/view.html" });
const c = view.contents[0];
console.log("view:", c?.mimeType, "text" in c! ? `${c.text.length} chars` : "no text");
await client.close();
