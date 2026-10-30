// The view: runs inside the host's sandboxed iframe and talks to the host through `App`.
import { App, applyDocumentTheme, applyHostStyleVariables, type McpUiHostContext } from "@modelcontextprotocol/ext-apps";

// The shape of review_items' structuredContent (see src/app.ts).
type Status = "to review" | "approved" | "skipped";
type Item = { id: string; details: Record<string, string>; status: Status; suggestion: string };
type Board = { title: string; approve: string; skip: string; details: string[]; items: Item[] };

const $ = (id: string) => document.getElementById(id)!;
const textOf = (r: { content?: { type: string; text?: string }[] }) => (r.content?.[0]?.type === "text" ? r.content[0].text ?? "" : "");
let board: Board | undefined;
let busy = false;

const app = new App({ name: "Board", version: "1.0.0" });

// 1. Match the host's look: light or dark, and its colours and fonts.
function applyHostLook(ctx: McpUiHostContext) {
  if (ctx.theme) applyDocumentTheme(ctx.theme);
  if (ctx.styles?.variables) applyHostStyleVariables(ctx.styles.variables);
}
app.onhostcontextchanged = applyHostLook;

// 2. The tool result arrives: draw a card per row, with Claude's suggestion on it.
app.ontoolresult = (result) => {
  if (result.isError) return fail(textOf(result) || "The tool failed.");
  board = result.structuredContent as Board;
  draw();
};
app.ontoolcancelled = () => {
  $("title").textContent = "The tool call was cancelled";
};

function fail(text: string) {
  $("title").textContent = "Something went wrong";
  $("lede").textContent = text;
  $("lede").classList.add("error");
}

function draw() {
  if (!board) return;
  const { title, approve, skip, items } = board;
  const count = (s: Status) => items.filter((i) => i.status === s).length;
  $("title").textContent = title;
  $("lede").textContent = items.length
    ? `${count("to review")} to review · ${count("approved")} ${approve.toLowerCase()} · ${count("skipped")} ${skip.toLowerCase()}`
    : "There are no rows in the CSV yet.";

  // textContent and createElement only, never innerHTML with data: your rows are data, not code.
  $("items").replaceChildren(
    ...items.map((item) => {
      const li = document.createElement("li");
      li.className = `item ${item.status === "to review" ? "" : item.status}`;
      const head = el("div", "head");
      head.append(el("span", "name", item.id), el("span", "badge", label(item.status)));
      li.append(head);
      const details = Object.entries(item.details).filter(([, v]) => v);
      if (details.length) li.append(el("p", "details", details.map(([k, v]) => `${k}: ${v}`).join(" · ")));
      if (item.suggestion) {
        const p = el("p", "suggestion");
        p.append(el("b", "", "Claude: "), item.suggestion);
        li.append(p);
      }
      const actions = el("div", "actions");
      if (item.status === "to review") {
        actions.append(button(approve, "yes", () => decide(item, "approved")), button(skip, "", () => decide(item, "skipped")));
      } else {
        actions.append(button("Undo", "link", () => decide(item, "to review")));
      }
      li.append(actions);
      return li;
    }),
  );
  $("footer").hidden = items.length === 0;
}

const label = (s: Status) => (s === "approved" ? `✓ ${board!.approve}` : s === "skipped" ? board!.skip : "To review");

function el(tag: string, className: string, text?: string) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function button(text: string, className: string, onClick: () => void) {
  const b = el("button", className, text) as HTMLButtonElement;
  b.type = "button";
  b.disabled = busy;
  b.onclick = onClick;
  return b;
}

function note(text: string, error = false) {
  $("note").textContent = text;
  $("note").classList.toggle("error", error);
}

// 3. A button: call the app-only set_status tool (it writes the CSV), then tell the model what you decided.
async function decide(item: Item, status: Status) {
  if (!board || busy) return;
  busy = true;
  draw();
  try {
    const result = await app.callServerTool({ name: "set_status", arguments: { id: item.id, status } });
    if (result.isError) throw new Error(textOf(result) || "Couldn't save that.");
    const saved = (result.structuredContent as { items: Item[] }).items;
    for (const i of board.items) i.status = saved.find((s) => s.id === i.id)?.status ?? i.status;
    // updateModelContext: the model reads this on your NEXT message. It doesn't start a reply.
    const summary = textOf(result);
    await app.updateModelContext({ content: [{ type: "text", text: `The user is deciding in the app. ${summary}` }] });
    note("Saved to the CSV. Claude will see this on your next message.");
  } catch (error) {
    note(error instanceof Error ? error.message : String(error), true);
  } finally {
    busy = false;
    draw();
  }
}

// 4. The done button: sendMessage hands a message to the chat as you. Claude.ai puts it in the message box with a
//    warning and waits for you to press Send: even a message from your own app needs your OK.
$("done").addEventListener("click", async () => {
  if (!board) return;
  const button = $("done") as HTMLButtonElement;
  button.disabled = true;
  try {
    const picked = board.items.filter((i) => i.status === "approved").map((i) => i.id);
    const text = picked.length
      ? `I've finished reviewing "${board.title}". I chose "${board.approve}" for: ${picked.join("; ")}. What should I do next for these?`
      : `I've finished reviewing "${board.title}" and didn't choose "${board.approve}" for any of them.`;
    const result = await app.sendMessage({ role: "user", content: [{ type: "text", text }] });
    if (result.isError) throw new Error("The chat didn't accept the message.");
    note("Your message is in the chat box. Press Send if Claude asks you to.");
  } catch (error) {
    note(error instanceof Error ? error.message : String(error), true);
  } finally {
    button.disabled = false;
  }
});

// 5. Connect last, after every handler is set, so no message is missed.
app.connect().then(() => {
  const ctx = app.getHostContext();
  if (ctx) applyHostLook(ctx);
});
