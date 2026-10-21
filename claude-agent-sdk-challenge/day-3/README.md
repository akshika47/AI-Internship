# Day 3: teach your agent your know-how

Day 1 gave you an agent. Day 2 gave it tools, so it can **do** things. Today you give it
**judgement**: what good looks like, what to avoid, how you'd do the job yourself. You write
that in plain English, in a **skill**, and then you **measure** whether it helped.

**You're done when** your agent does one real task from your week, the way you like it done.

This folder has:

- **Dr Aki's job-fit agent with a skill**, plus a shortlist that ranks a week of job ads in
  one go and an evaluation that measures the skill. A worked example, not the assignment.
- **`starter_skill.py`** and **`skill-template/`**: give *your* agent a skill, with no code.
- **Three example skills for other kinds of agent**: meeting notes, research briefs, email replies.

## What a skill is

A skill is a folder with a `SKILL.md` file: a name, a one-line description, and your rules.
The agent sees only the description until a task needs the skill, then reads the rest. Long
material goes in a `reference/` folder that it opens only when it needs it, so a skill can
hold a lot without slowing every run down.

```
.claude/skills/reviewing-cvs/
├── SKILL.md              when to use it, a workflow checklist, the six rules that matter most
└── reference/
    ├── uk-cv-rules.md    the full rule list, each with its source
    └── examples.md       before and after bullets, and what not to do
```

Tools let an agent *do* something new. A skill tells it *how you want it done*. The best
skills use both: this one tells the agent to run the `check_cv_bullets` tool on its own
work and fix what it finds, which is a feedback loop.

## 1. Set up

From the `AI-Internship` folder:

```bash
git pull
cd claude-agent-sdk-challenge/day-3
uv run check_setup.py
```

Your key is already in `claude-agent-sdk-challenge/.env`. New here? Do steps 1 and 2 of the
[Day 1 README](../day-1/README.md) first.

## 2. See the skill at work

```bash
uv run job_fit.py examples/job.md examples/cv-2.pdf
```

```
  · opening your skill: reviewing-cvs
  · reading cv-2.pdf
  · reading job.md
  · checking your tracker
  · checking 3 CV bullets
  · checking 3 CV bullets
  · saving to your tracker: Junior AI Automation Analyst, Fernhill Health, 7/10
  · writing up the report
```

`cv-2.pdf` is a two-column PDF CV from a marketing analyst moving into AI, with the kind of
lines most CVs have ("Responsible for…", "Helped…"). It opens the skill, drafts three CV bullets, runs `check_cv_bullets`, fixes what the
checker flagged, and checks again. The report shows each rewrite with the CV line it came
from, so you can see nothing was invented.

