# Prompts · Session 3 live builds (v3.2)

Run in a fresh copy of start/ with `claude`. Apollo and Clay connected (/mcp). Browser beside it.
Nothing is ever sent to anyone. No personal names, emails or phone numbers on screen.

## Build 1 · Competitor watch
_Promise: competitor and market monitoring to sharpen pitch intelligence._

**1.1 House rules and ideal client**

> Read j2i_context.md. Create CLAUDE.md for this folder with two parts: J2i's house rules (the data rules) and J2i's ideal client: who they sell to, the buyer, the user, who approves, and what disqualifies a prospect. J2i qualifies leads on four checks (budget, authority, AI readiness, clarity), each 0 or 1, total 0 to 4, where 3 or 4 means Qualified; write that in. Mark anything you are unsure of as ASSUMPTION.

- Say: The folder is empty. This file is the first thing J2i keeps: every later step reads it.

**1.2 The watchlist**

> Create watchlist.md: what a J2i buyer could choose instead of J2i. Three groups: AI proposal software (GovDash at govdash.com and Sweetspot at sweetspot.so), free help (APEX Accelerators), and other consultancies. For each software vendor list the pages to watch: homepage and pricing. Add two rules that are changing for these buyers this year, each with its official page, using at most 2 web searches. Mark anything you are unsure of as ASSUMPTION.

- Say: Larger sales teams buy software for this. The method is the same at any size: a short list, checked on a schedule.

**1.3 What changed in a year**

> For GovDash and Sweetspot, use the Wayback Machine (web.archive.org, free, no key) to get the homepage as it was about a year ago and the most recent saved copy. Save both to watch/ with the date in the file name. Compare the visible text and list what changed: headline, who it is for, what it covers, security claims, and anything about consultants or recompetes. Quote the old and new wording and give the archive link for each version. Do not guess when between the two dates a change happened.

- Look: Open both archive links for one vendor side by side in the browser.
- Point out: In testing (12 Oct), one vendor had added the line "No complex implementation. No consultants." and both had moved into recompetes, which is J2i's own way in.

**1.4 Battlecards**

> Write battlecards.html, one card per competitor on the watchlist: what they say now, what changed and when, where they are strong, where J2i fits, three questions to ask a buyer who is considering them, and likely objections with an honest answer. No badmouthing. Why J2i wins stays [TO CONFIRM] until there are real wins and losses. Add a short rules-to-watch strip from the watchlist. Then do a checking pass: remove any line without a link or mark it ASSUMPTION, and show what you removed. Put today's date on each card and open the page.

- Look: The cards in the browser. This is the page to read before a call.
- Point out: "Why J2i wins" is [TO CONFIRM]. Build 4's win-loss log is what fills it.

**1.5 Into Apollo, then a skill** [writes to Apollo]

> Add GovDash and Sweetspot to an Apollo list called "J2i · competitors", so nobody prospects them by mistake. Then save steps 1.2 to 1.4 as a skill called competitor-watch in .claude/skills: each run saves a new copy to watch/, compares it with the last copy in the folder, and updates a card only if something changed. Show me the skill file.

- Say: Next month this is one command, and it only reports what changed.
- If it stalls: open finished/battlecards.html.

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

## Build 2 · A scored list from public data
_Promise: LinkedIn lead intelligence and automated prospect scoring._

**2.1 Pull contract data**

> Pull federal contract awards from the USAspending API (no key needed) for veteran-owned and service-disabled veteran-owned businesses, NAICS 5415 and 5416, award activity Oct 2025 to Sep 2026, awards between $1M and $20M. Page through the results, up to 2,000 rows, and tell me the total and whether there were more. Include the award description. Save the raw data to data/. Do not analyse it yet.

- Say: Free, official government data. Anyone in this room can check it.

**2.2 Check before trusting**

> Check what you pulled before we trust it: duplicates, missing dates, anything that would double count a company. Tell me what you found, then fix it in code and show the before and after counts.

- Point out: The same award comes back twice, because every service-disabled veteran firm is also a veteran firm.

**2.3 Contracts ending, without the resellers**

