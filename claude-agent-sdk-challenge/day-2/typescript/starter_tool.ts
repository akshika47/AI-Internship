// Starter: the smallest agent with one tool you write yourself. Copy it for your own idea.
import { appendFileSync } from "node:fs";
import { createSdkMcpServer, query, tool, type Options } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";

import { loadEnv } from "./agent/env.js"; // ".js" here still finds env.ts

loadEnv(import.meta.url); // finds the .env in the claude-agent-sdk-challenge folder

const USAGE = `Starter: the smallest agent with one tool you write yourself. Copy it for your own idea.

Usage:
    npx tsx starter_tool.ts "your request"

Example:
    npx tsx starter_tool.ts "Read ../examples/job.md and save me three interview questions"

As it stands, the agent can read files and has one tool of yours: save_note, which adds
a line to notes.md. To make it yours, change three things:
    1. SYSTEM_PROMPT   what your agent is for
    2. the tool()      what your tool does (send a message, call an API, update a sheet...)
    3. allowedTools    add any other tools it needs
`;

const SYSTEM_PROMPT = "You are a helpful assistant. When you find something worth keeping, save it with save_note.";

// The time now as 2026-10-20 14:05, in your own time zone.
function now(): string {
  const d = new Date();
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

const saveNote = tool("save_note", "Save one short note to the user's notes file", { note: z.string() }, async (args) => {
  appendFileSync("notes.md", `- ${now()} ${args.note}\n`);
  return { content: [{ type: "text", text: "Saved to notes.md" }] };
});

const OPTIONS: Options = {
  systemPrompt: SYSTEM_PROMPT,
  tools: ["Read"], // built-in tools it has
  mcpServers: { my_tools: createSdkMcpServer({ name: "my_tools", tools: [saveNote] }) },
  allowedTools: ["Read", "mcp__my_tools__save_note"], // run these without asking
  model: "sonnet",
  maxTurns: 10,
  maxBudgetUsd: 1.0, // a cap per run; a normal run costs a few cents
};

// Print a message and stop, like Python's sys.exit("...").
function stop(message: string): never {
  console.error(message);
  process.exit(1);
}

async function main() {
  if (process.argv.length < 3) stop(USAGE);
  try {
    for await (const message of query({ prompt: process.argv[2], options: OPTIONS })) {
      if (message.type === "result" && message.subtype === "success") {
        console.log(message.result);
        console.log(`\n${message.num_turns} turns · $${(message.total_cost_usd ?? 0).toFixed(3)}`);
      }
    }
  } catch (error) {
    stop(`The agent couldn't run: ${error instanceof Error ? error.message : String(error)}`);
  }
}

main();
