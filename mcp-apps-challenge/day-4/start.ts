// `npm start` runs this after building: the MCP server on 3001 and the test page on 8080 (+ its sandbox on 8081).
// `npm start examples/weekly-numbers` runs another app folder. With no folder, it runs examples/job-board.
// `npm run share my-app` also opens a Cloudflare tunnel, so Claude can reach your laptop, and prints the
// connector URL to paste into Claude. Neither needs "--", which some editors turn into "–" when you paste.
import { spawn } from "node:child_process";
import fs from "node:fs";
import type { AddressInfo } from "node:net";
import { startTestPage } from "./host/serve.js";
import { connectorSecret, loadApp, startMcpServer, VIEW_FILE } from "./src/server.js";

const HOST = "localhost"; // the same name everywhere, so IPv4/IPv6 can't split them
const args = process.argv.slice(2).map((a) => a.replace(/^[–—]/, "--")); // "–share" pasted from a post still works
const share = args.includes("--share");
const folder = args.find((a) => !a.startsWith("-")) ?? "examples/job-board";

if (!fs.existsSync(VIEW_FILE)) {
  console.error("The view isn't built yet. Run `npm start` (it builds first) or `npm run build`.");
  process.exit(1);
}

try {
  const source = loadApp(folder);
  const mcpPath = `/mcp/${connectorSecret()}`;
  const mcp = await startMcpServer(source, 3001, HOST, mcpPath);
  const page = await startTestPage({ mcpUrl: `http://${HOST}:3001${mcpPath}`, port: 8080, sandboxPort: 8081, host: HOST });
  console.log(`
  App          ${source.config.title} (${folder})
  Test page    ${page.url}   <- open this
${share ? "" : "\n  To use it in Claude: stop this (Ctrl+C) and run  npm run share " + folder + "\n"}
  Press Ctrl+C to stop.
`);
  if (share) openTunnel(mcp.address() as AddressInfo, mcpPath);
} catch (error) {
  const e = error as NodeJS.ErrnoException & { port?: number };
  if (e.code === "EADDRINUSE") {
    console.error(`Port ${e.port} is already in use. Is npm start already running in another terminal? Stop it with Ctrl+C.`);
  } else {
    console.error(e.message ?? error);
  }
  process.exit(1);
}

/**
 * A Cloudflare quick tunnel: a temporary https address that forwards to your laptop. No account needed. It
 * lasts until you press Ctrl+C, and you get a new address each time.
 */
function openTunnel(address: AddressInfo, mcpPath: string) {
  // Point the tunnel at the exact address the server took (::1 or 127.0.0.1), not "localhost", which can differ.
  const target = address.family === "IPv6" ? `http://[${address.address}]:${address.port}` : `http://${address.address}:${address.port}`;
  const tunnel = spawn("cloudflared", ["tunnel", "--no-autoupdate", "--url", target], { stdio: ["ignore", "pipe", "pipe"] });
  let shown = false;
  const watch = (chunk: Buffer) => {
    const url = /https:\/\/[a-z0-9-]+\.trycloudflare\.com/.exec(chunk.toString())?.[0];
    if (!url || shown) return;
    shown = true;
    console.log(`  Connector URL (paste this into Claude):

  ${url}${mcpPath}

  Anyone with this URL can read your board and add rows to it, so keep it private: don't post it or show it
  in a screenshot. It stops working when you press Ctrl+C. It can take up to a minute to start answering.
`);
  };
  tunnel.stdout.on("data", watch);
  tunnel.stderr.on("data", watch);
  tunnel.on("error", (error: NodeJS.ErrnoException) => {
    if (error.code === "ENOENT") {
      console.error(`  Can't find cloudflared, the program that opens the tunnel. Install it, then run this again:
    Mac      brew install cloudflared
    Windows  winget install --id Cloudflare.cloudflared
    Linux    https://github.com/cloudflare/cloudflared/releases (see the Day 4 README for the commands)
  The test page above still works without it.
`);
    } else console.error(`  The tunnel didn't start: ${error.message}`);
  });
  tunnel.on("exit", (code) => {
    if (code && !shown) console.error(`  The tunnel stopped (cloudflared exited with ${code}). Try again in a minute.`);
  });
  const stop = () => {
    tunnel.kill();
    process.exit(0);
  };
  process.on("SIGINT", stop);
  process.on("SIGTERM", stop);
}
