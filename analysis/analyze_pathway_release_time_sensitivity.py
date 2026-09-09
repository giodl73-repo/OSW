"""Test M2 Drake pathways against deterministic release-time shifts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import statistics

from analyze_pathway_timestep_sensitivity import distance_km
from simulate_oscar_pathways import (
    DEFAULT_RELEASE_TIMES, VelocityField, gate_releases, integrate,
    load_assignment, parse_time,
)


DEFAULT_OFFSETS_DAYS = (-5.0, -2.5, 0.0, 2.5, 5.0)


def iso_time(value: dt.datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def analyze(
    payload: dict, release_times: tuple[str, ...] = DEFAULT_RELEASE_TIMES,
    release_count: int = 10, offsets_days: tuple[float, ...] = DEFAULT_OFFSETS_DAYS,
    duration_days: int = 30, timestep_hours: int = 6,
) -> dict:
    if 0.0 not in offsets_days:
        raise ValueError("release-time offsets must include zero reference")
    field = VelocityField(payload)
    releases = gate_releases(release_count)
    trials = []
    groups = []
    for central_time_text in release_times:
        central_time = parse_time(central_time_text)
        for release_index, (latitude, longitude) in enumerate(releases, 1):
            group_trials = []
            for offset_days in offsets_days:
                release_time = central_time + dt.timedelta(days=offset_days)
                result = integrate(
                    field, release_time, latitude, longitude,
                    duration_days, timestep_hours, 24,
                )
                trial = {
                    "id": f"{central_time_text[:10]}-{release_index:02d}-{offset_days:+g}d",
                    "base_id": f"{central_time_text[:10]}-{release_index:02d}",
                    "central_release_time": central_time_text,
                    "release_time": iso_time(release_time),
                    "release_index": release_index,
                    "time_offset_days": offset_days,
                    "release_latitude": latitude,
                    "release_longitude": longitude,
                    "status": result["status"],
                    "integrated_hours": result["integrated_hours"],
                    "travelled_km": result["travelled_km"],
                    "endpoint": result["points"][-1],
                }
                trials.append(trial); group_trials.append(trial)
            central = next(item for item in group_trials if item["time_offset_days"] == 0)
            completed = [item for item in group_trials if item["status"] == "completed"]
            distances = []
            if central["status"] == "completed":
                distances = [distance_km(central["endpoint"], item["endpoint"]) for item in completed]
            groups.append({
                "base_id": central["base_id"],
                "central_release_time": central_time_text,
                "release_index": release_index,
                "completed": len(completed),
                "terminated": len(group_trials) - len(completed),
                "completion_fraction": len(completed) / len(group_trials),
                "central_status": central["status"],
                "completed_endpoint_separation_from_central_km": None if not distances else {
                    "median": statistics.median(distances), "maximum": max(distances),
                },
            })
    completed_trials = sum(trial["status"] == "completed" for trial in trials)
    fully_stable = sum(group["completed"] == len(offsets_days) for group in groups)
    fully_lost = sum(group["completed"] == 0 for group in groups)
    mixed = len(groups) - fully_stable - fully_lost
    endpoint_groups = [
        group["completed_endpoint_separation_from_central_km"]
        for group in groups if group["completed_endpoint_separation_from_central_km"] is not None
    ]
    endpoint_medians = [item["median"] for item in endpoint_groups]
    endpoint_maxima = [item["maximum"] for item in endpoint_groups]
    return {
        "schema": "oceanlines.osw.m2-release-time-sensitivity.v1",
        "status": "deterministic release-time sensitivity for historical surface-pathway method pilot",
        "velocity_source": {
            "source_sha256": payload["source_sha256"], "field_sha256": payload["field_sha256"],
            "shape": payload["shape"], "space_stride": payload["display_stride"],
        },
        "experiment": {
            "central_release_times": list(release_times), "base_releases_per_time": release_count,
            "time_offset_days": list(offsets_days), "duration_days": duration_days,
            "timestep_hours": timestep_hours, "diffusion": "none",
        },
        "summary": {
            "base_releases": len(groups), "shifted_trials": len(trials),
            "completed_trials": completed_trials, "terminated_trials": len(trials) - completed_trials,
            "completion_fraction": completed_trials / len(trials),
            "fully_completed_windows": fully_stable,
            "mixed_windows": mixed,
            "fully_terminated_windows": fully_lost,
            "central_completed_windows": len(endpoint_groups),
            "median_of_completed_endpoint_medians_km": statistics.median(endpoint_medians),
            "p90_nearest_rank_of_completed_endpoint_medians_km": sorted(endpoint_medians)[round((len(endpoint_medians) - 1) * .9)],
            "maximum_completed_endpoint_separation_from_central_km": max(endpoint_maxima),
            "windows_with_maximum_endpoint_separation_over_200_km": sum(value > 200 for value in endpoint_maxima),
        },
        "groups": groups,
        "trials": trials,
        "interpretation": (
            "Deterministic release-time shifts test pathway phase sensitivity only. Equal trial "
            "counts are not probability, frequency, water-mass volume, residence, or heat transport."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("atlas/data/oscar-timeseries-drake-native-2018.js"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m2-drake-release-time-sensitivity-2018.json"))
    args = parser.parse_args()
    result = analyze(load_assignment(args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}: {result['summary']}")


if __name__ == "__main__":
    main()
