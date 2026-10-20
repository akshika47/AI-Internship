// Runs the agent once and hands back its report, or a StopRun explaining what went wrong.
import { existsSync, statSync } from "node:fs";
import { resolve } from "node:path";
import { query, type SDKResultMessage } from "@anthropic-ai/claude-agent-sdk";

import { OPTIONS } from "./options.js";
import type { Report } from "./schema.js";

// Something the user can fix. job_fit.ts prints the message and exits, with no stack trace.
export class StopRun extends Error {
  name = "StopRun";
}

// What one run gives back: the report, plus how many turns it took and what it cost.
export class Run {
  constructor(
    readonly report: Report,
    readonly turns: number,
    readonly costUsd: number,
  ) {}

  get summary(): string {
    return `${this.turns} turns · $${this.costUsd.toFixed(3)}`;
  }
}

export function isLink(job: string): boolean {
  return job.startsWith("http://") || job.startsWith("https://");
}

export function requireFile(path: string, what: string, hint: string): void {
  if (!existsSync(path) || !statSync(path).isFile()) {
    throw new StopRun(`Can't find ${what} at '${path}'. ${hint}`);
  }
}

// Stop before spending anything if a file isn't where you said it was.
export function checkInputs(job: string, cv: string): void {
  requireFile(cv, "your CV", "Check the name, or save it as cv.md in this folder.");
  if (!isLink(job)) {
    requireFile(job, "the job ad", "Use a link that starts with https://, or a file that exists.");
  }
}

// The agent streams messages while it works; the last one carries the answer.
export async function finalMessage(prompt: string): Promise<SDKResultMessage | undefined> {
  let result: SDKResultMessage | undefined;
  try {
    for await (const message of query({ prompt, options: OPTIONS })) {
      if (message.type === "result") result = message;
    }
  } catch (error) {
    const reason = error instanceof Error ? error.message : String(error);
    throw new StopRun(`The agent couldn't run: ${reason}\nThe Stuck? table in ../README.md has the usual fixes.`, {
      cause: error,
    });
  }
  return result;
}

export async function runAgent(job: string, cv: string): Promise<Run> {
  checkInputs(job, cv);
  const where = isLink(job) ? job : resolve(job);
  const result = await finalMessage(`My CV is the file ${resolve(cv)}. The job ad is at ${where}. How well do I fit?`);

  // Only a "success" result carries a report; the others say why the agent stopped early.
  if (result?.subtype !== "success" || result.structured_output === undefined) {
    throw new StopRun(`The agent stopped without a report (${result?.subtype ?? "no result"}).`);
  }
  const run = new Run(result.structured_output as Report, result.num_turns, result.total_cost_usd ?? 0);
  if (!run.report.ad_was_read) {
    throw new StopRun(
      `Couldn't read the job ad. ${run.report.verdict}\n` +
        `Copy the ad's text into job.md and run: npx tsx job_fit.ts job.md\n(${run.summary})`,
    );
  }
  return run;
}
