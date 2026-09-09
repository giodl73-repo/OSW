"""Audit the Agulhas junction with native-grid OSCAR surface velocity.

The result distinguishes a coherent current, a turning field, a return current,
and an intermittent leakage basin. It is a surface-motion description, not a
volume or heat-transport estimate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib

try:
    from simulate_oscar_pathways import VelocityField, integrate, load_assignment, parse_time
except ModuleNotFoundError:
    from analysis.simulate_oscar_pathways import VelocityField, integrate, load_assignment, parse_time


SEASONS = ("DJF", "MAM", "JJA", "SON")
SEASON_MONTHS = {"DJF": {12, 1, 2}, "MAM": {3, 4, 5}, "JJA": {6, 7, 8}, "SON": {9, 10, 11}}
RELEASE_TIMES = (
    "2017-12-16T00:00:00Z",
    "2018-03-18T00:00:00Z",
    "2018-06-17T00:00:00Z",
    "2018-09-16T00:00:00Z",
)

# Rectangles are declared diagnostic windows, not proposed ocean borders.
WINDOWS = (
    {
        "id": "boundary-current",
        "name": "Agulhas Current coastal sector",
        "role": "coherent western-boundary current",
        "extent": {"south": -37, "north": -28, "west": 25, "east": 34},
    },
    {
        "id": "retroflection",
        "name": "Agulhas retroflection sector",
        "role": "energetic turning field",
        "extent": {"south": -42, "north": -36, "west": 16, "east": 26},
    },
    {
        "id": "return-current",
        "name": "Agulhas Return Current sector",
        "role": "coherent eastward return current",
        "extent": {"south": -44, "north": -37, "west": 25, "east": 45},
    },
    {
        "id": "cape-basin",
        "name": "Cape Basin leakage sector",
        "role": "variable leakage and ring field",
        "extent": {"south": -40, "north": -30, "west": 5, "east": 20},
    },
)

SEEDS = (
    {"id": "boundary", "role": "boundary-current", "latitude": -34, "longitude": 29},
    {"id": "turn-west", "role": "retroflection", "latitude": -37, "longitude": 24},
    {"id": "turn-core", "role": "retroflection", "latitude": -39, "longitude": 20},
    {"id": "return-west", "role": "return-current", "latitude": -40, "longitude": 27},
    {"id": "return-east", "role": "return-current", "latitude": -39, "longitude": 32},
    {"id": "leakage-south", "role": "cape-basin", "latitude": -36, "longitude": 16},
    {"id": "leakage-north", "role": "cape-basin", "latitude": -34, "longitude": 12},
)


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def month_of(frame: dict) -> int:
    return int(frame["time"][5:7])


def validate_payload(payload: dict) -> None:
    times, rows, columns = payload["shape"]
    if times != len(payload["frames"]):
        raise ValueError("frame count does not match payload shape")
    if rows != len(payload["latitude_values"]) or columns != len(payload["longitude_values"]):
        raise ValueError("coordinate axes do not match payload shape")
    for frame in payload["frames"]:
        if len(frame["u_mm_s"]) != rows * columns or len(frame["v_mm_s"]) != rows * columns:
            raise ValueError("velocity frame does not match payload shape")


def window_indices(payload: dict, extent: dict) -> list[int]:
    nlon = len(payload["longitude_values"])
    return [
        row * nlon + column
        for row, latitude in enumerate(payload["latitude_values"])
        for column, longitude in enumerate(payload["longitude_values"])
        if extent["south"] <= latitude <= extent["north"]
        and extent["west"] <= longitude <= extent["east"]
    ]


def summarize_samples(samples: list[tuple[float, float]]) -> dict:
    if not samples:
        raise ValueError("diagnostic window contains no jointly finite velocity samples")
    mean_u = sum(u for u, _ in samples) / len(samples)
    mean_v = sum(v for _, v in samples) / len(samples)
    mean_speed = sum(math.hypot(u, v) for u, v in samples) / len(samples)
    return {
        "sample_count": len(samples),
        "mean_u_m_s": mean_u,
        "mean_v_m_s": mean_v,
        "mean_speed_m_s": mean_speed,
        "vector_coherence": 0 if mean_speed == 0 else math.hypot(mean_u, mean_v) / mean_speed,
        "eastward_fraction": sum(u > 0 for u, _ in samples) / len(samples),
        "westward_fraction": sum(u < 0 for u, _ in samples) / len(samples),
        "northward_fraction": sum(v > 0 for _, v in samples) / len(samples),
        "southward_fraction": sum(v < 0 for _, v in samples) / len(samples),
    }


def summarize_window(payload: dict, definition: dict) -> dict:
    indices = window_indices(payload, definition["extent"])
    seasons = []
    annual_samples = []
    for season in SEASONS:
        samples = []
        frame_count = 0
        for frame in payload["frames"]:
            if month_of(frame) not in SEASON_MONTHS[season]:
                continue
            frame_count += 1
            for index in indices:
                u, v = frame["u_mm_s"][index], frame["v_mm_s"][index]
                if u is not None and v is not None:
                    samples.append((u / 1000, v / 1000))
        annual_samples.extend(samples)
        seasons.append({"season": season, "frame_count": frame_count, **summarize_samples(samples)})
    return {
        **definition,
        "grid_cell_count": len(indices),
        "annual": summarize_samples(annual_samples),
        "seasons": seasons,
    }


def run_tracks(payload: dict, duration_days: int = 45) -> list[dict]:
    field = VelocityField(payload)
    tracks = []
    for release_time in RELEASE_TIMES:
        for seed in SEEDS:
            result = integrate(
                field, parse_time(release_time), seed["latitude"], seed["longitude"],
                duration_days=duration_days, timestep_hours=6, output_hours=24,
            )
            tracks.append({
                "id": f"{release_time[:10]}-{seed['id']}",
                "release_time": release_time,
                "seed": seed,
                **result,
            })
    return tracks


def run(path: pathlib.Path, duration_days: int = 45) -> dict:
    payload = load_assignment(path)
    validate_payload(payload)
    if payload["period_start"] != "2017-12-01" or payload["period_stop"] != "2018-11-21":
        raise ValueError("Agulhas audit requires the declared matched historical year")
    tracks = run_tracks(payload, duration_days)
    return {
        "schema": "oceanlines.osw.m2-agulhas-motion.v1",
        "status": "historical_surface_motion_junction_audit",
        "period": {"start": payload["period_start"], "stop": payload["period_stop"], "fields": len(payload["frames"])},
        "windows": [summarize_window(payload, definition) for definition in WINDOWS],
        "tracks": tracks,
        "track_summary": {
            "count": len(tracks),
            "completed": sum(track["status"] == "completed" for track in tracks),
            "release_times": list(RELEASE_TIMES),
            "seeds": len(SEEDS),
            "duration_days": duration_days,
        },
        "source": {
            "path": str(path),
            "sha256": sha256_file(path),
            "source_sha256": payload["source_sha256"],
            "field_sha256": payload["field_sha256"],
            "shape": payload["shape"],
            "sampled_extent": payload["sampled_extent"],
            "nominal_depth_m": payload["nominal_depth_m"],
        },
        "window_method": "Unweighted jointly finite native-grid OSCAR u/v samples inside four declared geographic diagnostic windows; seasons pool their native five-day fields.",
        "track_method": "Equal-count deterministic forward RK4 surface trajectories from seven declared seed points at four seasonal release times; six-hour steps and daily output; no diffusion or transport weighting.",
        "boundary": "One historical year of older OSCAR 2017.0 nominal-15-m velocity. Windows are diagnostic sectors, not borders. Trajectories are kinematic surface pathways, not water-mass identities, probabilities, volume transports, heat transports, or climatology. Agulhas leakage is intermittent and cannot be inferred from a single mean arrow.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("atlas/data/oscar-timeseries-agulhas-native-2018.js"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m2-agulhas-motion-2018.json"))
    parser.add_argument("--duration-days", type=int, default=45)
    args = parser.parse_args()
    result = run(args.input, args.duration_days)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
