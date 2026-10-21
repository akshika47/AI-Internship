// Everything the agent is allowed to do, in one place: prompt, tools, skills, answer shape, limits.
//
// buildOptions(true) is the Day 3 agent. buildOptions(false) is Day 2's agent, so you
// can run both on the same job and compare.
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import type { Options } from "@anthropic-ai/claude-agent-sdk";

import { showToolUse } from "./hooks.js";
import { BASE_PROMPT, SKILL_PROMPT } from "./prompt.js";
import { REPORT_SCHEMA } from "./schema.js";
import { CORE_TOOLS, SKILL_TOOLS, jobfitServer, toolNames } from "../tools/index.js";

// The day-3 folder, one above typescript/: skills load from .claude/skills/ there.
export const DAY_FOLDER = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..");
const SKILLS = ["reviewing-cvs"]; // the only skills this agent may use

export function buildOptions(useSkill: boolean, showSteps = true): Options {
  const builtIn = useSkill ? ["Read", "Skill"] : ["Read"]; // Skill is the tool that opens a skill
  const ours = [...CORE_TOOLS, ...(useSkill ? SKILL_TOOLS : [])];
  return {
    systemPrompt: useSkill ? SKILL_PROMPT : BASE_PROMPT,
    cwd: DAY_FOLDER,
    settingSources: ["project"], // this folder's skills only, never your personal ones
    skills: useSkill ? SKILLS : [],
    tools: builtIn,
    mcpServers: { jobfit: jobfitServer(useSkill) },
    allowedTools: [...builtIn, ...toolNames(ours)],
    outputFormat: { type: "json_schema", schema: REPORT_SCHEMA },
    hooks: showSteps ? { PreToolUse: [{ hooks: [showToolUse] }] } : {}, // off when runs overlap
    model: "sonnet",
    maxTurns: 20, // the check-and-fix loop adds a few turns
    maxBudgetUsd: 1.0, // a cap per run; a normal run costs a few cents
  };
}
