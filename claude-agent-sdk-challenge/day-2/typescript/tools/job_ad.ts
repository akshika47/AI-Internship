// A tool that fetches a job ad's full text.
//
// The SDK's built-in WebFetch hands the agent a summary of the page, which can drop the
// exact requirements. This tool downloads the page itself and returns all of its text.
import { tool } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";

const MAX_CHARS = 20_000; // a long job ad is about 8,000 characters; this leaves room

// Tags whose contents a reader never sees, and tags that start a new line.
const SKIP = new Set(["script", "style", "noscript", "svg", "head"]);
const BREAKS = new Set(["p", "li", "br", "h1", "h2", "h3", "h4", "div", "tr"]);

// Cuts a web page into pieces. Each match is one of:
//   a comment, a whole <script> or <style> (their code can contain "<", so we take them in one go),
//   a <!DOCTYPE> line, a tag like <p> or </p> or <br/>, or a run of text between tags.
const PIECES =
  /<!--[\s\S]*?-->|<(script|style)\b[\s\S]*?<\/\1\s*>|<[!?][^>]*>|<(\/?)([a-z][\w:-]*)[^>]*?(\/?)>|([^<]+|<)/gi;

// The most common &codes; in job ads. Anything else is left as it is.
const ENTITIES: Record<string, string> = {
  amp: "&", lt: "<", gt: ">", quot: '"', apos: "'", nbsp: " ",
  ndash: "–", mdash: "—", lsquo: "‘", rsquo: "’", ldquo: "“", rdquo: "”",
  hellip: "…", bull: "•", middot: "·", pound: "£", euro: "€",
};

// "&amp;" becomes "&", "&#8217;" and "&#x2019;" become "’".
function decodeEntities(text: string): string {
  return text.replace(/&(#x[0-9a-f]+|#\d+|[a-z]+);/gi, (whole, ref: string) => {
    if (!ref.startsWith("#")) return ENTITIES[ref] ?? whole;
    const code = Number(ref.replace(/^#x/i, "0x").replace(/^#/, ""));
    return code <= 0x10ffff ? String.fromCodePoint(code) : whole;
  });
}

// The visible text of a web page, skipping scripts and styles, one line per paragraph.
export function pageText(html: string): string {
  const parts: string[] = [];
  let skipping = 0; // how many hidden tags we're inside
  for (const [, , slash, tagName, selfClosing, data] of html.matchAll(PIECES)) {
    if (data !== undefined) {
      const text = decodeEntities(data).trim();
      if (skipping === 0 && text) parts.push(text + " ");
      continue;
    }
    if (tagName === undefined) continue; // a comment, a <!DOCTYPE>, or a whole script or style
    const tag = tagName.toLowerCase();
    if (BREAKS.has(tag) && slash !== "/") parts.push("\n");
    if (!SKIP.has(tag) || selfClosing === "/") continue;
    skipping = slash === "/" ? Math.max(0, skipping - 1) : skipping + 1;
  }
  const lines = parts.join("").split(/\r?\n/).map((line) => line.split(/\s+/).filter(Boolean).join(" "));
  return lines.filter((line) => line).join("\n");
}

// Download a page, or throw if the site says no (401, 403, 404...) or doesn't answer in 20 seconds.
async function download(url: string): Promise<{ finalUrl: string; html: string }> {
  const response = await fetch(url, {
    headers: { "User-Agent": "Mozilla/5.0 (job-fit agent)" },
    signal: AbortSignal.timeout(20_000),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status} ${response.statusText}`);
  return { finalUrl: response.url, html: await response.text() };
}

// "fetch failed" on its own says little; the reason underneath usually says more.
function describe(error: unknown): string {
  if (!(error instanceof Error)) return String(error);
  const cause = error.cause instanceof Error ? `: ${error.cause.message}` : "";
  return error.message + cause;
}

function failed(text: string) {
  return { content: [{ type: "text" as const, text }], isError: true };
}

export const fetchJobAd = tool(
  "fetch_job_ad",
  "Download a job ad from a link and return the page's full text. Use it for every job ad " +
    "given as a link (http or https). If the text is short or doesn't look like a job ad, " +
    "the ad is closed, blocked or loads only in a browser.",
  { url: z.string() },
  async (args) => {
    const url = args.url;
    if (!url.startsWith("http://") && !url.startsWith("https://")) return failed(`Not a web link: ${url}`);
    let page: { finalUrl: string; html: string };
    try {
      page = await download(url);
    } catch (error) {
      return failed(`Couldn't fetch ${url}: ${describe(error)}`); // blocked, not found, no connection...
    }

    const text = pageText(page.html).slice(0, MAX_CHARS);
    const words = text.split(/\s+/).filter(Boolean).length;
    const redirected = page.finalUrl.replace(/\/+$/, "") !== url.replace(/\/+$/, "");
    const note = redirected ? `(The link redirected to ${page.finalUrl}.)\n` : "";
    return { content: [{ type: "text", text: `${note}${words} words from ${page.finalUrl}:\n\n${text}` }] };
  },
  { annotations: { readOnlyHint: true } }, // it only reads a web page
);
