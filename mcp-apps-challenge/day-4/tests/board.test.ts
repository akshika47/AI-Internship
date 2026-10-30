// The board on its own: config checks, reading rows, and the one write. No server, no files.
import { describe, expect, it } from "vitest";
import { addItems, readConfig, readItems, setStatus, summarise } from "../src/board.js";
import { parseCsv, toCsv } from "../src/csv.js";

const config = readConfig(JSON.stringify({ title: "Jobs", csv: "jobs.csv", id: "role", details: ["fit"], approve: "Apply", ask: "Apply or skip?" }));
const csv = 'role,fit,notes\n"Analyst, Ledgerly",3,"Says ""senior"""\nAssociate,9,Hybrid\n';

describe("csv", () => {
  it("round-trips commas, quotes and line breaks", () => {
    const rows = [["a,b", 'say "hi"', "two\nlines"], ["plain", "", "x"]];
    expect(parseCsv(toCsv(rows))).toEqual(rows);
  });
  it("drops an Excel byte-order mark and Windows line endings", () => {
    expect(parseCsv("﻿a,b\r\n1,2\r\n")).toEqual([["a", "b"], ["1", "2"]]);
  });
});

describe("config", () => {
  it("fills in defaults", () => {
    expect(config).toMatchObject({ status: "status", skip: "Skip", sample: [] });
  });
  it("explains a bad config in plain words", () => {
    expect(() => readConfig("{")).toThrow(/isn't valid JSON/);
    expect(() => readConfig(JSON.stringify({ title: "x", csv: "a.csv", ask: "?" }))).toThrow(/"id"/);
  });
});

describe("readItems", () => {
  it("reads every row as to review when there's no status column", () => {
    expect(readItems(csv, config)).toEqual([
      { id: "Analyst, Ledgerly", details: { fit: "3" }, status: "to review" },
      { id: "Associate", details: { fit: "9" }, status: "to review" },
    ]);
  });
  it("names a missing column and lists the real ones", () => {
    const bad = { ...config, details: ["salary"] };
    expect(() => readItems(csv, bad)).toThrow('no column called "salary". Its columns are: role, fit, notes');
  });
  it("refuses an id column with repeats or blanks", () => {
    expect(() => readItems("role,fit\nA,1\nA,2\n", config)).toThrow(/appears twice/);
    expect(() => readItems("role,fit\n,3\n", config)).toThrow(/has no "role"/);
  });
});

describe("setStatus", () => {
  it("adds a status column on the first write and changes only that cell", () => {
    const out = setStatus(csv, config, "Associate", "approved");
    expect(parseCsv(out)).toEqual([
      ["role", "fit", "notes", "status"],
      ["Analyst, Ledgerly", "3", 'Says "senior"', ""],
      ["Associate", "9", "Hybrid", "approved"],
    ]);
  });
  it("undoes back to an empty cell", () => {
    const once = setStatus(csv, config, "Associate", "skipped");
    expect(readItems(setStatus(once, config, "Associate", "to review"), config)[1]!.status).toBe("to review");
  });
  it("refuses a row that doesn't exist", () => {
    expect(() => setStatus(csv, config, "Nope", "approved")).toThrow('no row with role "Nope"');
  });
});

it("summarises decisions with the app's own labels", () => {
  const items = readItems(setStatus(csv, config, "Associate", "approved"), config);
  expect(summarise(items, config)).toBe("Jobs. Apply (1): Associate. Skip (0): none. Still to review (1): Analyst, Ledgerly.");
});

describe("addItems", () => {
  it("appends new rows as to review and fills only real columns", () => {
    const r = addItems(csv, config, [{ id: "Junior Analyst, Fernhill", values: { fit: "7", notes: "From a job alert", salary: "30k" } }]);
    expect(r.added).toEqual(["Junior Analyst, Fernhill"]);
    expect(r.ignored).toEqual(["salary"]);
    const items = readItems(r.csv, config);
    expect(items).toHaveLength(3);
    expect(items[2]).toEqual({ id: "Junior Analyst, Fernhill", details: { fit: "7" }, status: "to review" });
    expect(parseCsv(r.csv)[3]).toEqual(["Junior Analyst, Fernhill", "7", "From a job alert"]);
  });
  it("never changes an existing row, and can't set a status", () => {
    const decided = setStatus(csv, config, "Associate", "approved");
    const r = addItems(decided, config, [{ id: "Associate", values: { fit: "1" } }, { id: "New", values: { status: "approved" } }]);
    expect(r.duplicates).toEqual(["Associate"]);
    expect(r.ignored).toEqual(["status"]);
    const items = readItems(r.csv, config);
    expect(items.find((i) => i.id === "Associate")).toMatchObject({ details: { fit: "9" }, status: "approved" });
    expect(items.find((i) => i.id === "New")!.status).toBe("to review");
  });
  it("defuses spreadsheet formulas copied in from an email", () => {
    const r = addItems(csv, config, [{ id: "=HYPERLINK(\"http://x\")", values: { fit: "-2", notes: "@SUM(A1)" } }]);
    const row = parseCsv(r.csv)[3]!;
    expect(row[0]).toBe("'=HYPERLINK(\"http://x\")");
    expect(row[1]).toBe("-2");
    expect(row[2]).toBe("'@SUM(A1)");
  });
  it("adds at most 20 rows in one go", () => {
    const many = Array.from({ length: 25 }, (_, i) => ({ id: `Role ${i}`, values: {} }));
    expect(addItems(csv, config, many).added).toHaveLength(20);
  });
});
