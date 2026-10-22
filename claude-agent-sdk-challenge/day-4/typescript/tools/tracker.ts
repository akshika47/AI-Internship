// Two tools for an applications tracker, kept in applications.csv next to job_fit.ts.
import { existsSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { basename } from "node:path";
import { tool } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";

const TRACKER = "applications.csv";
const COLUMNS = ["date", "role", "fit_score", "decision", "job_ad"];

type Row = Record<string, string>;

// shortlist.ts runs several jobs at once; one write at a time. Each write waits for the one
// before it to finish, so two runs can't both read the old file and lose each other's row.
let lastWrite: Promise<unknown> = Promise.resolve();
function oneAtATime<T>(write: () => T): Promise<T> {
  const next = lastWrite.then(write);
  lastWrite = next.catch(() => {}); // a failed write mustn't block the ones after it
  return next;
}

// Today's date as 2026-10-20, in your own time zone.
function today(): string {
  const now = new Date();
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
}

// A tiny CSV reader. A field in "double quotes" can hold commas and line breaks,
// and "" inside it stands for one " (so roles like "Analyst, Fernhill Health" survive).
function parseCsv(text: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [];
  let field = "";
  let inQuotes = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (inQuotes) {
      if (c === '"' && text[i + 1] === '"') {
        field += '"';
        i++;
      } else if (c === '"') {
        inQuotes = false;
      } else {
        field += c;
      }
    } else if (c === '"') {
      inQuotes = true;
    } else if (c === ",") {
      row.push(field);
      field = "";
    } else if (c === "\n" || c === "\r") {
      if (c === "\r" && text[i + 1] === "\n") i++;
      row.push(field);
      rows.push(row);
      row = [];
      field = "";
    } else {
      field += c;
    }
  }
  if (field !== "" || row.length > 0) {
    row.push(field);
    rows.push(row);
  }
  return rows.filter((r) => r.length > 1 || r[0] !== ""); // skip blank lines
}

// The writing side: quote a field only if it needs it, as Python's csv module does.
function csvField(value: string): string {
  return /[",\r\n]/.test(value) ? `"${value.replaceAll('"', '""')}"` : value;
}

export function readRows(): Row[] {
  if (!existsSync(TRACKER) || !statSync(TRACKER).isFile()) return [];
  const [header = [], ...lines] = parseCsv(readFileSync(TRACKER, "utf8"));
  return lines.map((cells) => Object.fromEntries(header.map((name, i) => [name, cells[i] ?? ""])));
}

export const checkTracker = tool(
  "check_tracker",
  "List every job already assessed: date, role, fit score, decision and where the ad came from. " +
    "Call this before writing the report so you can compare this job with earlier ones.",
  {}, // it takes no inputs
  async () => {
    const rows = readRows();
    if (rows.length === 0) {
      return { content: [{ type: "text", text: "The tracker is empty. This is the first job assessed." }] };
    }
    const lines = rows.map((r) => `${r.date} | ${r.role} | ${r.fit_score}/10 | ${r.decision} | ${r.job_ad}`);
    return { content: [{ type: "text", text: `${rows.length} jobs assessed so far:\n` + lines.join("\n") }] };
  },
  { annotations: { readOnlyHint: true } }, // it only looks, so it's safe to run any time
);

export const saveToTracker = tool(
  "save_to_tracker",
  "Save this job's result to the applications tracker. Call it once, after you've decided, " +
    "and only if you read the job ad in full. Saving the same job ad again updates its row.",
  {
    role: z.string().describe("Job title and company"),
    fit_score: z.number().int().min(0).max(10),
    decision: z.enum(["Apply now", "Apply after closing a gap", "Skip this one"]),
    job_ad: z.string().describe("The job ad's link, or its file name"),
  },
  async (args) =>
    oneAtATime(() => {
      const row: Row = {
        date: today(),
        role: args.role,
        fit_score: String(args.fit_score),
        decision: args.decision,
        job_ad: args.job_ad,
      };
      if (!row.job_ad.startsWith("http://") && !row.job_ad.startsWith("https://")) {
        row.job_ad = basename(row.job_ad); // a file name reads better than a full path
      }
      const rows = [...readRows().filter((r) => r.job_ad !== row.job_ad), row];
      const lines = [COLUMNS, ...rows.map((r) => COLUMNS.map((c) => r[c] ?? ""))];
      // "\r\n" ends each line, the same as Python's csv module, so both versions write the same file.
      writeFileSync(TRACKER, lines.map((cells) => cells.map(csvField).join(",") + "\r\n").join(""));
      return { content: [{ type: "text" as const, text: `Saved. The tracker now has ${rows.length} jobs.` }] };
    }),
);

