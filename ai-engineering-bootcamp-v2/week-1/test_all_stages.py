#!/usr/bin/env python3
"""Smoke-test all five stage APIs against the real OpenAI endpoint."""

import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx

WORKDIR = Path(__file__).resolve().parent
QUESTION = "What is Retrieval-Augmented Generation in one sentence?"


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def start_server(module: str, port: int) -> subprocess.Popen:
    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            f"{module}:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=WORKDIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def wait_up(base: str, timeout: float = 15.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if httpx.get(f"{base}/docs", timeout=1.0).status_code == 200:
                return True
        except httpx.HTTPError:
            pass
        time.sleep(0.3)
    return False


def post(base: str, payload: dict) -> tuple[int, dict]:
    r = httpx.post(f"{base}/ask", json=payload, timeout=120.0)
    return r.status_code, r.json()


def check(name: str, ok: bool, detail: str) -> bool:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {detail}")
    return ok


def test_stage1(base: str) -> bool:
    print("\n=== Stage 1: bare /ask ===")
    status, data = post(base, {"question": QUESTION})
    ok = True
    ok &= check("status", status == 200, f"HTTP {status}")
    ok &= check("answer type", isinstance(data.get("answer"), str), f"answer is str: {type(data.get('answer')).__name__}")
    ok &= check("tokens", isinstance(data.get("tokens_used"), int) and data["tokens_used"] > 0, f"tokens_used={data.get('tokens_used')}")
    ok &= check("no extra", set(data.keys()) == {"answer", "tokens_used"}, f"keys={list(data.keys())}")
    if ok:
        print(f"  answer preview: {data['answer'][:80]}...")
    return ok


def test_stage2(base: str) -> bool:
    print("\n=== Stage 2: structured output ===")
    status, data = post(base, {"question": QUESTION})
    ans = data.get("answer", {})
    ok = True
    ok &= check("status", status == 200, f"HTTP {status}")
    ok &= check("answer object", isinstance(ans, dict), "answer is object")
    ok &= check("confidence", isinstance(ans.get("confidence"), (int, float)), f"confidence={ans.get('confidence')}")
    ok &= check("sources_needed", isinstance(ans.get("sources_needed"), bool), f"sources_needed={ans.get('sources_needed')}")
    ok &= check("tokens", data.get("tokens_used", 0) > 0, f"tokens_used={data.get('tokens_used')}")
    ok &= check("no extra", set(data.keys()) == {"answer", "tokens_used"}, f"keys={list(data.keys())}")
    return ok


def test_stage3(base: str) -> bool:
    print("\n=== Stage 3: guardrail + retry ===")
    status_ok, data_ok = post(base, {"question": QUESTION})
    status_bad, data_bad = post(base, {"question": QUESTION, "force_bad": True})
    ok = True
    ok &= check("normal", status_ok == 200, f"normal HTTP {status_ok}")
    ok &= check("force_bad recovers", status_bad == 200, f"force_bad HTTP {status_bad} (retry should recover)")
    ok &= check("structured", isinstance(data_bad.get("answer"), dict), "force_bad answer is structured object")
    return ok


def test_stage4(base: str) -> bool:
    print("\n=== Stage 4: model + latency ===")
    status, data = post(base, {"question": QUESTION, "model": "gpt-4o-mini"})
    ok = True
    ok &= check("status", status == 200, f"HTTP {status}")
    ok &= check("model", data.get("model") == "gpt-4o-mini", f"model={data.get('model')}")
    ok &= check("latency", isinstance(data.get("latency_ms"), int) and data["latency_ms"] > 0, f"latency_ms={data.get('latency_ms')}")
    ok &= check("no cost yet", "cost_usd" not in data, "cost_usd absent (stage 4 only)")
    ok &= check("keys", set(data.keys()) == {"answer", "tokens_used", "model", "latency_ms"}, f"keys={list(data.keys())}")
    return ok


def test_stage5(base: str) -> bool:
    print("\n=== Stage 5: cost readout ===")
    _, mini = post(base, {"question": QUESTION, "model": "gpt-4o-mini"})
    status, full = post(base, {"question": QUESTION, "model": "gpt-4o"})
    ok = True
    ok &= check("status", status == 200, f"HTTP {status}")
    ok &= check("cost_usd", isinstance(full.get("cost_usd"), (int, float)) and full["cost_usd"] > 0, f"cost_usd={full.get('cost_usd')}")
    ok &= check("all fields", set(full.keys()) == {"answer", "tokens_used", "model", "latency_ms", "cost_usd"}, f"keys={list(full.keys())}")
    mini_cost = mini.get("cost_usd", 0)
    full_cost = full.get("cost_usd", 0)
    ok &= check("cost delta", full_cost > mini_cost, f"gpt-4o ${full_cost:.6f} > mini ${mini_cost:.6f}")
    return ok


TESTS = [
    ("serve_stage1", test_stage1),
    ("serve_stage2", test_stage2),
    ("serve_stage3", test_stage3),
    ("serve_stage4", test_stage4),
    ("serve_stage5", test_stage5),
]


def main() -> int:
    results: list[tuple[str, bool]] = []
    for module, test_fn in TESTS:
        port = free_port()
        base = f"http://127.0.0.1:{port}"
        proc = start_server(module, port)
        try:
            if not wait_up(base):
                print(f"\n=== {module}: FAIL — server did not start on {base} ===")
                results.append((module, False))
                continue
            results.append((module, test_fn(base)))
        finally:
            proc.terminate()
            proc.wait(timeout=5)
            time.sleep(0.5)

    print("\n" + "=" * 40)
    print("SUMMARY")
    for module, ok in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {module}")
    passed = sum(1 for _, ok in results if ok)
    print(f"\n{passed}/{len(results)} stages passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
