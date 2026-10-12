# Prompts · Session 3 (v5.1)

The folder is already set up: CLAUDE.md (who J2i is, the ideal client, the four checks, the house rules), the house style, the knowledge base, a fictional inbox and a fictional discovery call.

Each build is one prompt that produces one result. Run it live, or open the same page from finished/. That is the presenter's choice.

    cp -r start run-1 && cd run-1 && claude

Nothing is ever sent to anyone. No personal names, emails or phone numbers on screen.

## Build 1 · Battlecards
_Promise: competitor and market monitoring to sharpen pitch intelligence._

**1.1 Battlecards for two competitors**

> Build battlecards for GovDash (govdash.com) and Sweetspot (sweetspot.so). For each, get its homepage from about a year ago and the latest saved copy from the Wayback Machine, fetching web.archive.org/web/<timestamp>id_/<url> directly, keep the copies in watch/, and compare the wording. Then write battlecards.html. Start with a "What changed" table: old wording, new wording and a link to each archive copy. Then one card per vendor, short enough to fit a screen: what they say now, where they are strong, where J2i fits, three questions to ask a buyer who is considering them, and likely objections with an honest answer. No badmouthing. Why J2i wins stays [TO CONFIRM]. End with a short "Market" strip: two rules changing for these buyers this year, each with a source link, using at most 2 web searches, and say so when sources disagree. Check every claim against its source, remove what you cannot back up, and list what you removed at the bottom. Open the page.

- Say: One prompt. Claude finds what each competitor changed, writes the cards and checks its own claims. It takes about seven minutes.
- Look: battlecards.html. What changed at the top, then a card per competitor. Click an archive link to show the real page.
- Point out: "Why J2i wins" is [TO CONFIRM]. Real wins and losses fill it.
- If it stalls: open finished/battlecards.html.

**1.2 Use it before a call**

> I have a call tomorrow with the COO of a veteran-owned contractor who is also looking at Sweetspot. Using battlecards.html only, give me a 30-second answer to "why not just buy the software?" and the three questions I should ask. Name the line on the card each point comes from. Save it as call-prep.html and open it.

- Say: This is the point of the watch: a sharper answer in the next conversation.
- Look: call-prep.html.
- If it stalls: open finished/call-prep.html.

**1.3 Keep it running**

> Save what you did in 1.1 as a skill called competitor-watch in .claude/skills. Each run saves a new copy to watch/, compares it with the last saved copy, and updates a card only if something changed. Show me the skill file.

- Say: This is what makes it monitoring. Next month it is one command, and it reports only what changed.
- Note: Claude asks permission to write to .claude/skills. Approve it.

## Build 2 · Who to call first
_Promise: LinkedIn lead intelligence and automated prospect scoring._

**2.1 A scored list from public data**

> Build the list of who J2i should call first. Pull federal contract awards from the USAspending API (no key needed) for veteran-owned and service-disabled veteran-owned businesses, NAICS 5415 and 5416, award activity Oct 2025 to Sep 2026, awards between $1M and $20M, up to 2,000 rows, and remove duplicates. Find the services firms, not resellers, with contracts ending by 30 April 2027, and take the top 15. Look the top 10 up in Apollo with the free lookup and mark any you cannot match UNRESOLVED. Then tell me the credit cost and wait for my yes before you enrich the 5 best matches in Apollo, find titles (no names) for capture, proposal, COO and IT security at the best 3, and get open jobs and recent news for those 3 from Clay. Add the leads in inbound/. Score everyone on the four checks. Check every claim against its source and remove what you cannot back up. Write targets.html: the five best real companies to call first at the top, then a table that sorts on a column click and has a filter box, then what you removed. Open the page.

- Say: One prompt again. It will stop once to tell us the credit cost. Read it out, then say yes. It takes about fifteen minutes.
- Look: targets.html. The five to call first, then sort the table by end date.
- Point out: Public data gets a company to "worth a call". A conversation is what makes it Qualified.
- Point out: Government names rarely match a database. In testing, 4 of 10 matched cleanly.
- If it stalls: open finished/targets.html.

**2.2 Into Apollo** [writes to Apollo]

> Put the three best real companies that have an Apollo match into Apollo: add them to a list called "J2i pipeline · contracts ending", and create a deal for each, named with "(J2i demo)" at the end, with the reason to call in the description and a task "Send personal note". Search for an existing deal first. Do not add anyone to a sequence.

