"""Inventory movie variants published on the audited NASA SVS release pages."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASES = ROOT / "research" / "nasa-perpetual-ocean-objects.json"
OUTPUT = ROOT / "research" / "nasa-perpetual-ocean-release-media.json"


def main() -> None:
    ledger = json.loads(RELEASES.read_text(encoding="utf-8"))
    releases = []
    for release in ledger["releases"]:
        page_id = release["url"].rstrip("/").rsplit("/", 1)[-1]
        api_url = f"https://svs.gsfc.nasa.gov/api/{page_id}"
        request = urllib.request.Request(api_url, headers={"User-Agent": "OSW-Ocean-Motion-Almanac/1.0"})
        with urllib.request.urlopen(request, timeout=30) as response:
            page = json.load(response)
        if int(page["id"]) != int(page_id):
            raise ValueError(f"NASA API returned the wrong release for {page_id}")
        movies = []
        for group in page["media_groups"]:
            for item in group["items"]:
                media = item.get("instance") or {}
                if media.get("media_type") != "Movie":
                    continue
                movies.append({
                    "media_id": media["id"],
                    "url": media["url"],
                    "filename": media["filename"],
                    "width": media.get("width"),
                    "height": media.get("height"),
                    "group_id": group["id"],
                    "group_title": group.get("title") or None,
                    "group_description": group.get("description") or None,
                })
        if len({movie["url"] for movie in movies}) != len(movies):
            raise ValueError(f"Repeated movie URL in NASA release {page_id}")
        releases.append({
            "release_id": release["id"],
            "page_id": int(page_id),
            "title": page["title"],
            "source_page": release["url"],
            "api_url": api_url,
            "api_update_date": page["update_date"],
            "movies": movies,
        })
    output = {
        "schema": "osw.almanac.nasa-release-media.v1",
        "source_ledger": "research/nasa-perpetual-ocean-objects.json",
        "method": "List every Movie media item in each audited NASA SVS page API response. A release can publish multiple resolutions, formats, views, and compositing layers; these are media variants, not ocean-object identities. The separate 70-crop picker is inventoried in nasa-perpetual-ocean-tile-join.json.",
        "release_count": len(releases),
        "movie_listing_count": sum(len(release["movies"]) for release in releases),
        "releases": releases,
    }
    OUTPUT.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {output['movie_listing_count']} NASA movie listings across {len(releases)} audited releases")


if __name__ == "__main__":
    main()
