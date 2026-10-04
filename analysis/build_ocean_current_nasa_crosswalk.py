"""Give every atlas current a source-scoped relation to Perpetual Ocean 2."""

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
OUTPUT = RESEARCH / "ocean-current-nasa-crosswalk.json"


def read(name):
    return json.loads((RESEARCH / name).read_text(encoding="utf-8"))


def build():
    currents = read("ocean-current-almanac.json")["entries"]
    nasa = read("nasa-perpetual-ocean-objects.json")
    objects = read("nasa-ocean-object-state-crosswalk.json")["objects"]
    tiles = read("nasa-perpetual-ocean-tile-join.json")["current_joins"]
    direct = {item["almanac_current_id"]: item for item in nasa["objects"] if item.get("almanac_current_id")}
    external = {}
    examples = {}
    for item in nasa["objects"]:
        for context in item.get("external_current_context", []):
            external.setdefault(context["current_id"], []).append((item, context))
        for current_id in item.get("example_object_ids", []):
            examples.setdefault(current_id, []).append(item["id"])
    entries = []
    for current in currents:
        current_id = current["id"]
        related = []
        if current_id in direct:
            item = direct[current_id]
            joined = objects[item["id"]]
            related.append({
                "nasa_object_id": item["id"],
                "relation": "nasa_named_or_described_current",
                "support": item["support"],
                "source_urls": [evidence["source_url"] for evidence in joined["release_evidence"].values()],
            })
            status = "nasa_named_or_described"
        elif current_id in external:
            for item, context in external[current_id]:
                related.append({
                    "nasa_object_id": item["id"],
                    "relation": context["relation"],
                    "support": "independent_current_name_for_nasa_described_structure",
                    "source_locator": context.get("source_locator"),
                    "source_urls": [context["source_url"], *[evidence["source_url"] for evidence in objects[item["id"]]["release_evidence"].values()]],
                })
            status = "independent_context"
        else:
            status = "regional_movie_only"
        tile = tiles[current_id][0]
        entries.append({
            "current_id": current_id,
            "name": current["name"],
            "status": status,
            "object_relations": related,
            "nasa_class_example_ids": examples.get(current_id, []),
            "regional_movie": {
                "tile_id": tile["tile_id"],
                "url": tile["url"],
                "relation": "geographic_crop_navigation_only",
            },
        })
    counts = Counter(item["status"] for item in entries)
    return {
        "schema": "osw.almanac.current-nasa-crosswalk.v1",
        "current_ledger": "research/ocean-current-almanac.json",
        "nasa_object_ledger": "research/nasa-perpetual-ocean-objects.json",
        "source_evidence_crosswalk": "research/nasa-ocean-object-state-crosswalk.json",
        "regional_tile_join": "research/nasa-perpetual-ocean-tile-join.json",
        "rule": "NASA source text or narration establishes a NASA-identified object. Independently sourced feeder or downstream currents are contextual relations to a NASA-named flow or described structure. A regional crop is geographic navigation only and does not establish that the current appears or is named in any frame.",
        "status_definitions": {
            "nasa_named_or_described": "NASA names or specifically describes this current or flow in an audited release.",
            "independent_context": "An oceanographic source links this named current as a feeder of, or continuation from, a NASA-named flow or described structure; NASA does not identify this current by name.",
            "regional_movie_only": "Only a geographic NASA movie crop joins to this current's editorial locator; no NASA identity claim.",
        },
        "counts": {status: counts[status] for status in ("nasa_named_or_described", "independent_context", "regional_movie_only")},
        "entries": entries,
    }


if __name__ == "__main__":
    payload = build()
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(payload['entries'])} current/NASA relations: {payload['counts']}")
