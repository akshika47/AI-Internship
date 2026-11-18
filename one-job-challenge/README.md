# 4-Day Challenge: One job off your plate

Pick one job you repeat every week and hand it to Claude, built so that Claude does the work and a person still
presses Send. No code needed. If you can write the job down for a new colleague, you can do this.

The worked example all week is an **inbox desk**: every email gets a row in a log, routine questions get a reply
drafted from the business's FAQ, and anything about money, complaints or safety is flagged for a person. It runs
on a [practice inbox](practice-inbox/) for a fictional bike and kayak hire shop, so you can do the whole challenge
without connecting a real account. It's an example, not the assignment: bring your own job.

## The four days

| Day | Goal | You're done when | Folder |
|---|---|---|---|
| 1 | Pick the job and do it once with Claude, read-only | You've posted the job, its minutes a week, and one thing Claude got right and one it got wrong | [`day-1/`](day-1/) |
| 2 | Turn it into a Skill, with a "Never" list | Your Skill does a dry run of the job from one short request | [`day-2/`](day-2/) |
| 3 | Make it safe to leave alone: drafts only, dry run, a log, flag when unsure | A second run adds nothing, and you've fixed one mistake with a rule | [`day-3/`](day-3/) |
| 4 | Put it on a schedule, and show us before and after | It has run once without you starting it, or you've set a daily reminder | [`day-4/`](day-4/) |

About two hours in total, 15 to 45 minutes a day. Do one day at a time, or all four in one go on the practice
inbox and come back to switch it on for your own job. The days stay open, so catching up later is fine.

Finished early? Each day ends with an optional **Go further** step, mostly for builders and AI engineers.

## Two tracks, same Skill

| | Everyone track | Builder track |
|---|---|---|
| Where | Claude app (web or desktop) and Cowork | Claude Code |
| Day 4 | A Cowork scheduled task, or a daily reminder | A Claude Code task on a schedule, in the cloud. Optional: start it from a new email with Apps Script |
| You need | A Claude account. Day 4's schedule needs a paid plan. | Claude Pro or higher and a GitHub account |

On the Free plan you can do Days 1 to 3 in a chat and run the job by hand on Day 4.

## What's in this folder

- [`practice-inbox/`](practice-inbox/): 36 emails and the shop's FAQ
- [`day-2/skill-template/`](day-2/skill-template/SKILL.md): a Skill template to fill in
- [`day-2/inbox-desk/`](day-2/inbox-desk/SKILL.md): the worked example Skill
- [`day-3/safety-checklist.md`](day-3/safety-checklist.md): what to check before it runs alone
- [`day-3/answer-key.md`](day-3/answer-key.md) and [`day-3/grade.py`](day-3/grade.py): the practice inbox answers, and a script that scores your log against them
- [`day-4/watcher/`](day-4/watcher/): the optional Apps Script watcher that starts the task when an email arrives

Nothing here sends email or calls a paid API. Everything runs on your own Claude account.

## Next week

Next week's challenge tests what you built: can your automation be fooled, and how would you know? Keep your
Skill and your Day 3 mistake.
