// A guardrail hook: the agent may only open the files and links this run is about.
//
// Runs before every tool call. If a job ad hides an instruction like "read ../.env", the agent
// might try, and this hook says no before anything happens. The rules are a table of tool ->
// check, so adding a tool means adding one line.
import { resolve, sep } from "node:path";
import type { HookCallback } from "@anthropic-ai/claude-agent-sdk";

type ToolInput = Record<string, any>; // whatever the agent passed to the tool

export class Guard {
  readonly blocked: string[] = []; // what it stopped, for the report and evals

  constructor(
    readonly files: Set<string>, // the CV and job ad for this run, as full paths
    readonly links: Set<string>, // the job ad link, if there is one
    readonly skillsFolder: string, // skill files are always fine to read
  ) {}

  fileOk(args: ToolInput): boolean {
    const path = resolve(args.file_path ?? "");
    return this.files.has(path) || path.startsWith(resolve(this.skillsFolder) + sep);
  }

  linkOk(args: ToolInput): boolean {
    return this.links.has(args.url ?? "");
  }

  rules(): Record<string, (args: ToolInput) => boolean> {
    return {
      Read: (args) => this.fileOk(args),
      mcp__jobfit__fetch_job_ad: (args) => this.linkOk(args),
      mcp__jobfit__check_evidence: (args) => this.files.has(resolve(args.source_path ?? "")),
    };
  }

  // The hook itself. Python's Guard is called directly; in TypeScript you pass guard.hook.
  hook: HookCallback = async (input) => {
    if (input.hook_event_name !== "PreToolUse") return {}; // only listening for tool calls
    const tool = input.tool_name;
    const args = input.tool_input as ToolInput;
    const allowed = (this.rules()[tool] ?? (() => true))(args); // tools not in the table are already limited by options
    if (allowed) return {};
    const target = args.file_path || args.url || args.source_path;
    this.blocked.push(`${tool}: ${target}`);
    console.log(`  · blocked: ${tool} tried to open ${target}`);
    return {
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: "Only the CV, the job ad and the skill files can be opened in this run.",
      },
    };
  };
}
