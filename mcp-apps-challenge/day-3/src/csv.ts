// Reading and writing CSV files. Plain functions, no MCP: easy to test.

/** Split CSV text into rows of cells. Handles "quoted, cells", "" inside quotes, and Windows line endings. */
export function parseCsv(text: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [];
  let cell = "";
  let quoted = false;
  text = text.replace(/^﻿/, ""); // drop a byte-order mark if Excel added one
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

/** The opposite of parseCsv. Quotes a cell only when it has to (a comma, a quote or a line break in it). */
export function toCsv(rows: string[][]): string {
  const cell = (c: string) => (/[",\r\n]/.test(c) ? `"${c.replaceAll('"', '""')}"` : c);
  return rows.map((r) => r.map(cell).join(",")).join("\n") + "\n";
}
