// Job-fit agent, Day 3: reviews your CV against a job ad using your own know-how, from a skill.
// Run it with no arguments to see how to use it.
import { writeFileSync } from "node:fs";
import { parseArgs } from "node:util";

import { loadEnv } from "./agent/env.js"; // ".js" here still finds env.ts
import { reportPath, toMarkdown } from "./agent/report.js";
import { StopRun, runAgent } from "./agent/run.js";

loadEnv(import.meta.url); // finds the .env in the claude-agent-sdk-challenge folder

const USAGE = `Job-fit agent, Day 3: reviews your CV against a job ad using your own know-how, from a skill.

Usage:
    npx tsx job_fit.ts JOB_AD [CV] [--no-skill]

    JOB_AD      a link to the job ad, or a file you saved it in
    CV          your CV as a .md, .txt or .pdf file (defaults to cv.md)
    --no-skill  run Day 2's agent instead, to compare

Examples:
    npx tsx job_fit.ts ../examples/job.md ../examples/cv.md
    npx tsx job_fit.ts ../examples/job.md ../examples/cv.md --no-skill

Where things live:
    ../.claude/skills/reviewing-cvs/   the skill: SKILL.md plus reference/ files it reads when needed
    agent/                             prompt, answer shape, options, step log, run, report
    tools/                             fetch_job_ad, check_tracker, save_to_tracker, check_cv_bullets
    shortlist.ts                       the same agent over a whole list of job ads
    run_evals.ts                       measures the skill: the same jobs with and without it
`;

// Print a message and stop, like Python's sys.exit("...").
function exit(message: string): never {
  console.error(message);
  process.exit(1);
}

// What you typed after "npx tsx job_fit.ts", or the usage text if it doesn't fit.
function parse(): { job: string; cv: string; noSkill: boolean } {
  try {
    const { values, positionals } = parseArgs({
      options: { "no-skill": { type: "boolean", default: false } },
      allowPositionals: true,
    });
    if (positionals.length < 1 || positionals.length > 2) exit(USAGE);
    return { job: positionals[0], cv: positionals[1] ?? "cv.md", noSkill: values["no-skill"] };
  } catch {
    exit(USAGE); // an option it doesn't know, e.g. --skill
  }
}

async function main(args: { job: string; cv: string; noSkill: boolean }): Promise<void> {
  const run = await runAgent(args.job, args.cv, !args.noSkill);
  const path = reportPath(run.report.role, args.cv, args.noSkill ? "no-skill" : "");
  writeFileSync(path, toMarkdown(run.report));
  console.log(`\nSaved ${path} · ${run.summary}\nYour tracker is in applications.csv`);
}

try {
  await main(parse());
} catch (error) {
  if (!(error instanceof StopRun)) throw error; // a real bug: show the whole stack trace
  exit(`\n${error.message}`);
}
