#!/usr/bin/env bash
# Prove /ingest, /retrieve and /ask on a deployed URL with plain curl.
#   ./curl_demo.sh https://week1-ask-api.onrender.com
# Output is also saved to curl_demo_output.txt for the homework submission.
set -euo pipefail

BASE_URL="${1:-${API_BASE_URL:-http://127.0.0.1:8000}}"
BASE_URL="${BASE_URL%/}"
DIR="$(cd "$(dirname "$0")" && pwd)"
pretty() { python3 -m json.tool; }

{
echo "### GET $BASE_URL/health  (free Render services can take ~1 min to wake up)"
curl -s --max-time 120 "$BASE_URL/health" | pretty

echo; echo "### POST /ingest  (sample_docs/northwind_handbook.md)"
python3 -c 'import json,sys; print(json.dumps({"document_id": "northwind-handbook", "text": open(sys.argv[1]).read(), "chunk_size": 800, "chunk_overlap": 120, "metadata": {"source": "northwind_handbook.md"}}))' \
  "$DIR/sample_docs/northwind_handbook.md" \
  | curl -s -X POST "$BASE_URL/ingest" -H "Content-Type: application/json" -d @- | pretty

echo; echo "### POST /retrieve  (retrieval only, no LLM)"
curl -s -X POST "$BASE_URL/retrieve" -H "Content-Type: application/json" \
  -d '{"question": "What is the daily meal allowance when traveling internationally?", "top_k": 3}' | pretty

echo; echo "### POST /ask  -> cited answer"
curl -s -X POST "$BASE_URL/ask" -H "Content-Type: application/json" \
  -d '{"question": "What is the daily meal allowance when traveling internationally?"}' | pretty

echo; echo "### POST /ask  -> refusal (the handbook has no parental leave policy)"
curl -s -X POST "$BASE_URL/ask" -H "Content-Type: application/json" \
  -d '{"question": "What is the parental leave policy?"}' | pretty
} | tee "$DIR/curl_demo_output.txt"
