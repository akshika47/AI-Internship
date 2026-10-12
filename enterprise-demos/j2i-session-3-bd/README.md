# J2i Session 3 demo kit · business development with Claude Code

Live builds for the business development session of an AI enablement programme.
The presenter starts from an almost empty folder and builds a sales system step by step.

| Path | What it is |
|---|---|
| `PROMPTS.md` | The prompts, in order, with what to say and what to point out |
| `start/` | What the client has before the session: context notes, a fictional inbox, a fictional discovery call |
| `start/sprint-kit/` | Empty here. The client's templates are added privately (needed for Build 4 only) |
| `finished/` | Results of a tested run of Build 1, as the fallback if a step stalls |

## Run it

```
cp -r start run-1 && cd run-1 && claude
```

Then paste the prompts from `PROMPTS.md` one at a time. Always work in a copy so `start/` stays clean.

## What you need

- Claude Code
- Apollo and Clay connected as MCP servers (`/mcp` shows both). Build 1 needs Apollo only for step 1.5
- A browser beside the terminal

## Build 1 · Competitor watch (tested 12 Oct 2026)

1. House rules and ideal client
2. A watchlist of what a buyer could choose instead
3. What each competitor changed on its homepage in a year, from Internet Archive copies
4. A battlecard per competitor, with a checking pass
5. An Apollo list of competitors, and a skill that reruns monthly

Steps 1 to 4 took about 7 minutes on Sonnet; step 3 is the slow one. When step 5 asks for
permission to write to `.claude/skills/`, approve it.

## Rules

- Nothing is ever sent to anyone, and nobody is added to a sequence
- No personal names, emails or phone numbers on screen: titles only
- Real companies appear only with public facts. Every person who speaks is fictional and labelled
- Every claim has a source link or it is removed
- Paid steps state their credit cost before they run
