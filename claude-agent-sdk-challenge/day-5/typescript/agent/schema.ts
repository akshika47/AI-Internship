// The exact shape of the agent's answer. The SDK makes it fill in every field.

export const REPORT_SCHEMA = {
  type: "object",
  properties: {
    ad_was_read: { type: "boolean", description: "False if the job ad couldn't be read in full" },
    role: { type: "string", description: "Job title and company only, e.g. \"Data Analyst, Monzo\". No notes." },
    fit_score: { type: "integer", minimum: 0, maximum: 10 },
    decision: { type: "string", enum: ["Apply now", "Apply after closing a gap", "Skip this one"] },
    verdict: { type: "string", description: "Two sentences explaining the decision" },
    strengths: {
      type: "array",
      items: {
        type: "object",
        properties: {
          requirement: { type: "string", description: "What the job asks for" },
          cv_quote: { type: "string", description: "Exact words from the CV that show it. Use … to skip words." },
          note: { type: "string", description: "Optional: how well it matches, in a few words" },
        },
        required: ["requirement", "cv_quote"],
      },
    },
    gaps: {
      type: "array",
      items: {
        type: "object",
        properties: {
          requirement: { type: "string" },
          how_to_close_it: { type: "string" },
        },
        required: ["requirement", "how_to_close_it"],
      },
    },
    cv_bullets: {
      type: "array",
      maxItems: 3,
      items: {
        type: "object",
        properties: {
          from_cv: { type: "string", description: "The original CV line, quoted exactly" },
          rewritten: { type: "string", description: "The rewrite for this job" },
        },
        required: ["from_cv", "rewritten"],
      },
    },
    ad_keywords: {
      type: "array",
      items: { type: "string" },
      description: "Short keywords from the ad's essential requirements",
    },
    opening_line: { type: "string", description: "First line of a cover note" },
    tracker_note: { type: "string", description: "One sentence comparing this job with the tracker" },
  },
  required: [
    "ad_was_read", "role", "fit_score", "decision", "verdict", "strengths", "gaps", "cv_bullets",
    "ad_keywords", "opening_line", "tracker_note",
  ],
};

// The same shape as REPORT_SCHEMA, so TypeScript knows what the report holds.
export type Report = {
  ad_was_read: boolean;
  role: string;
  fit_score: number;
  decision: "Apply now" | "Apply after closing a gap" | "Skip this one";
  verdict: string;
  strengths: { requirement: string; cv_quote: string; note?: string }[];
  gaps: { requirement: string; how_to_close_it: string }[];
  cv_bullets: { from_cv: string; rewritten: string }[];
  ad_keywords: string[];
  opening_line: string;
  tracker_note: string;
  removed?: string[]; // added by the final checks (agent/verify.ts), never by the agent
};
