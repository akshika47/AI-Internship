// Evidence checks: is a quote really in the source? Pure code, so the answer is never a guess.
//
// The agent can run check_evidence on itself while it works, and agent/verify.ts runs the same
// check on the final report, where the agent can't skip it. "No evidence, no pass."
import { readFile } from "node:fs/promises";
import { extname } from "node:path";
import { tool } from "@anthropic-ai/claude-agent-sdk";
import { extractText } from "unpdf";
import { z } from "zod";

const ELLIPSIS = /\s*(?:\.\.\.|…)\s*/; // "first part … last part" means both parts must be there
const MIN_QUOTE_WORDS = 3; // shorter than this proves nothing: "Python" is on every CV

// The text of a CV or source file. PDFs are read with unpdf, everything else as text.
export async function sourceText(path: string): Promise<string> {
  if (extname(path).toLowerCase() !== ".pdf") return readFile(path, "utf8");
  const { text } = await extractText(new Uint8Array(await readFile(path)), { mergePages: true });
  return text;
}

// Ignore what PDFs and Markdown change: case, line breaks, bold marks, curly quotes.
export function normalise(text: string): string {
  const plain = text.replace(/[*_`]/g, "").replace(/[’‘]/g, "'").replace(/[“”]/g, '"');
  return plain.toLowerCase().split(/\s+/).filter(Boolean).join(" ");
}

// Takes spaces, full stops and double quotes off both ends, like Python's strip(' ."').
const trimEnds = (text: string): string => text.replace(/^[ ."]+|[ ."]+$/g, "");

// undefined if the quote is really in the source; otherwise what's wrong with it.
export function problemWith(quote: string, source: string): string | undefined {
  const parts = quote.split(ELLIPSIS).filter((p) => trimEnds(p)).map((p) => trimEnds(normalise(p)));
  const words = parts.reduce((sum, p) => sum + p.split(" ").filter(Boolean).length, 0);
  if (words < MIN_QUOTE_WORDS) return `too short to prove anything (${words} words)`;
  const missing = parts.filter((p) => !normalise(source).includes(p));
  return missing.length ? `not in the source: "${missing[0].slice(0, 60)}"` : undefined;
}

export const checkEvidence = tool(
  "check_evidence",
  "Check that each quote is really, word for word, in the source file (a CV or document). " +
    "Run it on every quote you plan to use as evidence, before writing the report, and fix or " +
    "drop any quote it reports. Quotes must be copied exactly; use … to skip words in the middle.",
  {
    source_path: z.string().describe("The file the quotes come from"),
    quotes: z.array(z.string()),
  },
  async (args) => {
    let source: string;
    try {
      source = await sourceText(args.source_path);
    } catch (error) {
      const reason = error instanceof Error ? error.message : String(error);
      return { content: [{ type: "text", text: `Couldn't read ${args.source_path}: ${reason}` }], isError: true };
    }
    const problems = args.quotes.map((q) => problemWith(q, source));
    const lines = problems.map((problem, i) => `${i + 1}. ${problem ?? "OK"}`);
    const verdict = problems.every((p) => p === undefined)
      ? "PASS"
      : "FIX the quotes above, then run check_evidence again.";
    return { content: [{ type: "text", text: [...lines, verdict].join("\n") }] };
  },
  { annotations: { readOnlyHint: true } },
);
