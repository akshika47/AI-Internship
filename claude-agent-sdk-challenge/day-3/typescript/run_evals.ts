// Measures the skill: runs each scenario with and without it and scores both the same way.
//
// Usage:
//     npx tsx run_evals.ts [SCENARIOS]
//
//     SCENARIOS   a JSON list of {"name", "job", "cv"}; defaults to ../examples/scenarios.json
//
// Scores come from the same checks as the check_cv_bullets tool (tools/cv_check.ts), plus one
// honesty check: is every "from_cv" line really in the CV? Lower is better for problems.
// Each scenario runs once per mode, so expect some variation between runs.
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";

import { loadEnv } from "./agent/env.js";
import { type Run, StopRun, runAgent } from "./agent/run.js";
import type { Report } from "./agent/schema.js";
import { Semaphore } from "./agent/shortlist.js";
import { missingKeywords, problemsIn } from "./tools/cv_check.js";

loadEnv(import.meta.url);

const AT_ONCE = 3;
const MODES = [false, true]; // without the skill, then with it

class Measure {
  constructor(
    readonly name: string,
    readonly score: (report: Report, cv: string) => number, // (report, CV text) -> number
    readonly better: "lower" | "higher",
  ) {}
}

// How many bullet problems of one kind the report has, e.g. "duty phrase".
function count(kind: string): (report: Report, cv: string) => number {
  return (report) =>
    report.cv_bullets.flatMap((b) => problemsIn(b.from_cv, b.rewritten)).filter((p) => p.startsWith(kind)).length;
}

// Honesty: a "from_cv" line that isn't really in the CV means the agent made it up.
function notQuoted(report: Report, cv: string): number {
  const normalise = (text: string) => text.toLowerCase().replaceAll("*", "").split(/\s+/).filter(Boolean).join(" ");
  return report.cv_bullets.filter((b) => !normalise(cv).includes(normalise(b.from_cv).replace(/\.+$/, ""))).length;
}

function keywordCoverage(report: Report, cv: string): number {
  const keywords = report.ad_keywords;
  const used = keywords.length - missingKeywords(report.cv_bullets.map((b) => b.rewritten), keywords).length;
  return keywords.length ? Math.round((100 * used) / keywords.length) : 0;
}

const MEASURES = [
  new Measure("Duty phrases in bullets", count("duty phrase"), "lower"),
  new Measure("Weak openers in bullets", count("weak opener"), "lower"),
  new Measure("US spellings", count("US spelling"), "lower"),
  new Measure("Numbers not on the CV", count("number"), "lower"),
  new Measure("Bullets not quoted from the CV", notQuoted, "lower"),
  new Measure("Ad keywords used (%)", keywordCoverage, "higher"),
];

class Scenario {
  constructor(
    readonly name: string,
    readonly job: string,
    readonly cv: string,
  ) {}
}

type Result = { scenario: Scenario; useSkill: boolean; run?: Run };

// The job and CV paths in the JSON are relative to the JSON file itself.
function loadScenarios(path: string): Scenario[] {
  const folder = dirname(path);
  const list: { name: string; job: string; cv: string }[] = JSON.parse(readFileSync(path, "utf8"));
  return list.map((s) => new Scenario(s.name, join(folder, s.job), join(folder, s.cv)));
}

async function runOne(scenario: Scenario, useSkill: boolean, limit: Semaphore): Promise<Result> {
  let run: Run | undefined;
  try {
    run = await limit.run(() => runAgent(scenario.job, scenario.cv, useSkill, false));
  } catch (error) {
    if (!(error instanceof StopRun)) throw error;
  }
  console.log(`  · ${useSkill ? "with" : "without"} skill: ${scenario.name}${run ? "" : " (failed)"}`);
  return { scenario, useSkill, run };
}

function scores(run: Run | undefined, cvPath: string): (number | undefined)[] {
  const cv = readFileSync(cvPath, "utf8");
  return MEASURES.map((m) => (run ? m.score(run.report, cv) : undefined));
}

// Percentages are averaged across scenarios; counts are added up.
function fmt(measure: Measure, total: number, n: number): string {
  return measure.name.endsWith("(%)") ? `${(total / n).toFixed(0)}%` : String(total);
}

function table(results: Result[]): string {
  const inMode = (mode: boolean) => results.filter((r) => r.useSkill === mode);
  const byMode = MODES.map((mode) => inMode(mode).map((r) => scores(r.run, r.scenario.cv)));
  const totals = byMode.map((rows) => MEASURES.map((_, i) => rows.reduce((sum, row) => sum + (row[i] ?? 0), 0)));
  const n = byMode[1].length || 1;
  const rows = MEASURES.map(
    (m, i) => `| ${m.name} | ${fmt(m, totals[0][i], n)} | ${fmt(m, totals[1][i], n)} | ${m.better} is better |`,
  );
  const cost = MODES.map((mode) => inMode(mode).reduce((sum, r) => sum + (r.run?.costUsd ?? 0), 0));
  return [
    `# Skill evaluation: ${n} scenarios`,
    "", "| Measure | Without skill | With skill | |", "|---|---|---|---|", ...rows,
    `| Cost | $${cost[0].toFixed(2)} | $${cost[1].toFixed(2)} | |`, "",
  ].join("\n");
}

async function main(path: string): Promise<void> {
  const scenarios = loadScenarios(path);
  console.log(`Running ${scenarios.length} scenarios with and without the skill...`);
  const limit = new Semaphore(AT_ONCE);
  const results = await Promise.all(scenarios.flatMap((s) => MODES.map((mode) => runOne(s, mode, limit))));
  const report = table(results);
  writeFileSync("eval-results.md", report);
  console.log("\n" + report + "\nSaved eval-results.md");
}

try {
  await main(process.argv[2] ?? "../examples/scenarios.json");
} catch (error) {
  if (!(error instanceof StopRun)) throw error;
  console.error(`\n${error.message}`);
  process.exit(1);
}
