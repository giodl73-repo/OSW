"""Combine independently named eddy labels without merging source identities."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

from shapely.ops import unary_union
from build_motion_state_join import PROVINCES, polygon_parts, project


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
OUTPUT = RESEARCH / "ocean-eddy-name-inventory.json"


def read(name: str) -> dict:
    return json.loads((RESEARCH / name).read_text(encoding="utf-8"))


def observed_center_state_codes(lon_lat: list[float]) -> list[str]:
    """Index a reported center point; this cannot establish ring containment."""
    root = ET.parse(PROVINCES).getroot()
    land_path = next(node.get("d") for node in root.iter() if node.get("class") == "land-context")
    land = unary_union(polygon_parts(land_path))
    point = project(lon_lat)
    return sorted(group.get("data-code") for group in root.iter()
                  if "province " in group.get("class", "") and
                  unary_union(polygon_parts(next(node.get("d") for node in group
                                               if node.tag.endswith("path")))).difference(land).covers(point))


def main() -> None:
    loop = read("named-loop-current-eddy-identities.json")
    loop_context = read("named-loop-eddy-nasa-context.json")
    published = read("named-loop-eddy-published-observations.json")
    kraken_figure = read("kraken-2013-figure2-state-audit.json")
    kraken_candidate = kraken_figure["state_candidate"]
    kraken_ssh = kraken_figure["dated_ssh_footprint_candidate"]
    if (kraken_candidate["id"] != "published:kraken-2013" or kraken_candidate["state_code"] != "CAMR"):
        raise ValueError("Unexpected Kraken figure state candidate")
    if (kraken_ssh["id"] != kraken_candidate["id"] or
            kraken_ssh["nominal_state_codes"] != ["CAMR", "CARB"]):
        raise ValueError("Unexpected Kraken dated SSH contour state assessment")
    geography = read("named-eddy-geography.json")
    geography_join = read("named-eddy-geography-join.json")
    nasa_ids = {item["id"] for item in read("nasa-perpetual-ocean-objects.json")["objects"]}
    if not {"ocean-eddies", "gulf-of-mexico-loop-eddies", "agulhas-rings"} <= nasa_ids:
        raise ValueError("NASA eddy class records are missing")
    loop_by_id = {item["id"]: item for item in loop_context["entries"]}
    if set(loop_by_id) != {item["id"] for item in loop["entries"]}:
        raise ValueError("Horizon names and NASA context differ")
    rows = []
    for item in loop["entries"]:
        context = loop_by_id[item["id"]]
        rows.append({
            "id": f"horizon:{item['id']}", "name": item["name"], "source_collection": "horizon_loop_current",
            "source_record_id": item["id"], "source_url": loop["source"],
            "identity_level": "individual_eddy", "identity_evidence": "numbered_primary_separation" if item["role"] == "primary" else "linked_secondary_name_undated",
            "source_event_number": item["source_number"], "source_event_date": item["initial_separation"],
            "date_evidence": {"initial_separation": item["initial_separation"], "independent_secondary_date": None if item["role"] == "secondary" else item["initial_separation"]},
            "related_primary_id": item["related_primary_id"], "basin": "Gulf of Mexico",
            "generic_nasa_class_id": "ocean-eddies", "specific_nasa_class_id": context["nasa_object_id"],
            "nasa_relation": "related_described_class_only", "nasa_individual_identity_claim": False,
            "state_locator_candidates": context["state_locator_candidates"], "state_relation": context["state_relation"],
            "locator_evidence_type": "shared_source_region_gateway",
            "published_observed_position": context["published_observed_position"],
            "published_dated_map_presence": context["published_dated_map_presence"],
            "nasa_movie_url": context["nasa_region_movie"]["url"], "movie_relation": context["nasa_region_movie"]["relation"],
            "temporal_relation": context["temporal_relation"], "atlas_anchor": f"#eddy-{item['id']}",
        })
    for item in published["entries"]:
        if not item["eddy_id"].startswith("published:"):
            raise ValueError("Published ring must have its own source-scoped ID")
        if item["name"] not in {entry["name"] for entry in loop["entries"]}:
            raise ValueError("Published ring name missing from the possible Horizon crosswalk")
        figure_candidate = kraken_candidate if item["eddy_id"] == kraken_candidate["id"] else None
        observed_center = item.get("observed_center")
        center_states = (observed_center_state_codes(observed_center["coordinate_lon_lat"])
                         if observed_center else [])
        if observed_center and len(center_states) != 1:
            raise ValueError(f"Published center must locate in exactly one approximate state: {item['eddy_id']}")
        state_candidates = ([figure_candidate["state_code"]] if figure_candidate else center_states)
        rows.append({
            "id": item["eddy_id"], "name": item["name"],
            "source_collection": "published_loop_current",
            "source_record_id": item["eddy_id"], "source_url": item["source_url"],
            "identity_level": "individual_eddy", "identity_evidence": "published_dated_observation_with_attributed_name" if item.get("name_origin") else "independent_published_named_observation",
            "name_origin": item.get("name_origin"),
            "source_event_number": None, "source_event_date": None,
            "date_evidence": {"observation_start": item["observation_start"],
                              "observation_end": item["observation_end"]},
            "independent_event_observations": item.get("independent_event_observations", []),
            "basin": "Gulf of Mexico", "generic_nasa_class_id": "ocean-eddies",
            "specific_nasa_class_id": None,
            "nasa_relation": "generic_eddy_class_context_only",
            "nasa_individual_identity_claim": False,
            "state_locator_candidates": state_candidates,
            "state_relation": ("figure_derived_red_curve_candidate_only" if figure_candidate else
                               "published_dated_center_point_candidate_only" if observed_center else "no_dated_footprint"),
            "locator_evidence_type": ("figure_derived_red_curve_pixels" if figure_candidate else
                                      "published_observed_center" if observed_center else "no_coordinate_extracted"),
            "figure_state_audit": ({**figure_candidate,
                                    "audit_path": "research/kraken-2013-figure2-state-audit.json",
                                    "source_pdf_sha256": kraken_figure["source_pdf_sha256"],
                                    "embedded_figure_sha256": kraken_figure["embedded_figure_sha256"]}
                                   if figure_candidate else None),
            "dated_ssh_footprint_audit": ({**kraken_ssh,
                                            "audit_path": "research/kraken-2013-figure2-state-audit.json"}
                                           if figure_candidate else None),
            "published_observed_position": ({**observed_center, "state_center_candidates": center_states,
                                              "source_url": item["source_url"]} if observed_center else None),
            "near_center_mooring": item.get("near_center_mooring"),
            "published_dated_map_presence": {
                "source_url": item["source_url"],
                "source_locator": item["source_locator"],
                "observation_start": item["observation_start"],
                "observation_end": item["observation_end"],
                "state_relation": "published_figure_geometry_not_digitized",
            },
            "nasa_movie_url": None, "movie_relation": None,
            "temporal_relation": "individual_nasa_identity_unverified",
            "atlas_anchor": "object.html?id=eddy%3A" + item["eddy_id"].replace(":", "%3A"),
        })
    if set(geography_join["entries"]) != {item["id"] for item in geography["entries"]}:
        raise ValueError("Named eddy geography and state join differ")
    for item in geography["entries"]:
        context = geography_join["entries"][item["id"]]
        class_context = context["nasa_class_context"]
        rows.append({
            "id": f"geography:{item['id']}", "name": item["name"], "source_collection": "named_eddy_geography",
            "source_record_id": item["id"], "source_url": geography["sources"][item["source"]],
            "identity_level": item["identity_level"], "identity_evidence": "source_dated_individual" if item["identity_level"] == "individual_eddy" else "named_family_or_recurring_region",
            "source_event_number": None, "source_event_date": None, "event_year": item.get("event_year"),
            "date_evidence": {
                "formation_period": item.get("formation", {}).get("period"),
                "observed_center_period": item.get("observed_center", {}).get("period"),
                "sample_date": item.get("sample_site", {}).get("date"),
                "reported_track_period": item.get("reported_track_period"),
                "reported_fate": item.get("reported_fate"),
                "reported_encounter": item.get("reported_encounter"),
            },
            "external_track_identifier": item.get("external_track_identifier"),
            "reported_lifetime_years_approx": item.get("reported_lifetime_years_approx"),
            "reported_travel_km_lower_bound": item.get("reported_travel_km_lower_bound"),
            "reported_motion_source_locator": item.get("reported_motion_source_locator"),
            "independent_source_census": (
                {**item["independent_source_census"], "source_url": geography["sources"][item["independent_source_census"]["source"]]}
                if item.get("independent_source_census") else None
            ),
            "related_primary_id": item.get("member_of"), "basin": item["basin"],
            "related_current_id": item.get("related_current_id"),
            "activity_region": (
                {**item["activity_region"], "source_url": geography["sources"][item["activity_region"]["source"]]}
                if item.get("activity_region") else None
            ),
            "supporting_source_urls": [geography["sources"][key] for key in item.get("supporting_sources", [])],
            "vertical_evidence": item.get("vertical_evidence"),
            "generic_nasa_class_id": class_context["generic_class_id"],
            "specific_nasa_class_id": class_context["specific_class_id"],
            "nasa_relation": class_context["specific_relation"] or class_context["generic_relation"],
            "nasa_related_flow_id": item.get("related_nasa_object_id"), "nasa_individual_identity_claim": False,
            "state_locator_candidates": context["state_locator_candidates"], "state_relation": "point_locator_only" if context["state_locator_candidates"] else "no_suitable_osw_state",
            "additional_observed_position_joins": context["additional_observed_position_joins"],
            "locator_evidence_type": "sample_site" if item.get("sample_site") else "observed_center" if item.get("observed_center") else "reported_event_point" if item.get("formation") else "editorial_region",
            "nasa_movie_url": context["nasa_region_movie"]["url"], "movie_relation": context["nasa_region_movie"]["relation"],
            "movie_depth_relation": context["nasa_region_movie"]["depth_relation"],
            "temporal_relation": context["nasa_region_movie"]["temporal_relation"], "atlas_anchor": f"#eddy-geography-{item['id']}",
        })
    if len({item["id"] for item in rows}) != len(rows):
        raise ValueError("Duplicate unified eddy record ID")
    if any(item["generic_nasa_class_id"] not in nasa_ids or item["specific_nasa_class_id"] and item["specific_nasa_class_id"] not in nasa_ids for item in rows):
        raise ValueError("Named eddy points to an unknown NASA class")
    output = {
        "schema": "osw.almanac.ocean-eddy-name-inventory.v1",
        "sources": ["research/named-loop-current-eddy-identities.json", "research/named-loop-eddy-nasa-context.json", "research/named-loop-eddy-published-observations.json", "research/kraken-2013-figure2-state-audit.json", "research/named-eddy-geography.json", "research/named-eddy-geography-join.json"],
        "scope": "One address for every independently named eddy label or named regional/family record currently admitted to the OSW almanac. This source-set inventory is not a complete global list of all eddies or all names. NOAA detection IDs are separate unnamed, dated observations.",
        "claim_limit": "NASA class and movie links are taxonomic or geographic context, never an individual identity match. A regional gateway, observed center, or sample station does not establish a closed footprint, OSW state containment, or a whole eddy track. Secondary Horizon names have no independent separation date in the source.",
        "record_count": len(rows),
        "horizon_name_count": len(loop["entries"]),
        "published_loop_record_count": len(published["entries"]),
        "horizon_numbered_event_count": loop["numbered_event_count"],
        "other_named_record_count": len(geography["entries"]),
        "source_dated_other_individual_count": sum(item["identity_level"] == "individual_eddy" for item in geography["entries"]),
        "entries": rows,
    }
    OUTPUT.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} named eddy records across {output['horizon_numbered_event_count']} Horizon events and {len(geography['entries'])} other names")


if __name__ == "__main__":
    main()
