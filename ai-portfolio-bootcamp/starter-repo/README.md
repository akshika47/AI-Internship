# AI Portfolio Bootcamp - starter repo

The scaffold the Week 0 setup checklist asks you to clone and run. Get it
working before Session 1: Session 2 is a live build clinic, and debugging a
Python install in front of forty people is a bad use of everyone's ninety
minutes.

It is deliberately small. A harness, a reference task, ten templates. You will
replace the reference task in Week 1 with your own; the harness shape stays.

---

## Setup

Requires **Python 3.11+**.

```bash
git clone https://github.com/akshika47/AI-Internship.git
cd AI-Internship/ai-portfolio-bootcamp/starter-repo

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env               # then add your ANTHROPIC_API_KEY
```

### The one-command run

```bash
python scripts/run_samples.py
```

That is the check the setup checklist is asking for. You should see six sample
tickets processed, each with a category, a priority, a confidence score, and a
human-review flag.

**It runs without an API key.** With no key set, the harness falls back to a
deterministic keyword stub so you can verify your install before your billing
is sorted. It prints a warning when it does. Those are not real predictions, and
the stub is the baseline your Week 1 system has to beat.

### Scoring

```bash
python evals/score.py
```

Scores the system against `evals/golden_set.jsonl` and prints per-metric and
per-slice numbers, P1 recall, p50/p95 latency, and a failure list you can paste
into the taxonomy section of your eval report.

---

## What is in here

```
src/
  config.py          Every setting, loaded from env. Nothing else reads os.environ.
  logging_setup.py   One JSON object per line on stderr. Week 2 needs these numbers.
  schema.py          Input and output models. THIS IS THE FILE YOU CHANGE FIRST.
  pipeline.py        run(input) -> output. One structured-output call.

scripts/
  run_samples.py     The one-command run.

data/
  sample_inputs.jsonl   Six reference tickets.

evals/
  golden_set.jsonl      Four labelled cases to show the format. Yours needs ~40.
  score.py              Exact-match scoring, slices, latency, failure list.
  report_template.md    The six-section eval report. Week 2's deliverable.

docs/
  README-template.md              Your project's README
  architecture-decision-record.md AI Engineer track
  discovery-and-deployment-plan.md FDE track
  prd-and-metrics-plan.md         AI PM track
  case-study-ai-engineer.md       Case study, three role variants
  case-study-fde.md
  case-study-ai-pm.md
  demo-video-script.md            30s problem / 90s demo / 45s results / 15s next
  linkedin-post.md
  interview-question-map.md

brief.md             Your one-page problem brief. Week 0's deliverable.
```

---

## The reference task

Support ticket triage: subject and body in, category and priority out. It was
chosen because it makes the two fields your brief has to specify obvious:

- **`confidence`** - how sure the system is, 0 to 1
- **`needs_human`** - whether a person has to look at this one

A system that is always confident and never escalates has not been designed, it
has just been written.

Note where `needs_human` is decided: in `pipeline.py`, in code, from the
confidence threshold and an irreversibility check. Not in the prompt. That is
the Week 1 lesson arriving early - a rule you cannot afford to have ignored
belongs in code, where it cannot be argued with.

---

## Replacing the reference task

Week 1 Session 2 scaffolds your own project from `brief.md`. The prompt is
roughly:

```
Read brief.md. Scaffold this project in the existing starter repo structure:

- src/ with config loading from env, structured logging, and a single
  run(input) -> output entry point that takes one record and returns the
  output schema described in the brief.
- Define the output schema explicitly. Include the confidence field and the
  human-review flag described under "what the system does".
- Do not add retrieval, caching or an agent loop. The architecture decision
  is a single structured-output call.
- Add a scripts/run_samples entry that runs 5 records from data/ end to end
  and prints the outputs.

Show me the plan before you write files.
```

That last line is the highest-value clause in the prompt. It turns a
twenty-minute rewrite into a thirty-second correction.

---

## Assignment checkpoints

| Week | Deliverable | Lives in |
| --- | --- | --- |
| 0 | One-page problem brief | `brief.md` |
| 1 | A v1 that runs end to end on 5 sample inputs | `src/`, `scripts/` |
| 2 | Eval report: golden set, before/after, failure taxonomy | `evals/` |
| 3 | Repo, README, demo video, case study, role artefact, LinkedIn post | `docs/` |

---

## Notes

- `.env` is gitignored. Never commit a key. If you leak one, rotate it at
  <https://console.anthropic.com/> before anything else.
- Expect a few dollars of API usage across the whole course.
- The harness never raises on a model failure. A failed record comes back with
  `confidence: 0.0` and `needs_human: true`, because dropping a record silently
  is worse than escalating one.
- Your repo must run from a clean checkout. Test it in a fresh directory before
  you submit, ideally on a machine that is not yours.
