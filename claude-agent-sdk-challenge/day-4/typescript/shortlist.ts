// Your weekly job shortlist: run the job-fit agent over a list of job ads and rank them.
// Run it with no arguments to see how to use it.
import { existsSync, statSync, writeFileSync } from "node:fs";
import { parseArgs } from "node:util";

import { loadEnv } from "./agent/env.js";
import { StopRun, checkInputs } from "./agent/run.js";
import { readJobList, shortlist, toMarkdownTable } from "./agent/shortlist.js";

loadEnv(import.meta.url);

const USAGE = `Your weekly job shortlist: run the job-fit agent over a list of job ads and rank them.

Usage:
    npx tsx shortlist.ts JOBS_LIST [CV] [--no-checks]

    JOBS_LIST   a text file with one job ad per line: a link, or a saved file
    CV          your CV (defaults to cv.md)

Example:
    npx tsx shortlist.ts ../examples/jobs/this-week.txt ../examples/cvs/ops-coordinator.pdf

It writes shortlist.md (ranked), one report per job, and updates applications.csv.
`;

function exit(message: string): never {
  console.error(message);
  process.exit(1);
}

function parse(): { jobsList: string; cv: string; noChecks: boolean } {
  try {
    const { values, positionals } = parseArgs({
      options: { "no-checks": { type: "boolean", default: false } },
      allowPositionals: true,
    });
    if (positionals.length < 1 || positionals.length > 2) exit(USAGE);
    return { jobsList: positionals[0], cv: positionals[1] ?? "cv.md", noChecks: values["no-checks"] };
  } catch {
    exit(USAGE);
  }
}

async function main(args: { jobsList: string; cv: string; noChecks: boolean }): Promise<void> {
  if (!existsSync(args.jobsList) || !statSync(args.jobsList).isFile()) {
    throw new StopRun(`Can't find your list at '${args.jobsList}'. Make a text file with one job link per line.`);
  }
  const jobs = readJobList(args.jobsList);
  for (const job of jobs) checkInputs(job, args.cv); // stop before spending anything if a file is missing
  console.log(`Assessing ${jobs.length} jobs, a few at a time...`);
  const outcomes = await shortlist(jobs, args.cv, !args.noChecks);
  writeFileSync("shortlist.md", toMarkdownTable(outcomes));
  console.log("\nSaved shortlist.md · your tracker is in applications.csv");
}

try {
  await main(parse());
} catch (error) {
  if (!(error instanceof StopRun)) throw error;
  exit(`\n${error.message}`);
}
