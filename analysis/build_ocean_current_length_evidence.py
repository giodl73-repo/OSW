"""Materialize the length evidence and ranking decision for every current."""

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research" / "ocean-current-almanac.json"
TARGET = ROOT / "research" / "ocean-current-length-evidence.json"


def classify(item):
    if item["length_km"] is not None:
        return "published_estimate"
    if item.get("length_lower_bound_km") is not None:
        return "derived_lower_bound" if item.get("length_bound_basis") else "published_lower_bound"
    if item.get("hypothesized_length_km") is not None:
        return "proposed_system_length"
    if item.get("sampled_reach"):
        return "sampled_reach_only"
    if item.get("section_observation") or item.get("survey_section"):
        return "section_only"
    return "no_numeric_length"


def build():
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    entries = []
    for item in source["entries"]:
        status = classify(item)
        source_key = item.get("length_source") or item.get("hypothesis_source")
        observations = []
        for field in ("sampled_reach", "section_observation", "survey_section"):
            if item.get(field):
                observation = item[field]
                observations.append({
                    "type": field,
                    "source_url": source["sources"][observation["source"]],
                    "alongflow_km_approx": observation.get("alongflow_km_approx"),
                    "cross_stream_width_km": observation.get("meridional_width_km"),
                    "source_locator": observation.get("source_locator"),
                })
        entries.append({
            "current_id": item["id"],
            "name": item["name"],
            "status": status,
            "rank_eligible": status == "published_estimate",
            "length_km": item["length_km"],
            "lower_bound_km": item.get("length_lower_bound_km"),
            "hypothesized_length_km": item.get("hypothesized_length_km"),
            "scope": item["length_scope"],
            "length_source_url": source["sources"].get(source_key) if source_key else None,
            "length_source_locator": item.get("length_source_locator"),
            "name_source_url": item.get("name_source_url") or source["sources"].get(item["name_source"]),
            "other_observations": observations,
            "source_reported_length_variants": [
                {**variant, "source_url": source["sources"][variant["source"]]}
                for variant in item.get("source_reported_length_variants", [])
            ],
        })
    counts = Counter(entry["status"] for entry in entries)
    return {
        "title": "Ocean current length evidence and rank eligibility",
        "source_ledger": "ocean-current-almanac.json",
        "rule": source["ranking_rule"],
        "status_definitions": {
            "published_estimate": "Published approximate along-current or current-system length admitted to the source-set ranking; system boundaries still differ.",
            "derived_lower_bound": "OSW conservative geometric floor from published extent points or latitude span; not a measured flow path.",
            "published_lower_bound": "Source states a lower limit for the named current; not a comparable whole-current estimate.",
            "proposed_system_length": "Published proposed continuity or system extent; hypothesis not admitted as established whole-current length.",
            "sampled_reach_only": "A survey sampled part of the flow; its reach does not set the full length.",
            "section_only": "A cross-stream section or transport observation locates the flow but supplies no along-current length.",
            "no_numeric_length": "No numeric along-current length or bound admitted in the current source set.",
        },
        "counts": {status: counts[status] for status in (
            "published_estimate", "derived_lower_bound", "published_lower_bound",
            "proposed_system_length", "sampled_reach_only", "section_only", "no_numeric_length"
        )},
        "entries": entries,
    }


if __name__ == "__main__":
    TARGET.write_text(json.dumps(build(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {TARGET.relative_to(ROOT)} with {len(build()['entries'])} records")
