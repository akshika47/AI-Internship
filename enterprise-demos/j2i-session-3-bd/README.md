# J2i Session 3 demo kit · business development with Claude Code

Live builds for the business development session of an AI enablement programme.
The presenter starts from an almost empty folder and builds a sales system step by step.

| Path | What it is |
|---|---|
| `PROMPTS.md` | The prompts, in order, with what to say and what to point out |
| `start/` | What the client has before the session: context notes, a fictional inbox, a fictional discovery call |
| `start/sprint-kit/` | Empty here. The client's templates are added privately (needed for Build 4 only) |
| `start/style/house.css` | The house style every result page uses |
| `finished/` | Pages from a tested run. Build 1 in full; Build 2 without the pages that rank real companies |

## Run it

```
cp -r start run-1 && cd run-1 && claude
```

Then paste the prompts from `PROMPTS.md` one at a time. Always work in a copy so `start/` stays clean.

## What you need

- Claude Code
- Apollo and Clay connected as MCP servers (`/mcp` shows both). Build 1 needs Apollo only for step 1.5
- A browser beside the terminal

## What a run produces

Everything a person reads is an HTML page. `index.html` is the home page, with a tile per page.

- Build 1 · Competitor watch: `watchlist.html`, `watch-changes.html`, `battlecards.html`, `call-prep.html`, and an Apollo list of competitors
- Build 2 · Who to call: `contracts-ending.html`, `inbox.html`, `targets.html` (sortable, with a filter), and an Apollo list, deals and tasks

Tested on Sonnet on 12 Oct 2026. Build 1 took about 8 minutes and Build 2 about 12, plus the Apollo and Clay steps
(5 Apollo credits, 6 Clay runs). When a step asks for permission to write to `.claude/skills/`, approve it.

`finished/` in this repo holds the Build 1 pages and the fictional inbox page only. The Build 2 pages that rank
real companies (`targets.html`, `contracts-ending.html`) and the Apollo and Clay results are left out on purpose,
because this repo is public. Their tiles on `index.html` and a few links on `watch-changes.html` therefore point at
files that are not here. A fresh run recreates them.

## Rules

- Nothing is ever sent to anyone, and nobody is added to a sequence
- No personal names, emails or phone numbers on screen: titles only
- Real companies appear only with public facts. Every person who speaks is fictional and labelled
- Every claim has a source link or it is removed
- Paid steps state their credit cost before they run
