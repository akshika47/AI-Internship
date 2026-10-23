// A step log: every tool call the agent makes, written to a file you can read after the run.
//
// Agent bugs live in the steps, not in a stack trace. This records each call, each result (and how long it
// took) and each failure, one JSON line per event, in the same format as the Python version, so the same
// reader works on it:  cd .. && uv run show_log.py typescript/logs/last-run.jsonl
//
// To add it to any Agent SDK agent:  const log = new DebugLog("logs/run.jsonl");  hooks: log.hooks([yourGuard])
import { appendFileSync, mkdirSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import type { HookCallback, Options } from "@anthropic-ai/claude-agent-sdk";

const KEEP_CHARS = 400; // long inputs and results are cut, so a log stays readable

function short(value: unknown): string {
  const text = typeof value === "string" ? value : JSON.stringify(value) ?? "";
  return text.length <= KEEP_CHARS ? text : `${text.slice(0, KEEP_CHARS)}… (+${text.length - KEEP_CHARS} chars)`;
}

export class DebugLog {
  private started = performance.now();

  constructor(readonly path: string) {
    mkdirSync(dirname(path), { recursive: true });
    writeFileSync(path, ""); // one run per file
  }

  write(event: string, fields: Record<string, unknown>): void {
    const t = Math.round((performance.now() - this.started) / 10) / 100;
    appendFileSync(this.path, JSON.stringify({ t, event, ...fields }) + "\n");
  }

  before: HookCallback = async (input) => {
    if (input.hook_event_name === "PreToolUse") {
      this.write("call", { id: input.tool_use_id, tool: input.tool_name, input: short(input.tool_input) });
    }
    return {};
  };

  after: HookCallback = async (input) => {
    if (input.hook_event_name === "PostToolUse") {
      this.write("result", { id: input.tool_use_id, tool: input.tool_name, output: short(input.tool_response), ms: input.duration_ms });
    }
    return {};
  };

  failed: HookCallback = async (input) => {
    if (input.hook_event_name === "PostToolUseFailure") {
      this.write("error", { id: input.tool_use_id, tool: input.tool_name, error: short(input.error), ms: input.duration_ms });
    }
    return {};
  };

  // The log runs first, so even a call your guard blocks is recorded.
  hooks(extraPreToolHooks: HookCallback[] = []): Options["hooks"] {
    return {
      PreToolUse: [{ hooks: [this.before, ...extraPreToolHooks] }],
      PostToolUse: [{ hooks: [this.after] }],
      PostToolUseFailure: [{ hooks: [this.failed] }],
    };
  }
}
