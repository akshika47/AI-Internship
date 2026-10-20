// The tools we wrote, handed to the agent through one small in-process server.
//
// Each tool lives in its own file. To add one: write it with tool(), import it here, and
// add it to the list. Its full name becomes mcp__jobfit__<tool name>.
import { createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";

import { fetchJobAd } from "./job_ad.js"; // ".js" here still finds job_ad.ts
import { checkTracker, saveToTracker } from "./tracker.js";

export const ALL_TOOLS = [fetchJobAd, checkTracker, saveToTracker];

export const jobfitServer = createSdkMcpServer({ name: "jobfit", tools: ALL_TOOLS });
export const JOBFIT_TOOLS = ALL_TOOLS.map((t) => `mcp__jobfit__${t.name}`);
