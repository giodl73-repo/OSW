"""Challenge the placement and lane boundaries of the Arctic M2 surface screens."""

from __future__ import annotations

import argparse
import json
import pathlib

try:
    from analyze_arctic_entrances_motion import GATES, load_assignment, sha256_file, summarize_gate
except ModuleNotFoundError:
    from analysis.analyze_arctic_entrances_motion import GATES, load_assignment, sha256_file, summarize_gate


FRAM_LATITUDES = (77.6666667, 78.0, 78.3333333, 78.6666667, 79.0, 79.3333333)
FRAM_EAST_STARTS = (363.0, 364.0, 365.0, 366.0, 367.0)
FRAM_WEST_ENDS = (358.0, 360.0, 362.0)
BARENTS_LONGITUDES = tuple(float(value) for value in range(20, 31))


def screen(payload: dict, base: dict, **changes) -> dict:
    definition = {**base, **changes}
    definition.pop("lanes", None)
    result = summarize_gate(payload, definition)
    return {
        "requested_fixed_coordinate": definition["target"],
        "sampled_fixed_coordinate": result["sampled_fixed_coordinate"],
        "along_min": definition["along_min"],
        "along_max": definition["along_max"],
        "gate_cell_count": result["gate_cell_count"],
        "annual_mean_normal_velocity_m_s": result["annual_frame_weighted_mean_normal_velocity_m_s"],
        "seasonal_mean_normal_velocity_m_s": {item["season"]: item["mean_normal_velocity_m_s"] for item in result["seasons"]},
    }


def summarize_cases(cases: list[dict], positive: bool) -> dict:
    values = [case["annual_mean_normal_velocity_m_s"] for case in cases]
    supports = [value > 0 if positive else value < 0 for value in values]
    return {
        "case_count": len(cases),
        "direction_support_count": sum(supports),
        "direction_support_fraction": sum(supports) / len(supports),
        "minimum_m_s": min(values),
        "maximum_m_s": max(values),
        "range_m_s": max(values) - min(values),
    }


def run(fram_path: pathlib.Path, barents_path: pathlib.Path) -> dict:
    fram = load_assignment(fram_path); barents = load_assignment(barents_path)
    east = [screen(fram, GATES["fram"], target=latitude, along_min=start, along_max=375.0) for latitude in FRAM_LATITUDES for start in FRAM_EAST_STARTS]
    west = [screen(fram, GATES["fram"], target=latitude, along_min=350.0, along_max=end) for latitude in FRAM_LATITUDES for end in FRAM_WEST_ENDS]
    barents_cases = [screen(barents, GATES["barents"], target=longitude) for longitude in BARENTS_LONGITUDES]
    return {
        "schema": "oceanlines.osw.m2-arctic-entrances-sensitivity.v1",
        "status": "nearby_surface_screen_and_lane_boundary_challenge",
        "fram_eastern_inflow": {"cases": east, "summary": summarize_cases(east, True), "expected_direction": "northward positive"},
        "fram_western_export": {"cases": west, "summary": summarize_cases(west, False), "expected_direction": "southward negative"},
        "barents_eastward_inflow": {"cases": barents_cases, "summary": summarize_cases(barents_cases, True), "expected_direction": "eastward positive"},
        "sources": [
            {"path": str(fram_path), "sha256": sha256_file(fram_path), "source_sha256": fram["source_sha256"], "field_sha256": fram["field_sha256"]},
            {"path": str(barents_path), "sha256": sha256_file(barents_path), "source_sha256": barents["source_sha256"], "field_sha256": barents["field_sha256"]},
        ],
        "boundary": "Nearby placements and lane bounds challenge unweighted nominal-15-m OSCAR surface screens only. Directional robustness is not uncertainty, probability, transport, or a full-depth gateway definition. Fram sensitivity reinforces the need to derive the M3 section and branches from native geometry and signed transport rather than copy one M2 line.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fram", type=pathlib.Path, default=pathlib.Path("atlas/data/oscar-timeseries-fram-native-2018.js"))
    parser.add_argument("--barents", type=pathlib.Path, default=pathlib.Path("atlas/data/oscar-timeseries-barents-native-2018.js"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m2-arctic-entrances-sensitivity-2018.json"))
    args = parser.parse_args()
    result = run(args.fram, args.barents)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
