// Job-fit agent, Day 2: compares your CV with a job ad and keeps an applications tracker.
// Run it with no arguments to see how to use it.
//
// Where things live:
//     agent/   what the agent is told (prompt.ts), the shape of its answer (schema.ts),
//              what it may do (options.ts), its step log (hooks.ts), running it (run.ts),
//              and the report it writes (report.ts)
//     tools/   the three tools we wrote: fetch_job_ad, check_tracker, save_to_tracker
import { writeFileSync } from "node:fs";

import { loadEnv } from "./agent/env.js"; // ".js" here still finds env.ts
import { reportPath, toMarkdown } from "./agent/report.js";
import { StopRun, runAgent } from "./agent/run.js";

loadEnv(import.meta.url); // finds the .env in the claude-agent-sdk-challenge folder

const USAGE = `Job-fit agent, Day 2: compares your CV with a job ad and keeps an applications tracker.

Usage:
    npx tsx job_fit.ts JOB_AD [CV]

    JOB_AD  a link to the job ad, or a file you saved it in
    CV      your CV as a .md, .txt or .pdf file (optional, defaults to cv.md)

Examples:
    npx tsx job_fit.ts ../examples/jobs/fernhill-automation-analyst.md ../examples/cvs/ops-coordinator.md
    npx tsx job_fit.ts https://job-boards.greenhouse.io/company/jobs/123 cv.pdf
`;

async function main(job: string, cv = "cv.md"): Promise<void> {
  const run = await runAgent(job, cv);
  const path = reportPath(run.report.role, cv);
  writeFileSync(path, toMarkdown(run.report));
  console.log(`\nSaved ${path} · ${run.summary}\nYour tracker is in applications.csv`);
}

// Print a message and stop, like Python's sys.exit("...").
function exit(message: string): never {
  console.error(message);
  process.exit(1);
}

const args = process.argv.slice(2); // what you typed after "npx tsx job_fit.ts"
if (args.length < 1 || args.length > 2) exit(USAGE);
try {
  await main(args[0], args[1]);
} catch (error) {
  if (!(error instanceof StopRun)) throw error; // a real bug: show the whole stack trace
  exit(`\n${error.message}`);
}
