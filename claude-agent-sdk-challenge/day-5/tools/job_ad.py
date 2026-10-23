"""A tool that fetches a job ad's full text.

The SDK's built-in WebFetch hands the agent a summary of the page, which can drop the
exact requirements. This tool downloads the page itself and returns all of its text.
"""
import urllib.request
from html.parser import HTMLParser
from typing import Any

from claude_agent_sdk import ToolAnnotations, tool

MAX_CHARS = 20_000  # a long job ad is about 8,000 characters; this leaves room


class _PageText(HTMLParser):
    """Collects the visible text of a web page, skipping scripts and styles."""

    SKIP = {"script", "style", "noscript", "svg", "head"}
    BREAKS = {"p", "li", "br", "h1", "h2", "h3", "h4", "div", "tr"}

    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self.skipping = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skipping += 1
        elif tag in self.BREAKS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skipping:
            self.skipping -= 1

    def handle_data(self, data):
        if not self.skipping and data.strip():
            self.parts.append(data.strip() + " ")

    def text(self) -> str:
        lines = (" ".join(line.split()) for line in "".join(self.parts).splitlines())
        return "\n".join(line for line in lines if line)


@tool(
    "fetch_job_ad",
    "Download a job ad from a link and return the page's full text. Use it for every job ad "
    "given as a link (http or https). If the text is short or doesn't look like a job ad, "
    "the ad is closed, blocked or loads only in a browser.",
    {"url": str},
    annotations=ToolAnnotations(readOnlyHint=True),  # it only reads a web page
)
async def fetch_job_ad(args: dict[str, Any]) -> dict[str, Any]:
    url = args["url"]
    if not url.startswith(("http://", "https://")):
        return {"content": [{"type": "text", "text": f"Not a web link: {url}"}], "is_error": True}
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (job-fit agent)"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            final_url = response.geturl()
            html = response.read().decode("utf-8", errors="replace")
    except Exception as error:  # blocked (401/403), not found, no connection...
        return {"content": [{"type": "text", "text": f"Couldn't fetch {url}: {error}"}], "is_error": True}

    parser = _PageText()
    parser.feed(html)
    text = parser.text()[:MAX_CHARS]
    note = f"(The link redirected to {final_url}.)\n" if final_url.rstrip("/") != url.rstrip("/") else ""
    return {"content": [{"type": "text", "text": f"{note}{len(text.split())} words from {final_url}:\n\n{text}"}]}
