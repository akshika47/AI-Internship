// Job-fit agent, Day 4: reviews your CV against a job ad, then checks every claim before you see it.
// Run it with no arguments to see how to use it.
import { writeFileSync } from "node:fs";
import { parseArgs } from "node:util";

import { loadEnv } from "./agent/env.js"; // ".js" here still finds env.ts
import { JUDGE, JURY } from "./agent/judge.js";
import { reportPath, toMarkdown } from "./agent/report.js";
import { StopRun, runAgent } from "./agent/run.js";

loadEnv(import.meta.url); // finds the .env in the claude-agent-sdk-challenge folder

const USAGE = `Job-fit agent, Day 4: reviews your CV against a job ad, then checks every claim before you see it.

Usage:
    npx tsx job_fit.ts JOB_AD [CV] [--no-checks] [--jury] [--log]

    JOB_AD       a link to the job ad, or a file you saved it in
    CV           your CV as a .md, .txt or .pdf file (defaults to cv.md)
    --no-checks  skip the final checks, to see what the agent wrote on its own
    --jury       three judge models vote on each claim, instead of one
    --log        write every step to logs/last-run.jsonl. Read it: cd .. && uv run show_log.py typescript/logs/last-run.jsonl

Examples:
    npx tsx job_fit.ts ../examples/jobs/fernhill-automation-analyst.md ../examples/cvs/career-changer.pdf
    npx tsx job_fit.ts ../examples/jobs/northgate-planted-instruction.md ../examples/cvs/ops-coordinator.pdf

Where things live:
    ../.claude/skills/reviewing-cvs/   the skill: SKILL.md plus reference/ files it reads when needed
    agent/                             prompt, answer shape, options, step log, guard, judge, verify, run, report
    tools/                             fetch_job_ad, check_tracker, save_to_tracker, check_cv_bullets, check_evidence
    shortlist.ts                       the same agent over a whole folder of job ads
    run_evals.ts                       evaluates the agent: evidence, support, steps followed, planted instructions
`;

type Args = { job: string; cv: string; noChecks: boolean; jury: boolean; log: boolean };

// Print a message and stop, like Python's sys.exit("...").
function exit(message: string): never {
  console.error(message);
  process.exit(1);
}

// What you typed after "npx tsx job_fit.ts", or the usage text if it doesn't fit.
function parse(): Args {
  try {
    const { values, positionals } = parseArgs({
      options: {
        "no-checks": { type: "boolean", default: false },
        jury: { type: "boolean", default: false },
        log: { type: "boolean", default: false },
      },
      allowPositionals: true,
    });
    if (positionals.length < 1 || positionals.length > 2) exit(USAGE);
    return { job: positionals[0], cv: positionals[1] ?? "cv.md", noChecks: values["no-checks"], jury: values.jury, log: values.log };
  } catch {
    exit(USAGE); // an option it doesn't know, e.g. --checks
  }
}

async function main(args: Args): Promise<void> {
  const run = await runAgent(args.job, args.cv, {
    checks: !args.noChecks,
    judges: args.jury ? JURY : JUDGE,
    logPath: args.log ? "logs/last-run.jsonl" : undefined,
  });
  const path = reportPath(run.report.role, args.cv, args.noChecks ? "no-checks" : "");
  writeFileSync(path, toMarkdown(run.report));
  for (const line of run.report.removed ?? []) console.log(`  · taken out: ${line}`);
  console.log(`\nSaved ${path} · ${run.summary}\nYour tracker is in applications.csv`);
}

try {
  await main(parse());
} catch (error) {
  if (!(error instanceof StopRun)) throw error; // a real bug: show the whole stack trace
  exit(`\n${error.message}`);
}
