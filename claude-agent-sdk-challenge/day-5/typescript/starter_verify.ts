// Starter: an agent that answers from a document, where every claim must quote it and pass two checks.
// Run it with no arguments to see how to use it.
import { existsSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { parseArgs } from "node:util";
import { query, type Options, type SDKResultMessage } from "@anthropic-ai/claude-agent-sdk";

import { loadEnv } from "./agent/env.js"; // ".js" here still finds env.ts
import { Guard } from "./agent/guard.js";
import { JUDGE, JURY, judge } from "./agent/judge.js";
import { problemWith, sourceText } from "./tools/evidence.js";

loadEnv(import.meta.url); // finds the .env in the claude-agent-sdk-challenge folder

const USAGE = `Starter: an agent that answers from a document, where every claim must quote it and pass two checks.

Usage:
    npx tsx starter_verify.ts SOURCE "your question" [--no-checks] [--jury]

Example:
    npx tsx starter_verify.ts ../examples/documents/policy.md "Can I work from Spain for three weeks this summer?"

This is "no evidence, no pass" for any agent that answers from sources (a RAG assistant, a
policy bot, a research helper). The agent must return each claim with an exact quote. Then:
    1. code checks the quote is really in the document
    2. a judge model checks the quote actually supports the claim
Claims that fail either check are shown as taken out, with the reason.
`;

const PROMPT = `Answer the user's question using only the document they give you. Read it first.
Break your answer into short claims. Every claim needs a quote copied word for word from the
document (use … to skip words). If the document doesn't answer something, say so as a claim
with an empty quote rather than guessing.`;

const ANSWER_SCHEMA = {
  type: "object",
  properties: {
    claims: {
      type: "array",
      items: {
        type: "object",
        properties: { claim: { type: "string" }, quote: { type: "string" } },
        required: ["claim", "quote"],
      },
    },
  },
  required: ["claims"],
};

type Claim = { claim: string; quote: string };
type Args = { source: string; question: string; noChecks: boolean; jury: boolean };

function options(source: string): Options {
  const guard = new Guard(new Set([source]), new Set(), join(dirname(source), "no-skills")); // this document only
  return {
    systemPrompt: PROMPT,
    tools: ["Read"],
    allowedTools: ["Read"],
    settingSources: [],
    outputFormat: { type: "json_schema", schema: ANSWER_SCHEMA },
    hooks: { PreToolUse: [{ hooks: [guard.hook] }] },
    model: "sonnet",
    maxTurns: 6,
    maxBudgetUsd: 0.5,
  };
}

// Print a message and stop, like Python's sys.exit("...").
function exit(message: string): never {
  console.error(message);
  process.exit(1);
}

function parse(): Args {
  try {
    const { values, positionals } = parseArgs({
      options: { "no-checks": { type: "boolean", default: false }, jury: { type: "boolean", default: false } },
      allowPositionals: true,
    });
    if (positionals.length !== 2) exit(USAGE);
    return { source: positionals[0], question: positionals[1], noChecks: values["no-checks"], jury: values.jury };
  } catch {
    exit(USAGE);
  }
}

async function main(args: Args): Promise<void> {
  const source = resolve(args.source);
  if (!existsSync(source) || !statSync(source).isFile()) exit(`Can't find ${args.source}.`);
  let result: SDKResultMessage | undefined;
  try {
    for await (const message of query({ prompt: `Document: ${source}\nQuestion: ${args.question}`, options: options(source) })) {
      if (message.type === "result") result = message;
    }
  } catch (error) {
    exit(`The agent couldn't run: ${error instanceof Error ? error.message : String(error)}`);
  }
  const answer = result?.subtype === "success" ? (result.structured_output as { claims?: Claim[] }) : undefined;
  const claims = answer?.claims ?? [];
  const text = await sourceText(source);

  const gaps = claims.filter((c) => !c.quote); // "the document doesn't say": honest, not a failure
  const quoted = claims.filter((c) => c.quote);
  const evidence = quoted.map((c) => problemWith(c.quote, text));
  const toJudge = quoted.flatMap((c, i) => (evidence[i] === undefined ? [{ i, c }] : []));
  const [verdicts, judgeCost] = args.noChecks
    ? [[], 0]
    : await judge(toJudge.map(({ c }) => ["follows", c.claim, c.quote]), args.jury ? JURY : JUDGE, args.question);
  const rejected = new Map<number, string>(
    toJudge.flatMap(({ i }, n) => (verdicts[n].supported ? [] : [[i, verdicts[n].reason] as const])),
  );

  const reasons = evidence.map((problem, i) => (args.noChecks ? undefined : (problem ?? rejected.get(i))));
  quoted.forEach((claim, i) => {
    const why = reasons[i];
    console.log(`${why ? "  taken out" : "  passed  "}  ${claim.claim}`);
    console.log(`              quote: "${claim.quote}"` + (why ? `\n              why: ${why}` : ""));
  });
  for (const claim of gaps) console.log(`  not in doc  ${claim.claim}`);
  const cost = (result?.total_cost_usd ?? 0) + judgeCost;
  const passed = reasons.filter((why) => why === undefined).length;
  console.log(
    `\n${quoted.length} quoted claims · ${passed} passed · ${gaps.length} gaps the document doesn't cover · $${cost.toFixed(3)}`,
  );
}

await main(parse());
