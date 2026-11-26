"""Render the NetBay filing markdown into PDFs for the Filings Copilot starter.

Maintainers only. Students do not need this.

    pip install reportlab pypdf
    python ai-fde-bootcamp/week-2/_build/build_filing_pdfs.py

Each `<!-- page: N -->` marker starts a new PDF page whose printed number is N.
The PDF page labels carry the same numbers, so `pypdf`'s `reader.page_labels`
returns the page an analyst would cite. The script fails if any printed page
overflows onto a second physical page, because that would break the mapping.
"""

import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from pypdf import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

STARTER = Path(__file__).resolve().parent.parent / "filings-copilot-starter"
FILINGS = STARTER / "data" / "filings"
PAGE_RE = re.compile(r"<!--\s*page:\s*(\d+)\s*-->")

BASE = dict(fontName="Times-Roman", fontSize=10.5, leading=14)
STYLES = {
    "title": ParagraphStyle("title", fontName="Times-Bold", fontSize=15, leading=19, spaceAfter=10),
    "meta": ParagraphStyle("meta", fontName="Helvetica", fontSize=8.5, leading=11, textColor="#444444"),
    "h2": ParagraphStyle("h2", fontName="Times-Bold", fontSize=12.5, leading=16, spaceBefore=10, spaceAfter=6),
    "h3": ParagraphStyle("h3", fontName="Times-Bold", fontSize=11, leading=14, spaceBefore=8, spaceAfter=4),
    "h4": ParagraphStyle("h4", fontName="Times-BoldItalic", fontSize=10.5, leading=14, spaceBefore=6, spaceAfter=3),
    "body": ParagraphStyle("body", spaceAfter=7, **BASE),
}


def parse(md: str):
    """Yield (kind, payload) blocks: title, meta, page, h2/h3/h4, para."""
    lines = md.splitlines()
    i = 0
    title = lines[0].lstrip("# ").strip()
    yield "title", title
    i = 1
    meta = []
    while i < len(lines) and not PAGE_RE.match(lines[i].strip()):
        if lines[i].strip():
            meta.append(lines[i].strip())
        i += 1
    yield "meta", meta
    para: list[str] = []

    def flush():
        nonlocal para
        if para:
            yield_block = ("para", para)
            para = []
            return yield_block
        return None

    for raw in lines[i:]:
        line = raw.strip()
        m = PAGE_RE.match(line)
        heading = re.match(r"^(#{2,4})\s+(.*)$", line)
        if m or heading or not line:
            b = flush()
            if b:
                yield b
        if m:
            yield "page", int(m.group(1))
        elif heading:
            yield f"h{len(heading.group(1))}", heading.group(2)
        elif line:
            para.append(line)
    b = flush()
    if b:
        yield b


def build(md_path: Path) -> Path:
    blocks = list(parse(md_path.read_text()))
    title = blocks[0][1]
    meta = dict(m.split(": ", 1) for m in blocks[1][1])
    pages: list[int] = []
    story = []
    for kind, payload in blocks:
        if kind == "title":
            story.append(Paragraph(escape(payload), STYLES["title"]))
        elif kind == "meta":
            story.append(Paragraph("<br/>".join(escape(m) for m in payload), STYLES["meta"]))
            story.append(Spacer(1, 10))
        elif kind == "page":
            if pages:
                story.append(PageBreak())
            pages.append(payload)
        elif kind in ("h2", "h3", "h4"):
            story.append(Paragraph(escape(payload), STYLES[kind]))
        else:
            # Consecutive short lines (tables like "Hosting Services: $412.3M") keep their breaks.
            story.append(Paragraph("<br/>".join(escape(l) for l in payload), STYLES["body"]))

    footer_left = f"{meta.get('Company', '')} · {meta.get('Form type', '')} · {meta.get('Fiscal period', '')}"

    def on_page(canvas, doc):
        idx = canvas.getPageNumber() - 1
        printed = pages[idx] if idx < len(pages) else None
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor("#555555")
        canvas.drawString(inch, 0.6 * inch, footer_left)
        if printed is not None:
            canvas.drawRightString(letter[0] - inch, 0.6 * inch, str(printed))
            canvas.addPageLabel(idx, style="D", start=printed)
        canvas.restoreState()

    out = md_path.with_suffix(".pdf")
    doc = SimpleDocTemplate(
        str(out), pagesize=letter, title=title, author="NetBay, Inc. (fictional, TAI Labs course data)",
        leftMargin=inch, rightMargin=inch, topMargin=inch, bottomMargin=inch,
    )
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)

    reader = PdfReader(str(out))
    if len(reader.pages) != len(pages):
        sys.exit(f"{out.name}: {len(reader.pages)} physical pages for {len(pages)} printed pages; a page overflowed")
    labels = [int(l) for l in reader.page_labels]
    if labels != pages:
        sys.exit(f"{out.name}: page labels {labels} != printed pages {pages}")
    print(f"{out.relative_to(STARTER)}  pages {pages}")
    return out


if __name__ == "__main__":
    for md in sorted(FILINGS.glob("*.md")):
        build(md)