- Look: Apollo. Saved records, Companies for the list; Win deals, Deals; Engage, Tasks.

**2.3 Keep it running**

> Save what you did in 2.1 as a skill called find-and-score in .claude/skills, including the reseller filter, the four checks and the checking pass. Show me the skill file.

- Say: Next week this is one command, and the list is fresh.
- Note: Claude asks permission to write to .claude/skills. Approve it.

## Tool tour · How Apollo and Clay work on their own
_Before Claude Code connects them: each tool now has its own AI agent. Show it once, inside the tool._

**T.1 Apollo AI Assistant** [paid: Apollo AI Assistant, 1 of 5 free chats]

> In Apollo, open AI Assistant and type: Find veteran-owned IT services companies in the US with 50 to 500 employees, and show me the most senior business development person at each.

- Say: Apollo can now build a list from a sentence. Good for jobs inside Apollo.
- Point out: It works on Apollo's own data only. It cannot see USAspending, the web or J2i's Sprint Kit.

**T.2 Clay Claygents and AI context** [paid: Clay credits if run]

> In Clay, open Claygents, choose the Account Scoring template, and describe: Score each company on J2i's four checks (budget, authority, AI readiness, clarity), each 0 or 1. Then open AI context and show where a company's ideal client description lives.

- Say: Clay builds agents from templates: prospecting, account scoring, contact scoring, copywriting. Same idea as our skills.
- Point out: Why we still use Claude Code: it works across Apollo, Clay, public data and J2i's files, and the skills it leaves are files J2i owns, not settings inside one vendor.

## Build 3 · Outreach a person sends
_Turns the list into conversations. Supports the lead intelligence promise._

**3.1 Messages and a follow-up plan**

> For the qualified companies and the best fictional inbound leads (up to 5 in total): a LinkedIn connection note under 300 characters, a follow-up and a short email, each using that company's one verified reason to call. For inbound leads write a reply, since they contacted J2i first. For real companies, never open with "your contract ends": it is why we chose them, not the first line. Add a follow-up plan: three touches over two weeks, then a 90-day nurture if there is no reply. Then check every message against its source and remove anything you cannot back up.

- Point out: Opening with public contract data reads as surveillance. It is why we chose them, not the first line.

**3.2 Warm routes, including teaming**

> For each company, the warm route in: a prime contractor they team with, an APEX Accelerator, a veteran business association, an event, or a shared contact. Mark guesses as guesses.

- Say: In government work, a prime contractor that already works with them is often the best way in.

**3.3 Capability statement**

> Draft J2i's one-page capability statement from CLAUDE.md: core competencies, past performance, differentiators, company data (UEI, CAGE, NAICS, certifications). Anything we do not know: [TO CONFIRM].

- Point out: [TO CONFIRM] instead of invented past performance.

**3.4 One page, then a skill**

> Put it all on outreach.html, one card per company, and open it. Then save as a skill called outreach.

- Say: A person reads, edits and sends every one of these.
- If it stalls: open finished/outreach.html.

## Build 4 · The J2i assistant, win-loss and the offer
_Promises: a knowledge assistant on J2i's work, win-loss mining, and a packaged offer._

**4.1 The knowledge base**

> Show me what is in knowledge/ as a tree, with one line on what each folder holds. Then add this rule to CLAUDE.md: answer J2i questions from knowledge/ only, name the file each answer comes from, and say "not in the files" when the answer is not there.

- Look: Open the knowledge/ folder and one file from method/ and one from templates/. This is what J2i already has.
- Say: Nothing is trained. The assistant reads these files each time, which is why it can name its source.

**4.2 Ask it three questions**

> Three questions. One: what goes in an Opportunity Map? Two: how do we qualify a lead, and if knowledge/ describes it in more than one way, say so plainly. Three: what did we charge our last client?

- Point out: Each answer names its file. The kit has two qualification tools (the four checks and a longer scorecard), and the assistant says so.
- Point out: The third answer is "not in the files". It does not guess a price.

**4.3 From the call to the Opportunity Map**

> Read calls/discovery-call.md. Pull the pain points in the client's own words, every number and every objection, then draft the one-page Opportunity Map from the template in knowledge/. Mark gaps ESTIMATE NEEDED or [VERIFY]. Save to deals/harborline/.

