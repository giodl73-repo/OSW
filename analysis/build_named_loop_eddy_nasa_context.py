"""Connect Horizon Loop Current names to NASA and OSW regional context.

Horizon supplies separation dates but no individual coordinates. A region
gateway, a date overlap, and a NASA movie crop never identify the same eddy.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

from shapely.ops import unary_union

from build_motion_state_join import polygon_parts, project
from build_nasa_perpetual_ocean_tile_join import candidate_tiles


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
OUTPUT = RESEARCH / "named-loop-eddy-nasa-context.json"


def read(name: str) -> dict:
    return json.loads((RESEARCH / name).read_text(encoding="utf-8"))


def region_states(point: list[float]) -> list[str]:
    root = ET.parse(ROOT / "figures" / "osw-province-atlas-interactive.svg").getroot()
    land_path = next(item.get("d") for item in root.iter() if item.get("class") == "land-context")
    land = unary_union(polygon_parts(land_path))
    projected = project(point)
    matches = []
    for group in root.iter():
        if "province " not in group.get("class", ""):
            continue
        path = next(item.get("d") for item in group if item.tag.endswith("path"))
        if unary_union(polygon_parts(path)).difference(land).covers(projected):
            matches.append(group.get("data-code"))
    return sorted(matches)


def main() -> None:
    names = read("named-loop-current-eddy-identities.json")
    events = read("named-loop-current-eddies.json")
    current_index = read("ocean-current-atlas-index.json")
    tiles = read("nasa-perpetual-ocean-tile-join.json")
    timeline = read("nasa-perpetual-ocean-crop-timeline.json")
    nasa = read("nasa-perpetual-ocean-objects.json")
    observations = read("named-loop-eddy-observations.json")
    observations_by_id = {}
    for observation in observations["entries"]:
        identity_id = observation["loop_identity_id"]
        if identity_id in observations_by_id:
            raise ValueError(f"Duplicate supplemental observation for {identity_id}")
        observations_by_id[identity_id] = observation
    unknown_observations = set(observations_by_id) - {item["id"] for item in names["entries"]}
    if unknown_observations:
        raise ValueError(f"Supplemental observations have unknown Loop identities: {sorted(unknown_observations)}")
    model_years = [int(value) for value in re.findall(r"\b\d{4}\b", tiles["model_period"])]
    if len(model_years) != 2 or model_years[0] > model_years[1]:
        raise ValueError("NASA model period is not a year range")
    if "gulf-of-mexico-loop-eddies" not in {item["id"] for item in nasa["objects"]}:
        raise ValueError("NASA Loop eddy class is missing")
    gateway = current_index["named_loop_current_eddies"]["region_locator"]
    states = region_states(gateway)
    if not states:
        raise ValueError("Loop eddy region gateway has no OSW state")
    movie = tiles["named_loop_current_eddies_region_join"]
    if movie["locator"] != gateway:
        raise ValueError("NASA tile and Loop eddy region locators differ")
    by_event = {item["source_number"]: item for item in events["entries"]}
    entries = []
    for item in names["entries"]:
        event = by_event[item["source_number"]]
        separation = event["initial_separation"]
        full_date = re.fullmatch(r"(\d{4})-\d{2}-\d{2}", separation)
        month_year = re.fullmatch(r"\d{2}/(\d{4})", separation)
        if not full_date and not month_year:
            raise ValueError(f"Unexpected Horizon separation date for {item['id']}: {separation}")
        event_year = int((full_date or month_year).group(1))
        in_model_years = model_years[0] <= event_year <= model_years[1]
        temporal_relation = (
            "separation_in_model_years_identity_unverified" if in_model_years
            else "separation_outside_model_years"
        ) if item["role"] == "primary" else (
            "related_event_in_model_years_secondary_undated" if in_model_years
            else "related_event_outside_model_years_secondary_undated"
        )
        observation = observations_by_id.get(item["id"])
        observed_position = None
        dated_map_presence = None
        if observation:
            if observation["name"] != item["name"]:
                raise ValueError(f"Supplemental observation name differs for {item['id']}")
            coordinate = observation["coordinate"]
            observed_states = region_states(coordinate)
            matching_tiles = candidate_tiles(tiles["tiles"], *coordinate)
            if not matching_tiles:
                raise ValueError(f"No NASA crop covers the reported center of {item['id']}")
            observed_position = {
                "coordinate": coordinate,
                "position_evidence": observation["position_evidence"],
                "period": observation["period"],
                "source_url": observation["source_url"],
                "source_citation": observation["source_citation"],
                "note": observation["note"],
                "state_point_candidates": observed_states,
                "nasa_region_movie": {"tile_id": matching_tiles[0]["id"], "url": matching_tiles[0]["url"], "relation": "regional_context_only"},
            }
            map_evidence = observation.get("dated_map_presence")
            if map_evidence:
                map_date = map_evidence["date"]
                datetime.fromisoformat(map_date)
                seek = timeline["dates"].get(map_date)
                dated_map_presence = {
                    **map_evidence,
                    "state_relation": "source_labeled_gulf_region_only",
                    "nasa_model_date_relation": "sos_date_list_overlap_identity_unverified" if seek else "outside_available_sos_date_list",
                    "nasa_crop_seek": {
                        "tile_id": matching_tiles[0]["id"],
                        "url": f"{matching_tiles[0]['url']}#t={seek['estimated_crop_seconds']}",
                        "estimated_seconds": seek["estimated_crop_seconds"],
                        "alignment_status": timeline["alignment_status"],
                        "relation": "same_date_geographic_context_only",
                    } if seek else None,
                }
        entries.append({
            "id": item["id"],
            "name": item["name"],
            "role": item["role"],
            "source_number": item["source_number"],
            "source_event_initial_separation": separation,
            "independent_separation_date": item["initial_separation"],
            "temporal_relation": temporal_relation,
            "state_locator_candidates": states,
            "state_relation": "shared_source_region_gateway_only",
            "published_observed_position": observed_position,
            "published_dated_map_presence": dated_map_presence,
            "nasa_object_id": "gulf-of-mexico-loop-eddies",
            "nasa_object_relation": "related_described_class_only",
            "nasa_region_movie": {"tile_id": movie["tile_id"], "url": movie["url"], "relation": "regional_context_only"},
        })
    output = {
        "schema": "osw.almanac.named-loop-eddy-nasa-context.v1",
        "source_names": "research/named-loop-current-eddy-identities.json",
        "source_events": "research/named-loop-current-eddies.json",
        "supplemental_observations": "research/named-loop-eddy-observations.json",
        "nasa_objects": "research/nasa-perpetual-ocean-objects.json",
        "nasa_tile_ledger": "research/nasa-perpetual-ocean-tile-join.json",
        "nasa_crop_timeline": "research/nasa-perpetual-ocean-crop-timeline.json",
        "model_period": tiles["model_period"],
        "crop_date_window_inferred": [timeline["date_start"], timeline["date_end"]],
        "crop_date_alignment_status": timeline["alignment_status"],
        "region_locator": gateway,
        "region_locator_basis": current_index["named_loop_current_eddies"]["locator_note"],
        "state_locator_candidates": states,
        "name_count": len(entries),
        "primary_separations_in_model_years": sum(item["temporal_relation"] == "separation_in_model_years_identity_unverified" for item in entries),
        "secondary_names_linked_to_model_year_events": sum(item["temporal_relation"] == "related_event_in_model_years_secondary_undated" for item in entries),
        "supplemental_position_count": sum(item["published_observed_position"] is not None for item in entries),
        "dated_map_presence_count": sum(item["published_dated_map_presence"] is not None for item in entries),
        "evidence_limit": "Horizon publishes no individual positions in its name table, so all names retain one Gulf regional gateway. Separately published positions are point evidence only, and secondary names have no independent separation dates. A source-labeled observational map and an inferred NASA crop seek on the same date do not establish matching eddy identities. Source-event date overlap with NASA model years or an inferred crop date window does not establish a NASA model identity, a visible ring, or an OSW state intersection or containment.",
        "entries": entries,
        "states": {code: [item["id"] for item in entries] for code in states},
        "states_with_published_positions": {
            code: [item["id"] for item in entries if item["published_observed_position"] and code in item["published_observed_position"]["state_point_candidates"]]
            for code in sorted({code for item in entries if item["published_observed_position"] for code in item["published_observed_position"]["state_point_candidates"]})
        },
    }
    OUTPUT.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(entries)} Loop names in {len(states)} source-region states; "
          f"{output['primary_separations_in_model_years']} primary separations in NASA model years")


if __name__ == "__main__":
    main()
