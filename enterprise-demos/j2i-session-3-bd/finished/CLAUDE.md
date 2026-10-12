# J2i house rules and ideal client

Source: `j2i_context.md`. Anything not stated there is marked **ASSUMPTION**: confirm it with J2i before relying on it.

## Part 1: House rules

### Data rules (from J2i's method)
1. Client data goes only into approved tools. ASSUMPTION: the approved-tools list is not written down yet. Ask which tools are approved before using client data anywhere new.
2. Every AI output is a draft until a named person reviews it. Say who the reviewer is; do not mark anything final yourself.
3. AI never invents a number. Where a figure is missing, write `ESTIMATE NEEDED`.
4. If a client asks how J2i works, answer honestly, including that AI is used.
5. Do not invent facts J2i has not given us: past performance, certifications held, company codes (UEI, CAGE, NAICS), headcount, revenue. Write `UNKNOWN` or `ASSUMPTION` instead.
6. Never put pricing, contracts or partner terms in the demo files; they are not in the public-safe context.
7. Inbound data in `inbound/` is fictional demo data. Treat it that way in outputs, but handle it with the rules above as if it were real.

### Output rules
8. **Anything a person will read is saved as an HTML page.** It links `style/house.css` (`<link rel="stylesheet" href="style/house.css">`, with the path adjusted for subfolders) and uses only its building blocks: `.page`, `.eyebrow`, `h1`, `.lede`, `.strip`, `.grid`, `.card`, `.tag`, `.was`/`.now`, `table.compare`, `.src`, `.foot`. No `<style>` blocks, no inline `style=` attributes, no other stylesheets or fonts. If a block is missing, ask before adding one to `house.css`.
9. **`index.html` is the home page.** It has one tile (`.card`) for every page and every Apollo list we create, each linking to its page, or for an Apollo list naming it and where it lives. Update `index.html` in the same step whenever a page or list is added. Never finish a task that adds one without updating it. ASSUMPTION: an Apollo list has no local file, so its tile carries the list name and a short note rather than a link.

## Part 2: Ideal client

### Who J2i sells to
- Mid-sized and larger veteran-owned businesses, including VA-approved vendors and government contractors. Larger firms give steadier work; small firms tend to "kick the tires".
- Commercial clients too, to build a track record (for example a healthcare clinic).
- ASSUMPTION: "mid-sized" means roughly 50 to 500 staff. J2i has not given a number.
- ASSUMPTION: the sectors with the most proof are healthcare and logistics, matching the consultant bench (data, healthcare, AI engineering, logistics, UX).

### Buyer, user, approver
Not stated in `j2i_context.md`. All three are ASSUMPTION:
- **Buyer** (the one who wants the outcome and holds the budget): owner, founder or president of a veteran-owned firm; a COO or operations head in a larger one.
- **User** (the one whose work changes): the operations, delivery, intake or back-office team that will use AI on real work. This ties to J2i's training offer.
- **Approver** (signs the spend): the owner or CEO in a mid-sized firm; in a larger one, an executive sponsor, with finance or contracts sign-off. Often the same person as the buyer in a small firm.

### Disqualifiers
Stated or implied by the method:
- Score 0 on the four checks.
- No budget signal and no one with authority after the first conversation.

All of these are ASSUMPTION, borrowed from the sprint-kit scorecard's "stop and re-think" list and J2i's direction:
- No budget owner after two conversations.
- They want the outcome but will not give access to the people whose work changes.
- Success depends on data or systems they cannot or will not let J2i near.
- No real problem and no trigger: "we should do something with AI."
- Wants only a build with no discovery. ASSUMPTION: J2i's one commitment is the 24-hour Map, and the offer is never solutioned on the call.

## Qualification: four checks, scored 0 or 1

| Check | Score 1 when |
|---|---|
| Budget | There is a budget signal: a number, an approved line, or a named owner of the spend. |
| Authority | The person we are talking to decides, or we have a direct line to who does. |
| AI readiness | They already use AI or have data and a team willing to adopt it. |
| Clarity | They can name the problem or outcome they want. |

The "Score 1 when" wording is ASSUMPTION; `j2i_context.md` names the four signals but not their anchors. Score only what is true today.

Total 0 to 4:
- **3 or 4 = Qualified.** Next step: discovery sprint.
- **1 or 2** (not Qualified): fit call or nurture.
- **0** (not Qualified): helpful email and a 90 day follow-up.

Always show the four scores and the total, not just the label. If a check cannot be judged from what we have, score it 0 and say it is unknown, not a guess.

Note: `sprint-kit/lead-qualification-scorecard.txt` uses a different 8-line, 0 to 3 scale (total 24). The four-check, 0 to 4 gate above is the one J2i uses for qualification. ASSUMPTION: the sprint-kit scorecard is background only and is not used for the Qualified decision.
