# Day 5: Ship it and show us

**You're done when:** someone else could run your agent, and you've posted a one-minute demo in the challenge
thread. Any agent counts, whatever it does and however far you got.

Today has three parts. The first two take about half an hour; the third is optional.

1. **Ship check:** make your agent runnable by someone who isn't you.
2. **Demo:** show it in one minute.
3. **Autopilot (optional):** let it run on a schedule, without you.

## 1. Ship check

A few things separate "works on my machine" from "you can run it too". Each one comes from the
[Agent SDK hosting](https://code.claude.com/docs/en/agent-sdk/hosting) and
[secure deployment](https://code.claude.com/docs/en/agent-sdk/secure-deployment) docs, or from something that
bit us this week:

| | What | Why |
|---|---|---|
| 1 | A README with the one command that runs it | The first thing anyone tries |
| 2 | A sample input | So people can try it without their own data |
| 3 | A `.env.example` with a placeholder | Shows where the key goes |
| 4 | `.env` kept out of git, and no key written in any file | A pushed key is a public key |
| 5 | `max_turns` and `max_budget_usd` | The SDK has no timeout of its own, so a stuck agent keeps spending |
| 6 | `tools=[...]` | `allowed_tools` only pre-approves tools; `tools` is what restricts them (Day 1) |
| 7 | A plain message when a run stops | Not a wall of traceback |
| 8 | The cost of a run, printed | So people know what they're spending |
| 9 | One check you can rerun | A test with a known answer, or your evals from Day 3 |

You don't have to tick these by hand. From this folder, point the ship check at your agent:

```bash
cd claude-agent-sdk-challenge/day-5
uv run ship_check.py ../day-4            # Dr Aki's agent
uv run ship_check.py ~/code/my-agent     # yours
```

It reads your folder (Python or TypeScript), calls no model and costs nothing. Every ✗ comes with the fix:

```
Ship check for day-4

  ✓ README with a run command: uv run check_setup.py
  ✓ Sample input: examples/cvs/career-changer.md
  ✓ .env.example with a placeholder (claude-agent-sdk-challenge/.env.example)
  ✓ .env is ignored by git
  ✓ No API keys written in your files
  ✓ Limits set: max_turns and max_budget_usd
  ✓ Tools restricted with tools=[...]
  ✓ Handles a stopped run
  ✓ Prints what a run cost
  ✓ A check you can rerun: run_evals.py

10 of 10 ready. Ready to ship: record your one-minute demo.
```

No README yet? Start from [`templates/README-template.md`](templates/README-template.md).

## 2. The one-minute demo

Record your screen (any recorder works; Loom, QuickTime and the Windows Snipping Tool all do), or post a GIF
or screenshots. One minute, four beats:

| Seconds | Show |
|---|---|
| 0 to 10 | Who it's for and the problem, in one sentence |
| 10 to 40 | A real run on a real input |
| 40 to 50 | One thing that went wrong this week and how you fixed it |
| 50 to 60 | How to run it yourself: your repo link and the command |

The third beat is the one people remember. Post it in the challenge thread with
[`templates/demo-post.md`](templates/demo-post.md). Prefer not to record? Three lines of text count too.

## 3. Autopilot (optional): an agent that works while you sleep

GitHub Actions can run your agent on a schedule, for free apart from the API cost. The key lives in GitHub's
secrets, never in your code, and each run can open an issue with the result.

Dr Aki's agent does this every Monday: it shortlists that week's job ads and opens an issue with the ranking.
See [`.github/workflows/agent-sdk-challenge-autopilot.yml`](../../.github/workflows/agent-sdk-challenge-autopilot.yml).
In our test, three jobs took 36 seconds and cost $0.19.

To do it for yours:

1. Put your agent in a GitHub repo of your own (with `.env` ignored; the ship check confirms it).
2. Copy [`autopilot/agent-autopilot.yml`](autopilot/agent-autopilot.yml) into that repo as
   `.github/workflows/agent-autopilot.yml`, and change the lines marked `CHANGE ME`.
3. In the repo: **Settings → Secrets and variables → Actions → New repository secret**, name it
   `ANTHROPIC_API_KEY`, paste your key.
4. **Actions → Agent autopilot → Run workflow** to try it now instead of waiting for the schedule.

Every scheduled run spends money, so keep the limits from the ship check in place. A public repo's Actions
logs are public too: print results, never the key.

## What about hosting it for anyone?

A public link where strangers can use your agent is a bigger step: their runs spend your key, and anything
they send becomes input your agent reads. If you go there, the
[secure deployment](https://code.claude.com/docs/en/agent-sdk/secure-deployment) docs cover isolation,
credentials and network limits. For this challenge, "someone can clone it and run it with their own key" is
shipped.

## Tests

`uv run pytest` runs the ship check's offline tests (no key, no cost). They run in CI on every pull request.

## What's in this folder

```
day-5/
├── ship_check.py          uv run ship_check.py PATH/TO/YOUR/AGENT
├── autopilot/
│   └── agent-autopilot.yml   a scheduled workflow to copy into your repo
├── templates/
│   ├── README-template.md    a README someone else can follow
│   └── demo-post.md          your demo post for the challenge thread
└── tests/                 offline tests for the ship check
```

## Stuck?

| You see | Try this |
|---|---|
| `Can't find a folder at …` | Give the path to the folder your agent's code is in |
| `.env is not in .gitignore` | Add a line `.env` to `.gitignore`. If you already pushed a key, rotate it on platform.claude.com |
| `Tools not restricted` but you do restrict them | The check looks for `tools=[` or `tools=SOME_NAME` in your code. Tell us in the thread if it missed yours |
| The autopilot run says "No ANTHROPIC_API_KEY secret" | The secret's name must be exactly `ANTHROPIC_API_KEY` |
| The autopilot can't open an issue | Keep `issues: write` under `permissions` in the workflow |
