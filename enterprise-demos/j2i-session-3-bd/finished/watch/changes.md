# Homepage changes: GovDash and Sweetspot

Compared from Wayback Machine captures of each homepage, about a year apart. Text is the visible page text only (scripts and styles removed). Files in this folder: the saved HTML (`*.html`) and extracted text (`*.txt`) for each capture.

I can only see the two captures, so a change here means the wording differs between those two dates. I do not know when in between it happened. Nothing below says what the products really do, only what the pages say.

| Version | Capture date | Archive link | Local file |
|---|---|---|---|
| GovDash, old | 2025-10-12 | https://web.archive.org/web/20251012150732/https://www.govdash.com/ | `govdash_2025-10-12.html` |
| GovDash, recent | 2026-09-14 | https://web.archive.org/web/20260914043812/https://www.govdash.com/ | `govdash_2026-09-14.html` |
| Sweetspot, old | 2025-10-09 | https://web.archive.org/web/20251009075216/https://www.sweetspot.so/ | `sweetspot_2025-10-09.html` |
| Sweetspot, recent | 2026-10-07 | https://web.archive.org/web/20261007154804/https://www.sweetspot.so/ | `sweetspot_2026-10-07.html` |

Notes on the captures:
- "About a year ago" is the nearest capture to 2025-10-12: 2025-10-12 for GovDash and 2025-10-09 for Sweetspot.
- "Most recent" is the latest capture found when asking for 2026-10-12: 2026-09-14 for GovDash and 2026-10-07 for Sweetspot. A newer page may exist that has not been captured.
- GovDash's recent capture arrived gzip-compressed. I decompressed it before saving, so the saved HTML is the decoded page.
- Wayback's "available" API returned HTTP 429 (too many requests) on every try. I fetched the captures from the `web.archive.org/web/<timestamp>id_/` addresses instead, which worked.
- Number counters on the recent GovDash page show as `0 % … 0 × … $0B+` in the text. The page animates them, so the final figures are not visible in this capture, except "300+ teams have won billions" and "$0B+ In Customer Wins".
- The old Sweetspot capture's footer says "© Sweetspot Chat, Inc. All Rights Reserved 2024" even though it was captured in October 2025. I did not use that to date the page.

## GovDash

| Check | Old (2025-10-12) | Recent (2026-09-14) |
|---|---|---|
| Headline | "Win contracts, advance missions" under the label "AI for Government Contracting" | "AI infrastructure to win government contracts" (page title: "GovDash \| AI Infrastructure for Government Contractors") |
| Subhead | "Produce high-quality proposals, run capture, organize your data and manage the full GovCon lifecycle. All in one place." | "Accelerate BD, capture, proposals, pricing, contracts, and more. Top GovCons bring their teams and AI agents together on GovDash." |
| Who it is for | Sign-up form asks "We primarily sell to": Federal, State and Local, Both, "None, I am BD consultant". Also asks annual government contract revenue (Under $10M up to $100M+) and team size ("Just me" up to "500 +"). Proof line: "Hundreds of teams have grown their businesses with GovDash". | Nav lists solutions by size: Small Business, Mid-Market, Enterprise. By role: Business Development, Capture Managers, Proposal Managers, Contract Managers, Leadership. By market: Defense, FedCiv, Health, SLED. Proof line: "300+ teams have won billions with GovDash". |
| What it covers | "Supercharge capture, proposals and contracts." Sections: Opportunity identification, Capture development, Winning proposals, Contract management, AI assistants for everyone. "Replace multiple broken tools with GovDash, one powerful AI platform for capture, proposals, contract management and more." Product menu: Capture Cloud, Proposal Cloud, Contract Cloud. | "Run opportunity identification, capture development, CRM, pricing, proposals, contracts and more - in one unified platform." Tabs: Discover, Capture, Pricer, Proposal, Contracts. Product menu adds Dash AI Agent, Data Library, Reports, Integrations. Pricing and CRM are new in the page wording. |
| Security claims | "GovDash complies with NIST 800-171 and FedRAMP Moderate standards, and runs in Azure / AWS GovCloud." "GovDash adheres to NIST-800-171 and FedRAMP Moderate controls." "GovDash runs on FedRAMP-compliant infrastructure." "All GovDash employees are based in the United States." | "FedRAMP Moderate Equivalent & Ready: C3PAO audited and on the FedRAMP marketplace. NIST SP 800-53 aligned controls platform-wide." "CUI Protection: DFARS 252.204-7012 compliance for CUI across storage, processing, and transmission." "US-Based Personnel: All team members are US-based. No offshore data handling or support." Also: "Your data is never used to train models or shared across customer boundaries." and "Self-Hosted Option: Deploy in your own cloud environment for full infrastructure control." |
| Consultants | Only in the form: "None, I am BD consultant" as a choice for "We primarily sell to". No other mention. | No mention of consultants in the page text. |
| Recompetes | No mention. | No mention. |

