// Code that runs at points in the agent's loop. Here: print each step as it happens.
import { basename } from "node:path";
import type { HookCallback } from "@anthropic-ai/claude-agent-sdk";

type ToolInput = Record<string, any>; // whatever the agent passed to the tool

// One line per tool: how to describe that step to a person.
const STEP_LABELS: Record<string, (args: ToolInput) => string> = {
  Read: (args) => `reading ${basename(args.file_path)}`,
  mcp__jobfit__fetch_job_ad: () => "fetching the job ad",
  mcp__jobfit__check_tracker: () => "checking your tracker",
  mcp__jobfit__save_to_tracker: (args) => `saving to your tracker: ${args.role}, ${args.fit_score}/10`,
  Skill: (args) => `opening your skill: ${args.skill ?? ""}`,
  mcp__jobfit__check_cv_bullets: (args) => `checking ${args.bullets.length} CV bullets`,
  mcp__jobfit__check_evidence: (args) => `checking ${args.quotes.length} quotes are really in the CV`,
  StructuredOutput: () => "writing up the report",
};

// For a tool without a friendly label: show its name and the start of its input.
function rawLabel(tool: string): (args: ToolInput) => string {
  return (args) => `${tool} ${JSON.stringify(args).slice(0, 60)}`;
}

// Runs before every tool call, so you can watch the agent work.
export const showToolUse: HookCallback = async (input) => {
  if (input.hook_event_name !== "PreToolUse") return {}; // only listening for tool calls
  const tool = input.tool_name;
  const label = STEP_LABELS[tool] ?? rawLabel(tool);
  console.log(`  · ${label(input.tool_input as ToolInput)}`);
  return {};
};
