"""Streamlit UI for the Week 2 RAG API: ingest documents, test retrieval, ask grounded questions.

Run:
  streamlit run demo_page.py
"""

import json
import os
import re
from pathlib import Path

import httpx
import streamlit as st

WORKDIR_CMD = "ai-engineering-bootcamp-v2/week-1v2"
MODELS = ["gpt-4o-mini", "gpt-4o", "o3-mini"]
SAMPLE_DOC = Path(__file__).resolve().parent / "sample_docs" / "northwind_handbook.md"


def render_curl(base_url: str, path: str, payload: dict) -> str:
    body = json.dumps(payload)
    if len(body) > 400:
        body = json.dumps({**payload, "text": payload["text"][:120] + "..."})
    return (
        f'curl -s -X POST {base_url.rstrip("/")}{path} '
        f'-H "Content-Type: application/json" '
        f"-d '{body}'"
    )


def call_json(method: str, url: str, payload: dict | None = None) -> tuple[int, dict | str]:
    try:
        if method == "POST":
            response = httpx.post(url, json=payload, timeout=120.0)
        else:
            # Render free services can take ~1 minute to wake up.
            response = httpx.get(url, timeout=60.0)

        try:
            return response.status_code, response.json()
        except json.JSONDecodeError:
            return response.status_code, response.text
    except httpx.ConnectError:
        return 0, {"error": f"Cannot reach {url}. Start the API server first."}
    except httpx.HTTPError as exc:
        return 0, {"error": str(exc)}


def show_status(status: int) -> None:
    st.markdown(f"**HTTP {status}**" if status else "**Request failed**")


def render_chunks(chunks: list[dict], cited: set[str] | None = None) -> None:
    for chunk in chunks:
        mark = " ✅ cited" if cited and chunk["chunk_id"] in cited else ""
        title = f"{chunk['score']:.3f} · {chunk['chunk_id']}{mark}"
        with st.expander(title, expanded=bool(mark)):
            st.text(chunk["text"])
            st.caption(json.dumps(chunk.get("metadata", {})))


def render_attempts(data: dict) -> None:
    attempts = data.get("attempts", [])
    if not attempts:
        return
    st.markdown("### Attempts")
    for attempt in attempts:
        status = "passed" if attempt.get("ok") else "failed"
        title = f"Attempt {attempt.get('attempt')}: {attempt.get('step')} ({status})"
        with st.expander(title, expanded=not attempt.get("ok")):
            st.write(attempt.get("message"))
            if attempt.get("raw_output"):
                st.markdown("**Raw model output**")
                st.code(attempt["raw_output"], language="json")
            if attempt.get("validation_error"):
                st.markdown("**Validation error**")
                st.code(attempt["validation_error"], language="text")


st.set_page_config(page_title="Week 2 RAG Demo", layout="centered")
st.title("Week 2: RAG `/ingest` + `/ask`")
st.caption("Ingest text → chunk + embed into Chroma → retrieve top-k → grounded, cited answer.")

base_url = st.sidebar.text_input(
    "API base URL", os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
).rstrip("/")

if st.sidebar.button("Check API health"):
    status, data = call_json("GET", f"{base_url}/health")
    show_status(status)
    st.sidebar.json(data)

st.sidebar.markdown("### Documents in the store")
if st.sidebar.button("Refresh"):
    st.session_state["documents"] = call_json("GET", f"{base_url}/documents")[1]
docs = st.session_state.get("documents")
if isinstance(docs, dict) and "documents" in docs:
    if docs["documents"]:
        st.sidebar.table(docs["documents"])
    else:
        st.sidebar.caption("Empty. Ingest a document first.")
elif docs:
    st.sidebar.json(docs)

st.sidebar.markdown("### Run locally")
st.sidebar.code(
    f"cd {WORKDIR_CMD}\n"
    "source .venv/bin/activate\n"
    "uvicorn main:app --port 8000 --reload\n"
    "streamlit run demo_page.py",
    language="bash",
)

ingest_tab, retrieve_tab, ask_tab = st.tabs(["1. Ingest", "2. Retrieve (no LLM)", "3. Ask"])

