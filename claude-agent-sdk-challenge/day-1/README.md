# Day 1: a job-fit agent

Give it your CV and a job ad. It reads both and writes you a short report:

- **Apply now, apply after closing a gap, or skip**, with a fit score out of 10
- where you're strong, quoting your own CV as proof
- the gaps, and how to close each one
- three CV bullets aimed at this job
- a first line for your cover note

It never invents experience. If your CV doesn't show it, it goes under gaps.

> New to this? You only need to copy and paste the commands below. If anything
> goes wrong, the error and the fix are in the **Stuck?** table at the bottom,
> and you can always post your error in the challenge thread.

## 1. Install uv (once)

[uv](https://docs.astral.sh/uv/) installs Python and the packages for you.

macOS / Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows (PowerShell):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Close the terminal and open a new one so it picks up `uv`.

## 2. Get the code and add your key

```bash
git clone https://github.com/akshika47/AI-Internship.git
cd AI-Internship/claude-agent-sdk-challenge/day-1
cp .env.example .env
```

Open `.env` in any text editor and replace `sk-ant-...` with your API key.
Get one at [platform.claude.com](https://platform.claude.com/) under **API keys**, and add a
little credit under **Billing**. A Claude Pro or Max plan doesn't cover the API.
(If you already use Claude Code, the SDK may fall back to that login when no key is set.
For the challenge, use an API key so you can see what each run costs.)

Check your setup. This costs nothing; it doesn't test the key itself, your first run does:

```bash
uv run check_setup.py
```

The first time, uv downloads Python and the SDK, so give it a minute.

## 3. Run it on the sample files

```bash
uv run job_fit.py examples/job.md examples/cv.md
```

You'll watch it work:

```
  · reading cv.md
  · reading job.md
  · writing up the report

Saved job-fit-junior-ai-automation-analyst-fernhill-health-cv.md · 5 turns · $0.220
```

Open that file. `examples/cv.md` and `examples/job.md` are made up, so have a look at
both to see what the agent was given.

## 4. Run it on your own CV

Save your CV in this folder (`day-1`, where you ran the commands above) as `cv.pdf`, or
as `cv.md` by pasting the text from Word into a text file. In Windows Notepad, set
**Save as type: All files**, or you'll end up with `cv.md.txt`.

Then point it at a real job ad. Replace the link with the real one and run **one** of these:

```bash
uv run job_fit.py https://link-to-the-job-ad          # if your CV is cv.md
uv run job_fit.py https://link-to-the-job-ad cv.pdf   # if your CV is cv.pdf
```

If the job site won't let it in, save the ad's text as `job.md` and run:

```bash
uv run job_fit.py job.md
```

Each job and CV gets its own report file. Your CV (any file with "cv" in its name),
`job.md`, `.env` and your reports are in `.gitignore`, so they stay on your machine.

## TypeScript instead?

The same agent is in [`typescript/`](typescript/). From this folder:

```bash
cd typescript
npm install
cp ../.env .env
npx tsx job_fit.ts ../examples/job.md ../examples/cv.md
```

## How it works

Everything that matters is in the `OPTIONS` block of `job_fit.py`:

| Setting | What it does |
|---|---|
| `system_prompt` | Its job description and rules, like "never add numbers, skills or outcomes". |
| `tools` | The only two things it can do: read a file and fetch a web page. |
| `output_format` | The exact shape of its answer, so the code can turn it into a report. |
| `hooks` | Runs a bit of your code before each step. Here it prints what the agent is doing. |
| `max_turns`, `max_budget_usd` | Safety limits: at most 15 steps and 50 cents per run. |

In our tests a run cost about 5 to 25 cents.

**Things to try:** change the rules in `SYSTEM_PROMPT` (make it harsher, or write in
American English), add a field to `REPORT_SCHEMA` like `"interview_questions"`, or run it
on three jobs and compare the scores.

## Stuck?

| You see | Try this |
|---|---|
| `uv: command not found` | Close the terminal, open a new one, try again. |
| `✗ No .env file yet` or `✗ .env still has the placeholder` | Make sure `.env` is in the day-1 folder and has your real key after `ANTHROPIC_API_KEY=`, with no spaces or quotes. |
| `Invalid API key` | Copy the key again from platform.claude.com. Keys are only shown once, so you may need a new one. |
| A credit or billing error | Add credit under Billing at platform.claude.com. |
| `Can't find your CV at 'cv.md'` | Your CV isn't in this folder, or has a different name. Use the name it really has: `uv run job_fit.py job.md my-cv.pdf` |
| `Couldn't read the job ad` | Some sites block bots (Indeed) or only show the ad in a browser (Ashby). Greenhouse and LinkedIn links usually work. Otherwise, save the ad's text as `job.md`. |
