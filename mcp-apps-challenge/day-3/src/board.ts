// The board behind the app: your config, your CSV's rows, and the one change the app may make (a row's status).
// Plain functions, no MCP and no files: easy to test.

import { z } from "zod";
import { parseCsv, toCsv } from "./csv.js";

// ---------- the config: app.config.json ----------

export const STATUSES = ["to review", "approved", "skipped"] as const;
export type Status = (typeof STATUSES)[number];

const column = z.string().trim().min(1);

export const ConfigSchema = z.object({
  title: z.string().trim().min(1).max(60),
  csv: z.string().trim().min(1), // a path inside the app's folder, e.g. "applications.csv"
  id: column, // a column whose value is different on every row, e.g. "role"
  details: z.array(column).max(6).default([]), // other columns to show under each row
  status: column.default("status"), // the column the app writes. Added to the CSV if it isn't there yet
  approve: z.string().trim().min(1).max(24).default("Approve"), // the button labels
  skip: z.string().trim().min(1).max(24).default("Skip"),
  ask: z.string().trim().min(1).max(500), // what Claude should suggest for each row
  sample: z.array(z.object({ id: z.string(), suggestion: z.string() })).default([]), // example suggestions for the test page
});
export type Config = z.infer<typeof ConfigSchema>;

/** Check app.config.json and explain the first problem in plain words. */
export function readConfig(json: string): Config {
  let raw: unknown;
  try {
    raw = JSON.parse(json);
  } catch (error) {
    throw new Error(`app.config.json isn't valid JSON: ${(error as Error).message}`);
  }
  const parsed = ConfigSchema.safeParse(raw);
  if (!parsed.success) {
    const issue = parsed.error.issues[0]!;
    throw new Error(`app.config.json: "${issue.path.join(".") || "(top)"}" ${issue.message}`);
  }
  return parsed.data;
}

// ---------- the rows ----------

export type Item = { id: string; details: Record<string, string>; status: Status };

type Table = { header: string[]; lines: string[][] };

function table(text: string, config: Config): Table {
  const [header, ...lines] = parseCsv(text);
  if (!header) throw new Error(`${config.csv} is empty.`);
  const missing = [config.id, ...config.details].filter((c) => !header.includes(c));
  if (missing.length) {
    throw new Error(`${config.csv} has no column called ${missing.map((c) => `"${c}"`).join(", ")}. Its columns are: ${header.join(", ")}.`);
  }
  const at = header.indexOf(config.id);
  const seen = new Set<string>();
  for (const cells of lines) {
    const id = (cells[at] ?? "").trim();
    if (!id) throw new Error(`A row in ${config.csv} has no "${config.id}". Every row needs one.`);
    if (seen.has(id)) throw new Error(`"${id}" appears twice in the "${config.id}" column. Pick an id column with a different value on every row.`);
    seen.add(id);
  }
  return { header, lines };
}

const toStatus = (value: string | undefined): Status => {
  const v = (value ?? "").trim().toLowerCase();
  return v === "approved" || v === "skipped" ? v : "to review"; // anything else, including empty, still needs a look
};

/** Every row of the CSV, as the app shows it. */
export function readItems(text: string, config: Config): Item[] {
  const { header, lines } = table(text, config);
  const col = (name: string) => header.indexOf(name);
  return lines.map((cells) => ({
    id: cells[col(config.id)]!.trim(),
    details: Object.fromEntries(config.details.map((d) => [d, (cells[col(d)] ?? "").trim()])),
    status: toStatus(col(config.status) >= 0 ? cells[col(config.status)] : ""),
  }));
}

/**
 * The one write the app can make: set one row's status. Returns the new CSV text.
 * Only that one cell changes. Every other cell, and the order of rows and columns, stays as it was.
 */
export function setStatus(text: string, config: Config, id: string, status: Status): string {
  const { header, lines } = table(text, config);
  const idCol = header.indexOf(config.id);
  const row = lines.find((cells) => cells[idCol]?.trim() === id);
  if (!row) throw new Error(`There is no row with ${config.id} "${id}".`);
  let statusCol = header.indexOf(config.status);
  if (statusCol < 0) {
    header.push(config.status); // first write: add the status column at the end
    statusCol = header.length - 1;
  }
  for (const cells of lines) while (cells.length < header.length) cells.push("");
  row[statusCol] = status === "to review" ? "" : status;
  return toCsv([header, ...lines]);
}

/** One line for the model: what the user has decided so far. */
export function summarise(items: Item[], config: Config): string {
  const names = (s: Status) => items.filter((i) => i.status === s).map((i) => i.id);
  const part = (label: string, list: string[]) => `${label} (${list.length}): ${list.length ? list.join("; ") : "none"}`;
  return [
    `${config.title}.`,
    part(`${config.approve}`, names("approved")) + ".",
    part(`${config.skip}`, names("skipped")) + ".",
    part("Still to review", names("to review")) + ".",
  ].join(" ");
}
