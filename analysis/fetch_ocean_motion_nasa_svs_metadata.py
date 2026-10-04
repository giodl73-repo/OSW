"""Explicitly refresh bibliographic receipts for NASA SVS motion release pages."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research" / "nasa-perpetual-ocean-objects.json"
OUTPUT = ROOT / "research" / "ocean-motion-nasa-svs-metadata.json"
USER_AGENT = "OSW-source-audit/0.1 (https://github.com/giodl73-repo/OSW)"


def fetch(source_url: str) -> dict:
    page_id = urlsplit(source_url).path.strip("/")
    if not page_id.isdigit() or urlsplit(source_url).hostname != "svs.gsfc.nasa.gov":
        raise ValueError(f"Expected a NASA SVS numeric page: {source_url}")
    api_url = f"https://svs.gsfc.nasa.gov/api/{page_id}/"
    request = urllib.request.Request(api_url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read()
    item = json.loads(raw)
    if str(item["id"]) != page_id:
        raise ValueError(f"SVS page ID mismatch: {page_id} / {item['id']}")
    credits = [{"role": group["role"], "people": [person["name"] for person in group.get("people", [])]}
               for group in item.get("credits", [])]
    return {"source_url": source_url, "api_url": api_url, "page_id": int(page_id),
            "response_sha256": hashlib.sha256(raw).hexdigest(),
            "title": item["title"], "release_date": item.get("release_date"),
            "update_date": item.get("update_date"), "credits": credits,
            "studio": item.get("studio"), "progress": item.get("progress"),
            "metadata_note": "NASA SVS page API bibliography and credits; inspect item media exceptions separately."}


def main() -> None:
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    urls = sorted({item["url"] for item in ledger["releases"]})
    records = [fetch(url) for url in urls]
    result = {"schema": "osw.almanac.nasa-svs-metadata-receipts.v1",
              "retrieved_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "source_ledger": str(LEDGER.relative_to(ROOT)).replace("\\", "/"),
              "api_documentation": "https://svs.gsfc.nasa.gov/help/",
              "scope": "Source-page metadata and credits for seven NASA SVS motion releases; no media rights conclusion.",
              "requested_count": len(urls), "matched_count": len(records), "records": records}
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}: {len(records)} NASA SVS records")


if __name__ == "__main__":
    main()
