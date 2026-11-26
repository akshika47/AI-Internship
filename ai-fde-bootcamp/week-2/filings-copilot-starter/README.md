# Filings Copilot starter · AI FDE Week 2

Filings Copilot is an analyst Q&A service for Northgate Capital. Analysts ask questions about NetBay's SEC filings and get an answer with page-level citations, or a clear refusal when the filings do not answer the question.

This folder is the Monday scaffold plus everything Assignment 2 needs: the filings, the tenant notes, and the sample analyst queries. NetBay, Northgate Capital and Riverside Partners are fictional. The numbers are made up but consistent across documents.

## Run the scaffold

```bash
cd ai-fde-bootcamp/week-2/filings-copilot-starter
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn src.app:app --reload
```

In another terminal:

```bash
curl http://localhost:8000/health      # {"ok":true}
python scripts/smoke.py                # /health ok, /ask returns 501 (expected today)
```

`POST /ingest` and `POST /ask` return 501 until you fill them in during the guided build. The `Answer` and `Citation` contracts are already in `src/schemas.py`.

## What is in `data/`

| File | What it is | Pages you can cite |
|---|---|---|
| `filings/netbay-10q-q3-2026` | 10-Q for Q3 2026, filed 2026-10-28. The most recent filing. | 1, 5, 18, 27, 39, 47, 62, 71 |
| `filings/netbay-10q-q2-2026` | 10-Q for Q2 2026, filed 2026-07-29. Superseded by Q3 for current questions. | 1, 5, 17, 26, 37, 44, 58, 66 |
| `filings/netbay-10k-2025` | 10-K for fiscal 2025, filed 2026-02-18. Superseded for current questions. | 1, 2, 4, 14, 38, 42, 47, 58, 74, 76, 88 |
| `filings/netbay-earnings-release-q3-2026` | Q3 2026 earnings release (8-K Ex. 99.1), filed 2026-10-07. Preliminary numbers. | 1, 2, 3 |
| `tenants/northgate-capital/saved-notes.md` | Northgate's private notes on NETB. | 1 |
| `tenants/riverside-partners/saved-notes.md` | Riverside's private notes on NETB. | 1 |
| `manifest.json` | Metadata for every document: form type, fiscal period, as_of date, which tenants may see it. | |
| `supersession.json` | Which sections are superseded by which newer section. | |

Each filing comes as **markdown** and as a **PDF**. Pick one for `/ingest`:

- **Markdown:** `<!-- page: N -->` starts printed page N. Everything after it, until the next marker, is on page N.
- **PDF:** use the printed page number, not the PDF page index. With `pypdf`, `reader.page_labels[i]` gives the printed number for page `i`. Real filings work the same way.

The filings skip pages (a real 10-Q is 70+ pages). Cite the printed number you see.

## The rules your retriever has to follow

**Tenants.** Filings are public, so ingest each filing once for each tenant (`northgate-capital` and `riverside-partners`). Saved notes are private: ingest each tenant's notes only under that tenant. Filter on `tenant_id` *before* the similarity search. A Northgate query must never retrieve a Riverside note, and the other way round.

**Superseded passages.** `supersession.json` lists sections that a newer filing replaces. Set `superseded_by` on those chunks and drop them at retrieval time, unless the query asks about the old period ("in fiscal 2025", "in Q2 2026").

**Evidence states.** Every `/ask` returns one of:

| Evidence | When | Example in `evals/queries.jsonl` |
|---|---|---|
| `enough` | A current passage answers it. Cite the page. | q-01 cloud revenue growth, Q3 10-Q p.47 |
| `missing` | Nothing relevant cleared your threshold. Empty `citations`. | q-04 gross margin by geography |
| `conflicting` | Two current passages disagree. Return both citations and stop. | q-03 total Q3 revenue: 10-Q $643.3M vs earnings release $644.1M |
| `stale` | The best match was superseded. Cite the newest passage that answers and say the old one is superseded. | q-05 data center metros: 10-K seven, Q2 eight, Q3 nine |

`citations` must always be a subset of what you retrieved.

## Evals

`evals/queries.jsonl` has 15 sample analyst queries. Each row gives the tenant, the evidence state you should return, and the filing and page you should cite. Run every one through `POST /ask` and commit the outputs.

`evals/retrieval_golden.jsonl` is yours to write: 15 rows labelled against **your** chunk ids, before you look at any model output.

```json
{"query_id": "g-01", "query": "What was NetBay's cloud revenue growth in the last reported quarter?", "must_include": ["<your chunk id for Q3 10-Q, Hosting Services, p.47>"], "must_exclude": ["<your chunk id for 10-K, Hosting Services, p.42>"], "tenant_id": "northgate-capital", "tags": ["mda", "segment-revenue"]}
```

Then report recall@5, MRR and must_exclude violations for BM25 only, dense only, hybrid + RRF, and hybrid + rerank. The full hand-in list is on the Assignment 2 page.
