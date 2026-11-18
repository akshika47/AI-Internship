---
name: inbox-desk
description: Go through new emails for a small business, log every email as one row, draft replies to routine questions from the FAQ, and flag anything about money, complaints, safety or unclear cases for a person. Never sends anything. Use when asked to "run the inbox desk", "check the inbox", or when a scheduled task says "inbox-desk". Arguments - "dry-run" (read only, report what would change) and "since YYYY-MM-DD" (default 7 days ago).
---

# Inbox desk

Worked example for the 4-day "One job off your plate" challenge. The business is the fictional
Saltline Bike & Kayak Hire in Port Mango (see `practice-inbox/`). Copy this skill and change it for your own job.

## Never

- **Never send, forward or delete an email.** Drafts only. A person reads every draft and presses Send.
- **Never promise a refund, discount, free extra or exception.** Only the owner, Rosa, decides those. Flag them.
- **Never reply to a safety report.** Flag it as urgent at the top of the report so a person acts today.
- **Never invent a fact.** Prices, hours and rules come from `faq.md` only. If the FAQ doesn't answer it, flag it.
- **Never change a row a person has edited.** People set Status to `Done`; leave those rows alone.
- **Never write anything in dry-run.** Report what you would do instead.

## Where things are

| What | Practice inbox (files) | Real inbox (connectors) |
|---|---|---|
| Emails | `practice-inbox/emails/*.md` | Gmail, `in:inbox after:<since>` |
| Facts and policies | `practice-inbox/faq.md` | your own FAQ file or doc |
| Log | `desk/log.csv` | a Google Sheet tab called `Log` |
| Drafts | `desk/drafts/<email-id>.md` | Gmail drafts, as replies in the thread |

`desk/` sits in the folder you're working in, next to `practice-inbox/`, never inside it. Create it if it's missing.

An email's **id** is its file name without `.md`, exactly as written, leading zero included
(`07-ebike-ridge-loop-again`), or its Gmail message id.

In a chat with no files or connectors, show the log as a table and each draft in a code block instead.

## 1. Read what is already done

Read the log. Keep the set of ids already logged. **An id that is already in the log is skipped**, so running
the desk twice never adds a row twice. If the log doesn't exist yet (and not dry-run), create it with this header:

```
id,received,from,type,summary,urgency,action,status
```

## 2. Read the new emails

Every email received on or after `since` whose id is not in the log. Read the whole email, not just the subject.

## 3. Decide each one

- **type**: `question`, `booking`, `cancellation`, `complaint`, `invoice`, `review`, `safety`, `job`, `newsletter`, `other`
- **urgency**: `urgent` (safety, or a booking for today or tomorrow), `today`, `this week`, `none`
- **action**:
  - `draft reply`: a routine question or booking request the FAQ fully answers
  - `flag for Rosa`: money (refunds, discounts, deposits back, invoices to pay), complaints, safety, anything the FAQ doesn't cover, anything you're unsure about
  - `log only`: reviews, invoices and receipts (the amounts go in the summary), job applications
  - `skip`: newsletters and automated notifications (still one row, so they're counted)
- **summary**: one line a person can act on, with any amount, date or booking detail in it
- **status**: `draft ready`, `needs a person`, `logged` or `skipped`
- **A duplicate** (the same text sent twice): draft a reply to the first only. The second gets action
  `log only` and status `logged`, with "duplicate of <id>" in its summary.
- **A chaser** ("Re:", "did you get my email?") is not a duplicate. Write one draft that answers both and apologises
  for the wait. Both rows get action `draft reply`.
- **Another language**: draft the reply in that language, and put an English summary in the log.

When unsure, choose `flag for Rosa`. A flag costs a person ten seconds. A wrong promise costs a customer.

## 4. Draft the replies (skip in dry-run)

One draft per `draft reply` email. Plain text, short, friendly. Answer only from `faq.md`.
If a booking request is missing details (date, number of people, bike or kayak), ask for exactly those.
Sign off as:

```
Best,
Rosa
Saltline Bike & Kayak Hire
```

## 5. Write the log (skip in dry-run)

Add one row per new email, newest first. Never edit an existing row. Put double quotes around any field that
contains a comma, so every row keeps exactly 8 columns.

## 6. Report

End every run with this report, in this order:

1. **Urgent**: anything a person must handle today, with the reason
2. **Needs a person**: each flagged email in one line
3. **Drafts ready**: how many, with the subjects
4. **Counts**: rows added, skipped as already logged, by type
5. **Unsure**: anything you guessed

In dry-run, the report starts with `DRY RUN: nothing was written.`
