# Day 2: give your agent tools you write yourself

On Day 1 the agent used tools that come with the SDK: `Read` for files and `WebFetch` for
web pages. Today you write your own. A tool is a normal function plus a name, a
description and the inputs it takes. The agent reads the description and decides when to
call it; your code does the work.

This folder has two things:

- **`job_fit.py`**: Dr Aki's job-fit agent with two new tools that keep an applications
  tracker. It's a worked example, not the assignment.
- **`starter_tool.py`**: the smallest agent with one tool of your own. Copy it for
  whatever you're building.

## 1. Set up (two minutes if you did Day 1)

```bash
cd AI-Internship
git pull
cd claude-agent-sdk-challenge/day-2
cp ../day-1/.env .env
uv run check_setup.py
```

New here? Do steps 1 and 2 of the [Day 1 README](../day-1/README.md) first, then come back.

## 2. Run the job-fit agent twice

```bash
uv run job_fit.py examples/job.md examples/cv.md
uv run job_fit.py examples/job-2.md examples/cv.md
```

You'll see the two new steps:

```
  · reading cv.md
  · reading job-2.md
  · checking your tracker
  · saving to your tracker: AI Product Analyst, Ledgerly, 3/10
  · writing up the report
```

Open `applications.csv`: one row per job. The second report ends with a line comparing
the job with the first one. Run it on more job ads and the tracker grows.

## 3. How the tools work

Open `tracker_tools.py`. Each tool is a function with `@tool` on top:

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

`job_fit.py` hands the tools to the agent in three lines:

```python
tools=BUILT_IN_TOOLS,                          # Read and WebFetch, as on Day 1
mcp_servers={"tracker": tracker_server},       # plus the tools we wrote
allowed_tools=BUILT_IN_TOOLS + TRACKER_TOOLS,  # all of them run without asking you
```

That's it. The agent decides when to call them, based on the description and the rules
in `SYSTEM_PROMPT`.

## 4. Write a tool for your own agent

Try the starter first:

```bash
uv run starter_tool.py "Read examples/job.md and save me three interview questions"
```

It reads the file, calls `save_note` three times, and `notes.md` appears. Then copy
`starter_tool.py` and change the three things its first lines list: the prompt, the tool,
and the allowed tools.

What tool does your agent need? Think about the one thing it can't do yet:

| Your agent… | A tool it might need |
|---|---|
| turns meeting notes into actions | `add_task`: add each action to a to-do file, or a Trello or Notion board |
| writes a research brief | `save_source`: keep each link it used, so you can check them later |
| helps with your inbox | `draft_reply`: write a reply into a drafts file for you to send |
| tracks prices, news or jobs | `compare_with_last_time`: read yesterday's results and say what changed |

Two rules worth keeping from day one: give each tool a description that says **when** to
use it, and keep anything that changes things (sends, deletes, pays) out until Day 4,
when we add guardrails.

## TypeScript instead?

The same agent, tools and starter are in [`typescript/`](typescript/). From this folder:

```bash
cd typescript
npm install
cp ../.env .env
npx tsx job_fit.ts ../examples/job.md ../examples/cv.md
npx tsx starter_tool.ts "Read ../examples/job.md and save me three interview questions"
```

In TypeScript a tool is `tool(name, description, zodSchema, handler)`; see `tracker_tools.ts`.

## Stuck?

| You see | Try this |
|---|---|
| `✗ No .env file yet` | Run `cp ../day-1/.env .env` from this folder, or follow Day 1 step 2. |
| `Invalid API key` | Copy the key again from platform.claude.com. |
| `Reached maximum budget` | The run hit its $1 cap. Run it again; if it keeps happening, post in the thread. |
| The agent never calls your tool | Make the description say when to use it, and mention the tool in `SYSTEM_PROMPT`. |
| `ModuleNotFoundError: tracker_tools` | Run the script from inside `day-2`, where `tracker_tools.py` is. |
