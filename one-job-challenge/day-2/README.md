# Day 2: Turn it into a Skill

Yesterday you explained the job in a chat. Today you write it down once, as a **Skill**, so Claude does it the
same way every time without you explaining again.

A Skill is a folder with one file, `SKILL.md`: a name, one line saying when to use it, and the instructions.
Claude loads it when a request matches that line.
([What are Skills?](https://support.claude.com/en/articles/12512176-what-are-skills))

## The part that matters most: "Never"

Most of a Skill is steps. The most useful part is the list of things it must never do, because those are the
mistakes that cost you a customer. Yesterday's last line ("what would go wrong if a new person did it") is your
starting point. The worked example's list:

```
- Never send, forward or delete an email. Drafts only. A person reads every draft and presses Send.
- Never promise a refund, discount, free extra or exception. Only the owner decides those. Flag them.
- Never reply to a safety report. Flag it as urgent at the top of the report so a person acts today.
- Never invent a fact. Prices, hours and rules come from faq.md only. If the FAQ doesn't answer it, flag it.
```

## Today's task (about 30 minutes)

### 1. Write your Skill with Claude's help

Go back to yesterday's chat (or start a new one and paste your Day 1 notes). Upload or paste
[`skill-template/SKILL.md`](skill-template/SKILL.md), then ask:

```
Turn this job into a Skill using the template I attached. Use what you learned in this chat.
Fill in every section, keep the Never list, and add the mistakes we saw today as Never rules or decision rules.
Keep the dry-run mode. Give me the finished SKILL.md.
```

Read it line by line. It's your job, so you're the expert: fix anything that isn't how you'd do it.

Want to see a finished one first? [`inbox-desk/SKILL.md`](inbox-desk/SKILL.md) is the worked example for the
practice inbox.

### 2. Install it

Name the folder exactly like the `name:` line in the file (lowercase letters, numbers and hyphens, for example
`inbox-desk`), with `SKILL.md` inside.

**In the Claude app (web or desktop), and Cowork:**
1. Settings → Capabilities: turn on **Code execution and file creation** (on newer accounts it's called
   **Create and edit files**). Skills need it.
2. Zip the folder.
3. Customize → Skills → **+** → Create skill → **Upload a skill**, and choose the zip.

Upload errors usually mean the folder name doesn't match `name:`, or the name has capitals or spaces.
([Use Skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude))

**On the Free plan:** if you don't see **Upload a skill**, nothing is wrong on your side. Paste the whole
SKILL.md at the start of a chat instead. It works the same for this week,
you just paste it each time.

**In Claude Code:** put the folder at `.claude/skills/<name>/SKILL.md` inside your project folder. Claude Code
picks it up the next time you start it there.

### 3. Try it as a dry run

Start a new chat (or Cowork task, or Claude Code session) with your inputs connected or uploaded. With the
practice inbox, upload `inbox-all.md` and `faq.md`. Then:

```
Run inbox-desk as a dry run.
```

Use your own Skill's name. It should start with `DRY RUN: nothing was written`, go through every item, and end
with the report your Skill asks for. If it doesn't use the Skill, say its name: "Use the inbox-desk skill".

## Go further (optional)

- **Test the description line.** In two new chats, ask "check the inbox" and "write me a birthday message".
  The first should use your Skill and the second shouldn't. If either goes wrong, make the `description:` line
  more exact.
- **Move the facts out of the rules.** Put your FAQ, price list or style guide in its own file in the Skill
  folder (for example `reference.md`), and say in SKILL.md when to read it. The rules stay short, and you can
  change a price without touching them.

## Post in the challenge thread

- Your Skill's **Never** list (leave out anything private)
- One rule you wouldn't have thought of on Day 1

Tomorrow: [Day 3, make it safe to leave alone](../day-3/).
