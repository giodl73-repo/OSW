"""Fetch compact full-depth HYCOM samples at five Indonesian candidate gates."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib

import netCDF4
import numpy as np

try:
    from analyze_indonesian_gate_readiness import GATES, sha256_file
except ModuleNotFoundError:
    from analysis.analyze_indonesian_gate_readiness import GATES, sha256_file


SOURCE_URL = "https://tds.hycom.org/thredds/dodsC/GLBa0.08/expt_91.2/2018"
VARIABLES = ("temperature", "salinity", "u", "v")


def finite_or_none(value) -> float | None:
    if np.ma.is_masked(value):
        return None
    number = float(value)
    return round(number, 6) if math.isfinite(number) and abs(number) < 1e20 else None


def select_indices(axis: np.ndarray, minimum: float, maximum: float) -> list[int]:
    return [int(index) for index in np.flatnonzero((axis >= minimum) & (axis <= maximum))]


def gate_sample(dataset, gate: dict, time_index: int, latitudes: np.ndarray, longitudes: np.ndarray) -> dict:
    if gate["orientation"] == "zonal":
        fixed_index = int(np.argmin(abs(latitudes - gate["target"])))
        along_indices = select_indices(longitudes, gate["along_min"], gate["along_max"])
        ys = [fixed_index] * len(along_indices); xs = along_indices
        sampled_fixed = float(latitudes[fixed_index])
        section_slices = (fixed_index, slice(along_indices[0], along_indices[-1] + 1)) if along_indices else None
    else:
        fixed_index = int(np.argmin(abs(longitudes - gate["target"])))
        along_indices = select_indices(latitudes, gate["along_min"], gate["along_max"])
        ys = along_indices; xs = [fixed_index] * len(along_indices)
        sampled_fixed = float(longitudes[fixed_index])
        section_slices = (slice(along_indices[0], along_indices[-1] + 1), fixed_index) if along_indices else None
    if not xs:
        raise ValueError(f"no native points selected for {gate['code']}")
    values = {name: [] for name in VARIABLES}
    for name in VARIABLES:
        section = np.ma.asarray(dataset[name][time_index, :, section_slices[0], section_slices[1]])
        if section.ndim != 2:
            raise ValueError(f"unexpected {name} section shape for {gate['code']}: {section.shape}")
        values[name] = [[finite_or_none(value) for value in level] for level in section]
    return {
        **gate,
        "sampled_fixed_coordinate": round(sampled_fixed, 6),
        "points": [{"latitude": round(float(latitudes[y]), 6), "longitude": round(float(longitudes[x]), 6)} for y, x in zip(ys, xs)],
        "values": values,
    }


def fetch(url: str, date: int, retrieved_at: str) -> dict:
    with netCDF4.Dataset(url) as dataset:
        dates = np.asarray(dataset["Date"][:])
        matches = np.flatnonzero(np.floor(dates).astype(int) == date)
        if len(matches) != 1:
            raise ValueError(f"expected exactly one HYCOM field for {date}, found {len(matches)}")
        time_index = int(matches[0])
        latitudes = np.asarray(dataset["Latitude"][:, 0], dtype=float)
        longitudes = np.asarray(dataset["Longitude"][0, :], dtype=float)
        depths = [round(float(value), 3) for value in dataset["Depth"][:]]
        gates = [gate_sample(dataset, gate, time_index, latitudes, longitudes) for gate in GATES]
        metadata = {name: {"units": getattr(dataset[name], "units", None), "long_name": getattr(dataset[name], "long_name", None)} for name in VARIABLES}
        experiment = getattr(dataset, "experiment", None)
    request = {"url": url, "date": date, "variables": list(VARIABLES), "gates": [{key: gate[key] for key in ("code", "orientation", "target", "along_min", "along_max")} for gate in GATES]}
    request_sha = hashlib.sha256(json.dumps(request, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {
        "schema": "oceanlines.osw.m3-hycom-indonesian-gates.v1",
        "status": "compact_full_depth_candidate_gate_sample",
        "retrieved_at": retrieved_at,
        "source": {"url": url, "institution": "Naval Research Laboratory", "experiment": experiment, "nominal_horizontal_resolution": "1/12 degree", "request_sha256": request_sha},
        "date": str(date),
        "depth_m": depths,
        "variables": metadata,
        "gates": gates,
        "boundary": "One daily HYCOM analysis field on 33 standard z levels. Candidate axis-aligned sections are a geometry/readiness test, not INSTANT mooring sections, native HYCOM face transports, a time mean, validation, branch closure, volume transport, or heat transport.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=SOURCE_URL)
    parser.add_argument("--date", type=int, default=20181116)
    parser.add_argument("--retrieved-at", default="2026-09-03")
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("atlas/data/hycom-indonesian-gates-20181116.json"))
    args = parser.parse_args()
    payload = fetch(args.url, args.date, args.retrieved_at)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")
    print(f"sha256 {sha256_file(args.output)}")
    for gate in payload["gates"]:
        surface = gate["values"]["temperature"][0]
        print(f"{gate['code']}: {sum(value is not None for value in surface)}/{len(surface)} surface wet · {len(payload['depth_m'])} levels")


if __name__ == "__main__":
    main()
