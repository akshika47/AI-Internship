// Checks the judge itself: runs it on cases where we know the right answer.
// Run it with --help to see how to use it.
import { readFileSync } from "node:fs";
import { parseArgs } from "node:util";

import { loadEnv } from "./agent/env.js";
import { JUDGE, JURY, type Question, type Verdict, judge } from "./agent/judge.js";

loadEnv(import.meta.url);

const USAGE = `Checks the judge itself: runs it on cases where we know the right answer.

Usage:
    npx tsx check_judge.ts [CASES] [--jury]

    CASES   a JSON list of {"question", "claim", "quote", "expected", "note", "user_question"?};
            defaults to ../evals/judge-cases.json

A judge you haven't tested is just another opinion. Add a case every time it gets one wrong,
and run this before you trust a change to its instructions. Costs about a cent.
`;

type Case = { question: Question; claim: string; quote: string; expected: boolean; note: string; user_question?: string };

async function main(path: string, models: string[]): Promise<boolean> {
  const cases: Case[] = JSON.parse(readFileSync(path, "utf8"));
  // Cases that share a user question go to the judge together, with that question as context.
  const byQuestion = new Map<string, Case[]>();
  for (const c of cases) byQuestion.set(c.user_question ?? "", [...(byQuestion.get(c.user_question ?? "") ?? []), c]);
  const results: [Case, Verdict][] = [];
  let cost = 0;
  for (const [userQuestion, group] of byQuestion) {
    const [verdicts, spent] = await judge(group.map((c) => [c.question, c.claim, c.quote]), models, userQuestion);
    results.push(...group.map((c, i): [Case, Verdict] => [c, verdicts[i]]));
    cost += spent;
  }
  for (const [c, verdict] of results) {
    const mark = verdict.supported === c.expected ? "right" : "WRONG";
    console.log(`  ${mark}  ${verdict.supported ? "pass" : "fail"} (${verdict.votes})  ${c.note}`);
  }
  const right = results.filter(([c, v]) => v.supported === c.expected).length;
  console.log(`\n${right} of ${results.length} right with ${models.join(", ")} · $${cost.toFixed(3)}`);
  return right === results.length;
}

// What you typed after "npx tsx check_judge.ts", or the usage text if it doesn't fit.
function parse(): { cases: string; jury: boolean } {
  try {
    const { values, positionals } = parseArgs({
      options: { jury: { type: "boolean", default: false } },
      allowPositionals: true,
    });
    if (positionals.length > 1) throw new Error("too many arguments");
    return { cases: positionals[0] ?? "../evals/judge-cases.json", jury: values.jury };
  } catch {
    console.error(USAGE); // an option it doesn't know, e.g. --help
    process.exit(1);
  }
}

const args = parse();
process.exit((await main(args.cases, args.jury ? JURY : JUDGE)) ? 0 : 1);
