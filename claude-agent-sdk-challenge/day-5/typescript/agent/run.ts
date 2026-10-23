// Runs the agent once, checks its report, and hands back both, or a StopRun explaining what went wrong.
import { existsSync, statSync } from "node:fs";
import { resolve } from "node:path";
import { query, type SDKResultMessage } from "@anthropic-ai/claude-agent-sdk";

import { DebugLog } from "./debug_log.js";
import { Guard } from "./guard.js";
import { JUDGE } from "./judge.js";
import { SKILLS_FOLDER, buildOptions } from "./options.js";
import type { Report } from "./schema.js";
import { type Verification, verify, withoutFailures } from "./verify.js";

// Something the user can fix. job_fit.ts prints the message and exits, with no stack trace.
export class StopRun extends Error {
  name = "StopRun";
}

export class Run {
  constructor(
    readonly report: Report, // after the checks: failed claims removed
    readonly rawReport: Report, // exactly what the agent wrote
    readonly steps: string[], // every tool it called, in order: its trajectory
    readonly blocked: string[], // what the guardrail stopped
    readonly verification: Verification | undefined, // undefined when the checks are turned off
    readonly turns: number,
    readonly costUsd: number, // the agent plus the judge
  ) {}

  get summary(): string {
    const removed = this.verification ? ` · ${this.verification.failed.length} claims removed` : "";
    return `${this.turns} turns · $${this.costUsd.toFixed(3)}${removed}`;
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

export function guardFor(job: string, cv: string): Guard {
  const files = new Set([resolve(cv), ...(isLink(job) ? [] : [resolve(job)])]);
  return new Guard(files, new Set(isLink(job) ? [job] : []), SKILLS_FOLDER);
}

// The agent streams messages while it works; the last one carries the answer.
export async function agentResult(
  prompt: string,
  guard: Guard,
  showSteps: boolean,
  log?: DebugLog,
): Promise<[SDKResultMessage | undefined, string[]]> {
  let result: SDKResultMessage | undefined;
  const steps: string[] = [];
  try {
    for await (const message of query({ prompt, options: buildOptions(guard, showSteps, log) })) {
      if (message.type === "assistant") {
        steps.push(...message.message.content.flatMap((block) => (block.type === "tool_use" ? [block.name] : [])));
      } else if (message.type === "result") {
        result = message;
      }
    }
  } catch (error) {
    const reason = error instanceof Error ? error.message : String(error);
    throw new StopRun(`The agent couldn't run: ${reason}\nThe Stuck? table in ../README.md has the usual fixes.`, {
      cause: error,
    });
  }
  return [result, steps];
}

export type RunSettings = { checks?: boolean; judges?: string[]; showSteps?: boolean; logPath?: string };

export async function runAgent(
  job: string,
  cv: string,
  { checks = true, judges = JUDGE, showSteps = true, logPath }: RunSettings = {},
): Promise<Run> {
  checkInputs(job, cv);
  const guard = guardFor(job, cv);
  const log = logPath ? new DebugLog(logPath) : undefined;
  const where = isLink(job) ? job : resolve(job);
  const [result, steps] = await agentResult(
    `My CV is the file ${resolve(cv)}. The job ad is at ${where}. How well do I fit?`,
    guard,
    showSteps,
    log,
  );

  // Only a "success" result carries a report; the others say why the agent stopped early.
  if (result?.subtype !== "success" || result.structured_output === undefined) {
    throw new StopRun(`The agent stopped without a report (${result?.subtype ?? "no result"}).`);
  }
  const raw = result.structured_output as Report;
  if (!raw.ad_was_read) {
    throw new StopRun(
      `Couldn't read the job ad. ${raw.verdict}\n` + `Copy the ad's text into job.md and run: npx tsx job_fit.ts job.md`,
    );
  }

  const verification = checks ? await verify(raw, cv, judges) : undefined;
  const report = verification ? withoutFailures(raw, verification) : raw;
  const cost = (result.total_cost_usd ?? 0) + (verification?.costUsd ?? 0);
  log?.write("end", {
    turns: result.num_turns,
    cost_usd: Math.round(cost * 10000) / 10000,
    blocked: guard.blocked,
    taken_out: verification ? verification.failed.map((c) => ({ claim: c.claim.claim, why: c.evidence ?? c.reason })) : [],
  });
  return new Run(report, raw, steps, guard.blocked, verification, result.num_turns, cost);
}
