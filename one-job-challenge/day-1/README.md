# Day 1: Pick the job, and do it once with Claude

No setup today. Pick one job you repeat every week, write down how you do it, and do it once with Claude in a
normal chat. Claude only reads today. It doesn't write, send or change anything.

## 1. Pick one job (10 minutes)

A good first job:

- **comes back every week**, so the time you save adds up
- **has clear inputs**: emails, a folder, a sheet, a calendar
- **ends in a draft or a list**, so a mistake costs you a minute of reading
- **is one you already know how to do**: you could explain it to a new hire in five minutes, and never have the five minutes

Ten jobs that fit. Pick one of these or bring your own.

| Job | Good for | Claude reads | Claude writes (a draft or a list) | You still do |
|---|---|---|---|---|
| **Inbox desk**: log every email, draft the routine replies | Business owners, support, anyone with a shared inbox | Your inbox, your FAQ | A log row per email, reply drafts | Read and send the drafts, handle what it flags |
| **Receipts and invoices to a sheet** | Freelancers, founders, finance | Emails with receipts or invoices | One row each: date, supplier, amount, invoice number | Check the totals, pay |
| **Meeting notes to actions** | Managers, founders, consultants | A transcript or your notes | Decisions, actions with owners, a follow-up email draft | Send the follow-up |
| **Enquiry follow-up** | Sales, agencies, coaches | New form or email enquiries | A tailored reply draft, a row in your lead list | Send it, decide price |
| **Weekly report** | Founders, operators, team leads | A sheet, a folder of updates | A one-page summary with what changed | Read it, add judgement |
| **Calendar prep** | Anyone with back-to-back meetings | Tomorrow's calendar, related emails | One paragraph per meeting: who, why, what's open | Show up prepared |
| **Applications and sign-ups log** | Recruiters, community and event managers | Application or sign-up emails | One row each, with what's missing | Decide who goes forward |
| **Content repurposing** | Creators, marketers, founders | One long piece (post, talk, newsletter) | Short posts in your voice, as drafts | Edit and publish |
| **Overdue invoice reminders** | Freelancers, small agencies | Your invoices sheet | A polite reminder draft for each overdue one | Send them |
| **Changelog or release notes** | Developers, product people | Merged pull requests or commits | Plain-language notes for users | Publish |

**Sounds like you?** One person for each job:

- **Inbox desk:** a salon owner who answers "how much is a balayage?" from their phone between clients, several times a day.
- **Receipts to a sheet:** a freelance designer who spends the last Sunday of every month digging receipts out of Gmail for the accountant.
- **Meeting notes to actions:** a PM who leaves the weekly planning call with a page of notes and sends the follow-up a day later, when half of it is forgotten.
- **Enquiry follow-up:** a consultant who comes home from an event with a pocket of business cards and means to write to every one.
- **Weekly report:** an operations lead at a 20-person company who copies numbers from three sheets into one update for the founders every Friday.
- **Calendar prep:** a recruiter with candidate calls back to back who scrolls old threads before each one to remember who's who.
- **Applications and sign-ups:** a community manager who copies workshop sign-ups into a sheet by hand, then writes to everyone who forgot their time zone.
- **Content repurposing:** a coach who gives the same talk every month and never turns it into the posts they keep meaning to write.
- **Overdue invoice reminders:** a freelance photographer who knows exactly who owes them money and puts off the "just checking in" email another week.
- **Release notes:** a developer who has to explain a sprint's merged pull requests to customers who have never seen a pull request.

No job in mind yet? Use the practice inbox this week and pick your own job after. Rather not connect your real inbox yet? Use our **practice inbox**: 36 emails to a
fictional bike and kayak hire shop, with its FAQ. It's in [`../practice-inbox/`](../practice-inbox/). The worked
example all week is the inbox desk on that inbox.

## 2. Write down how you do it today (10 minutes)

Open a note and write your steps the way you'd explain them to a new colleague. Then time yourself doing it once,
or estimate from last week.

```
Job: inbox desk
How often: every weekday
Time it takes: about 40 minutes
Steps:
1. Open the inbox, read each new email
2. Answer the easy ones (hours, prices) from memory
3. Leave refunds and complaints for later
4. Note bookings in the calendar
What would go wrong if a new person did it: promising a refund, missing a safety issue
```

The last line matters most. Tomorrow it becomes your Skill's "Never" list.

## 3. Do it once with Claude, read-only (15 minutes)

Open a new chat at [claude.ai](https://claude.ai). Give Claude the inputs: connect the app it needs (see below),
or upload the files. With the practice inbox, upload `inbox-all.md` and `faq.md` from the practice inbox folder.

Then paste this, with your steps in it:

```
I want to hand this job to you, step by step. Today, only read and tell me what you'd do. Don't write, send or change anything.

The job: <name>
How I do it today:
<your steps>

Go through the input and show me:
1. A table with one row per item and what you'd do with it
2. Drafts of anything you'd write, clearly marked as drafts
3. Everything you weren't sure about, and why
```

Read what comes back as if a new colleague wrote it. Where is it right? Where would you have done it differently?

**Connecting your own apps:** in Claude, open Customize → Connectors, find the one your job needs (Gmail, Google
Calendar or Google Drive) and click Connect. In a chat, turn it on from the **+** button under the message box →
Connectors. Claude asks before it drafts or sends anything in Gmail, so read those prompts. You can turn a
connector off again in the same place, any time. If you'd rather not
connect a real account this week, the practice inbox works for every day of the challenge.

## Go further (optional)

Give the same input and prompt to two models, for example Sonnet and Haiku (in Claude Code, or in the app if
your plan lets you choose), and put their tables side by side. Every row where they disagree is a place your
Skill will need a clear rule tomorrow.

## 4. Post in the challenge thread

- The job you picked and roughly how many minutes a week it takes
- One thing Claude got right, and one thing it got wrong or wasn't sure about

Tomorrow: [Day 2, turn it into a Skill](../day-2/).