Now the same job without the skill (this is Day 2's agent):

```bash
uv run job_fit.py examples/job.md examples/cv-2.pdf --no-skill
```

Open both reports side by side.

## 3. The real task: your weekly shortlist

Put this week's job ads in a text file, one link (or saved file) per line, like
`examples/jobs.txt`. Then:

```bash
uv run shortlist.py examples/jobs.txt examples/cv.pdf
```

It assesses three ads at a time, writes a report for each, adds them all to
`applications.csv`, and writes `shortlist.md`, ranked best fit first:

| # | Role | Fit | Decision |
|---|---|---|---|
| 1 | Operations & AI Associate, Brightpath Logistics | 9/10 | Apply now |
| 2 | Junior AI Automation Analyst, Fernhill Health | 8/10 | Apply now |
| 3 | AI Product Analyst, Ledgerly | 3/10 | Skip this one |

In our tests that was three jobs in about 25 seconds for 11 to 13 cents. With your own CV and real links:
`uv run shortlist.py my-jobs.txt cv.pdf`.

## 4. Measure it: does the skill actually help?

Anthropic's advice for skills is to test with and without them and keep only what makes a
difference. `run_evals.py` does that: it runs each scenario in `examples/scenarios.json` both
ways and scores the results with the same checks the agent uses, plus an honesty check (is
every quoted CV line really in the CV?).

```bash
uv run run_evals.py
```

Our results over three scenarios with PDF CVs, including a career changer, across two runs:

| Measure | Without skill | With skill |
|---|---|---|
| Duty phrases, weak openers, US spellings | 0 | 0 |
| Numbers not on the CV | 0 | 0 |
| Bullets not quoted from the CV | 0 | 0 |
| **Job ad keywords used in the bullets** | **14%** | **36% to 46%** |

Day 2's honesty rules already kept the bullets clean, so the skill's real gain was matching
the employer's language: two and a half to three times as often. That's what evaluations are for: they tell
you *where* a skill helps, so you don't keep rules that change nothing. Each scenario runs
once per mode, so your numbers will vary a little, as ours did.

## 5. Give your own agent a skill

Try one of the example skills first, with and without:

```bash
uv run starter_skill.py turning-notes-into-actions "Turn examples/meeting-notes.md into actions"
uv run starter_skill.py turning-notes-into-actions "Turn examples/meeting-notes.md into actions" --no-skill
```

With the skill, every action gets an owner and a date, or "not stated" instead of a guess,
and decisions and open questions are kept apart.

Then make yours:

1. Copy `skill-template/` into `.claude/skills/` and rename it, lowercase with hyphens, for
   example `writing-weekly-updates`. Use the same name in the `name:` line.
2. Write the **description** first: what it does and when to use it. The agent decides whether
   to open the skill from this line alone.
3. Write 3 to 6 **rules**: what you know that a smart new colleague wouldn't. Skip the obvious.
4. Add **one example**: a small input and the output you want. It teaches more than five rules.
5. Run it with and without: `uv run starter_skill.py your-skill-name "your request"`.

Plugging it into your own Day 2 agent takes four options, the same ones `agent/options.py` uses:

```python
cwd=THIS_FOLDER,                  # where .claude/skills/ is
setting_sources=["project"],      # load this folder's skills only, never your personal ones
skills=["your-skill-name"],       # and only the ones you name
tools=["Read", "Skill"],          # Skill is the built-in tool that opens a skill
```

**Why `setting_sources=["project"]`?** By default the SDK also loads skills from your own
`~/.claude/skills/`. If you use Claude Code, those would leak into your agent. This keeps it
to the skills in this folder.

## How the code is organised

```
day-3/
├── job_fit.py            one job:      uv run job_fit.py JOB_AD [CV] [--no-skill]
├── shortlist.py          many jobs:    uv run shortlist.py JOBS_LIST [CV]
├── run_evals.py          measure:      uv run run_evals.py
├── starter_skill.py      any skill:    uv run starter_skill.py SKILL "request"
├── .claude/skills/       reviewing-cvs (with reference/), plus three example skills
├── skill-template/       copy this to make your own
├── agent/                prompt, schema, options (with or without the skill), hooks, run, report, shortlist
├── tools/                fetch_job_ad, check_tracker, save_to_tracker, check_cv_bullets (cv_check.py)
├── examples/             two fictional PDF CVs (with text copies), three job ads, jobs.txt, scenarios.json, notes, an email
└── typescript/           the same, in TypeScript
```

## Stuck?

| You see | Try this |
|---|---|
| `✗ No .env file yet` | In the `claude-agent-sdk-challenge` folder run `cp .env.example .env` and put your key in it. |
| No `opening your skill` line | Check the folder is `.claude/skills/<name>/SKILL.md` and the `name:` line matches the folder name. |
| `No skill called '...'` | The starter lists the skills it can see. Check the spelling, lowercase with hyphens. |
| The agent opens the skill but ignores a rule | Make the rule shorter and bolder, put it near the top, and add an example of it. |
| Your evaluation shows no difference | That's useful: the rule isn't adding anything. Change it or drop it. |
| `Couldn't read the job ad` | Save the ad's text as a file and put the file name in your list instead of the link. |

Sources for the CV rules are listed in `.claude/skills/reviewing-cvs/reference/uk-cv-rules.md`.
The skill design follows Anthropic's [skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).
