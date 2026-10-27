// Runs the MCP server on your laptop, over HTTP at http://localhost:3001/mcp.
// The tools and the view are in app.ts. This file reads your app's folder and does the file writes, safely.

import fs from "node:fs";
import type { Server } from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { NodeStreamableHTTPServerTransport } from "@modelcontextprotocol/node";
import cors from "cors";
import express from "express";
import { createServer, VIEW_URI, type Source } from "./app.js";
import { readConfig, readItems } from "./board.js";

export { VIEW_URI };
export const ROOT = fileURLToPath(new URL("..", import.meta.url));
export const VIEW_FILE = path.join(ROOT, "dist/view/index.html");

/**
 * Load an app folder: its app.config.json and the CSV it names. Checks everything up front, so a typo shows up
 * when you run npm start, not halfway through a chat.
 */
export function loadApp(folder: string): Source {
  const dir = path.resolve(ROOT, folder);
  const configFile = path.join(dir, "app.config.json");
  if (!fs.existsSync(configFile)) throw new Error(`There's no app.config.json in ${path.relative(ROOT, dir) || "."}.`);
  const config = readConfig(fs.readFileSync(configFile, "utf-8"));

  // The CSV must sit inside the app's folder. A config can't point the app at any other file on your laptop.
  const csvFile = path.resolve(dir, config.csv);
  if (path.relative(dir, csvFile).startsWith("..") || path.isAbsolute(path.relative(dir, csvFile))) {
    throw new Error(`"csv" must be a file inside ${path.relative(ROOT, dir)}, e.g. "data.csv". Got "${config.csv}".`);
  }
  if (!fs.existsSync(csvFile)) throw new Error(`Can't find ${path.relative(ROOT, csvFile)}. Check "csv" in app.config.json.`);
  const readCsv = () => fs.readFileSync(csvFile, "utf-8");
  readItems(readCsv(), config); // fail now if a column is missing or an id repeats

  return {
    config,
    readCsv,
    writeCsv(text) {
      // Keep a copy of your original file the first time the app changes it.
      const backup = `${csvFile}.bak`;
      if (!fs.existsSync(backup)) fs.copyFileSync(csvFile, backup);
      // Write to a temporary file, then swap it in: a crash mid-write can't leave half a CSV.
      const temp = `${csvFile}.tmp`;
      fs.writeFileSync(temp, text, "utf-8");
      fs.renameSync(temp, csvFile);
    },
    viewHtml() {
      if (!fs.existsSync(VIEW_FILE)) throw new Error("The view isn't built yet. Run `npm run build` (npm start does it for you).");
      return fs.readFileSync(VIEW_FILE, "utf-8");
    },
  };
}

/** Serve the MCP server over Streamable HTTP. Port 0 picks a free port (the tests use that). */
export function startMcpServer(source: Source, port = 3001, host = "localhost"): Promise<Server> {
  const app = express();
  app.use(cors()); // the test page on another port calls us from the browser
  app.use(express.json());

  // Stateless: a fresh server for every request, so nothing is shared between callers.
  app.all("/mcp", async (req, res) => {
    const server = createServer(source);
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
