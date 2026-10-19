# Day 1: a job-fit agent

This week's first agent: give it your CV and a job ad, and it writes you a short report:

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

## 3. Tonight: the code drop 🔓

The agent itself (`job_fit.py`) lands here this evening. Until then:

- get `uv run check_setup.py` to all green ticks
- save your CV in this folder as `cv.md` or `cv.pdf` (it stays on your machine)
- find one job ad you'd actually apply for, and keep the link

Tonight, `git pull` brings in the code, and this README gets the steps to run it.

## Stuck?

| You see | Try this |
|---|---|
| `uv: command not found` | Close the terminal, open a new one, try again. |
| `✗ No .env file yet` or `✗ .env still has the placeholder` | Make sure `.env` is in the day-1 folder and has your real key after `ANTHROPIC_API_KEY=`, with no spaces or quotes. |
| `Invalid API key` | Copy the key again from platform.claude.com. Keys are only shown once, so you may need a new one. |
| A credit or billing error | Add credit under Billing at platform.claude.com. |
