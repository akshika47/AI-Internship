// The final gate: every claim in the report has to pass two checks, or it's taken out.
//
// 1. Evidence (code): its quote is really in the CV, word for word.
// 2. Support (a judge model): the quote actually backs up what the claim says.
//
// This runs after the agent finishes, in plain TypeScript, so the agent can't skip it or talk
// its way past it. It's "no evidence, no pass", enforced rather than requested.
import { JUDGE, type Question, judge } from "./judge.js";
import type { Report } from "./schema.js";
import { problemWith, sourceText, wholeSentence } from "../tools/evidence.js";

export class Claim {
  constructor(
    readonly kind: "strength" | "bullet",
    readonly index: number, // its position in that list in the report
    readonly claim: string,
    readonly quote: string,
  ) {}

  // What the judge checks: a strength must be shown by its quote; a bullet must say only what its quote says.
  get question(): Question {
    return ({ strength: "shows", bullet: "says only" } as const)[this.kind];
  }
}

export class Check {
  constructor(
    readonly claim: Claim,
    readonly evidence: string | undefined, // undefined means the quote was found
    readonly supported: boolean,
    readonly reason: string,
  ) {}

  get passed(): boolean {
    return this.evidence === undefined && this.supported;
  }
}

export class Verification {
  constructor(
    readonly checks: Check[],
    readonly costUsd: number,
  ) {}

  get failed(): Check[] {
    return this.checks.filter((c) => !c.passed);
  }
}

export function claimsIn(report: Report): Claim[] {
  const strengths = report.strengths.map((s, i) => new Claim("strength", i, s.requirement, s.cv_quote));
  const bullets = report.cv_bullets.map((b, i) => new Claim("bullet", i, b.rewritten, b.from_cv));
  return [...strengths, ...bullets];
}

export async function verify(report: Report, cvPath: string, judges: string[] = JUDGE): Promise<Verification> {
  const cv = await sourceText(cvPath);
  const claims = claimsIn(report);
  const evidence = claims.map((c) => problemWith(c.quote, cv));
  // Only claims with real quotes go to the judge: there's no point asking about a quote that doesn't exist.
  const toJudge = claims.filter((_, i) => evidence[i] === undefined);
  // The judge reads each quote finished to the end of its sentence (all real CV text), so a quote cut at a
  // line wrap can't make a true claim look unsupported. Found with the Day 5 step log.
  const [verdicts, cost] = await judge(toJudge.map((c) => [c.question, c.claim, wholeSentence(c.quote, cv)]), judges);
  const byClaim = new Map(toJudge.map((c, i) => [c, verdicts[i]]));
  const checks = claims.map((c, i) => {
    const verdict = byClaim.get(c);
    return new Check(c, evidence[i], verdict?.supported ?? false, verdict?.reason ?? "quote not in the CV");
  });
  return new Verification(checks, cost);
}

// The report with every failed claim taken out, and a record of what was removed and why.
export function withoutFailures(report: Report, verification: Verification): Report {
  const dropped = new Set(verification.failed.map((c) => `${c.claim.kind} ${c.claim.index}`));
  const keep = <T>(kind: Claim["kind"], items: T[]) => items.filter((_, i) => !dropped.has(`${kind} ${i}`));
  return {
    ...report,
    strengths: keep("strength", report.strengths),
    cv_bullets: keep("bullet", report.cv_bullets),
    removed: verification.failed.map((c) => `${c.claim.claim}: ${c.evidence ?? c.reason}`),
  };
}
