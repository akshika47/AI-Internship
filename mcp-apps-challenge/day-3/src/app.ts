// The MCP server: three tools and one view. Claude suggests, you decide in the app.
//
//   list_items     the model calls it to read your rows.
//   review_items   the model calls it with one suggestion per row. Its result opens the view.
//   set_status     only the view calls it, when you click a button. The ONLY tool that changes anything.
//   ui://board/view.html   the view itself: one HTML file, built by `npm run build` into dist/view/.

import { registerAppResource, registerAppTool, RESOURCE_MIME_TYPE } from "@modelcontextprotocol/ext-apps/server";
import { McpServer } from "@modelcontextprotocol/server";
import { z } from "zod";
import { readItems, setStatus, STATUSES, summarise, type Config, type Item } from "./board.js";

export const VIEW_URI = "ui://board/view.html";
const MAX_ROWS = 200; // more than this and the model's context fills up. Filter your CSV first

/** Where the config, the CSV and the view come from. src/server.ts reads and writes real files. */
export interface Source {
  config: Config;
  readCsv(): string;
  writeCsv(text: string): void;
  viewHtml(): string;
}

function problem(text: string) {
  return { content: [{ type: "text" as const, text }], isError: true };
}

const line = (item: Item) =>
  [item.id, ...Object.entries(item.details).map(([k, v]) => `${k}: ${v || "-"}`), `status: ${item.status}`].join(" | ");

export function createServer(source: Source): McpServer {
  const { config } = source;
  const server = new McpServer({ name: "board-app", version: "1.0.0" });
  const items = () => readItems(source.readCsv(), config);

  // 1. The model reads the rows. Plain text, no view.
  server.registerTool(
    "list_items",
    {
      title: `List ${config.title}`,
      description:
        `Lists the rows of the user's "${config.title}" with their status (to review, approved or skipped). ` +
        `Call this first, then call review_items with one suggestion per row.`,
      inputSchema: z.object({
        status: z.enum(["to review", "approved", "skipped", "all"]).default("to review").describe("Which rows to list."),
      }),
      annotations: { readOnlyHint: true },
    },
    async ({ status }) => {
      const all = items();
      const rows = all.filter((i) => status === "all" || i.status === status);
      const shown = rows.slice(0, MAX_ROWS);
      const text = [
        `${config.title}: ${rows.length} row(s) with status "${status}", out of ${all.length}.`,
        ...shown.map(line),
        rows.length > shown.length ? `(Only the first ${MAX_ROWS} are listed.)` : "",
        `Next: call review_items with one short suggestion per row. ${config.ask}`,
      ].filter(Boolean);
      return { content: [{ type: "text", text: text.join("\n") }], structuredContent: { items: shown } };
    },
  );

  // 2. The model shows its suggestions in the app. The user decides there, not the model.
  registerAppTool(
    server,
    "review_items",
    {
      title: `Review ${config.title}`,
      description:
        `Opens "${config.title}" as an app where the user approves or skips each row. ` +
        `Pass one short suggestion per row, using the id from list_items. ${config.ask} ` +
        `Never claim a row is approved: only the user can approve, in the app.`,
      inputSchema: z.object({
        suggestions: z
          .array(z.object({ id: z.string().max(200), suggestion: z.string().max(300) }))
          .max(MAX_ROWS)
          .default([])
          .describe("One suggestion per row id, e.g. {\"id\": \"...\", \"suggestion\": \"Apply: strong fit.\"}")
          .meta({ examples: [config.sample] }),
      }),
      annotations: { readOnlyHint: true },
      _meta: { ui: { resourceUri: VIEW_URI } },
    },
    async ({ suggestions }) => {
      const all = items().slice(0, MAX_ROWS);
      const ids = new Set(all.map((i) => i.id));
      const unknown = suggestions.filter((s) => !ids.has(s.id)).map((s) => s.id);
      const by = new Map(suggestions.map((s) => [s.id, s.suggestion]));
      const shown = all.map((i) => ({ ...i, suggestion: by.get(i.id) ?? "" }));
      const toReview = shown.filter((i) => i.status === "to review").length;
      const text = [
        `Showing ${shown.length} row(s) of "${config.title}" to the user, ${toReview} still to review. ` +
          `They approve or skip each one in the app, and you'll see their choices.`,
        unknown.length ? `These ids aren't in the CSV, so their suggestions weren't shown: ${unknown.join("; ")}. Use the ids from list_items.` : "",
      ].filter(Boolean);
      return {
        content: [{ type: "text", text: text.join("\n") }],
        structuredContent: { title: config.title, approve: config.approve, skip: config.skip, details: config.details, items: shown },
      };
    },
  );

  // 3. The one write. Only the view calls it, and it can only change the status cell of a row that exists.
  //    visibility ["app"] hides it from the model, but anyone who can reach this server can call it: it is NOT a
  //    security boundary. That's why it accepts so little: a row id that must exist, and one of three statuses.
  registerAppTool(
    server,
    "set_status",
    {
      title: "Set status",
      description: "Sets one row's status. Called by the app when the user clicks a button.",
      inputSchema: z.object({
        id: z.string().min(1).max(200),
        status: z.enum(STATUSES),
      }),
      annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: true },
      _meta: { ui: { resourceUri: VIEW_URI, visibility: ["app"] } },
    },
    async ({ id, status }) => {
      try {
        source.writeCsv(setStatus(source.readCsv(), config, id, status));
      } catch (error) {
        return problem((error as Error).message);
      }
      const now = items();
      return { content: [{ type: "text", text: summarise(now, config) }], structuredContent: { items: now } };
    },
  );

  // 4. The view. No _meta.ui.csp, so it can't load anything from the internet.
  registerAppResource(server, "Board view", VIEW_URI, { mimeType: RESOURCE_MIME_TYPE }, async () => ({
    contents: [{ uri: VIEW_URI, mimeType: RESOURCE_MIME_TYPE, text: source.viewHtml() }],
  }));

  return server;
}
