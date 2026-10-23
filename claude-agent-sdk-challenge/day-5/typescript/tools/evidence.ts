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

// If a found quote stops mid-sentence, the rest of that sentence; undefined if it ends where its sentence does.
// Found with the Day 5 step log: CVs wrap long lines, and the agent quoted only the first line of a sentence.
// The quote was real, so it passed, but the judge then rightly took out true claims that used the rest.
export function restOfSentence(quote: string, source: string): string | undefined {
  if (/[.!?;)]\s*$/.test(quote)) return undefined;
  const last = trimEnds(normalise(quote.split(ELLIPSIS).at(-1) ?? ""));
  const text = normalise(source);
  const at = text.indexOf(last);
  if (!last || at < 0) return undefined;
  const rest = text.slice(at + last.length).trimStart();
  const sentence = rest.split(/(?<=[.!?])\s| - /)[0];
  return sentence && /^[a-z0-9]/i.test(sentence) ? sentence : undefined;
}

// The next few words of a quote that stops mid-sentence, to show the agent what it left out.
export function goesOn(quote: string, source: string): string | undefined {
  return restOfSentence(quote, source)?.split(" ").slice(0, 8).join(" ");
}

// The quote, finished to the end of its sentence: what the judge should read. All of it is in the source.
export function wholeSentence(quote: string, source: string): string {
  const rest = restOfSentence(quote, source);
  return rest ? `${quote.trimEnd()} ${rest}` : quote;
}

export const checkEvidence = tool(
  "check_evidence",
  "Check that each quote is really, word for word, in the source file (a CV or document). " +
    "Run it on every quote you plan to use as evidence, before writing the report, and fix or " +
    "drop any quote it reports. Quotes must be copied exactly; use … to skip words in the middle. " +
    "Quote the whole sentence your claim relies on, even when it wraps onto the next line.",
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
    // A quote that stops mid-sentence is a problem here too: a judge will only see what you quoted.
    const problems = args.quotes.map((q) => {
      const more = goesOn(q, source);
      return problemWith(q, source) ?? (more ? `stops mid-sentence; it goes on "${more} …". Quote the whole sentence.` : undefined);
    });
    const lines = problems.map((problem, i) => `${i + 1}. ${problem ?? "OK"}`);
    const verdict = problems.every((p) => p === undefined)
      ? "PASS"
      : "FIX the quotes above, then run check_evidence again.";
    return { content: [{ type: "text", text: [...lines, verdict].join("\n") }] };
  },
  { annotations: { readOnlyHint: true } },
);
