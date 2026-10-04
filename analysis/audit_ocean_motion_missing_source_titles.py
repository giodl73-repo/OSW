"""Show source-page title evidence for high-impact untitled motion sources.

This is an explicit network review aid. It does not change the release package
or infer a citation from a filename alone.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "almanac" / "release" / "v0.1.0" / "source-review-queue.json"
MAX_BYTES = 12_000_000
USER_AGENT = "OSW-source-audit/0.1 (https://github.com/giodl73-repo/OSW)"


class PageMetadata(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.title_parts: list[str] = []
        self.meta: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "title":
            self.in_title = True
        if tag == "meta" and values.get("content"):
            key = values.get("property") or values.get("name")
            if key:
                self.meta[key.lower()] = values["content"]

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)


def inspect(row: dict) -> dict:
    url = row["url"]
    result = {"url": url, "record_count": row["record_count"]}
    try:
        request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/pdf"})
        with urlopen(request, timeout=22) as response:
            raw = response.read(MAX_BYTES + 1)
            result["final_url"] = response.url
            result["content_type"] = response.headers.get_content_type()
        if len(raw) > MAX_BYTES:
            result["status"] = "too_large"
            return result
        result["response_sha256"] = hashlib.sha256(raw).hexdigest()
        if raw.startswith(b"%PDF"):
            reader = PdfReader(io.BytesIO(raw))
            result["status"] = "pdf"
            result["pdf_title"] = str(reader.metadata.title) if reader.metadata and reader.metadata.title else None
            result["cover_excerpt"] = " ".join((reader.pages[0].extract_text() or "").split())[:450]
        else:
            parser = PageMetadata()
            parser.feed(raw.decode("utf-8", errors="replace"))
            result["status"] = "html"
            result["page_title"] = " ".join(" ".join(parser.title_parts).split())
            result["og_title"] = parser.meta.get("og:title")
            result["citation_title"] = parser.meta.get("citation_title")
            result["citation_author"] = parser.meta.get("citation_author")
            result["citation_doi"] = parser.meta.get("citation_doi")
    except (HTTPError, URLError, TimeoutError, ValueError, OSError) as error:
        result["status"] = "unavailable"
        result["error"] = str(error)[:160]
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    candidates = [row for row in queue if not row.get("title") and not row["url"].lower().endswith(".nc")]
    with ThreadPoolExecutor(max_workers=5) as pool:
        for result in pool.map(inspect, candidates[:args.limit]):
            print(json.dumps(result, ensure_ascii=True), flush=True)


if __name__ == "__main__":
    main()
