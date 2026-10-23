// The tools we wrote, handed to the agent through one small in-process server.
//
// Each tool lives in its own file. To add one: write it with tool(), import it here, and
// add it to a list. Its full name becomes mcp__jobfit__<tool name>.
import { createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";

import { checkCvBullets } from "./cv_check.js"; // ".js" here still finds cv_check.ts
import { checkEvidence } from "./evidence.js";
import { fetchJobAd } from "./job_ad.js";
import { checkTracker, saveToTracker } from "./tracker.js";

export const CORE_TOOLS = [fetchJobAd, checkTracker, saveToTracker]; // Day 2's tools
export const SKILL_TOOLS = [checkCvBullets, checkEvidence]; // the checks the skill relies on

export function toolNames(tools: { name: string }[]): string[] {
  return tools.map((t) => `mcp__jobfit__${t.name}`);
}

// A new server for every run, so runs that overlap (shortlist.ts) each get their own.
export function jobfitServer(withSkillTools: boolean) {
  return createSdkMcpServer({ name: "jobfit", tools: [...CORE_TOOLS, ...(withSkillTools ? SKILL_TOOLS : [])] });
}
