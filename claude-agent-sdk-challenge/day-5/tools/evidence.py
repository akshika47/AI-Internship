"""Evidence checks: is a quote really in the source? Pure code, so the answer is never a guess.

The agent can run check_evidence on itself while it works, and agent/verify.py runs the same
check on the final report, where the agent can't skip it. "No evidence, no pass."
"""
import re
from pathlib import Path
from typing import Any

from claude_agent_sdk import ToolAnnotations, tool
from pypdf import PdfReader

ELLIPSIS = re.compile(r"\s*(?:\.\.\.|…)\s*")  # "first part … last part" means both parts must be there
MIN_QUOTE_WORDS = 3  # shorter than this proves nothing: "Python" is on every CV


def source_text(path: str | Path) -> str:
    """The text of a CV or source file. PDFs are read with pypdf, everything else as text."""
    path = Path(path)
    if path.suffix.lower() == ".pdf":
        return " ".join(page.extract_text() or "" for page in PdfReader(path).pages)
    return path.read_text()


def normalise(text: str) -> str:
    """Ignore what PDFs and Markdown change: case, line breaks, bold marks, curly quotes."""
    text = re.sub(r"[*_`]", "", text).replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return " ".join(text.lower().split())


def problem_with(quote: str, source: str) -> str | None:
    """None if the quote is really in the source; otherwise what's wrong with it."""
    parts = [normalise(p).strip(' ."') for p in ELLIPSIS.split(quote) if p.strip(' ."')]
    words = sum(len(p.split()) for p in parts)
    if words < MIN_QUOTE_WORDS:
        return f"too short to prove anything ({words} words)"
    missing = [p for p in parts if p not in normalise(source)]
    return f'not in the source: "{missing[0][:60]}"' if missing else None


def rest_of_sentence(quote: str, source: str) -> str | None:
    """If a found quote stops mid-sentence, the rest of that sentence; None if it ends where its sentence does.

    Found with the Day 5 step log: CVs wrap long lines, and the agent quoted only the first line of a sentence.
    The quote was real, so it passed, but the judge then rightly took out true claims that used the rest.
    """
    if quote.rstrip().endswith((".", "!", "?", ";", ")")):
        return None
    last = normalise(ELLIPSIS.split(quote)[-1]).strip(' ."')
    text = normalise(source)
    at = text.find(last)
    if not last or at < 0:
        return None
    rest = text[at + len(last):].lstrip()
    sentence = re.split(r"(?<=[.!?])\s| - ", rest, maxsplit=1)[0]
    return sentence if sentence and sentence[0].isalnum() else None


def goes_on(quote: str, source: str) -> str | None:
    """The next few words of a quote that stops mid-sentence, to show the agent what it left out."""
    rest = rest_of_sentence(quote, source)
    return " ".join(rest.split()[:8]) if rest else None


def whole_sentence(quote: str, source: str) -> str:
    """The quote, finished to the end of its sentence: what the judge should read. All of it is in the source."""
    rest = rest_of_sentence(quote, source)
    return f"{quote.rstrip()} {rest}" if rest else quote


@tool(
    "check_evidence",
    "Check that each quote is really, word for word, in the source file (a CV or document). "
    "Run it on every quote you plan to use as evidence, before writing the report, and fix or "
    "drop any quote it reports. Quotes must be copied exactly; use … to skip words in the middle. "
    "Quote the whole sentence your claim relies on, even when it wraps onto the next line.",
    {
        "type": "object",
        "properties": {
            "source_path": {"type": "string", "description": "The file the quotes come from"},
            "quotes": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["source_path", "quotes"],
    },
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def check_evidence(args: dict[str, Any]) -> dict[str, Any]:
    try:
        source = source_text(args["source_path"])
    except OSError as error:
        return {"content": [{"type": "text", "text": f"Couldn't read {args['source_path']}: {error}"}], "is_error": True}
    results = [(q, problem_with(q, source)) for q in args["quotes"]]
    # A quote that stops mid-sentence is a problem here too: a judge will only see what you quoted.
    results = [(q, p or (f'stops mid-sentence; it goes on "{goes_on(q, source)} …". Quote the whole sentence.' if goes_on(q, source) else None))
               for q, p in results]
    lines = [f"{i}. {'OK' if p is None else p}" for i, (q, p) in enumerate(results, 1)]
    verdict = "PASS" if all(p is None for _, p in results) else "FIX the quotes above, then run check_evidence again."
    return {"content": [{"type": "text", "text": "\n".join(lines + [verdict])}]}
