// Runs the agent over a list of job ads, a few at a time, and ranks the results.
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";

import { reportPath, toMarkdown } from "./report.js";
import { type Run, StopRun, isLink, runAgent } from "./run.js";

const AT_ONCE = 3; // parallel runs: fast enough, and gentle on rate limits and job sites

// Lets at most `size` jobs run at once; the rest wait their turn, like Python's asyncio.Semaphore.
export class Semaphore {
  private waiting: (() => void)[] = [];

  constructor(private free: number) {}

  async run<T>(work: () => Promise<T>): Promise<T> {
    if (this.free > 0) this.free--;
    else await new Promise<void>((wake) => this.waiting.push(wake));
    try {
      return await work();
    } finally {
      const next = this.waiting.shift();
      if (next) next(); // hand our place straight to the next job in the queue
      else this.free++;
    }
  }
}

// One job's result: a run, or the problem that stopped it.
export class Outcome {
  constructor(
    readonly job: string,
    readonly run?: Run,
    readonly problem = "",
  ) {}
}

// jobs.txt: one link or file per line. Files are relative to the list; # lines are skipped.
export function readJobList(path: string): string[] {
  const folder = dirname(path);
  const lines = readFileSync(path, "utf8").split(/\r?\n/).map((line) => line.trim());
  return lines.filter((line) => line && !line.startsWith("#")).map((line) => (isLink(line) ? line : join(folder, line)));
}

async function assess(job: string, cv: string, checks: boolean, limit: Semaphore): Promise<Outcome> {
  let run: Run;
  try {
    run = await limit.run(() => runAgent(job, cv, { checks, showSteps: false }));
  } catch (error) {
    if (!(error instanceof StopRun)) throw error; // a real bug: let it surface
    return new Outcome(job, undefined, error.message.split("\n")[0]);
  }
  writeFileSync(reportPath(run.report.role, cv), toMarkdown(run.report));
  console.log(`  · ${run.report.fit_score}/10  ${run.report.role}  (${run.summary})`);
  return new Outcome(job, run);
}

export async function shortlist(jobs: string[], cv: string, checks = true): Promise<Outcome[]> {
  const limit = new Semaphore(AT_ONCE);
  return Promise.all(jobs.map((job) => assess(job, cv, checks, limit)));
}

export function toMarkdownTable(outcomes: Outcome[]): string {
  const done = outcomes.filter((o): o is Outcome & { run: Run } => o.run !== undefined);
  done.sort((a, b) => b.run.report.fit_score - a.run.report.fit_score);
  const failed = outcomes.filter((o) => !o.run);
  const why = (verdict: string) => `${verdict.split(". ")[0].replace(/\.+$/, "")}.`; // its first sentence
  const rows = done.map(
    (o, i) =>
      `| ${i + 1} | ${o.run.report.role} | ${o.run.report.fit_score}/10 | ${o.run.report.decision} | ${why(o.run.report.verdict)} |`,
  );
  const lines = ["# Your job shortlist", "", "| # | Role | Fit | Decision | Why |", "|---|---|---|---|---|", ...rows];
  if (failed.length) lines.push("", "## Couldn't assess", "", ...failed.map((o) => `- ${o.job}: ${o.problem}`));
  const cost = done.reduce((sum, o) => sum + o.run.costUsd, 0);
  return [...lines, "", `${done.length} jobs assessed for $${cost.toFixed(2)}. Full reports are next to this file.`].join("\n") + "\n";
}
