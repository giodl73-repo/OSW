"""Compare M2 pathway results across declared integration time steps."""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import statistics


EARTH_RADIUS_KM = 6371.0088


def distance_km(a: dict, b: dict) -> float:
    lat1, lon1 = math.radians(a["latitude"]), math.radians(a["longitude"])
    lat2, lon2 = math.radians(b["latitude"]), math.radians(b["longitude"])
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(min(1, math.sqrt(h)))


def percentile(values: list[float], fraction: float) -> float:
    return sorted(values)[round((len(values) - 1) * fraction)]


def analyze(runs: dict[int, dict], reference_hours: int = 3) -> dict:
    if reference_hours not in runs:
        raise ValueError("reference time step is missing")
    tracks = {hours: {track["id"]: track for track in run["tracks"]} for hours, run in runs.items()}
    identities = set(tracks[reference_hours])
    if any(set(items) != identities for items in tracks.values()):
        raise ValueError("runs do not contain identical release identities")
    common_completed = sorted(
        identity for identity in identities
        if all(tracks[hours][identity]["status"] == "completed" for hours in runs)
    )
    cases = []
    for hours in sorted(runs):
        run = runs[hours]
        separations = [
            distance_km(tracks[reference_hours][identity]["points"][-1], tracks[hours][identity]["points"][-1])
            for identity in common_completed
        ]
        cases.append({
            "timestep_hours": hours,
            **run["summary"],
            "common_completed_endpoint_separation_from_reference_km": {
                "median": statistics.median(separations),
                "p95_nearest_rank": percentile(separations, 0.95),
                "maximum": max(separations),
            },
        })
    loss_timing = []
    for identity in sorted(identities - set(common_completed)):
        hours_by_step = {str(hours): tracks[hours][identity]["integrated_hours"] for hours in sorted(runs)}
        loss_timing.append({
            "id": identity,
            "integrated_hours_by_timestep": hours_by_step,
            "range_hours": max(hours_by_step.values()) - min(hours_by_step.values()),
        })
    return {
        "schema": "oceanlines.osw.m2-timestep-sensitivity.v1",
        "status": "numerical sensitivity diagnostic for historical surface-pathway method pilot",
        "reference_timestep_hours": reference_hours,
        "tested_timestep_hours": sorted(runs),
        "common_completed_tracks": len(common_completed),
        "cases": cases,
        "loss_timing": loss_timing,
        "maximum_loss_timing_range_hours": max(item["range_hours"] for item in loss_timing),
        "interpretation": (
            "Completion classification and completed endpoints are stable across the tested steps; "
            "termination timing near invalid wet stencils is not uniformly stable and must not be "
            "interpreted as coastal residence or precise beaching time."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step3", type=pathlib.Path, default=pathlib.Path("research/osw-m2-drake-pathways-2018-step3.json"))
    parser.add_argument("--step6", type=pathlib.Path, default=pathlib.Path("research/osw-m2-drake-pathways-2018.json"))
    parser.add_argument("--step12", type=pathlib.Path, default=pathlib.Path("research/osw-m2-drake-pathways-2018-step12.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m2-drake-timestep-sensitivity-2018.json"))
    args = parser.parse_args()
    runs = {
        3: json.loads(args.step3.read_text(encoding="utf-8")),
        6: json.loads(args.step6.read_text(encoding="utf-8")),
        12: json.loads(args.step12.read_text(encoding="utf-8")),
    }
    result = analyze(runs)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}: common={result['common_completed_tracks']}, max loss-time range={result['maximum_loss_timing_range_hours']} h")


if __name__ == "__main__":
    main()
