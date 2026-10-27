// The view: runs inside the host's sandboxed iframe and talks to the host through `App`.
import { App, applyDocumentTheme, applyHostStyleVariables, type McpUiHostContext } from "@modelcontextprotocol/ext-apps";

// The shape of returns_chart's structuredContent (see src/server.ts).
type Row = { product: string; returned: number; sold: number; rate: number };
type ChartData = { category: string; quarter: string; total: number; rows: Row[] };
type Reasons = { product: string; total: number; reasons: { reason: string; count: number }[] };

const $ = (id: string) => document.getElementById(id)!;
let data: ChartData | undefined;
let selected = ""; // the product whose reasons the button will show

const app = new App({ name: "Returns chart", version: "1.0.0" });

// 1. Match the host's look: light or dark, and its colours and fonts.
function applyHostLook(ctx: McpUiHostContext) {
  if (ctx.theme) applyDocumentTheme(ctx.theme);
  if (ctx.styles?.variables) applyHostStyleVariables(ctx.styles.variables);
}
app.onhostcontextchanged = applyHostLook;

// 2. The tool result arrives: draw the chart from structuredContent.
app.ontoolresult = (result) => {
  if (result.isError) {
    const text = result.content?.[0]?.type === "text" ? result.content[0].text : "The tool failed.";
    $("title").textContent = "Something went wrong";
    $("lede").textContent = text;
    $("lede").classList.add("error");
    return;
  }
  data = result.structuredContent as ChartData;
  selected = data.rows[0]?.product ?? "";
  draw();
};

app.ontoolcancelled = () => {
  $("title").textContent = "The tool call was cancelled";
};

function draw() {
  if (!data) return;
  const { category, quarter, total, rows } = data;
  $("eyebrow").textContent = `${category} · ${quarter}`;
  $("title").textContent = `${total} returns`;
  $("lede").textContent = rows.length
    ? `${rows[0].product} had the most. Click a bar to pick a product.`
    : `No sales for ${category} in ${quarter}.`;

  const max = Math.max(1, ...rows.map((r) => r.returned));
  const list = $("bars");
  list.replaceChildren(); // textContent and createElement below, never innerHTML: product names are data, not code
  rows.forEach((r) => {
    const row = document.createElement("button");
    row.type = "button";
    row.className = r.returned === max && r.returned > 0 ? "row top" : "row"; // the biggest bar (or bars, on a tie) is highlighted
    row.setAttribute("aria-pressed", String(r.product === selected));
    row.innerHTML = `<span class="name"></span><span class="count"></span><span class="track"><span class="fill"></span></span>`;
    row.querySelector(".name")!.textContent = r.product;
    row.querySelector(".count")!.textContent = `${r.returned} of ${r.sold} · ${r.rate}%`;
    (row.querySelector(".fill") as HTMLElement).style.width = `${(100 * r.returned) / max}%`;
    row.onclick = () => {
      selected = r.product;
      draw();
    };
    const li = document.createElement("li");
    li.append(row);
    list.append(li);
  });

  $("detail").hidden = rows.length === 0;
  $("reasons-btn").textContent = `Show the reasons for ${selected}`;
  $("reasons").replaceChildren();
  $("note").textContent = "";
}

// 3. The button: call the app-only tool, show the answer, then tell the model what the user looked at.
$("reasons-btn").addEventListener("click", async () => {
  if (!data) return;
  const button = $("reasons-btn") as HTMLButtonElement;
  button.disabled = true;
  try {
    const result = await app.callServerTool({
      name: "return_reasons",
      arguments: { product: selected, category: data.category, quarter: data.quarter },
    });
    if (result.isError) throw new Error(result.content?.[0]?.type === "text" ? result.content[0].text : "Failed");
    const { product, total, reasons } = result.structuredContent as Reasons;

    $("reasons").replaceChildren(
      ...reasons.map(({ reason, count }) => {
        const li = document.createElement("li");
        li.innerHTML = "<span></span><b></b>";
        li.querySelector("span")!.textContent = reason;
        li.querySelector("b")!.textContent = `${count} of ${total}`;
        return li;
      }),
    );

    // updateModelContext: the model reads this on the user's NEXT message. It doesn't start a reply.
    const summary = reasons.map((r) => `${r.reason} ${r.count}`).join(", ") || "no returns";
    const line = `User looked at return reasons for ${product} (${data.category}, ${data.quarter}): ${summary}.`;
    await app.updateModelContext({ content: [{ type: "text", text: line }] });
    $("note").textContent = "Sent to the model: " + line;
    $("note").classList.remove("error");
  } catch (error) {
    $("note").textContent = String(error instanceof Error ? error.message : error);
    $("note").classList.add("error");
  } finally {
    button.disabled = false;
  }
});

// 4. Connect last, after every handler is set, so no message is missed.
app.connect().then(() => {
  const ctx = app.getHostContext();
  if (ctx) applyHostLook(ctx);
});
