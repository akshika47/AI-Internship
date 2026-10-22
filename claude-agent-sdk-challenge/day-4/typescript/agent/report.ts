// Turns the agent's answer into the Markdown report you open.
import { basename, extname } from "node:path";

import type { Report } from "./schema.js";

type Section = {
  heading: string;
  lines: (report: Report) => string[]; // an empty list leaves the section out
};

const SECTIONS: Section[] = [
  {
    heading: "Where you're strong",
    lines: (r) => r.strengths.map((s) => `- **${s.requirement}**: "${s.cv_quote}"` + (s.note ? ` (${s.note})` : "")),
  },
  { heading: "Gaps", lines: (r) => r.gaps.map((g) => `- **${g.requirement}**: ${g.how_to_close_it}`) },
  { heading: "CV bullets for this role", lines: (r) => r.cv_bullets.map((b) => `- ${b.rewritten}\n  *was: ${b.from_cv}*`) },
  { heading: "Cover note opener", lines: (r) => (r.opening_line ? [`> ${r.opening_line}`] : []) },
  { heading: "Compared with your tracker", lines: (r) => [r.tracker_note] },
  { heading: "Taken out by the checks", lines: (r) => (r.removed ?? []).map((line) => `- ${line}`) },
];

export function toMarkdown(report: Report): string {
  const header = `# ${report.role}\n\n**${report.decision} · fit ${report.fit_score}/10.** ${report.verdict}\n`;
  const body = SECTIONS.map((s) => ({ heading: s.heading, lines: s.lines(report) }))
    .filter((s) => s.lines.length > 0)
    .map((s) => `## ${s.heading}\n\n${s.lines.join("\n")}\n`);
  return [header, ...body].join("\n");
}

// job-fit-junior-ai-automation-analyst-fernhill-health-cv.md: one report per job and CV.
// suffix marks a variant, e.g. "no-skill", so a comparison run doesn't overwrite the real one.
export function reportPath(role: string, cv: string, suffix = ""): string {
  const cvName = basename(cv, extname(cv)); // "../examples/cvs/ops-coordinator.md" becomes "ops-coordinator"
  const slug = `${role} ${cvName} ${suffix}`.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 90);
  return `job-fit-${slug || "report"}.md`;
}
