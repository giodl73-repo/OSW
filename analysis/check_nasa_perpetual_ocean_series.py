"""Compare NASA's live Perpetual Ocean 2 feed and release links with the ledger.

The offline almanac checker verifies internal joins. This check additionally
detects newly tagged or directly linked NASA releases that need a source audit.
"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "research" / "nasa-perpetual-ocean-source-audit.json"
OBJECTS = ROOT / "research" / "nasa-perpetual-ocean-objects.json"


def main() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    request = urllib.request.Request(
        audit["series_discovery"]["api_url"],
        headers={"User-Agent": "OSW-Ocean-Motion-Almanac/1.0"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        feed = json.load(response)
    if feed["next"] is not None or feed["count"] != len(feed["results"]):
        raise ValueError("NASA series feed is paginated; cannot prove coverage")
    live = {int(item["id"]): item["title"] for item in feed["results"]}
    recorded = set(audit["series_discovery"]["tagged_release_ids"])
    release_pages = {int(item["url"].rstrip("/").rsplit("/", 1)[-1]) for item in objects["releases"]}
    if set(live) != recorded or not recorded <= release_pages:
        raise ValueError(f"NASA series coverage changed: new={sorted(set(live) - recorded)}, "
                         f"removed={sorted(recorded - set(live))}, "
                         f"missing ledger pages={sorted(recorded - release_pages)}")
    shared = audit["user_shared_post_provenance"]
    canonical_id = int(shared["canonical_nasa_url"].rstrip("/").rsplit("/", 1)[-1])
    canonical_feed = next(item for item in feed["results"] if int(item["id"]) == canonical_id)
    if canonical_feed["release_date"][:10] != shared["canonical_nasa_release_date"]:
        raise ValueError("Shared post provenance has the wrong canonical NASA release date")
    # The series tag omits linked alternate editions and the original film.
    # Audit the direct NASA release graph as a second coverage boundary.
    reviewed_exclusions = {
        int(item["page_id"])
        for item in audit["series_discovery"]["reviewed_related_exclusions"]
    }
    if reviewed_exclusions & release_pages:
        raise ValueError("A reviewed exclusion is also in the object release ledger")
    linked_pages = set()
    for page_id in sorted(release_pages):
        page_request = urllib.request.Request(
            f"https://svs.gsfc.nasa.gov/api/{page_id}",
            headers={"User-Agent": "OSW-Ocean-Motion-Almanac/1.0"},
        )
        with urllib.request.urlopen(page_request, timeout=30) as response:
            page = json.load(response)
        for relation in ("related", "sources", "alternate_versions", "newer_versions", "older_versions"):
            linked_pages.update(int(item["id"]) for item in page.get(relation, []))
    unreviewed = linked_pages - release_pages - reviewed_exclusions
    if unreviewed:
        raise ValueError(f"NASA release graph has unreviewed directly linked pages: {sorted(unreviewed)}")
    stale_exclusions = reviewed_exclusions - linked_pages
    if stale_exclusions:
        raise ValueError(f"Reviewed exclusions are no longer linked by NASA releases: {sorted(stale_exclusions)}")
    print(f"OK: all {len(live)} live NASA Perpetual Ocean 2 series releases and "
          f"{len(linked_pages)} directly linked NASA pages are reviewed")
    for page_id, title in sorted(live.items()):
        print(f"  {page_id}: {title}")


if __name__ == "__main__":
    main()
