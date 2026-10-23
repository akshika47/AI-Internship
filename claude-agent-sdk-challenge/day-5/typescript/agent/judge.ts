// A judge: does each quote actually support the claim made from it?
//
// Code can prove a quote is in the CV (tools/evidence.ts). It can't tell whether the claim goes
// further than the quote does: "Wrote a monthly summary" doesn't support "turned marketing data
// into plain recommendations for non-specialists". That takes reading, so a separate model call,
// with no tools and one narrow job, checks it.
//
// A jury asks three different models and takes the majority, which agrees with people more
// often and leans less on one model's quirks (Verga et al., 2024, "Replacing Judges with Juries").
import { query, type Options, type SDKResultMessage } from "@anthropic-ai/claude-agent-sdk";

export const JUDGE = ["sonnet"];
export const JURY = ["haiku", "sonnet", "opus"];

export const INSTRUCTIONS = `You check claims against the exact source text they cite. Each item has a
"question" telling you which check it needs. Answer it from the quote alone.

"shows": does the quote show real evidence of the requirement? Level words in the requirement
("basic", "some", "nice to have", "essential") describe the job, not the candidate: ignore them.
Supported if the quote clearly demonstrates it; not supported if the quote only hints, or needs
an assumption to get there.

"says only": does the rewrite say only what the quote says? Rewording, reordering,
shortening and changing tense ("Write" to "Wrote", "Responsible for X" to "Ran X") are fine,
and so is linking two things the quote states side by side ("Rebuilt X; cut Y" to "Cut Y by
rebuilding X"). Not supported if it adds anything the quote doesn't say: a result,
number, audience, purpose, skill, scope or seniority, even if it sounds plausible.

"follows": does the claim follow from the quote, applied to the facts in the user's question?
Applying a stated rule to their situation (their country, their dates) and simple arithmetic
are fine. Not supported if it needs a fact that neither the quote nor the question gives.

Judge only the text given. Don't use outside knowledge, and don't give the benefit of the doubt.`;

export const VERDICTS_SCHEMA = {
  type: "object",
  properties: {
    verdicts: {
      type: "array",
      items: {
        type: "object",
        properties: {
          id: { type: "integer" },
          supported: { type: "boolean" },
          reason: { type: "string", description: "One short sentence" },
        },
        required: ["id", "supported", "reason"],
      },
    },
  },
  required: ["verdicts"],
};

// The question tells the judge which check an item needs.
export type Question = "shows" | "says only" | "follows";

// One judge's answer for one item, exactly as VERDICTS_SCHEMA describes it.
type Vote = { id: number; supported: boolean; reason: string };

export class Verdict {
  constructor(
    readonly supported: boolean,
    readonly reason: string,
    readonly votes: string, // e.g. "2 of 3" for a jury, "1 of 1" for one judge
  ) {}
}

async function oneJudge(model: string, items: object[]): Promise<[Map<number, Vote>, number]> {
  const options: Options = {
    systemPrompt: INSTRUCTIONS,
    model,
    tools: [],
    settingSources: [],
    outputFormat: { type: "json_schema", schema: VERDICTS_SCHEMA },
    maxTurns: 3,
    maxBudgetUsd: 0.25,
  };
  let result: SDKResultMessage | undefined;
  for await (const message of query({ prompt: JSON.stringify(items, null, 1), options })) {
    if (message.type === "result") result = message;
  }
  const answer = result?.subtype === "success" ? (result.structured_output as { verdicts?: Vote[] }) : undefined;
  const votes = answer?.verdicts ?? [];
  return [new Map(votes.map((v) => [v.id, v])), result?.total_cost_usd ?? 0];
}

// itemsIn: [question, claim, quote]. userQuestion gives the facts a "follows" claim may apply
// the quote to. Returns one verdict per item, by majority across the models, plus the cost.
export async function judge(
  itemsIn: [Question, string, string][],
  models: string[] = JUDGE,
  userQuestion = "",
): Promise<[Verdict[], number]> {
  if (itemsIn.length === 0) return [[], 0];
  const items = itemsIn.map(([question, claim, quote], id) => ({ id, question, claim, quote }));
  const asked = userQuestion ? items.map((item) => ({ ...item, user_question: userQuestion })) : items;
  const ballots = await Promise.all(models.map((model) => oneJudge(model, asked))); // jury members vote in parallel
  const cost = ballots.reduce((sum, [, spent]) => sum + spent, 0);
  const verdicts = items.map((_, i) => {
    const votes = ballots.flatMap(([ballot]) => ballot.get(i) ?? []);
    const yes = votes.filter((v) => v.supported).length;
    const majority = yes * 2 > models.length; // a missing vote counts as a no: no evidence, no pass
    const reason = votes.find((v) => v.supported === majority)?.reason ?? "no verdict returned";
    return new Verdict(majority, reason, `${yes} of ${models.length}`);
  });
  return [verdicts, cost];
}
