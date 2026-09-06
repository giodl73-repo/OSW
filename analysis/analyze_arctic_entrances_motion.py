"""Compare one-year OSCAR surface motion across the paired Atlantic-Arctic entrances."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib

try:
    from simulate_oscar_pathways import load_assignment
except ModuleNotFoundError:
    from analysis.simulate_oscar_pathways import load_assignment


SEASONS = ("DJF", "MAM", "JJA", "SON")
SEASON_MONTHS = {"DJF": {12, 1, 2}, "MAM": {3, 4, 5}, "JJA": {6, 7, 8}, "SON": {9, 10, 11}}
GATES = {
    "fram": {
        "name": "Fram Strait surface screen",
        "orientation": "zonal",
        "target": 78.8333333,
        "along_min": 350.0,
        "along_max": 372.0,
        "positive": "northward toward Arctic",
        "component": "v",
        "lanes": (
            {"name": "western export lane", "along_min": 350.0, "along_max": 360.0},
            {"name": "central transition lane", "along_min": 360.3333333, "along_max": 364.6666667},
            {"name": "eastern inflow lane", "along_min": 365.0, "along_max": 375.0},
        ),
    },
    "barents": {
        "name": "Barents Sea Opening surface screen",
        "orientation": "meridional",
        "target": 20.3333333,
        "along_min": 71.0,
        "along_max": 74.6666667,
        "positive": "eastward into Barents Sea",
        "component": "u",
    },
}


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def month_of(frame: dict) -> int:
    return int(frame["time"][5:7])


def gate_indices(payload: dict, definition: dict) -> tuple[list[int], float]:
    latitudes = payload["latitude_values"]
    longitudes = payload["longitude_values"]
    if definition["orientation"] == "zonal":
        row = min(range(len(latitudes)), key=lambda index: abs(latitudes[index] - definition["target"]))
        columns = [index for index, value in enumerate(longitudes) if definition["along_min"] <= value <= definition["along_max"]]
        return [row * len(longitudes) + column for column in columns], latitudes[row]
    column = min(range(len(longitudes)), key=lambda index: abs(longitudes[index] - definition["target"]))
    rows = [index for index, value in enumerate(latitudes) if definition["along_min"] <= value <= definition["along_max"]]
    return [row * len(longitudes) + column for row in rows], longitudes[column]


def summarize_gate(payload: dict, definition: dict) -> dict:
    indices, sampled_coordinate = gate_indices(payload, definition)
    component_key = "v_mm_s" if definition["component"] == "v" else "u_mm_s"
    seasons = []
    for season in SEASONS:
        frame_means = []
        all_samples = []
        for frame in payload["frames"]:
            if month_of(frame) not in SEASON_MONTHS[season]:
                continue
            samples = [frame[component_key][index] / 1000 for index in indices if frame[component_key][index] is not None]
            if samples:
                frame_means.append(sum(samples) / len(samples))
                all_samples.extend(samples)
        mean = sum(frame_means) / len(frame_means)
        mean_absolute = sum(abs(value) for value in all_samples) / len(all_samples)
        seasons.append({
            "season": season,
            "frame_count": len(frame_means),
            "sample_count": len(all_samples),
            "mean_normal_velocity_m_s": mean,
            "mean_absolute_normal_velocity_m_s": mean_absolute,
            "signed_persistence": 0 if mean_absolute == 0 else mean / mean_absolute,
            "positive_sample_fraction": sum(value > 0 for value in all_samples) / len(all_samples),
        })
    all_weight = sum(item["frame_count"] for item in seasons)
    annual_mean = sum(item["mean_normal_velocity_m_s"] * item["frame_count"] for item in seasons) / all_weight
    result = {
        **definition,
        "sampled_fixed_coordinate": sampled_coordinate,
        "gate_cell_count": len(indices),
        "seasons": seasons,
        "annual_frame_weighted_mean_normal_velocity_m_s": annual_mean,
    }
    lane_results = []
    for lane in definition.get("lanes", ()):
        lane_definition = {**definition, **lane}
        lane_definition.pop("lanes", None)
        summarized = summarize_gate(payload, lane_definition)
        lane_results.append({
            "name": lane["name"],
            "along_min": lane["along_min"],
            "along_max": lane["along_max"],
            "gate_cell_count": summarized["gate_cell_count"],
            "annual_frame_weighted_mean_normal_velocity_m_s": summarized["annual_frame_weighted_mean_normal_velocity_m_s"],
            "seasons": summarized["seasons"],
        })
    if lane_results:
        result["lanes"] = lane_results
    return result


def validate_payload(payload: dict) -> None:
    rows, columns = payload["shape"][1:]
    if len(payload["latitude_values"]) != rows or len(payload["longitude_values"]) != columns:
        raise ValueError("coordinate axes do not match payload shape")
    for frame in payload["frames"]:
        if len(frame["u_mm_s"]) != rows * columns or len(frame["v_mm_s"]) != rows * columns:
            raise ValueError("velocity frame does not match payload shape")


def run(fram_path: pathlib.Path, barents_path: pathlib.Path) -> dict:
    paths = {"fram": fram_path, "barents": barents_path}
    payloads = {name: load_assignment(path) for name, path in paths.items()}
    for payload in payloads.values():
        validate_payload(payload)
    if any(payload["period_start"] != "2017-12-01" or payload["period_stop"] != "2018-11-21" for payload in payloads.values()):
        raise ValueError("paired entrances require the declared matched historical year")
    return {
        "schema": "oceanlines.osw.m2-arctic-entrances-motion.v1",
        "status": "paired_historical_surface_motion_screens",
        "period": {"start": "2017-12-01", "stop": "2018-11-21", "fields": 71},
        "entrances": [summarize_gate(payloads[name], GATES[name]) for name in ("fram", "barents")],
        "sources": [{
            "entrance": name,
            "path": str(path),
            "sha256": sha256_file(path),
            "source_sha256": payloads[name]["source_sha256"],
            "field_sha256": payloads[name]["field_sha256"],
            "shape": payloads[name]["shape"],
            "sampled_extent": payloads[name]["sampled_extent"],
            "nominal_depth_m": payloads[name]["nominal_depth_m"],
        } for name, path in paths.items()],
        "gate_method": "Unweighted mean of finite native-grid OSCAR normal-velocity samples on one declared grid-aligned surface screen; seasonal means first average each frame across the screen, then average frames.",
        "boundary": "One historical year of older OSCAR 2017.0 nominal-15-m velocity. These screens show direction and seasonality only: they are not full-depth gateway definitions, Atlantic Water classifications, volume transport, heat transport, climatology, or Arctic heat delivery. OSCAR stops at 80N, so the Fram domain is clipped there without extrapolation.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fram", type=pathlib.Path, default=pathlib.Path("atlas/data/oscar-timeseries-fram-native-2018.js"))
    parser.add_argument("--barents", type=pathlib.Path, default=pathlib.Path("atlas/data/oscar-timeseries-barents-native-2018.js"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m2-arctic-entrances-motion-2018.json"))
    args = parser.parse_args()
    result = run(args.fram, args.barents)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
