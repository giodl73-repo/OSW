"""Join eddy families, recurring names, and source-dated events to atlas states and NASA crops.

Locators are regional gateways, published centers, or sample stations. They do not prove
an eddy footprint, NASA identity, or containment in an OSW state.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from shapely.ops import unary_union

from build_motion_state_join import polygon_parts, project
from build_nasa_perpetual_ocean_tile_join import candidate_tiles


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
SOURCE = RESEARCH / "named-eddy-geography.json"
TILES = RESEARCH / "nasa-perpetual-ocean-tile-join.json"
CROP_TIMELINE = RESEARCH / "nasa-perpetual-ocean-crop-timeline.json"
NASA_OBJECTS = RESEARCH / "nasa-perpetual-ocean-objects.json"
PROVINCES = ROOT / "figures" / "osw-province-atlas-interactive.svg"
OUTPUT = RESEARCH / "named-eddy-geography-join.json"


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    tile_ledger = json.loads(TILES.read_text(encoding="utf-8"))
    crop_timeline = json.loads(CROP_TIMELINE.read_text(encoding="utf-8"))
    nasa_objects = {item["id"] for item in json.loads(NASA_OBJECTS.read_text(encoding="utf-8"))["objects"]}
    current_ids = {item["id"] for item in json.loads((RESEARCH / "ocean-current-almanac.json").read_text(encoding="utf-8"))["entries"]}
    if not {"ocean-eddies", "agulhas-rings"} <= nasa_objects:
        raise ValueError("NASA eddy class records are missing")
    tiles = tile_ledger["tiles"]
    period_years = [int(year) for year in re.findall(r"\b\d{4}\b", tile_ledger["model_period"])]
    if len(period_years) != 2 or period_years[0] > period_years[1]:
        raise ValueError("NASA crop model period is not a year range")
    province_root = ET.parse(PROVINCES).getroot()
    land_path = next(item.get("d") for item in province_root.iter() if item.get("class") == "land-context")
    land = unary_union(polygon_parts(land_path))
    states = {}
    for group in province_root.iter():
        if "province " not in group.get("class", ""):
            continue
        path = next(item.get("d") for item in group if item.tag.endswith("path"))
        states[group.get("data-code")] = unary_union(polygon_parts(path)).difference(land)
    if len(states) != 56:
        raise ValueError(f"Expected 56 OSW states, found {len(states)}")
    entries = {}
    state_index = {code: [] for code in states}
    observed_position_index = {code: [] for code in states}
    for item in source["entries"]:
        eddy_id = item["id"]
        if item.get("related_current_id") and item["related_current_id"] not in current_ids:
            raise ValueError(f"Unknown related current for {eddy_id}")
        point = project(item["locator"])
        excluded = set(item.get("state_exclusions", []))
        if not excluded <= set(states):
            raise ValueError(f"Unknown state exclusion for {eddy_id}")
        candidates = sorted(code for code, shape in states.items() if code not in excluded and shape.covers(point))
        tile_matches = candidate_tiles(tiles, *item["locator"])
        if not tile_matches:
            raise ValueError(f"No NASA region crop for {eddy_id}")
        best = tile_matches[0]
        event_year = item.get("event_year")
        temporal_relation = ("outside_model_period" if not period_years[0] <= event_year <= period_years[1]
                             else "year_overlap_identity_unverified") if event_year else "recurring_name_no_generation_match"
        observed_months = item.get("source_observed_months", [])
        if temporal_relation != "outside_model_period" and observed_months and all(month < crop_timeline["date_start"][:7] for month in observed_months):
            temporal_relation = "source_observations_before_inferred_crop_window"
        agulhas_member = eddy_id == "agulhas-rings-family" or item.get("member_of") == "agulhas-rings-family"
        additional_positions = []
        for observation in item.get("additional_observed_positions", []):
            coordinate = observation["coordinate"]
            observed_point = project(coordinate)
            observed_states = sorted(code for code, shape in states.items() if code not in excluded and shape.covers(observed_point))
            observed_tiles = candidate_tiles(tiles, *coordinate)
            if not observed_tiles:
                raise ValueError(f"No NASA regional crop for observed position of {eddy_id}")
            additional_positions.append({
                "date": observation.get("date"),
                "period": observation.get("period"),
                "coordinate": coordinate,
                "evidence_type": observation["evidence_type"],
                "state_center_candidates": observed_states,
                "nasa_region_movie": {"tile_id": observed_tiles[0]["id"], "url": observed_tiles[0]["url"], "relation": "regional_context_only"},
                "note": observation["note"],
            })
            for code in observed_states:
                observed_position_index[code].append({"eddy_id": eddy_id, "date": observation.get("date"), "period": observation.get("period"), "evidence_type": observation["evidence_type"]})
        entries[eddy_id] = {
            "state_locator_candidates": candidates,
            "additional_observed_position_joins": additional_positions,
            "explicit_state_exclusions": sorted(excluded),
            "nasa_class_context": {
                "generic_class_id": "ocean-eddies",
                "generic_relation": "osw_taxonomic_class_context_only",
                "specific_class_id": "agulhas-rings" if agulhas_member else None,
                "specific_relation": ("same_named_family_class" if eddy_id == "agulhas-rings-family" else
                                      "external_member_of_nasa_named_family") if agulhas_member else None,
                "individual_nasa_identity_claim": False,
            },
            "nasa_region_movie": {"tile_id": best["id"], "url": best["url"], "relation": "regional_context_only", "depth_relation": "subsurface_visibility_unverified" if item.get("vertical_evidence") else "not_assessed", "model_period": tile_ledger["model_period"], "crop_date_start": crop_timeline["date_start"], "crop_date_end": crop_timeline["date_end"], "crop_date_alignment_status": crop_timeline["alignment_status"], "temporal_relation": temporal_relation},
        }
        for code in candidates:
            state_index[code].append(eddy_id)
    for ids in state_index.values():
        ids.sort()
    for visits in observed_position_index.values():
        visits.sort(key=lambda visit: (visit["date"] or "", visit["eddy_id"]))
    output = {
        "schema": "osw.almanac.named-eddy-geography-join.v1",
        "source_ledger": "research/named-eddy-geography.json",
        "state_geometry": "figures/osw-province-atlas-interactive.svg",
        "nasa_tile_ledger": "research/nasa-perpetual-ocean-tile-join.json",
        "nasa_crop_timeline": "research/nasa-perpetual-ocean-crop-timeline.json",
        "nasa_object_ledger": "research/nasa-perpetual-ocean-objects.json",
        "method": "Point-in-coast-masked-OSW-state and point-in-NASA-crop joins with explicit semantic state exclusions. Points retain their reported-center, core-water sample-station, or editorial-gateway evidence type; none supplies a closed footprint.",
        "evidence_limit": "State locator candidates do not establish that a particular eddy is contained or intersects a state. NASA eddy-class links are OSW taxonomic context, not identification of an individual eddy in NASA footage. NASA crop links are geographic context and do not establish NASA identification or a dated match. A dated individual outside the model period cannot appear in the linked film. The crop date window is inferred across NASA releases; earlier source observations have no verified frame match, but the inferred window does not prove those months are absent from every crop.",
        "entries": entries,
        "states": state_index,
        "states_with_additional_observed_positions": observed_position_index,
    }
    OUTPUT.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(entries)} named eddy geography joins across {sum(bool(ids) for ids in state_index.values())} states")


if __name__ == "__main__":
    main()
