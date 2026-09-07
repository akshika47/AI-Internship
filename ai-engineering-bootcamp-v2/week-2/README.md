# Week 2 — RAG & Vector Databases

Build a Retrieval-Augmented Generation (RAG) pipeline end to end: embeddings,
chunking strategies, a vector store, retrieval, and evaluation with RAGAS.

## Contents

| Folder | What's inside |
|--------|---------------|
| [`rag-vector-databases/`](rag-vector-databases/) | Live-session notebook + setup files. Start here. |

## Setup

```bash
cd rag-vector-databases
cp .env.example .env          # OPENAI_API_KEY=sk-...
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the live session

```bash
cd rag-vector-databases
jupyter notebook rag_vector_databases_live_session.ipynb
```

Run the cells in order — each one builds on the previous. See
[`rag-vector-databases/README.md`](rag-vector-databases/README.md) for the full
walkthrough and learning objectives.

## Project layout

```
week-2/
└── rag-vector-databases/
    ├── rag_vector_databases_live_session.ipynb   # The live session
    ├── requirements.txt
    ├── .env.example
    ├── .gitignore
    └── README.md
```
