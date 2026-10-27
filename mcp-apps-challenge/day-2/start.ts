// `npm start` runs this after building: the MCP server on 3001 and the test page on 8080 (+ its sandbox on 8081).
import fs from "node:fs";
import { startTestPage } from "./host/serve.js";
import { startMcpServer, VIEW_FILE } from "./src/server.js";

const HOST = "localhost"; // the same name everywhere, so IPv4/IPv6 can't split them

if (!fs.existsSync(VIEW_FILE)) {
  console.error("The view isn't built yet. Run `npm start` (it builds first) or `npm run build`.");
  process.exit(1);
}

try {
  await startMcpServer(3001, HOST);
  const page = await startTestPage({ mcpUrl: `http://${HOST}:3001/mcp`, port: 8080, sandboxPort: 8081, host: HOST });
  console.log(`
  MCP server   http://${HOST}:3001/mcp
  Test page    ${page.url}   <- open this

  Press Ctrl+C to stop.
`);
} catch (error) {
  const e = error as NodeJS.ErrnoException & { port?: number };
  if (e.code === "EADDRINUSE") {
    console.error(`Port ${e.port} is already in use. Is npm start already running in another terminal? Stop it with Ctrl+C.`);
  } else {
    console.error(error);
  }
  process.exit(1);
}
