// Free tests for the numbers. No server, no browser: just the functions in src/returns.ts.
import fs from "node:fs";
import { describe, expect, it } from "vitest";
import { listChoices, parseCsv, readOrders, reasonsFor, returnsByProduct, summarise } from "../src/returns.js";

const orders = readOrders(fs.readFileSync(new URL("../data/orders.csv", import.meta.url), "utf-8"));

describe("the story in the demo data", () => {
  const result = returnsByProduct(orders, "Lighting", "2026-Q3");

  it("Lighting had 92 returns in 2026-Q3, out of 318 sold", () => {
    expect(result.total).toBe(92);
    expect(result.sold).toBe(318);
  });

  it("the Aurora Glass Pendant had 77 of them and comes first", () => {
    expect(result.rows[0]).toEqual({ product: "Aurora Glass Pendant", returned: 77, sold: 96, rate: 80.2 });
  });

  it("rows are sorted by returns, biggest first", () => {
    const counts = result.rows.map((r) => r.returned);
    expect(counts).toEqual([...counts].sort((a, b) => b - a));
    expect(result.rows).toHaveLength(6);
  });

  it("rates are percent with one decimal", () => {
    for (const r of result.rows) expect(r.rate).toBe(Math.round((1000 * r.returned) / r.sold) / 10);
  });

  it("most pendant returns were damaged", () => {
    const why = reasonsFor(orders, "Aurora Glass Pendant", "Lighting", "2026-Q3");
    expect(why.total).toBe(77);
    expect(why.reasons[0]).toEqual({ reason: "damaged", count: 74 });
  });

  it("the summary sentence carries the headline on its own", () => {
    expect(summarise(result)).toBe(
      "Lighting had 92 returns in 2026-Q3 out of 318 items sold (28.9%). Aurora Glass Pendant had the most: 77 of 96 sold (80.2%).",
    );
  });

  it("knows which categories and quarters exist", () => {
    const { categories, quarters } = listChoices(orders);
    expect(categories).toEqual(["Bath", "Bedding", "Decor", "Kitchen", "Lighting"]);
    expect(quarters[0]).toBe("2025-Q3");
    expect(quarters.at(-1)).toBe("2026-Q3");
  });
});

describe("edge cases", () => {
  it("a quarter with no sales gives no rows and a plain sentence", () => {
    const empty = returnsByProduct(orders, "Lighting", "2024-Q1");
    expect(empty).toMatchObject({ total: 0, sold: 0, rows: [] });
    expect(summarise(empty)).toBe("Lighting had no sales in 2024-Q1, so there are no returns to show.");
  });

  it("cancelled orders don't count", () => {
    const csv = [
      "order_date,status,product,category,returned,return_reason",
      "2026-07-01,completed,Lamp,Lighting,yes,damaged",
      "2026-07-02,cancelled,Lamp,Lighting,yes,damaged",
      "2026-07-03,completed,Lamp,Lighting,no,",
    ].join("\n");
    expect(returnsByProduct(readOrders(csv), "Lighting", "2026-Q3").rows).toEqual([
      { product: "Lamp", returned: 1, sold: 2, rate: 50 },
    ]);
  });

  it("quoted cells can hold commas, quotes and Windows line endings", () => {
    expect(parseCsv('a,b\r\n"Lamp, brass","He said ""hi"""\r\n')).toEqual([
      ["a", "b"],
      ["Lamp, brass", 'He said "hi"'],
    ]);
    const csv = 'order_date,status,product,category,returned,return_reason\n2026-08-01,completed,"Lamp, brass",Lighting,yes,"too big, and heavy"';
    const why = reasonsFor(readOrders(csv), "Lamp, brass", "Lighting", "2026-Q3");
    expect(why.reasons).toEqual([{ reason: "too big, and heavy", count: 1 }]);
  });

  it("a CSV without the columns we need says which are missing", () => {
    expect(() => readOrders("date,item\n2026-01-01,Lamp")).toThrow(
      "The CSV is missing these columns: order_date, status, product, category, returned, return_reason.",
    );
  });

  it("an unknown product just has no reasons", () => {
    expect(reasonsFor(orders, "Flying Carpet", "Lighting", "2026-Q3")).toMatchObject({ total: 0, reasons: [] });
  });
});