- Say: The call is fictional, written in J2i's own discovery method. In Session 1 this took four prompts.

**4.4 Proposal, process map, stakeholder map**

> Now draft the proposal for a discovery sprint (a short project, not a training programme): problem, approach, scope and what is not included, success measures, who signs off, and price left as [J2i to set]. Then the process map and the stakeholder map, using the buying committee from the call. Save to deals/harborline/ and open a one-page summary.

- Point out: Scope and sign-off are named before any work starts.
- If it stalls: open finished/deals/harborline/.

**4.5 They said yes: close it**

> The client said yes to the discovery sprint. Draft the engagement letter and the statement of work from the templates in knowledge/, using the scope from the proposal. Leave price, dates and signatures as [J2i to set]. List anything a person must check before it is sent.

- Say: Proposal to signature is where deals stall. The templates are J2i's own, from Session 4.

**4.6 After delivery: expand**

> Imagine the sprint is delivered. From deals/harborline/, draft three things: a short case study (problem, what changed, a quote placeholder), a request asking the client to act as a reference, and a referral ask. Mark everything that needs the client's approval.

- Point out: 56% of buyers talk to a firm's references before buying. This is how J2i gets them.

**4.7 Win-loss: the first patterns**

> Create win-loss.md. Log every lead we dropped or parked today with its reason, and every objection from the call. Give each one an outcome: won, lost or no decision, and the competitor or alternative the buyer considered, if one was named. Then say what patterns you see and what we should change in our targeting or messages because of them. Save the Harborline deal into knowledge/deals/ so the assistant learns it.

- Say: With one week of leads this is a starter log. After ten deals, the same prompt finds real patterns.

**4.8 The packaged offer**

> Two prospects had the same problem: a contract ending and a small proposal team. Write a one-page offer for a fixed-scope "Recompete Readiness Map": who it is for, what the client gets, how long it takes, how it leads into the discovery sprint, and price logic with the price left as [J2i to set]. Save offer.html and open it.

- Say: This is the problem we kept seeing, turned into something J2i can sell.

**4.9 Launch plan and the numbers**

> Write a one-page launch plan for the Recompete Readiness Map in three phases (before launch, launch, after launch): the goal, one number to track and the channels for each. Then work back from J2i's goal of about ten clients this year to how many conversations, discovery calls and maps that needs, with every conversion rate marked ASSUMPTION. Save launch-plan.html and open it.

- Say: The offer is not finished until there is a plan to sell it and a number that says whether it is working.

## Packaging an offer · explained, not built
_Promise: turning a recurring client problem into a productised, repeatable tool._

No prompt here. The presenter explains it with slides 38 to 42: the three levels, the Recompete Readiness Map as an example, the five checks, the offer ladder and the numbers. Steps 4.8 and 4.9 (the offer page and the launch plan) are there if the room wants to see the example written up.

## Close · Handover and the system
_What J2i keeps, and how a new consultant starts._

**W.1 The pipeline runs itself, but never sends**

> Set up the weekly run. Write workflows/weekly-pipeline.md: what runs every Monday (rerun competitor-watch and find-and-score, create Apollo deals and tasks for new qualified companies), what never runs automatically (sending any message, anything the client sees), and where a person signs off. Write run-weekly.sh that runs it with claude -p, and show the cron line to schedule it, but do not install it. Then run it once now and show what changed.

- Say: Session 2 rule, applied to sales: the workflow finds and prepares; a person decides and sends.

**H.1 Onboarding and setup**

> Write ONBOARDING.md for a new J2i consultant: what is in this folder, the weekly routine (Monday competitor watch, Tuesday refresh the list, daily personal notes, Thursday follow-ups, Friday pipeline review), the five numbers to track, a first-week exercise, and what J2i needs to run it: a Claude plan, its own Apollo and Clay accounts and connectors, and SAM.gov registration for government work.


**H.2 Gather the system**

> Copy the parts J2i keeps into j2i-bd/: CLAUDE.md, .claude/skills, knowledge/, win-loss.md, offer.html and ONBOARDING.md. Then show it with tree -a -L 3 j2i-bd.

- Say: We started with an empty folder. This is J2i's business development system. A new consultant copies it on day one.
