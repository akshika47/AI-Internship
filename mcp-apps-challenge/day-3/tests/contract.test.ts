// The contract with a host: start the real server on a copy of an example app and talk to it over HTTP.
// Needs the view built first (`npm test` does that).
import fs from "node:fs";
import type { Server } from "node:http";
import type { AddressInfo } from "node:net";
import os from "node:os";
import path from "node:path";
import { Client, StreamableHTTPClientTransport, type CallToolResult } from "@modelcontextprotocol/client";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { loadApp, ROOT, startMcpServer } from "../src/server.js";

let dir: string;
let http: Server;
let client: Client;

beforeAll(async () => {
  dir = fs.mkdtempSync(path.join(os.tmpdir(), "board-")); // a copy, so the tests never change the examples
  fs.cpSync(path.join(ROOT, "examples/job-board"), dir, { recursive: true });
  http = await startMcpServer(loadApp(dir), 0);
  client = new Client({ name: "contract-test", version: "1.0.0" });
  await client.connect(new StreamableHTTPClientTransport(new URL(`http://localhost:${(http.address() as AddressInfo).port}/mcp`)));
});

afterAll(async () => {
  await client?.close();
  http?.close();
  fs.rmSync(dir, { recursive: true, force: true });
});

const call = async (name: string, args: Record<string, unknown>) => (await client.callTool({ name, arguments: args })) as CallToolResult;
const text = (r: CallToolResult) => (r.content[0]?.type === "text" ? r.content[0].text : "");
const csv = () => fs.readFileSync(path.join(dir, "applications.csv"), "utf-8");
const BRIGHTPATH = "Operations & AI Associate, Brightpath Logistics";

describe("tools/list", () => {
  it("links review_items to the view and hides set_status from the model", async () => {
    const { tools } = await client.listTools();
    const by = Object.fromEntries(tools.map((t) => [t.name, t]));
    expect(Object.keys(by).sort()).toEqual(["list_items", "review_items", "set_status"]);
    expect(by.review_items!._meta?.ui).toEqual({ resourceUri: "ui://board/view.html" });
    expect(by.set_status!._meta?.ui).toMatchObject({ visibility: ["app"] });
    expect(by.list_items!.annotations?.readOnlyHint).toBe(true);
    expect(by.set_status!.annotations?.readOnlyHint).toBe(false);
  });
  it("puts the config's ask in review_items' description, for the model", async () => {
    const { tools } = await client.listTools();
    expect(tools.find((t) => t.name === "review_items")!.description).toContain("suggest apply or skip");
  });
});

describe("list_items", () => {
  it("gives the model every row to review, one per line, and what to do next", async () => {
    const r = await call("list_items", {});
    expect(text(r)).toContain("6 row(s) with status \"to review\", out of 6");
    expect(text(r)).toContain(`${BRIGHTPATH} | fit_score: 9 | decision: Apply now`);
    expect(text(r)).toContain("Next: call review_items");
  });
});

describe("review_items", () => {
  it("attaches suggestions to rows and reports ids it doesn't know", async () => {
    const r = await call("review_items", { suggestions: [{ id: BRIGHTPATH, suggestion: "Apply." }, { id: "Made up", suggestion: "?" }] });
    const board = r.structuredContent as { approve: string; items: { id: string; suggestion: string }[] };
    expect(board.approve).toBe("Apply");
    expect(board.items.find((i) => i.id === BRIGHTPATH)!.suggestion).toBe("Apply.");
    expect(text(r)).toContain("These ids aren't in the CSV");
    expect(text(r)).toContain("Made up");
  });
});

describe("set_status", () => {
  it("writes one cell, keeps a backup of the original, and returns a summary", async () => {
    const before = csv();
    const r = await call("set_status", { id: BRIGHTPATH, status: "approved" });
    expect(r.isError).toBeFalsy();
    expect(text(r)).toContain(`Apply (1): ${BRIGHTPATH}.`);
    expect(csv()).toContain(`"${BRIGHTPATH}",9,Apply now,Asks for Python and process automation. Hybrid in Leeds.,approved`);
    expect(fs.readFileSync(path.join(dir, "applications.csv.bak"), "utf-8")).toBe(before);
    expect(fs.existsSync(path.join(dir, "applications.csv.tmp"))).toBe(false);
  });
  it("refuses an unknown row and an unknown status without touching the file", async () => {
    const before = csv();
    expect((await call("set_status", { id: "Made up", status: "approved" })).isError).toBe(true);
    expect((await call("set_status", { id: BRIGHTPATH, status: "deleted" })).isError).toBe(true);
    expect(csv()).toBe(before);
  });
});

describe("loadApp", () => {
  it("refuses a config whose csv points outside the app folder", () => {
    const bad = fs.mkdtempSync(path.join(os.tmpdir(), "board-bad-"));
    fs.writeFileSync(path.join(bad, "app.config.json"), JSON.stringify({ title: "x", csv: "../secrets.csv", id: "a", ask: "?" }));
    expect(() => loadApp(bad)).toThrow(/must be a file inside/);
    fs.rmSync(bad, { recursive: true, force: true });
  });
  it("loads all three examples", () => {
    for (const name of ["job-board", "weekly-numbers", "todo-from-notes"]) {
      expect(loadApp(path.join(ROOT, "examples", name)).config.title).toBeTruthy();
    }
  });
});

it("serves the view as one MCP App HTML file", async () => {
  const { contents } = await client.readResource({ uri: "ui://board/view.html" });
  expect(contents[0]).toMatchObject({ mimeType: "text/html;profile=mcp-app" });
  expect("text" in contents[0]! && contents[0].text).toContain("Claude suggests, you decide");
});
