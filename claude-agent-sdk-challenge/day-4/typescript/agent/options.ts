// Everything the agent is allowed to do, in one place: prompt, tools, skills, guardrail, limits.
//
// This is the Day 3 agent (skill on) plus a guardrail hook. What happens after it finishes, the
// evidence and support checks, lives in agent/verify.ts.
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import type { Options } from "@anthropic-ai/claude-agent-sdk";

import type { Guard } from "./guard.js";
import { showToolUse } from "./hooks.js";
import { SKILL_PROMPT } from "./prompt.js";
import { REPORT_SCHEMA } from "./schema.js";
import { CORE_TOOLS, SKILL_TOOLS, jobfitServer, toolNames } from "../tools/index.js";

// The day-4 folder, one above typescript/: skills load from .claude/skills/ there.
export const DAY_FOLDER = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..");
export const SKILLS_FOLDER = join(DAY_FOLDER, ".claude", "skills");
const SKILLS = ["reviewing-cvs"]; // the only skills this agent may use
const BUILT_IN = ["Read", "Skill"]; // Skill is the tool that opens a skill

export function buildOptions(guard: Guard, showSteps = true): Options {
  const hooks = showSteps ? [showToolUse, guard.hook] : [guard.hook]; // the guard always runs; the step log is optional
  return {
    systemPrompt: SKILL_PROMPT,
    cwd: DAY_FOLDER,
    settingSources: ["project"], // this folder's skills only, never your personal ones
    skills: SKILLS,
    tools: BUILT_IN,
    mcpServers: { jobfit: jobfitServer(true) },
    allowedTools: [...BUILT_IN, ...toolNames([...CORE_TOOLS, ...SKILL_TOOLS])],
    outputFormat: { type: "json_schema", schema: REPORT_SCHEMA },
    hooks: { PreToolUse: [{ hooks }] },
    model: "sonnet",
    maxTurns: 25, // two check-and-fix loops now
    maxBudgetUsd: 1.0, // a cap per run; a normal run costs a few cents
  };
}
