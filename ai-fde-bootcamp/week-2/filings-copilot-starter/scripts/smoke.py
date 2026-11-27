"""Smoke test for the scaffold.

    python scripts/smoke.py                        # in-process, no server needed
    python scripts/smoke.py --url http://localhost:8000

Today it expects /ask to return 501. Delete that expectation by Thursday,
when /ask returns a real Answer.
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def client(url: str | None):
    if url:
        import httpx

        return httpx.Client(base_url=url, timeout=30)
    from fastapi.testclient import TestClient

    from src.app import app

    return TestClient(app)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="running service, e.g. http://localhost:8000")
    args = parser.parse_args()
    c = client(args.url)

    start = time.perf_counter()
    r = c.get("/health")
    ms = (time.perf_counter() - start) * 1000
    assert r.status_code == 200 and r.json().get("ok") is True, r.text
    print(f"GET /health   {r.status_code} {r.json()} in {ms:.0f} ms")

    r = c.post(
        "/ask",
        json={
            "query": "What was NetBay's cloud revenue growth in the last reported quarter?",
            "tenant_id": "northgate-capital",
        },
    )
    print(f"POST /ask     {r.status_code} {r.json()}")
    assert r.status_code == 501, "Expected 501 from the scaffold. Built /ask already? Update this check."

    print("smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
