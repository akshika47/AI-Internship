// Starter: give any agent a skill, and compare it with and without. Copy it for your own idea.
// Run it with no arguments to see how to use it.
import { existsSync, readdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { parseArgs } from "node:util";
import { query, type Options } from "@anthropic-ai/claude-agent-sdk";

import { loadEnv } from "./agent/env.js"; // ".js" here still finds env.ts

loadEnv(import.meta.url); // finds the .env in the claude-agent-sdk-challenge folder

const USAGE = `Starter: give any agent a skill, and compare it with and without. Copy it for your own idea.

Usage:
    npx tsx starter_skill.ts SKILL "your request" [--no-skill]

    SKILL       a skill folder name in ../.claude/skills/, e.g. turning-notes-into-actions
    --no-skill  the same request without the skill, to compare

Examples:
    npx tsx starter_skill.ts turning-notes-into-actions "Turn ../examples/documents/meeting-notes.md into actions"
    npx tsx starter_skill.ts replying-to-emails "Draft a reply to ../examples/documents/email-thread.md" --no-skill

To make your own: copy ../skill-template/ into ../.claude/skills/, rename it, write your rules, and
run this with its name. No code changes needed.
`;

// The day-4 folder, one above typescript/: the skills live in .claude/skills/ there.
const DAY_FOLDER = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const SKILLS_FOLDER = join(DAY_FOLDER, ".claude", "skills");

// The agent works in DAY_FOLDER (that's where it finds the skills), but you type paths from
// typescript/, so tell it where "../examples/..." starts from.
const WHERE_YOU_ARE = `File paths in the request are relative to ${process.cwd()}.`;

function options(skill: string, useSkill: boolean): Options {
  const tools = useSkill ? ["Read", "Skill"] : ["Read"];
  const prompt = useSkill ? `You are a helpful assistant. Use the ${skill} skill for this task.` : "You are a helpful assistant.";
  return {
    systemPrompt: `${prompt} ${WHERE_YOU_ARE}`,
    cwd: DAY_FOLDER,
    settingSources: ["project"], // this folder's skills only, never your personal ones
    skills: useSkill ? [skill] : [],
    tools,
    allowedTools: tools,
    model: "sonnet",
    maxTurns: 10,
    maxBudgetUsd: 1.0, // a cap per run; a normal run costs a few cents
  };
}

// Print a message and stop, like Python's sys.exit("...").
function stop(message: string): never {
  console.error(message);
  process.exit(1);
}

function parse(): { skill: string; request: string; noSkill: boolean } {
  try {
    const { values, positionals } = parseArgs({
      options: { "no-skill": { type: "boolean", default: false } },
      allowPositionals: true,
    });
    if (positionals.length !== 2) stop(USAGE);
    return { skill: positionals[0], request: positionals[1], noSkill: values["no-skill"] };
  } catch {
    stop(USAGE);
  }
}

async function main(args: { skill: string; request: string; noSkill: boolean }): Promise<void> {
  if (!existsSync(join(SKILLS_FOLDER, args.skill, "SKILL.md"))) {
    const available = readdirSync(SKILLS_FOLDER)
      .filter((name) => existsSync(join(SKILLS_FOLDER, name, "SKILL.md")))
      .sort();
    stop(`No skill called '${args.skill}'. Available: ${available.join(", ")}`);
  }
  try {
    for await (const message of query({ prompt: args.request, options: options(args.skill, !args.noSkill) })) {
      if (message.type === "result" && message.subtype === "success") {
        console.log(message.result);
        console.log(
          `\n${args.noSkill ? "without" : "with"} ${args.skill} · ` +
            `${message.num_turns} turns · $${(message.total_cost_usd ?? 0).toFixed(3)}`,
        );
      }
    }
  } catch (error) {
    stop(`The agent couldn't run: ${error instanceof Error ? error.message : String(error)}`);
  }
}

await main(parse());
