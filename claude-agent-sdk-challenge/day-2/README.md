# Day 2: give your agent tools you write yourself

On Day 1 the agent used tools that come with the SDK, like `Read` for files. Today you
write your own. A tool is a normal function plus a name, a description and the inputs it
takes. The agent reads the description and decides when to call it; your code does the work.

This folder has two things:

- **`job_fit.py`**: Dr Aki's job-fit agent, now with three tools of its own. It's a
  worked example, not the assignment.
- **`starter_tool.py`**: the smallest agent with one tool of your own. Copy it for
  whatever you're building.

## What the job-fit agent can do now

| Tool | What it does | Changes anything? |
|---|---|---|
| `fetch_job_ad` | Downloads a job ad from a link and gives the agent the page's **full text** | No, it only reads the page |
| `check_tracker` | Reads `applications.csv`: every job checked so far, with date, role, score, decision and link | No, it only looks |
| `save_to_tracker` | Adds this job's result to `applications.csv`. Checking the same ad again updates its row | Yes, it writes that one file |

So on top of Day 1's report, it can now:

- **read the whole job ad**: the SDK's built-in `WebFetch` hands the agent a summary of the
  page, which can drop exact requirements. `fetch_job_ad` gets every word.
- **remember** every job across runs, instead of starting from nothing each time
- **compare**: each report ends with how this job ranks against the earlier ones
- **build you a list**: `applications.csv` opens in Excel or Google Sheets

What it still can't do: send anything, apply for jobs, or touch files other than your CV,
the job ad and `applications.csv`. That's on purpose until Day 4, when we add guardrails.

## How the code is organised

```
day-2/
├── job_fit.py          the entry point: reads your command, runs the agent, saves the report
├── agent/
│   ├── prompt.py       what the agent is for, and its rules
│   ├── schema.py       the exact shape of its answer
│   ├── options.py      what it may do: tools, limits, model
│   ├── hooks.py        prints each step while it works
│   ├── run.py          runs it once and checks the answer
│   └── report.py       turns the answer into the Markdown report
├── tools/
│   ├── __init__.py     hands every tool to the agent
│   ├── job_ad.py       fetch_job_ad
│   └── tracker.py      check_tracker and save_to_tracker
├── starter_tool.py     a one-tool agent to copy for your own idea
├── check_setup.py      checks your setup without spending anything
├── examples/           a fictional CV (cv.md, cv.pdf) and two job ads
└── typescript/         the same, in TypeScript
```

Each file has one job, so when you want to change something you know where to look:
the rules are in `prompt.py`, the tools are in `tools/`, the limits are in `options.py`.

## 1. Set up (one minute if you did Day 1)

From the `AI-Internship` folder you downloaded on Day 1:

```bash
git pull
cd claude-agent-sdk-challenge/day-2
uv run check_setup.py
```

Your key lives in one `.env` in `claude-agent-sdk-challenge`, and every day finds it.
If you set up Day 1 before this change, your key is in `day-1/.env`. Move it up once,
from the `claude-agent-sdk-challenge` folder:

```bash
mv day-1/.env .env
```

`check_setup.py` spots this and tells you the same command.

New here? Do steps 1 and 2 of the [Day 1 README](../day-1/README.md) first (they include
downloading the repo and creating `.env`), then come back.

## 2. Run the job-fit agent

```bash
uv run job_fit.py examples/job.md examples/cv.md
uv run job_fit.py examples/job-2.md examples/cv.md
```

You'll see the new steps:

```
  · reading cv.md
  · reading job-2.md
  · checking your tracker
  · saving to your tracker: AI Product Analyst, Ledgerly, 3/10
  · writing up the report

Saved job-fit-ai-product-analyst-ledgerly-cv.md · 6 turns · $0.022
```

Open `applications.csv`: one row per job. The second report ends with a line comparing
the job with the first one.

Now try a real job ad by link, with your own CV saved in this folder:

```bash
uv run job_fit.py https://link-to-the-job-ad cv.pdf
```

This time you'll also see `· fetching the job ad`. Your CV, the reports and
`applications.csv` are in `.gitignore`, so they stay on your machine. In our tests a run
cost 2 to 6 cents.

## 3. How the tools work

Each tool is a function with `@tool` on top. This is the one in `tools/tracker.py`:

```python
@tool(
    "check_tracker",                                   # its name
    "List every job already assessed. Call this before "
    "writing the report so you can compare.",          # when to use it (the agent reads this)
    {},                                                # the inputs it takes (none)
    annotations=ToolAnnotations(readOnlyHint=True),    # it only looks, never changes anything
)
async def check_tracker(args):
    ...                                                # your code: read applications.csv
```

`tools/__init__.py` puts them all on one small server that runs inside your script:

```python
ALL_TOOLS = [fetch_job_ad, check_tracker, save_to_tracker]
jobfit_server = create_sdk_mcp_server(name="jobfit", tools=ALL_TOOLS)
```

And `agent/options.py` hands that server to the agent:

```python
tools=["Read"],                                # the only built-in tool it has
mcp_servers={"jobfit": jobfit_server},         # plus the tools we wrote
allowed_tools=["Read"] + JOBFIT_TOOLS,         # all of them run without asking you
```

The agent decides when to call each one, from its description and the rules in
`agent/prompt.py`.

**To add a tool:** write it in a new file in `tools/`, import it in `tools/__init__.py`,
add it to `ALL_TOOLS`, and mention it in the prompt's rules. Nothing else changes.

## 4. Write a tool for your own agent

Try the starter first:

```bash
uv run starter_tool.py "Read examples/job.md and save me three interview questions"
```

It reads the file, calls `save_note` three times, and `notes.md` appears. Then copy
`starter_tool.py` and change the three things its first lines list: the prompt, the tool,
and the allowed tools. When it grows past one tool, split it the way `job_fit.py` is split.

What tool does your agent need? Think about the one thing it can't do yet:

| Your agent… | A tool it might need |
|---|---|
| turns meeting notes into actions | `add_task`: add each action to a to-do file, or a Trello or Notion board |
| writes a research brief | `save_source`: keep each link it used, so you can check them later |
| helps with your inbox | `draft_reply`: write a reply into a drafts file for you to send |
| tracks prices, news or jobs | `compare_with_last_time`: read yesterday's results and say what changed |

Two rules worth keeping: give each tool a description that says **when** to use it, and
keep anything that changes things (sends, deletes, pays) out until Day 4, when we add
guardrails.

## TypeScript instead?

The same agent, tools and starter are in [`typescript/`](typescript/), in the same layout
(`agent/`, `tools/`). From this folder:

```bash
cd typescript
npm install
npx tsx job_fit.ts ../examples/job.md ../examples/cv.md
npx tsx starter_tool.ts "Read ../examples/job.md and save me three interview questions"
```

In TypeScript a tool is `tool(name, description, zodSchema, handler)`; see `tools/tracker.ts`.

## Stuck?

| You see | Try this |
|---|---|
| `✗ No .env file yet` | In the `claude-agent-sdk-challenge` folder run `cp .env.example .env` and put your key in it. |
| `Invalid API key` | Copy the key again from platform.claude.com. |
| `Couldn't read the job ad` | The site blocked the download or only shows the ad in a browser. Save the ad's text as `job.md` and run `uv run job_fit.py job.md`. |
| `Reached maximum budget` | The run hit its $1 cap. Run it again; if it keeps happening, post in the thread. |
| The agent never calls your tool | Make the description say when to use it, and mention the tool in the prompt's rules. |
| `ModuleNotFoundError: agent` or `tools` | Run the script from inside `day-2`, where those folders are. |
