# Day 3: Make it safe to leave alone

Yesterday's Skill works while you watch it. Today you check it on its own. In one survey, people said they
spend about 4.5 hours a week fixing AI output
([Zapier, Nov 2025](https://itbrief.com.au/story/ai-workslop-zapier-survey-finds-ai-delivers-gains-as-well-as-costly-corrections)).
The four habits below are for that.

## The four habits

1. **Drafts, not actions.** It writes drafts and rows. A person sends, pays and deletes.
2. **A dry run first.** Ask for `dry-run` and it reports what it would do without writing anything.
3. **A log as its memory.** It reads the log before it starts and skips anything already in it, so a second
   run never does the work twice. The log is also where you look when something goes wrong.
4. **Unsure means flag.** When it can't tell, it hands the item to a person with a reason.

Open your Skill and check it has all four. The worked example, [`../day-2/inbox-desk/`](../day-2/inbox-desk/SKILL.md),
has each one. Look for "Never", "dry-run", "already in the log" and "flag".

## Today's task (about 30 minutes)

### 1. Dry run

Start a new task or chat with your Skill and ask:

```
Run <your skill name> as a dry run.
```

Check the report starts with `DRY RUN: nothing was written`, and check that nothing was written: no new file,
row or draft.

### 2. Real run, then the same run again

```
Run <your skill name>.
```

Check what it wrote. **In a plain chat**, the log is a file Claude makes for you: download it after this run,
and upload it again with the next one, so Claude can see what's already done. In Cowork or Claude Code it stays
in your folder.

Then run exactly the same request a second time. **The second run should add nothing**,
and its report should say every item was already in the log. If it added rows again, tell Claude what happened
and ask it to fix the Skill's "read what is already done" step.

### 3. Check its work

On the practice inbox, compare the log with the [answer key](answer-key.md). Count how many of the 36 emails got the right action, and look hard at:

- the safety report. It should be flagged as urgent and not answered.
- the refund requests. They should be flagged for a person, with no promise in any draft.
- the email in another language

On your own job, check 20 items by hand. A low first score is useful: every wrong row is a rule you get to add.

### 4. Fix one thing

Find one mistake, then add one line to the Skill's "Never" list or decision rules so it can't happen again. Run
it again after the fix. A new rule can cause a new mistake: when we told the worked example how to handle a
duplicate email, the next run treated a polite "did you get my email?" follow-up as a duplicate too, and it
took one more rule to fix.

Then go through the [safety checklist](safety-checklist.md). Every line should be a yes before Day 4.

## Go further (optional)

- **Score it with a script.** With Python installed, from the `day-3` folder:
  `python3 grade.py answer-key.md <your folder>/desk/log.csv`. It prints the type, urgency and action scores
  and lists every row where the action differs from the key. Action is the score that matters. Urgency will be
  lower if you run the whole inbox at once, because the key judges urgency at the moment each email arrived.
- **Run it three times.** Delete `desk/` between runs so each one starts empty, and score each run. If the score
  moves from run to run, the rows that change are where your rules need to be more exact. Next week's
  challenge picks up from here.

## Post in the challenge thread

- Your score on the practice inbox (for example 31 of 36), or how many of your 20 items it got right
- The mistake you found and the rule you added

Tomorrow: [Day 4, put it on a schedule](../day-4/).