with ingest_tab:
    uploaded = st.file_uploader("Upload a .txt or .md file (optional)", type=["txt", "md"])
    if uploaded is not None:
        default_text = uploaded.getvalue().decode("utf-8", errors="replace")
        default_id = re.sub(r"[^A-Za-z0-9._-]+", "-", Path(uploaded.name).stem)
    else:
        default_text = SAMPLE_DOC.read_text() if SAMPLE_DOC.exists() else ""
        default_id = "northwind-handbook"

    with st.form("ingest_form"):
        document_id = st.text_input("document_id", default_id)
        text = st.text_area("Text", default_text, height=250)
        col1, col2 = st.columns(2)
        chunk_size = col1.number_input("chunk_size (chars)", 100, 4000, 800, step=50)
        chunk_overlap = col2.number_input("chunk_overlap (chars)", 0, 1000, 120, step=10)
        source = st.text_input("metadata.source", uploaded.name if uploaded else "northwind_handbook.md")
        ingest_submitted = st.form_submit_button("Ingest", type="primary")

    ingest_payload = {
        "document_id": document_id,
        "text": text,
        "chunk_size": int(chunk_size),
        "chunk_overlap": int(chunk_overlap),
        "metadata": {"source": source} if source else {},
    }
    st.code(render_curl(base_url, "/ingest", ingest_payload), language="bash")

    if ingest_submitted:
        with st.spinner("Chunking, embedding, upserting..."):
            status, data = call_json("POST", f"{base_url}/ingest", ingest_payload)
        show_status(status)
        if isinstance(data, dict) and "chunks_upserted" in data:
            cols = st.columns(4)
            cols[0].metric("Chunks", data["chunks_upserted"])
            cols[1].metric("Embedding tokens", data["embedding_tokens"])
            cols[2].metric("Latency", f"{data['latency_ms']} ms")
            cols[3].metric("Cost", f"${data['cost_usd']:.6f}")
            st.session_state.pop("documents", None)
        st.json(data)

with retrieve_tab:
    with st.form("retrieve_form"):
        r_question = st.text_input("Question", "How many PTO days can I roll over?")
        r_top_k = st.slider("top_k", 1, 10, 4, key="r_top_k")
        retrieve_submitted = st.form_submit_button("Retrieve", type="primary")

    retrieve_payload = {"question": r_question, "top_k": r_top_k}
    st.code(render_curl(base_url, "/retrieve", retrieve_payload), language="bash")

    if retrieve_submitted:
        with st.spinner("Embedding question and searching..."):
            status, data = call_json("POST", f"{base_url}/retrieve", retrieve_payload)
        show_status(status)
        if isinstance(data, dict) and "chunks" in data:
            if not data["chunks"]:
                st.warning("No chunks found. Ingest a document first.")
            render_chunks(data["chunks"])
        with st.expander("Raw JSON"):
            st.json(data)

with ask_tab:
    with st.form("ask_form"):
        question = st.text_area(
            "Question", "What is the daily meal allowance when traveling internationally?", height=80
        )
        st.caption("Try something the docs don't cover, e.g. *What is the parental leave policy?*")
        col1, col2 = st.columns(2)
        model = col1.selectbox("Model", MODELS, index=0)
        top_k = col2.slider("top_k", 1, 10, 4)
        force_bad = st.checkbox("Force a bad first response to demo validation + retry", value=False)
        ask_submitted = st.form_submit_button("Ask", type="primary")

    ask_payload = {"question": question, "model": model, "top_k": top_k, "force_bad": force_bad}
    st.code(render_curl(base_url, "/ask", ask_payload), language="bash")

    if ask_submitted:
        with st.spinner("Retrieving, grounding, generating..."):
            status, data = call_json("POST", f"{base_url}/ask", ask_payload)
        show_status(status)
        if isinstance(data, dict) and isinstance(data.get("answer"), dict):
            answer = data["answer"]
            st.markdown("### Answer")
            if answer["refused"]:
                st.warning(answer["answer"])
            else:
                st.success(answer["answer"])
                st.markdown("**Citations:** " + ", ".join(f"`{c}`" for c in answer["citations"]))
            st.caption(f"confidence: {answer['confidence']} | refused: {answer['refused']}")

            cols = st.columns(4)
            cols[0].metric("Model", str(data.get("model", "-")))
            cols[1].metric("Tokens", str(data.get("tokens_used", "-")))
            cols[2].metric("Latency", f"{data.get('latency_ms', '-')} ms")
            cols[3].metric("Cost", f"${data.get('cost_usd', 0):.6f}")

            st.markdown("### Retrieved chunks")
            render_chunks(data.get("retrieved_chunks", []), set(answer["citations"]))
            render_attempts(data)
        with st.expander("Raw JSON"):
            st.json(data)