Other GovDash differences:
- Old claims: "Write compelling, compliant proposals 60% faster", "150% more weekly opportunities", "Cut proposal time by up to 60%". The recent text keeps the themes but shows animated counters.
- New wording on accuracy: "Built for organizations where accuracy isn't optional" and "Outputs pull from your past performance, docs, and capture context, and cite the source."
- New wording on agents: "Dash is our digital teammate" and "Top GovCons bring their teams and AI agents together".

## Sweetspot

| Check | Old (2025-10-09) | Recent (2026-10-07) |
|---|---|---|
| Headline | "AI for Government Contracting." | "AI for Government Contracting" (same words), followed by "Sweetspot is AI for GovCon, bringing capture, pipeline management, and proposal writing into one secure platform." |
| Subhead | "Sweetspot leverages AI to help you find, manage, and bid on federal, state, local, and education government opportunities." | "Replace your patchwork of tools with integrated government contracting AI for capture, pipeline management, and proposals." (under "The Complete Capture Solution"). |
| Who it is for | "Trusted by top public sector teams". Covers federal, state, local and education. Banner: "Sweetspot AI Form Fill is now live!" | "Trusted by leading government contractors". "Trusted by Fortune 500 government contractors". "500+ GovCon teams". FAQ: "The platform is designed for business development, capture, and proposal teams in government contracting firms with a history of past performance." Quote from "Leading National Security Advisory Firm". |
| What it covers | Four steps: Search, Ask, Manage, Respond. Features: AI-Powered Search, Pipelines & Pursuits, Proposal Copilot, Business Intelligence. Grants and SBIRs are named. | Menu: Opportunity Discovery, Federal Market Intelligence ("Search 167M+ federal awards"), Agentic Monitors, Pipeline Management, Proposal Engine, Organization Library, Enterprise Security. Adds DIBBS, award analysis, teaming partner search, competitor analysis, GSA eBuy and GovWin integrations. Grants and SBIRs are no longer named in the visible text (federal grants still appear under Opportunity Discovery). |
| Security claims | None in the visible text. Only: "privately trained on your company's data". | Badges "CMMC L2", "SOC 2 Type II", "FedRAMP® Moderate Authorization (In Progress)". FAQ: "meets federal cybersecurity standards and is CMMC Level 2 and SOC 2 Type II certified. Sweetspot adheres to a zero data retention policy and provides granular role-based access controls". |
| Consultants | No mention. | "No complex implementation. No consultants. Just connect your systems and start winning." Also "Most teams are fully onboarded and live within a few days, with the Sweetspot team handling setup and training." |
| Recompetes | No mention. | Menu item "Recompete Tracking: Track recompete opportunities". "Federal Market Intelligence: Search 167M+ federal awards to find incumbents, partners, competitors, recompetes, and forecasts". FAQ: "including recompetes, sole-source-eligible contracts, and small business set-asides". |

## What matters for J2i

- **"No consultants" is aimed at J2i.** Sweetspot's recent page says "No complex implementation. No consultants." That is a direct pitch against an engagement like J2i's. The old capture has no such line. I can't say when it was added.
- **Both vendors now publish security claims** that line up with the CMMC watch item in `watchlist.md`. Whether those claims are true is not checked here. Treat them as claims only.
- **Recompetes are a Sweetspot selling point in the recent capture.** The old capture has nothing. GovDash has no recompete wording in either capture.
- **GovDash moved from a project-style pitch to "AI infrastructure" and AI agents.** It now names size tiers (Small Business, Mid-Market, Enterprise). J2i's targets (mid-sized and larger veteran-owned firms) fit the Mid-Market and Enterprise tiers.

## ASSUMPTION list
- ASSUMPTION: the captures are representative of what a visitor saw on those dates. Wayback may capture a page mid-load, and animated content can be missing.
- ASSUMPTION: a phrase missing from the text of one capture was missing from the page. It may have been loaded by script and not saved.
- Pricing pages were not compared. The task covered only homepages.
