"""Print the stored chunk closest to a question.

Usage:
  .\.venv\Scripts\python.exe search_chapter.py "What is a Lang factor?"
"""

import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from vector_store import query_similar

load_dotenv(Path(__file__).resolve().parent / ".env")

question = " ".join(sys.argv[1:]).strip()
if not question:
    print('Add a question in quotes, for example:')
    print(r'.\.venv\Scripts\python.exe search_chapter.py "What is a Lang factor?"')
    raise SystemExit(1)

matches = query_similar(OpenAI(), question, top_k=1)
match = matches[0]
print(match["metadata"].get("source"))
print("chunk", match["metadata"].get("chunk_index"))
print(match["text"])
