// check_cv_bullets: finds the CV mistakes that have a clear right answer, with code, not opinion.
//
// The skill tells the agent to draft bullets, run this, fix what it reports, and run it again.
// The same checks score the evaluations in run_evals.ts, so "better" is measured the same way twice.
import { tool } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";

const DUTY_PHRASES = ["responsible for", "duties included", "tasked with", "in charge of"];
const WEAK_OPENERS = ["helped", "assisted", "worked on", "tried", "attempted", "involved in", "participated"];
// US stem -> UK stem, so "optimizing" and "organized" are caught too
const US_SPELLINGS: Record<string, string> = {
  optimiz: "optimis", organiz: "organis", analyz: "analys", prioritiz: "prioritis",
  utiliz: "utilis", standardiz: "standardis", behavior: "behaviour", color: "colour",
  center: "centre", modeling: "modelling", favorit: "favourit",
};
const MAX_WORDS = 30; // a bullet longer than this stops being skimmable
const NUMBER = /\d[\d,.]*/g;

export type Bullet = { from_cv: string; rewritten: string };

// One check: its name, and what it finds in (original, rewritten).
class Check {
  constructor(
    readonly name: string,
    readonly finds: (original: string, rewritten: string) => string[],
  ) {}
}

const words = (text: string): string[] => text.split(/\s+/).filter(Boolean);
const trimPunctuation = (n: string): string => n.replace(/^[.,]+|[.,]+$/g, ""); // "1,200." -> "1,200"
const numbersIn = (text: string): Set<string> => new Set((text.match(NUMBER) ?? []).map(trimPunctuation));

function dutyPhrases(original: string, rewritten: string): string[] {
  return DUTY_PHRASES.filter((p) => rewritten.toLowerCase().includes(p)).map((p) => `duty phrase "${p}"`);
}

function weakOpener(original: string, rewritten: string): string[] {
  const firstWords = words(rewritten.toLowerCase()).slice(0, 2).join(" ");
  return WEAK_OPENERS.filter((w) => firstWords.startsWith(w)).map((w) => `weak opener "${w}"`);
}

function usSpelling(original: string, rewritten: string): string[] {
  const found = rewritten.toLowerCase().match(/[a-z]+/g) ?? [];
  return found.flatMap((w) =>
    Object.keys(US_SPELLINGS)
      .filter((stem) => w.startsWith(stem))
      .map((stem) => `US spelling "${w}" (use "${US_SPELLINGS[stem] + w.slice(stem.length)}")`),
  );
}

function inventedNumbers(original: string, rewritten: string): string[] {
  const onCv = numbersIn(original);
  return [...numbersIn(rewritten)].filter((n) => !onCv.has(n)).map((n) => `number "${n}" is not in the CV line`);
}

function tooLong(original: string, rewritten: string): string[] {
  const count = words(rewritten).length;
  return count > MAX_WORDS ? [`${count} words (keep it under ${MAX_WORDS})`] : [];
}

const CHECKS = [
  new Check("duty phrases", dutyPhrases),
  new Check("weak openers", weakOpener),
  new Check("US spellings", usSpelling),
  new Check("invented numbers", inventedNumbers),
  new Check("too long", tooLong),
];

export function problemsIn(original: string, rewritten: string): string[] {
  return CHECKS.flatMap((check) => check.finds(original, rewritten));
}

export function missingKeywords(rewrites: string[], keywords: string[]): string[] {
  const text = rewrites.join(" ").toLowerCase();
  return keywords.filter((k) => !text.includes(k.toLowerCase()));
}

// The text the agent reads back: one line per bullet, then keyword coverage, then a verdict.
export function review(bullets: Bullet[], keywords: string[]): string {
  const lines = bullets.map((b, i) => `${i + 1}. ${problemsIn(b.from_cv, b.rewritten).join(", ") || "OK"}`);
  const missing = missingKeywords(bullets.map((b) => b.rewritten), keywords);
  const covered = keywords.length - missing.length;
  const notUsed = missing.length ? ` (not used: ${missing.join(", ")}; fine if the CV can't honestly support them)` : "";
  const clean = lines.every((line) => line.endsWith("OK"));
  lines.push(`Ad keywords used: ${covered} of ${keywords.length}${notUsed}`);
  lines.push(clean ? "PASS" : "FIX the issues above, then run check_cv_bullets again.");
  return lines.join("\n");
}

export const checkCvBullets = tool(
  "check_cv_bullets",
  "Check rewritten CV bullets for duty phrases, weak openers, US spellings, numbers that " +
    "aren't in the original CV line, and length; and report which of the job ad's keywords " +
    "they use. Run it after drafting bullets and again after every fix, until it says PASS.",
  {
    bullets: z.array(
      z.object({
        from_cv: z.string().describe("The original CV line, quoted exactly"),
        rewritten: z.string().describe("Your rewrite of that line"),
      }),
    ),
    ad_keywords: z
      .array(z.string())
      .describe("Short keywords from the ad's essential requirements, e.g. Python, Zapier"),
  },
  async (args) => ({ content: [{ type: "text", text: review(args.bullets, args.ad_keywords) }] }),
  { annotations: { readOnlyHint: true } }, // it only reads what you pass it
);
