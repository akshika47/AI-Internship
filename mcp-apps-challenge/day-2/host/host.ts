// A tiny MCP Apps host, to test your app without Claude or ChatGPT.
// It does what a real host does, minus the model: connect, list tools, call one, show its view, pass messages.
import {
  AppBridge,
  getToolUiResourceUri,
  isToolVisibilityAppOnly,
  isToolVisibilityModelOnly,
  PostMessageTransport,
  RESOURCE_MIME_TYPE,
} from "@modelcontextprotocol/ext-apps/app-bridge";
import { Client, StreamableHTTPClientTransport, type CallToolResult, type Tool } from "@modelcontextprotocol/client";

const $ = <T extends HTMLElement = HTMLElement>(id: string) => document.getElementById(id) as T;
const HOST = { name: "MCP Apps test page", version: "1.0.0" };
const dark = matchMedia("(prefers-color-scheme: dark)").matches;

let tools: Tool[] = [];
let bridge: AppBridge | undefined;

function show(id: string, text: string, kind: "" | "empty" | "error" = "") {
  $(id).textContent = text;
  $(id).className = kind;
}

const textOf = (result: CallToolResult) =>
  result.content.map((c) => (c.type === "text" ? c.text : `[${c.type}]`)).join("\n") || "(no text)";

// ---------- 1. connect and list tools ----------
const config: { mcpUrl: string; sandboxUrl: string } = await (await fetch("/api/config")).json();
const client = new Client(HOST);
try {
  await client.connect(new StreamableHTTPClientTransport(new URL(config.mcpUrl)));
  tools = (await client.listTools()).tools;
  $("status").innerHTML = `Connected to <code></code>`;
  $("status").querySelector("code")!.textContent = config.mcpUrl;
} catch (error) {
  show("status", `Can't reach the MCP server at ${config.mcpUrl}. Is npm start still running? (${error})`, "error");
  throw error;
}

// The model only sees tools whose visibility includes "model". App-only tools are hidden from it.
const modelTools = tools.filter((t) => !isToolVisibilityAppOnly(t));
const hidden = tools.filter((t) => isToolVisibilityAppOnly(t)).map((t) => t.name);
for (const t of modelTools) $("tool").append(new Option(getToolUiResourceUri(t) ? `${t.name} (has a view)` : t.name, t.name));
$("hidden-tools").textContent = hidden.length ? `Hidden from the model (app-only): ${hidden.join(", ")}` : "";

// Fill the JSON box with the tool's default input, so you can just press the button.
function fillInput() {
  const tool = tools.find((t) => t.name === $<HTMLSelectElement>("tool").value);
  const props = (tool?.inputSchema.properties ?? {}) as Record<string, { default?: unknown }>;
  const example = Object.fromEntries(Object.entries(props).filter(([, p]) => p.default !== undefined).map(([k, p]) => [k, p.default]));
  $<HTMLTextAreaElement>("input").value = JSON.stringify(example, null, 2);
}
$("tool").addEventListener("change", fillInput);
fillInput();
$<HTMLButtonElement>("call").disabled = modelTools.length === 0;

// ---------- 2. call the tool ----------
$("call").addEventListener("click", async () => {
  const tool = tools.find((t) => t.name === $<HTMLSelectElement>("tool").value)!;
  let input: Record<string, unknown>;
  try {
    input = JSON.parse($<HTMLTextAreaElement>("input").value || "{}");
  } catch {
    show("content", "That input isn't valid JSON.", "error");
    return;
  }
  $<HTMLButtonElement>("call").disabled = true;
  try {
    const result = (await client.callTool({ name: tool.name, arguments: input })) as CallToolResult;
    show("content", textOf(result), result.isError ? "error" : ""); // this text is what the model reads
    show("context", "Nothing yet. Click a button in the app.", "empty");
    $("structured").textContent = JSON.stringify(result.structuredContent ?? null, null, 2);
    const uri = getToolUiResourceUri(tool);
    if (uri) await showView(uri, input, result);
  } catch (error) {
    show("content", String(error), "error");
  } finally {
    $<HTMLButtonElement>("call").disabled = false;
  }
});

// ---------- 3. show the view in a sandbox, and pass messages ----------
async function showView(uri: string, input: Record<string, unknown>, result: CallToolResult) {
  // Read the view's HTML from the server (the ui:// resource).
  const { contents } = await client.readResource({ uri });
  const view = contents[0];
  if (!view || view.mimeType !== RESOURCE_MIME_TYPE || !("text" in view)) throw new Error(`${uri} is not an MCP App view.`);

  // Close the previous view, if any.
  if (bridge) {
    await Promise.race([bridge.teardownResource({}), new Promise((r) => setTimeout(r, 500))]).catch(() => {});
    await bridge.close();
  }

  // Load the sandbox proxy (another port = another origin) and wait until it says it's ready.
  const iframe = document.createElement("iframe");
  iframe.setAttribute("sandbox", "allow-scripts allow-same-origin allow-forms");
  iframe.title = "MCP App";
  const ready = new Promise<void>((resolve) => {
    const onMessage = (e: MessageEvent) => {
      if (e.source === iframe.contentWindow && e.data?.method === "ui/notifications/sandbox-proxy-ready") {
        window.removeEventListener("message", onMessage);
        resolve();
      }
    };
    window.addEventListener("message", onMessage);
  });
  iframe.src = config.sandboxUrl;
  $("frame-box").replaceChildren(iframe);
  await ready;

  // The bridge is the host's side of the conversation with the view.
  bridge = new AppBridge(
    null, // we answer the view's requests ourselves, below
    HOST,
    { serverTools: {}, updateModelContext: { text: {} } },
    { hostContext: { theme: dark ? "dark" : "light", platform: "web", displayMode: "inline", availableDisplayModes: ["inline"] } },
  );

  // The view asks to call a server tool (app.callServerTool). A host must refuse tools that are for the model only.
  bridge.oncalltool = async (params) => {
    const target = tools.find((t) => t.name === params.name);
    if (!target || isToolVisibilityModelOnly(target)) throw new Error(`The view may not call ${params.name}.`);
    return (await client.callTool(params)) as CallToolResult;
  };
  // The view tells the model something (app.updateModelContext). Each update replaces the last one.
  bridge.onupdatemodelcontext = async ({ content }) => {
    const text = (content ?? []).map((c) => (c.type === "text" ? c.text : `[${c.type}]`)).join("\n");
    show("context", text || "(cleared)", text ? "" : "empty");
    return {};
  };
  // The view sends a chat message (app.sendMessage). We just show it.
  bridge.onmessage = async ({ content }) => {
    show("context", "Message: " + content.map((c) => (c.type === "text" ? c.text : "")).join(" "));
    return {};
  };
  // The view reports its height, so the iframe fits it.
  bridge.onsizechange = async ({ height }) => {
    if (height) iframe.style.height = `${height}px`;
  };

  const initialised = new Promise<void>((resolve) => (bridge!.oninitialized = () => resolve()));
  await bridge.connect(new PostMessageTransport(iframe.contentWindow!, iframe.contentWindow!));
  await bridge.sendSandboxResourceReady({ html: view.text }); // the proxy writes the HTML into its inner iframe
  await initialised;
  await bridge.sendToolInput({ arguments: input });
  await bridge.sendToolResult(result); // the view's app.ontoolresult runs now
}
