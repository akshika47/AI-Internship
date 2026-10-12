# J2i Session 3 demo kit · business development with Claude Code

Live builds for the business development session of an AI enablement programme.
The folder is already set up. Each build is one main prompt that produces one page.
The presenter can run a build live or open the same page from `finished/`.

## Where to look

- **`start/`** is everything the presenter works with: `CLAUDE.md`, the house style, the knowledge base, the inbox and the call. Copy this folder and run the prompts inside the copy.
- **`finished/`** is everything to show without running it live. Open **`finished/all-pages.html`**: one file with every page on a tab. It works in any browser, including sandboxed ones that cannot follow links between local files.
- **`PROMPTS.md`** is what to paste, in order.

Deck: https://claude.ai/artifact/66Ycaor6HCpxs6oQVZL8kS

## What is in the folder

| Path | What it is |
|---|---|
| `PROMPTS.md` | The prompts, in order, with what to say and what to point out |
| `start/CLAUDE.md` | Who the client is, the ideal client, the four qualification checks, the house rules |
| `start/style/house.css` | The house style every result page uses |
| `start/knowledge/` | The knowledge base structure. The files are added privately (needed for Build 4 only) |
| `start/inbound/`, `start/calls/` | A fictional inbox and a fictional discovery call |
| `finished/` | Pages from a tested run: the fallback. Open `finished/all-pages.html` |

## Run it

```
cp -r start run-1 && cd run-1 && claude
```

Then paste the prompts from `PROMPTS.md` one at a time. Always work in a copy so `start/` stays clean.

## What you need

- Claude Code
- Apollo and Clay connected as MCP servers (`/mcp` shows both). Only Build 2 uses them
- A browser beside the terminal

## The builds

| Build | Main prompt | Result |
|---|---|---|
| 1 · Battlecards | 1.1 | `battlecards.html`: what two competitors changed in a year, then a card for each |
| | 1.2 | `call-prep.html`: a 30-second answer and three questions from the card |
| | 1.3 | A saved skill, so it reruns monthly and reports only what changed |
| 2 · Who to call first | 2.1 | `targets.html`: a scored list from public contract data, sortable |
| | 2.2 | An Apollo list, deals and tasks for the top three |
| | 2.3 | A saved skill |

Build 2 stops once to state the Apollo and Clay credit cost and waits for a yes (about 5 Apollo credits and 6 Clay runs).
When a step asks for permission to write to `.claude/skills/`, approve it.

## The fallback pages

The pages in `finished/` come from a step-by-step run on 12 Oct 2026, so there are more of them than the builds
above produce today. They show the same results.

### Opening the tested pages

Open `finished/all-pages.html` in a browser. Every page is a tab in that one file.

If you prefer separate pages, serve the folder so links work in any browser:

```
cd finished && python3 -m http.server 8765
```

then open http://localhost:8765/index.html. The same command works inside a run folder during a live build.

| Page | Build | What it shows |
|---|---|---|
| `watchlist.html` | 1 | What a buyer could choose instead, and the pages to watch |
| `watch-changes.html` | 1 | Each competitor's homepage a year ago and now |
| `battlecards.html` | 1 | What changed, then one card per competitor |
| `call-prep.html` | 1 | A 30-second answer and three questions, built from the card |
| `contracts-ending.html` | 2 | Veteran-owned firms with federal contracts ending soon (public USAspending data) |
| `inbox.html` | 2 | Keep, park or drop for each inbound lead (all fictional) |
| `targets.html` | 2 | Who to call first: the scored list, sortable, with a filter box |

These pages are the fallback for the live session: if a step stalls, open the matching page here and carry on.
Saved copies of competitor pages are not in the repo; `watch-changes.html` links to the Internet Archive instead.
Company details on `targets.html` come from public federal data plus Apollo and Clay lookups on 12 Oct 2026.
No personal names, emails or phone numbers are included.

## Rules

- Nothing is ever sent to anyone, and nobody is added to a sequence
- No personal names, emails or phone numbers on screen: titles only
- Real companies appear only with public facts. Every person who speaks is fictional and labelled
- Every claim has a source link or it is removed
- Paid steps state their credit cost before they run
