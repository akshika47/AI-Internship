"""Minimal Streamlit UI for the Week 1 v2 `/ask` demo.

Run:
  streamlit run demo_page.py
"""

import json
import os

import httpx
import streamlit as st

WORKDIR_CMD = "ai-engineering-bootcamp-v2/week-1v2"
MODELS = ["gpt-4o-mini", "gpt-4o", "o3-mini"]


def build_payload(question: str, model: str, force_bad: bool) -> dict:
    return {
        "question": question,
        "model": model,
        "force_bad": force_bad,
    }


def render_curl(base_url: str, payload: dict) -> str:
    body = json.dumps(payload)
    return (
        f'curl -s -X POST {base_url.rstrip("/")}/ask '
        f'-H "Content-Type: application/json" '
        f"-d '{body}'"
    )


def call_json(method: str, url: str, payload: dict | None = None) -> tuple[int, dict | str]:
    try:
        if method == "POST":
            response = httpx.post(url, json=payload, timeout=120.0)
        else:
            response = httpx.get(url, timeout=5.0)

        try:
            return response.status_code, response.json()
        except json.JSONDecodeError:
            return response.status_code, response.text
    except httpx.ConnectError:
        return 0, {"error": f"Cannot reach {url}. Start the API server first."}
    except httpx.HTTPError as exc:
        return 0, {"error": str(exc)}


def render_attempts(data: dict | str) -> None:
    if not isinstance(data, dict):
        return

    attempts = data.get("attempts", [])
    if not attempts:
        return

    st.markdown("### Attempts")
    for attempt in attempts:
        status = "passed" if attempt.get("ok") else "failed"
        title = f"Attempt {attempt.get('attempt')}: {attempt.get('step')} ({status})"
        with st.expander(title, expanded=True):
            st.write(attempt.get("message"))
            if attempt.get("raw_output"):
                st.markdown("**Raw model output**")
                st.code(attempt["raw_output"], language="json")
            if attempt.get("validation_error"):
                st.markdown("**Validation error**")
                st.code(attempt["validation_error"], language="text")


def render_response_summary(data: dict | str) -> None:
    if not isinstance(data, dict) or "error" in data:
        return

    answer = data.get("answer")
    if isinstance(answer, dict):
        st.markdown("### Answer")
        st.write(answer.get("answer", ""))
        st.caption(
            f"confidence: {answer.get('confidence')} | "
            f"sources_needed: {answer.get('sources_needed')}"
        )

    metric_cols = st.columns(4)
    metric_cols[0].metric("Model", str(data.get("model", "-")))
    metric_cols[1].metric("Tokens", str(data.get("tokens_used", "-")))
    metric_cols[2].metric("Latency", f"{data.get('latency_ms', '-')} ms")
    metric_cols[3].metric("Cost", f"${data.get('cost_usd', '-')}")


st.set_page_config(page_title="Week 1 v2 /ask Demo", layout="centered")
st.title("Week 1 v2: Minimal `/ask` Demo")
st.caption(
    "One final demo endpoint. The separate `stages/` files show how this grows step by step."
)

base_url = st.sidebar.text_input(
    "API base URL", os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
)
st.sidebar.markdown("### Start the API")
st.sidebar.code(
    f"cd {WORKDIR_CMD}\n"
    "source .venv/bin/activate\n"
    "uvicorn main:app --host 127.0.0.1 --port 8000 --reload",
    language="bash",
)
st.sidebar.markdown("### Start this page")
st.sidebar.code(
    f"cd {WORKDIR_CMD}\nsource .venv/bin/activate\nstreamlit run demo_page.py",
    language="bash",
)

with st.form("ask_form"):
    question = st.text_area(
        "Question",
        "What is Retrieval-Augmented Generation in one sentence?",
        height=100,
    )
    model = st.selectbox("Model", MODELS, index=0)
    force_bad = st.checkbox(
        "Force a bad first response to demo validation + retry",
        value=False,
    )
    submitted = st.form_submit_button("Ask", type="primary")

payload = build_payload(question, model, force_bad)

st.markdown("### Request")
st.code(render_curl(base_url, payload), language="bash")

col1, col2 = st.columns(2)
with col1:
    if st.button("Check API health"):
        status, data = call_json("GET", f"{base_url.rstrip('/')}/health")
        st.markdown(f"**HTTP {status}**" if status else "**Not connected**")
        st.json(data)

if submitted:
    with st.spinner("Calling /ask..."):
        status, data = call_json("POST", f"{base_url.rstrip('/')}/ask", payload)
    st.markdown("### Response")
    st.markdown(f"**HTTP {status}**" if status else "**Request failed**")
    render_response_summary(data)
    render_attempts(data)
    st.markdown("### Raw JSON")
    st.json(data)
