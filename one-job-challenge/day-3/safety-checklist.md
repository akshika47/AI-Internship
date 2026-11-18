# Safety checklist

Go through this before your automation runs without you watching. Every line should be a yes.

## What it can do

- [ ] It only **drafts**. Sending, paying, deleting and publishing are done by a person.
- [ ] It only has the connectors and files this job needs. Everything else is turned off for it.
- [ ] Its "Never" list names the mistakes that would hurt in your job, as rules.
- [ ] Facts come from one place you control (an FAQ, a price list, a policy doc), and the Skill says so.

## How it runs

- [ ] It has a **dry-run** mode that writes nothing, and you've run it.
- [ ] It keeps a **log** (a sheet or a CSV), and it checks the log first.
- [ ] You've run it **twice in a row** and the second run added nothing new.
- [ ] Every run ends with a short report: what needs a person, what it did, what it guessed.

## When it's wrong

- [ ] When it's unsure, it **flags** the item for a person instead of guessing.
- [ ] You know where to look when something goes wrong (the log, the run's history).
- [ ] You know how to stop it: pause the schedule, or turn off the trigger.

## Before you trust it

- [ ] You've checked its work on at least 20 real items, or the practice inbox's answer key.
- [ ] You've written down one mistake it made and the rule you added so it won't happen again.
