"""Compare split/merge branch-selection rules for the OSW-D3 heatwave lineage."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "atlas" / "data" / "noaa-crw-mhw-point-north-atlantic-2026.json"
DEFAULT_LINEAGE = ROOT / "research" / "osw-d3-noaa-crw-mhw-lineage-2026.json"
DEFAULT_OUTPUT = ROOT / "research" / "osw-d6-noaa-crw-mhw-branch-sensitivity-2026.json"
ANCHOR_DATE = "2026-07-23"


def load_module(filename, name):
    path = Path(__file__).with_name(filename)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


TRACK = load_module("track_noaa_crw_mhw_footprint.py", "osw_tracker_branch_sensitivity")


POLICIES = [
    {"policy_id": "greatest_intersection", "label": "largest shared footprint"},
    {"policy_id": "greatest_iou", "label": "best proportional shape match"},
    {"policy_id": "greatest_candidate_inherited_fraction", "label": "purest inherited candidate"},
    {"policy_id": "largest_overlapping_component", "label": "largest overlapping component"},
]


def component_sha256(component):
    encoded = ";".join(f"{y},{x}" for y, x in sorted(component)).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def candidate_summary(candidate):
    return {
        "pixel_count": len(candidate["component"]),
        "intersection_pixels": candidate["intersection_pixels"],
        "iou": round(candidate["iou"], 4),
        "seed_side_retained_fraction": round(candidate["previous_retained_fraction"], 4),
        "candidate_inherited_fraction": round(candidate["current_inherited_fraction"], 4),
        "component_sha256": component_sha256(candidate["component"]),
    }


def choose_candidate(candidates, policy_id):
    """Choose one overlapping component using a declared, deterministic score."""
    if not candidates:
        return None
    tie = lambda item: (-item["intersection_pixels"], min(item["component"]))
    if policy_id == "greatest_intersection":
        key = lambda item: (-item["intersection_pixels"], -item["iou"], min(item["component"]))
    elif policy_id == "greatest_iou":
        key = lambda item: (-item["iou"], *tie(item))
    elif policy_id == "greatest_candidate_inherited_fraction":
        key = lambda item: (-item["current_inherited_fraction"], *tie(item))
    elif policy_id == "largest_overlapping_component":
        key = lambda item: (-len(item["component"]), *tie(item))
    else:
        raise ValueError(f"unknown policy: {policy_id}")
    return sorted(candidates, key=key)[0]


def new_state(seed):
    return {"tracked": {ANCHOR_DATE: seed}, "transitions": [], "forward_open": True, "backward_open": True}


def extend_states(states, paths, dates, start_index, direction):
    if direction == "forward":
        sequence = dates[start_index + 1:]
        neighbor = lambda date_value: dates[dates.index(date_value) - 1]
        open_key = "forward_open"
    else:
        sequence = reversed(dates[:start_index])
        neighbor = lambda date_value: dates[dates.index(date_value) + 1]
        open_key = "backward_open"
    for date_value in sequence:
        _, _, _, active = TRACK.read_field(paths[date_value])
        for policy in POLICIES:
            state = states[policy["policy_id"]]
            if not state[open_key]:
                continue
            seed_side_date = neighbor(date_value)
            seed_side_component = state["tracked"][seed_side_date]
            candidates = TRACK.overlapping_components(active, seed_side_component)
            selected = choose_candidate(candidates, policy["policy_id"])
            if selected is None:
                state[open_key] = False
                state[f"{direction}_stop"] = {"date": date_value, "reason": "no exact-overlap candidate"}
                continue
            state["tracked"][date_value] = selected["component"]
            state["transitions"].append({
                "extension_direction": direction,
                "seed_side_date": seed_side_date,
                "candidate_date": date_value,
                "candidate_count": len(candidates),
                "branch_ambiguity": len(candidates) > 1,
                "selected": candidate_summary(selected),
                "candidates": [candidate_summary(item) for item in candidates],
            })


def decode_runs(rows, latitudes, longitudes):
    lat_index = {round(float(value), 3): index for index, value in enumerate(latitudes)}
    lon_index = {round(float(value), 3): index for index, value in enumerate(longitudes)}
    component = set()
    for latitude, runs in rows:
        y = lat_index[round(latitude, 3)]
        for west, east, _category in runs:
            start = lon_index[round(west, 3)]
            stop = lon_index[round(east, 3)]
            component.update((y, x) for x in range(start, stop + 1))
    return component


def build(source_path=DEFAULT_SOURCE, lineage_path=DEFAULT_LINEAGE, output_path=DEFAULT_OUTPUT):
    source_path, lineage_path, output_path = map(Path, (source_path, lineage_path, output_path))
    source = json.loads(source_path.read_text(encoding="utf-8"))
    lineage = json.loads(lineage_path.read_text(encoding="utf-8"))
    dates = [item["date"] for item in source["files"]]
    with tempfile.TemporaryDirectory(prefix="osw-crw-branches-") as temporary:
        paths = TRACK.download_and_verify(source["files"], Path(temporary))
        latitudes, longitudes, _, active = TRACK.read_field(paths[ANCHOR_DATE])
        anchor = (
            int(abs(latitudes - source["coordinate"]["latitude_degrees_north"]).argmin()),
            int(abs(longitudes - source["coordinate"]["longitude_degrees_east"]).argmin()),
        )
        seed = TRACK.FOOTPRINT.connected_component(active, anchor)
        states = {policy["policy_id"]: new_state(seed) for policy in POLICIES}
        start_index = dates.index(ANCHOR_DATE)
        extend_states(states, paths, dates, start_index, "forward")
        extend_states(states, paths, dates, start_index, "backward")

    baseline = states["greatest_intersection"]["tracked"]
    expected = {
        item["date"]: decode_runs(item["component_rows"], latitudes, longitudes)
        for item in lineage["daily_footprints"]
    }
    if baseline != expected:
        raise ValueError("greatest-intersection branch does not reproduce OSW-D3 cell for cell")

    results = []
    baseline_hashes = {date_value: component_sha256(component) for date_value, component in baseline.items()}
    for policy in POLICIES:
        state = states[policy["policy_id"]]
        ordered_dates = [date_value for date_value in dates if date_value in state["tracked"]]
        hashes = {date_value: component_sha256(state["tracked"][date_value]) for date_value in ordered_dates}
        differing_dates = [date_value for date_value in ordered_dates if baseline_hashes.get(date_value) != hashes[date_value]]
        results.append({
            **policy,
            "tracked_window": {"start": ordered_dates[0], "end": ordered_dates[-1], "day_count": len(ordered_dates)},
            "forward_stop": state.get("forward_stop"),
            "backward_stop": state.get("backward_stop"),
            "branch_ambiguous_transition_count": sum(item["branch_ambiguity"] for item in state["transitions"]),
            "selected_component_sha256_by_date": hashes,
            "differs_from_baseline_on_dates": differing_dates,
            "transitions": sorted(state["transitions"], key=lambda item: dates.index(item["candidate_date"])),
        })

    baseline_result = results[0]
    comparison = []
    for result in results[1:]:
        comparison.append({
            "policy_id": result["policy_id"],
            "same_tracked_window": result["tracked_window"] == baseline_result["tracked_window"],
            "same_daily_components": not result["differs_from_baseline_on_dates"],
            "differing_daily_component_count": len(result["differs_from_baseline_on_dates"]),
            "first_differing_date": result["differs_from_baseline_on_dates"][0] if result["differs_from_baseline_on_dates"] else None,
        })

    payload = {
        "schema": "osw.ocean-object-branch-sensitivity.v1",
        "detection_id": "OSW-D6",
        "status": "branch_policy_bakeoff",
        "object_id": "OBJ046",
        "object_name": "marine heatwave",
        "source_artifacts": [
            {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in (source_path, lineage_path)
        ],
        "controlled_choices": {
            "seed": f"four-neighbor component containing the OSW-D1 anchor on {ANCHOR_DATE}",
            "minimum_overlap": "at least one exact native-grid cell",
            "branch_policies": POLICIES,
            "selection_direction": "each policy is applied outward from the anchor independently forward and backward",
            "longitude_periodicity": True,
        },
        "results": results,
        "comparison_to_greatest_intersection": comparison,
        "identity_evaluation": {
            "result": "policy_dependent",
            "finding": "Four declared split/merge branch-selection policies are compared cell for cell; matching lifetimes can coexist with different selected daily components.",
        },
        "boundary": "This bakeoff follows exact-overlap threshold-state components, not water parcels. The four scores are an illustrative diagnostic set, not uniquely correct tracking laws. A policy is applied in extension direction from the anchor, which is not equivalent to reconstructing a causal history backward in time. Connectivity, gap, minimum-overlap, forcing, advection, subsurface continuity, attribution, and impacts remain separate tests.",
    }
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--lineage", type=Path, default=DEFAULT_LINEAGE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build(args.source, args.lineage, args.output)
    print(f'wrote {args.output}: {len(payload["results"])} branch policies')


if __name__ == "__main__":
    main()
