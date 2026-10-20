// Everything the agent is allowed to do, in one place: prompt, tools, answer shape, limits.
import type { Options } from "@anthropic-ai/claude-agent-sdk";

import { showToolUse } from "./hooks.js";
import { SYSTEM_PROMPT } from "./prompt.js";
import { REPORT_SCHEMA } from "./schema.js";
import { JOBFIT_TOOLS, jobfitServer } from "../tools/index.js";

const BUILT_IN_TOOLS = ["Read"]; // from the SDK: read a file (your CV, or a job ad you saved)

export const OPTIONS: Options = {
  systemPrompt: SYSTEM_PROMPT,
  tools: BUILT_IN_TOOLS, // the only built-in tool it has
  mcpServers: { jobfit: jobfitServer }, // plus the tools we wrote (see tools/)
  allowedTools: [...BUILT_IN_TOOLS, ...JOBFIT_TOOLS], // all of them run without asking you
  outputFormat: { type: "json_schema", schema: REPORT_SCHEMA },
  hooks: { PreToolUse: [{ hooks: [showToolUse] }] },
  model: "sonnet",
  maxTurns: 15,
  maxBudgetUsd: 1.0, // a cap per run; a normal run costs a few cents
};