> Using the End Date field (the current end date), which companies have contracts ending between today and 30 April 2027? Group by company and rank by number of contracts ending, then soonest end date. Look at the award descriptions and flag companies whose awards are mostly hardware or software resale, because they are not J2i's ideal client. Show the top 15 services firms as a table: contracts ending, total value, earliest end date.

- Say: When a contract ends, the work is usually bid again, and the firm holding it has to write a new proposal to keep it.
- Look: Open usaspending.gov in the browser, search one company from the table, and show the real record.
- Point out: In testing, 3 of the top 5 by contract count were large resellers. Ranking by count alone points at the wrong firms.

**2.4 Add the inbox**

> Add the inbound leads in inbound/. For each item say keep, park (a real business, not now) or drop (not a business lead), with one reason. Mark them as fictional.

- Point out: Vendors, job seekers and recruiters dropped, each with a reason.

**2.5 Find them in Apollo**

> For the top 10 real companies, find each one in Apollo with the free lookup only. If there are several candidates, pick the one most likely to hold the federal contract and say why; if you cannot tell from name and domain, say UNRESOLVED. Do not spend credits.

- Point out: Government names rarely match a database. In testing, 4 of 10 needed a human check.

**2.6 Save the list into Apollo** [writes to Apollo]

> Create Apollo accounts for the matched real companies and add them to a list called "J2i pipeline · contracts ending". Skip the fictional inbound leads. Give me the link.

- Look: Switch to the Apollo tab and open the list. The companies are in the CRM.

**2.7 Company details and the buying committee** [paid: Apollo, about 5 to 10 credits]

> Enrich the top 5 companies in Apollo (size, revenue, location, what they sell). Tell me the credit cost before you start and stop if it would go over 10 credits. Then, for the best 3 fits, find the people J2i would need on its side: the capture or proposal lead, the COO or CEO, and IT security. Titles only, no names, emails or phone numbers.

- Say: Read out the credit cost Claude shows before it runs.
- Point out: A sale like this needs more than one person on the client side: a user, a buyer and an approver.

**2.8 Signals from Clay, checked** [paid: Clay, 3 companies × 2 functions]

> For the best 3 fits, get open job postings and recent company news from Clay. Flag hiring for capture, proposal or business development roles. Before using any result, check it is the same company (same website) and dated in the last six months; list what you discarded and why.

- Point out: In testing, Clay returned news about a different company with a similar name, and stories from 2018 to 2022. The job post (a Proposal Manager) was the real signal.

**2.9 Score, then check every claim**

> Score every company, real and fictional, on J2i's four checks, each 0 or 1, total 0 to 4. Large resellers fail the ideal-client fit; say so. Write one line on why to call this month, with the source link. Then do a separate checking pass: compare every claim with its source and remove anything you cannot back up. Show how many claims you checked, how many you removed, and each removed claim. Save targets.html and open it.

- Look: The ranked list in the browser, then the list of removed claims.

**2.10 Into the pipeline** [writes to Apollo]

> Create a deal in Apollo for each real company scoring 3 or 4, with a task "Send personal note" for its owner. Do not add anyone to a sequence.

- Look: Apollo: Win deals, then Deals. The pipeline exists.

**2.11 Save it as a skill**

> Save steps 2.1 to 2.9 as a skill called find-and-score, including the reseller filter, the four checks and the checking pass.

- If it stalls: open finished/targets.html; finished/scripts/ rebuilds the data.

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

**4.1 Create the assistant**

> Move sprint-kit/ into knowledge/ and add a short index. From now on answer J2i questions from knowledge/ only, name the file each answer comes from, and add that rule to CLAUDE.md.


**4.2 Ask it**

> Two questions: what are J2i's lead qualification checks, and what goes in an Opportunity Map? If knowledge/ describes qualification in more than one way, say so plainly.

- Point out: Each answer names the file it came from. The kit has two qualification tools (the Session 1 four checks and an 8-line scorecard), and the assistant says so.

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

## Showcase · The Recompete Readiness Map tool
_Promise: turning a recurring client problem into a productised, repeatable tool. Built before the session._

**S.1 Run the packaged tool**

> /recompete-readiness-map <a real company name from the list>

- Look: The one-page map for that company in the browser.
- If it stalls: open the saved map in finished/.

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
