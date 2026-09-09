"""Project the admitted North Atlantic heatwave lineage onto ocean-state addresses."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

try:
    from acquire_ocean_state_hydrography_pilot import sha256_text_file
except ImportError:  # pragma: no cover
    from analysis.acquire_ocean_state_hydrography_pilot import sha256_text_file


ROOT = Path(__file__).resolve().parents[1]
EVENT_SPACING_DEG = 0.05
EARTH_RADIUS_KM = 6371.0088


def decode_province_grid(payload: dict) -> list[str | None]:
    rows, columns = payload["grid"]["shape"]
    decoded: list[str | None] = [None] * (rows * columns)
    for row, start, end, code in payload["footprint_runs"]:
        decoded[row * columns + start:row * columns + end + 1] = [code] * (end - start + 1)
    return decoded


def province_at(longitude: float, latitude: float, grid: dict, decoded: list[str | None]) -> str | None:
    rows, columns = grid["shape"]
    column = round((longitude - grid["longitude_start"]) / grid["spacing_degrees"])
    row = round((latitude - grid["latitude_start"]) / grid["spacing_degrees"])
    return decoded[row * columns + column] if 0 <= row < rows and 0 <= column < columns else None


def pixel_area_km2(latitude: float, spacing: float = EVENT_SPACING_DEG) -> float:
    south = math.radians(latitude - spacing / 2)
    north = math.radians(latitude + spacing / 2)
    return EARTH_RADIUS_KM ** 2 * math.radians(spacing) * (math.sin(north) - math.sin(south))


def footprint_state_overlap(component_rows: list, province_grid: dict, decoded: list[str | None]) -> dict:
    counts, areas = {}, {}
    for latitude, intervals in component_rows:
        for west, east, _category in intervals:
            pixel_count = round((east - west) / EVENT_SPACING_DEG) + 1
            for index in range(pixel_count):
                longitude = west + index * EVENT_SPACING_DEG
                code = province_at(longitude, latitude, province_grid, decoded) or "UNASSIGNED"
                counts[code] = counts.get(code, 0) + 1
                areas[code] = areas.get(code, 0.0) + pixel_area_km2(latitude)
    total_area = sum(areas.values())
    return {
        "pixel_count": sum(counts.values()),
        "states": [
            {"province": code, "pixel_count": counts[code], "area_km2": round(areas[code], 3), "area_fraction": round(areas[code] / total_area, 6)}
            for code in sorted(counts, key=lambda item: (-areas[item], item))
        ],
    }


def build(root: Path = ROOT) -> dict:
    root = Path(root)
    paths = {
        "primary": root / "research/osw-d3-noaa-crw-mhw-lineage-2026.json",
        "family": root / "research/osw-d7-noaa-crw-mhw-lineage-family-2026.json",
        "pruning": root / "research/osw-d8-noaa-crw-mhw-family-pruning-2026.json",
        "gap": root / "research/osw-d9-noaa-crw-mhw-typed-gap-graph-2026.json",
        "crosscheck": root / "research/osw-d10-oisst-mhw-bridge-crosscheck-2026.json",
        "provinces": root / "research/longhurst-2007-gebco-2026-depths.json",
        "adjacency": root / "research/longhurst-2007-province-adjacency.json",
    }
    data = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in paths.items()}
    province_grid = data["provinces"]["grid"]
    decoded = decode_province_grid(data["provinces"])
    graph_edges = {item["edge_id"] for item in data["adjacency"]["edges"]}

    primary_days = []
    for day in data["primary"]["daily_footprints"]:
        overlap = footprint_state_overlap(day["component_rows"], province_grid, decoded)
        if overlap["pixel_count"] != day["summary"]["pixel_count"]:
            raise ValueError(f"expanded footprint count differs on {day['date']}")
        primary_days.append({
            "date": day["date"], "address": {"geometry_edition": "longhurst-v4-54", "depth_support": "sea_surface_skin"},
            "footprint_area_km2": day["summary"]["area_km2"], "centroid": day["summary"]["centroid"],
            "province_overlap": overlap["states"], "dominant_province": overlap["states"][0]["province"],
            "maximum_category": day["summary"]["maximum_category"], "evidence_class": "satellite_analysis_threshold_footprint",
        })

    family_nodes = []
    node_state = {}
    for node in data["family"]["nodes"]:
        centroid = node["summary"]["centroid"]
        code = province_at(centroid["longitude_degrees_east"], centroid["latitude_degrees_north"], province_grid, decoded)
        node_state[node["node_id"]] = code
        family_nodes.append({"node_id": node["node_id"], "date": node["date"], "centroid": centroid, "province_by_centroid": code, "on_primary_branch": node["on_d3_primary_branch"], "area_km2": node["summary"]["area_km2"], "pixel_count": node["summary"]["pixel_count"], "address_precision": "nearest_committed_0.25_degree_province_assignment_at_component_centroid"})

    transitions = []
    for edge in data["family"]["edges"]:
        source, target = node_state[edge["from"]], node_state[edge["to"]]
        edge_id = "--".join(sorted((source, target))) if source != target else None
        transitions.append({
            **edge, "source_province": source, "target_province": target,
            "province_relation": "same_reference_state" if source == target else "adjacent_reference_state_transition",
            "source_graph_edge": edge_id,
            "source_graph_edge_confirmed": edge_id in graph_edges if edge_id else None,
            "evidence_meaning": "exact footprint-pixel lineage overlap plus centroid address change; not transported heat or measured cross-border flux",
        })

    post_gap = []
    for node in data["gap"]["post_gap_primary_lineage"]["nodes"]:
        centroid = node["summary"]["centroid"]
        post_gap.append({"node_id": node["node_id"], "date": node["date"], "province_by_centroid": province_at(centroid["longitude_degrees_east"], centroid["latitude_degrees_north"], province_grid, decoded), "status": "conditional_one_day_gap_extension"})

    primary_states = sorted({day["dominant_province"] for day in primary_days})
    family_states = sorted({node["province_by_centroid"] for node in family_nodes})
    crossing_candidates = [item for item in transitions if item["province_relation"] != "same_reference_state"]
    state_passports = []
    for code in family_states:
        nodes = [node for node in family_nodes if node["province_by_centroid"] == code]
        state_passports.append({
            "province": code,
            "roles": (["source", "transit", "destination"] if code in primary_states else ["unresolved_side_branch"]),
            "family_node_count": len(nodes), "primary_node_count": sum(node["on_primary_branch"] for node in nodes),
            "first_date": min(node["date"] for node in nodes), "last_date": max(node["date"] for node in nodes),
            "property_inventory": "not_joined_stage_3_is_2018_Drake_temperature",
            "boundary_exchange": "not_joined_stage_4_is_2018_SANT--SSTC",
            "uncertainty": "component identity and centroid-to-province assignment sensitivity; no transported-quantity uncertainty",
        })

    return {
        "schema": "osw-ocean-event-state-route-v1",
        "status": "stage_6_surface_event_route_complete_with_transport_unresolved",
        "event": {"detection_id": data["primary"]["detection_id"], "object_id": data["primary"]["object_id"], "name": data["primary"]["object_name"], "primary_interval": data["primary"]["tracked_window"], "depth_support": "sea_surface_skin"},
        "primary_route": {"days": primary_days, "province_sequence": primary_states, "finding": "The complete 21-day primary footprint remains dominantly inside GFST; movement within a state is not a border crossing."},
        "lineage_family_route": {"nodes": family_nodes, "transitions": transitions, "split_node_count": data["family"]["summary"]["split_node_count"], "merge_node_count": data["family"]["summary"]["merge_node_count"], "province_crossing_candidate_count": len(crossing_candidates), "crossing_candidates": crossing_candidates, "finding": "One small off-primary branch changes centroid address from GFST to adjacent NWCS after inheriting 13 pixels (0.62% of its source); this is a geometric lineage branch, not measured heat delivery."},
        "state_passports": state_passports,
        "conditional_gap_extension": {"typed_bridge": data["gap"]["typed_bridge"], "nodes": post_gap, "finding": "The governed one-day-gap extension remains in GFST by centroid through August 18, but is conditional on the declared gap policy."},
        "controls": {
            "exact_lineage_limits": data["primary"]["lineage_limits"],
            "weak_branch": {"node_id": "2026-07-29-C02", "province": "NWCS", "inherited_pixels": 13, "source_retained_fraction": 0.0062, "interpretation": "low-retention side branch rather than the primary route"},
            "independent_surface_temperature": data["crosscheck"]["identity_evaluation"],
        },
        "identity_sensitivity": {"area_pruning": data["pruning"]["identity_evaluation"], "typed_gap": data["gap"]["identity_evaluation"], "route_result": "The 21-node primary GFST route survives all tested family area thresholds; the post-gap GFST extension remains policy-conditioned."},
        "evidence_ladder": {
            "geometric_overlap": "supported_exact_daily_pixel_overlap_and_committed_province_assignment",
            "observed_property_propagation": "partially_supported_satellite_analysis_category_continuity_not_a_heat_quantity",
            "model_pathway": "unsupported",
            "volume_exchange": "unsupported_no_matched_edge_time_or_product",
            "heat_transport": "unsupported_no_matched_edge_time_or_product",
        },
        "state_account_timeline": [{"date": day["date"], "event_shock": {"dominant_province": day["dominant_province"], "area_km2": day["footprint_area_km2"], "maximum_category": day["maximum_category"]}, "inventory": "not_available_at_event_time", "exchange": "not_available_at_event_edge_or_time", "revision_status": "primary_exact_overlap_lineage"} for day in primary_days],
        "sources": {name: {"path": path.relative_to(root).as_posix(), "canonical_lf_sha256": sha256_text_file(path)} for name, path in paths.items()},
        "unsupported": ["causal heat origin", "three-dimensional depth penetration", "volume transported across GFST--NWCS", "heat transported across GFST--NWCS", "velocity pathway", "event energy inventory", "termination mechanism", "probability"],
        "boundary": "State routes describe where thresholded surface footprints and lineage nodes occur. Exact pixel inheritance and adjacency do not prove that water or heat crossed a province edge. The 2018 Drake inventories and exchange pilot are spatially and temporally unrelated and are explicitly not joined to this 2026 event.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=Path("research/ocean-event-state-route-2026.json"))
    parser.add_argument("--browser-output", type=Path, default=Path("exchange/events.js"))
    args = parser.parse_args()
    result = build(args.root)
    output = args.output if args.output.is_absolute() else args.root / args.output
    browser = args.browser_output if args.browser_output.is_absolute() else args.root / args.browser_output
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    browser.write_text("window.OSW_EVENTS = " + json.dumps(result, separators=(",", ":")) + ";\n", encoding="utf-8", newline="\n")
    print(json.dumps({"primary_states": result["primary_route"]["province_sequence"], "family_states": [item["province"] for item in result["state_passports"]], "crossing_candidates": result["lineage_family_route"]["province_crossing_candidate_count"]}, indent=2))


if __name__ == "__main__":
    main()
