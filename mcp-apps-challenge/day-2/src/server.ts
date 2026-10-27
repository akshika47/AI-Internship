// Runs the MCP server on your laptop, over HTTP at http://localhost:3001/mcp.
// The tools and the view are defined in app.ts.

import fs from "node:fs";
import type { Server } from "node:http";
import { NodeStreamableHTTPServerTransport } from "@modelcontextprotocol/node";
import cors from "cors";
import express from "express";
import { createServer as createAppServer, VIEW_URI, type Source } from "./app.js";

export { VIEW_URI };
const DATA_FILE = new URL("../data/orders.csv", import.meta.url);
export const VIEW_FILE = new URL("../dist/view/index.html", import.meta.url);

const files: Source = {
  ordersCsv: () => fs.readFileSync(DATA_FILE, "utf-8"),
  viewHtml: () => {
    if (!fs.existsSync(VIEW_FILE)) {
      throw new Error("The view isn't built yet. Run `npm run build` (npm start does it for you).");
    }
    return fs.readFileSync(VIEW_FILE, "utf-8");
  },
};

export const createServer = () => createAppServer(files);

/** Serve the MCP server over Streamable HTTP. Port 0 picks a free port (the tests use that). */
export function startMcpServer(port = 3001, host = "localhost"): Promise<Server> {
  const app = express();
  app.use(cors()); // the test page on another port calls us from the browser
  app.use(express.json());

  // Stateless: a fresh server for every request, so nothing is shared between callers.
  app.all("/mcp", async (req, res) => {
    const server = createServer();
    const transport = new NodeStreamableHTTPServerTransport({ sessionIdGenerator: undefined });
    res.on("close", () => {
      transport.close().catch(() => {});
      server.close().catch(() => {});
    });
    try {
      await server.connect(transport);
      await transport.handleRequest(req, res, req.body);
    } catch (error) {
      console.error("MCP error:", error);
      if (!res.headersSent) res.status(500).json({ jsonrpc: "2.0", error: { code: -32603, message: "Internal server error" }, id: null });
    }
  });

  return new Promise((resolve, reject) => {
    const http = app.listen(port, host);
    http.once("listening", () => resolve(http));
    http.once("error", reject);
  });
}
