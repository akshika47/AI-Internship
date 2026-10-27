// Serves the test page (port 8080) and the sandbox proxy (port 8081).
// Two ports = two origins: the view runs on 8081 and can't touch the page on 8080. Claude and ChatGPT do the same.

import type { AddressInfo } from "node:net";
import type { Server } from "node:http";
import { fileURLToPath } from "node:url";
import express from "express";

const BUILT_PAGE = fileURLToPath(new URL("../dist/host/", import.meta.url));
const SANDBOX_FILE = fileURLToPath(new URL("./sandbox.html", import.meta.url));

// The view declared no outside domains, so it gets none: only inline code, and nothing from the internet.
const CSP = [
  "default-src 'self' 'unsafe-inline'",
  "script-src 'self' 'unsafe-inline'",
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data: blob:",
  "font-src 'self' data:",
  "connect-src 'self'",
  "frame-src 'none'",
  "object-src 'none'",
  "base-uri 'none'",
].join("; ");

function listen(app: express.Express, port: number, host: string): Promise<Server> {
  return new Promise((resolve, reject) => {
    const server = app.listen(port, host);
    server.once("listening", () => resolve(server));
    server.once("error", reject);
  });
}

const portOf = (server: Server) => (server.address() as AddressInfo).port;

export async function startTestPage(opts: { mcpUrl: string; port?: number; sandboxPort?: number; host?: string }) {
  const host = opts.host ?? "localhost";

  const sandbox = express();
  sandbox.get(["/", "/sandbox.html"], (_req, res) => {
    res.setHeader("Content-Security-Policy", CSP);
    res.setHeader("Cache-Control", "no-store");
    res.sendFile(SANDBOX_FILE);
  });
  const sandboxServer = await listen(sandbox, opts.sandboxPort ?? 8081, host);
  const sandboxUrl = `http://${host}:${portOf(sandboxServer)}/sandbox.html`;

  const page = express();
  page.get("/api/config", (_req, res) => res.json({ mcpUrl: opts.mcpUrl, sandboxUrl }));
  page.use(express.static(BUILT_PAGE));
  const pageServer = await listen(page, opts.port ?? 8080, host).catch((error) => {
    sandboxServer.close(); // don't leave half of it running
    throw error;
  });

  return { url: `http://${host}:${portOf(pageServer)}`, servers: [pageServer, sandboxServer] };
}
