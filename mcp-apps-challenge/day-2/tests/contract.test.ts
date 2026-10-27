// The contract with a host: start the real server on a free port and talk to it with a real MCP client over HTTP.
// Needs the view built first (`npm test` does that).
import type { AddressInfo } from "node:net";
import type { Server } from "node:http";
import { Client, StreamableHTTPClientTransport, type CallToolResult } from "@modelcontextprotocol/client";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { startMcpServer } from "../src/server.js";

let http: Server;
let client: Client;

beforeAll(async () => {
  http = await startMcpServer(0); // 0 = any free port
  const port = (http.address() as AddressInfo).port;
  client = new Client({ name: "contract-test", version: "1.0.0" });
  await client.connect(new StreamableHTTPClientTransport(new URL(`http://localhost:${port}/mcp`)));
});

afterAll(async () => {
  await client?.close();
  http?.close();
});

const call = async (name: string, args: Record<string, unknown>) =>
  (await client.callTool({ name, arguments: args })) as CallToolResult;
const text = (r: CallToolResult) => (r.content[0]?.type === "text" ? r.content[0].text : "");

describe("tools/list", () => {
  it("lists returns_chart with a link to the view", async () => {
    const { tools } = await client.listTools();
    const chart = tools.find((t) => t.name === "returns_chart");
    expect(chart?._meta?.ui).toMatchObject({ resourceUri: "ui://returns/view.html" });
    expect(chart?.annotations?.readOnlyHint).toBe(true);
  });

  it("marks return_reasons as app-only (it is still listed: hosts do the hiding)", async () => {
    const { tools } = await client.listTools();
    const reasons = tools.find((t) => t.name === "return_reasons");
    expect(reasons?._meta?.ui).toMatchObject({ visibility: ["app"] });
  });
});

describe("returns_chart", () => {
  it("returns the three parts: content for the model, structuredContent for the view, and the view link on the tool", async () => {
    const result = await call("returns_chart", {});
    expect(result.isError).toBeFalsy();
    expect(text(result)).toBe(
      "Lighting had 92 returns in 2026-Q3 out of 318 items sold (28.9%). Aurora Glass Pendant had the most: 77 of 96 sold (80.2%).",
    );
    const data = result.structuredContent as { category: string; quarter: string; total: number; rows: { product: string }[] };
    expect(data).toMatchObject({ category: "Lighting", quarter: "2026-Q3", total: 92 });
    expect(data.rows[0]).toEqual({ product: "Aurora Glass Pendant", returned: 77, sold: 96, rate: 80.2 });
    // The view link lives on the tool definition, so the host knows which view to open before the call.
    const { tools } = await client.listTools();
    expect(tools.find((t) => t.name === "returns_chart")?._meta?.ui).toMatchObject({ resourceUri: "ui://returns/view.html" });
  });

  it("accepts lower case and spaces", async () => {
    const result = await call("returns_chart", { category: " lighting ", quarter: "2026-q3" });
    expect(result.structuredContent).toMatchObject({ category: "Lighting", quarter: "2026-Q3", total: 92 });
  });

  it("explains an unknown category", async () => {
    const result = await call("returns_chart", { category: "Garden" });
    expect(result.isError).toBe(true);
    expect(text(result)).toBe('Unknown category "Garden". Use one of: Bath, Bedding, Decor, Kitchen, Lighting.');
  });

  it("explains a badly written quarter", async () => {
    const result = await call("returns_chart", { quarter: "Q3 2026" });
    expect(result.isError).toBe(true);
    expect(text(result)).toBe('"Q3 2026" is not a quarter. Write it like 2026-Q3 (year, dash, Q, 1 to 4).');
  });

  it("explains a quarter with no data, listing the ones that have it", async () => {
    const result = await call("returns_chart", { quarter: "2024-Q1" });
    expect(result.isError).toBe(true);
    expect(text(result)).toBe("There is no data for 2024-Q1. Use one of: 2025-Q3, 2025-Q4, 2026-Q1, 2026-Q2, 2026-Q3.");
  });
});

describe("return_reasons", () => {
  it("gives the reasons with counts", async () => {
    const result = await call("return_reasons", { product: "Aurora Glass Pendant" });
    expect(result.isError).toBeFalsy();
    expect(text(result)).toBe("Aurora Glass Pendant (Lighting, 2026-Q3): 77 returns. damaged 74, wrong size 3.");
    expect(result.structuredContent).toMatchObject({
      total: 77,
      reasons: [{ reason: "damaged", count: 74 }, { reason: "wrong size", count: 3 }],
    });
  });

  it("explains an unknown product, listing the real ones", async () => {
    const result = await call("return_reasons", { product: "Flying Carpet" });
    expect(result.isError).toBe(true);
    expect(text(result)).toMatch(/^No product "Flying Carpet" in Lighting for 2026-Q3\. Use one of: Aurora Glass Pendant, /);
  });

  it("refuses an empty product name", async () => {
    const result = await call("return_reasons", { product: "" });
    expect(result.isError).toBe(true);
    expect(text(result)).toContain("Give a product name, e.g. Aurora Glass Pendant.");
  });
});

describe("the view resource", () => {
  it("is an MCP App HTML file that loads nothing from the internet", async () => {
    const { contents } = await client.readResource({ uri: "ui://returns/view.html" });
    expect(contents).toHaveLength(1);
    expect(contents[0].mimeType).toBe("text/html;profile=mcp-app");
    const html = "text" in contents[0] ? contents[0].text : "";
    expect(html).toContain("<title>Returns chart</title>");
    // No external scripts, styles, images or fonts. (The bundled library contains URLs as plain strings,
    // like JSON Schema ids, so we look for places a URL would be LOADED from, not for the text "http".)
    expect(html).not.toMatch(/<script[^>]+src=/i);
    expect(html).not.toMatch(/<link[^>]+href=/i);
    expect(html).not.toMatch(/(src|href)\s*=\s*["']?https?:/i);
    expect(html).not.toMatch(/url\(\s*["']?https?:/i);
    expect(html).not.toMatch(/@import/i);
  });

  it("declares no outside domains", async () => {
    const { contents } = await client.readResource({ uri: "ui://returns/view.html" });
    expect((contents[0]._meta as { ui?: { csp?: unknown } } | undefined)?.ui?.csp).toBeUndefined();
  });
});
