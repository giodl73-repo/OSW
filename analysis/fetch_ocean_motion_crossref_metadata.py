"""Explicitly refresh DOI citation metadata for the ocean motion source queue."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "almanac" / "release" / "v0.1.0" / "source-review-queue.json"
OUTPUT = ROOT / "research" / "ocean-motion-crossref-metadata.json"
USER_AGENT = "OSW-source-audit/0.1 (https://github.com/giodl73-repo/OSW)"


def doi_from_url(url: str) -> str | None:
    parsed = urllib.parse.urlsplit(url)
    if parsed.netloc.lower() not in {"doi.org", "www.doi.org", "dx.doi.org"}:
        return None
    return urllib.parse.unquote(parsed.path.lstrip("/"))


def fetch(doi: str) -> dict:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read()
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as error:
        return {"doi": doi, "status": "unavailable", "error": str(error)[:180], "api_url": url}
    message = json.loads(raw)["message"]
    registered_doi = message.get("DOI", "")
    if registered_doi.casefold() != doi.casefold():
        return {"doi": doi, "status": "doi_mismatch", "registered_doi": registered_doi, "api_url": url}
    authors = []
    for author in message.get("author", []):
        label = " ".join(part for part in (author.get("given"), author.get("family")) if part)
        if label:
            authors.append(label)
    published = message.get("published", {}).get("date-parts", [[]])[0]
    return {"doi": doi, "status": "matched", "api_url": url,
            "response_sha256": hashlib.sha256(raw).hexdigest(),
            "title": (message.get("title") or [None])[0],
            "authors": authors, "publisher": message.get("publisher"),
            "publication_date_parts": published,
            "work_type": message.get("type"),
            "deposited_license_urls": [item["URL"] for item in message.get("license", []) if item.get("URL")],
            "metadata_note": "Crossref bibliographic metadata; license links do not establish reuse rights for OSW's source material."}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--missing-only", action="store_true",
                        help="retain pinned existing receipts and fetch only newly used DOIs")
    args = parser.parse_args()
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    dois = sorted({doi for row in queue if (doi := row.get("doi") or doi_from_url(row["url"]))})
    existing = {}
    if args.missing_only and OUTPUT.exists():
        prior = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if prior.get("schema") != "osw.almanac.crossref-citation-receipts.v1":
            raise ValueError("Unknown existing Crossref receipt schema")
        existing = {row["doi"].casefold(): row for row in prior["records"]}
        if len(existing) != len(prior["records"]):
            raise ValueError("Duplicate existing Crossref DOI receipt")
    records = []
    for index, doi in enumerate(dois, 1):
        record = existing.get(doi.casefold()) or fetch(doi)
        records.append(record)
        print(f"{index}/{len(dois)} {doi} {record['status']}" +
              (" retained" if doi.casefold() in existing else " fetched"), flush=True)
        if index < len(dois) and doi.casefold() not in existing:
            time.sleep(0.2)
    result = {"schema": "osw.almanac.crossref-citation-receipts.v1",
              "retrieved_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "source_queue": "almanac/release/v0.1.0/source-review-queue.json",
              "api_documentation": "https://www.crossref.org/documentation/retrieve-metadata/rest-api/",
              "scope": "Bibliographic metadata for DOI URLs used by the OSW ocean motion candidate; no rights conclusion.",
              "requested_count": len(dois), "matched_count": sum(row["status"] == "matched" for row in records),
              "records": records}
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("Wrote", OUTPUT.relative_to(ROOT), result["matched_count"], "matched", flush=True)


if __name__ == "__main__":
    main()
