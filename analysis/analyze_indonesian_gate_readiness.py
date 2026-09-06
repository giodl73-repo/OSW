"""Audit whether native OSCAR can support named Indonesian Throughflow screens."""

from __future__ import annotations

import argparse
import json
import pathlib
import statistics

try:
    from analyze_arctic_entrances_motion import gate_indices, month_of, sha256_file, validate_payload, SEASONS, SEASON_MONTHS
    from simulate_oscar_pathways import load_assignment
except ModuleNotFoundError:
    from analysis.analyze_arctic_entrances_motion import gate_indices, month_of, sha256_file, validate_payload, SEASONS, SEASON_MONTHS
    from analysis.simulate_oscar_pathways import load_assignment


# These are candidate grid-aligned surface screens, not observational sections.
# Their first job is to expose whether a 1/3-degree product leaves enough wet
# samples to justify an M2 direction diagnostic at each narrow passage.
GATES = (
    {"code": "MAK", "name": "Makassar Strait", "role": "primary upper-ocean inflow", "orientation": "zonal", "target": -2.5, "along_min": 117.5, "along_max": 120.0, "component": "v", "positive_multiplier": -1, "positive": "southward"},
    {"code": "LIF", "name": "Lifamatola Passage", "role": "deep eastern inflow", "orientation": "zonal", "target": -1.8333333, "along_min": 126.3333333, "along_max": 127.6666667, "component": "v", "positive_multiplier": -1, "positive": "southward"},
    {"code": "LOM", "name": "Lombok Strait", "role": "western outflow", "orientation": "zonal", "target": -8.5, "along_min": 115.0, "along_max": 116.3333333, "component": "v", "positive_multiplier": -1, "positive": "southward toward Indian Ocean"},
    {"code": "OMB", "name": "Ombai Strait", "role": "central deep outflow", "orientation": "meridional", "target": 125.0, "along_min": -9.1666667, "along_max": -8.0, "component": "u", "positive_multiplier": -1, "positive": "westward toward Indian Ocean"},
    {"code": "TIM", "name": "Timor Passage", "role": "eastern broad outflow", "orientation": "meridional", "target": 126.0, "along_min": -12.5, "along_max": -9.5, "component": "u", "positive_multiplier": -1, "positive": "westward toward Indian Ocean"},
)


def summarize(payload: dict, gate: dict) -> dict:
    indices, sampled_coordinate = gate_indices(payload, gate)
    component_key = f"{gate['component']}_mm_s"
    frame_valid = []
    frame_means = []
    seasonal = []
    for frame in payload["frames"]:
        values = [frame[component_key][index] for index in indices]
        valid = [gate["positive_multiplier"] * value / 1000 for value in values if value is not None]
        frame_valid.append(len(valid))
        frame_means.append(sum(valid) / len(valid) if valid else None)
    for season in SEASONS:
        selected = [value for frame, value in zip(payload["frames"], frame_means) if month_of(frame) in SEASON_MONTHS[season] and value is not None]
        seasonal.append({"season": season, "frame_count": len(selected), "mean_declared_positive_velocity_m_s": sum(selected) / len(selected) if selected else None})
    finite_means = [value for value in frame_means if value is not None]
    minimum = min(frame_valid)
    columns = len(payload["longitude_values"])
    point_support = []
    for index in indices:
        row, column = divmod(index, columns)
        finite_frames = sum(frame[component_key][index] is not None for frame in payload["frames"])
        point_support.append({"latitude": payload["latitude_values"][row], "longitude": payload["longitude_values"][column], "finite_frames": finite_frames})
    # A one-cell screen can suggest motion but cannot describe passage structure.
    if minimum >= 3:
        readiness = "screenable_at_m2"
    elif minimum >= 1:
        readiness = "direction_only_underresolved"
    else:
        readiness = "not_screenable"
    annual_mean = sum(finite_means) / len(finite_means) if finite_means else None
    direction_consistent = annual_mean is not None and annual_mean > 0
    verdict = "usable_surface_hint" if readiness == "screenable_at_m2" and direction_consistent else "surface_sign_conflict" if readiness == "screenable_at_m2" else readiness
    return {
        **gate,
        "sampled_fixed_coordinate": sampled_coordinate,
        "candidate_grid_points": len(indices),
        "finite_points_per_frame": {"minimum": minimum, "median": statistics.median(frame_valid), "maximum": max(frame_valid)},
        "finite_fraction_minimum": minimum / len(indices) if indices else 0,
        "readiness": readiness,
        "direction_consistent_with_declared_path": direction_consistent,
        "verdict": verdict,
        "annual_frame_weighted_mean_declared_positive_velocity_m_s": annual_mean,
        "point_support": point_support,
        "seasons": seasonal,
    }


def run(path: pathlib.Path) -> dict:
    payload = load_assignment(path)
    validate_payload(payload)
    if payload["period_start"] != "2017-12-01" or payload["period_stop"] != "2018-11-21":
        raise ValueError("Indonesian readiness audit requires the declared matched historical year")
    gates = [summarize(payload, gate) for gate in GATES]
    return {
        "schema": "oceanlines.osw.m2-indonesian-gate-readiness.v1",
        "status": "historical_surface_gate_resolvability_audit",
        "period": {"start": payload["period_start"], "stop": payload["period_stop"], "fields": len(payload["frames"])},
        "gates": gates,
        "source": {"path": str(path), "sha256": sha256_file(path), "source_sha256": payload["source_sha256"], "field_sha256": payload["field_sha256"], "shape": payload["shape"], "sampled_extent": payload["sampled_extent"], "nominal_depth_m": payload["nominal_depth_m"]},
        "method": "Candidate axis-aligned screens sample finite native-grid OSCAR normal velocity. Readiness requires at least three finite points in every frame; one or two points are retained only as an explicitly underresolved direction hint.",
        "boundary": "This is a grid-support audit, not validation of the geographic section. Older OSCAR 2017.0 nominal-15-m velocity cannot represent full-depth sill geometry, tidal mixing, temperature/salinity transformation, volume transport, heat transport, or the simultaneous INSTANT observational estimate. Narrow passages may require a finer native model or mooring product.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("atlas/data/oscar-timeseries-indonesian-native-2018.js"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m2-indonesian-gate-readiness-2018.json"))
    args = parser.parse_args()
    result = run(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")
    for gate in result["gates"]:
        points = gate["finite_points_per_frame"]
        mean = gate["annual_frame_weighted_mean_declared_positive_velocity_m_s"]
        print(f"{gate['code']}: {gate['readiness']} · wet {points['minimum']}/{gate['candidate_grid_points']} · mean {mean:+.4f} m/s" if mean is not None else f"{gate['code']}: {gate['readiness']} · no finite mean")


if __name__ == "__main__":
    main()
