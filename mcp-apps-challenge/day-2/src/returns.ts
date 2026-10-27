// The numbers behind the chart. Plain functions, no MCP: easy to test, easy to swap for your own data on Day 3.
//
// A "return" means the same thing as in the Build Your First MCP workshop:
// one order line marked returned = "yes", counted by ORDER date, with cancelled orders left out.
// "sold" is the number of order lines (not units), so rate = returned lines / sold lines.

export type Order = {
  order_date: string; // "2026-07-14"
  status: string; // "completed" or "cancelled"
  product: string;
  category: string;
  returned: boolean;
  return_reason: string; // "" when not returned
};

export type ProductRow = { product: string; returned: number; sold: number; rate: number }; // rate is a percent, e.g. 80.2
export type Reason = { reason: string; count: number };

// ---------- reading the CSV ----------

/** Split CSV text into rows of cells. Handles "quoted, cells", "" inside quotes, and Windows line endings. */
export function parseCsv(text: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [];
  let cell = "";
  let quoted = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') { cell += '"'; i++; } // "" is one quote
      else if (ch === '"') quoted = false;
      else cell += ch;
    } else if (ch === '"') quoted = true;
    else if (ch === ",") { row.push(cell); cell = ""; }
    else if (ch === "\n" || ch === "\r") {
      if (ch === "\r" && text[i + 1] === "\n") i++;
      row.push(cell); cell = "";
      if (row.some((c) => c !== "")) rows.push(row); // skip blank lines
      row = [];
    } else cell += ch;
  }
  row.push(cell);
  if (row.some((c) => c !== "")) rows.push(row);
  return rows;
}

const NEEDED = ["order_date", "status", "product", "category", "returned", "return_reason"] as const;

/** Turn the CSV into orders. Throws a plain message if a column we need is missing. */
export function readOrders(text: string): Order[] {
  const [header, ...lines] = parseCsv(text.replace(/^﻿/, "")); // drop a byte-order mark if Excel added one
  if (!header) throw new Error("The CSV is empty.");
  const col = header.map((h) => h.trim().toLowerCase());
  const missing = NEEDED.filter((name) => !col.includes(name));
  if (missing.length) throw new Error(`The CSV is missing these columns: ${missing.join(", ")}.`);
  const at = (cells: string[], name: string) => (cells[col.indexOf(name)] ?? "").trim();
  return lines.map((cells) => ({
    order_date: at(cells, "order_date"),
    status: at(cells, "status").toLowerCase(),
    product: at(cells, "product"),
    category: at(cells, "category"),
    returned: at(cells, "returned").toLowerCase() === "yes",
    return_reason: at(cells, "return_reason"),
  }));
}

// ---------- quarters ----------

/** "2026-07-14" -> "2026-Q3" */
export function quarterOf(date: string): string {
  const month = Number(date.slice(5, 7));
  return `${date.slice(0, 4)}-Q${Math.ceil(month / 3)}`;
}

/** Turn " 2026-q3 " into "2026-Q3", or return null if it isn't a quarter. */
export function normaliseQuarter(quarter: string): string | null {
  const q = quarter.trim().toUpperCase();
  return /^\d{4}-Q[1-4]$/.test(q) ? q : null;
}

// ---------- what the tools need ----------

/** The categories and quarters in the data, sorted. Used to check input and to write helpful errors. */
export function listChoices(orders: Order[]) {
  return {
    categories: [...new Set(orders.map((o) => o.category))].sort(),
    quarters: [...new Set(orders.map((o) => quarterOf(o.order_date)))].sort(),
  };
}

/** Orders that count: not cancelled, in this category and this quarter. */
function counted(orders: Order[], category: string, quarter: string): Order[] {
  return orders.filter(
    (o) => o.status !== "cancelled" && o.category === category && quarterOf(o.order_date) === quarter,
  );
}

/** One percent with one decimal: 77 of 96 -> 80.2 */
export function percent(part: number, whole: number): number {
  return whole === 0 ? 0 : Math.round((1000 * part) / whole) / 10;
}

/** Returns per product in a category and quarter, most returns first. */
export function returnsByProduct(orders: Order[], category: string, quarter: string) {
  const byProduct = new Map<string, ProductRow>();
  for (const o of counted(orders, category, quarter)) {
    const row = byProduct.get(o.product) ?? { product: o.product, returned: 0, sold: 0, rate: 0 };
    row.sold += 1;
    if (o.returned) row.returned += 1;
    byProduct.set(o.product, row);
  }
  const rows = [...byProduct.values()].map((r) => ({ ...r, rate: percent(r.returned, r.sold) }));
  // Most returns first; on a tie, the higher rate; then A to Z so the order never jumps around.
  rows.sort((a, b) => b.returned - a.returned || b.rate - a.rate || a.product.localeCompare(b.product));
  const total = rows.reduce((sum, r) => sum + r.returned, 0);
  const sold = rows.reduce((sum, r) => sum + r.sold, 0);
  return { category, quarter, total, sold, rows };
}

/** Why one product came back, most common reason first. */
export function reasonsFor(orders: Order[], product: string, category: string, quarter: string) {
  const counts = new Map<string, number>();
  for (const o of counted(orders, category, quarter)) {
    if (o.product !== product || !o.returned) continue;
    const reason = o.return_reason || "no reason given";
    counts.set(reason, (counts.get(reason) ?? 0) + 1);
  }
  const reasons: Reason[] = [...counts].map(([reason, count]) => ({ reason, count }));
  reasons.sort((a, b) => b.count - a.count || a.reason.localeCompare(b.reason));
  const total = reasons.reduce((sum, r) => sum + r.count, 0);
  return { product, category, quarter, total, reasons };
}

/** The one sentence the model reads. It has to make sense on its own, with no chart. */
export function summarise(result: ReturnType<typeof returnsByProduct>): string {
  const { category, quarter, total, sold, rows } = result;
  if (rows.length === 0) return `${category} had no sales in ${quarter}, so there are no returns to show.`;
  const top = rows[0];
  const overall = `${category} had ${total} returns in ${quarter} out of ${sold} items sold (${percent(total, sold)}%).`;
  if (total === 0) return overall;
  return `${overall} ${top.product} had the most: ${top.returned} of ${top.sold} sold (${top.rate}%).`;
}
