"""Derive a reproducible land-bounded native U-face Drake Passage gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib

import netCDF4
import numpy as np


TARGET = {"longitude_deg": -67.0, "south_endpoint_deg": -64.0, "north_endpoint_deg": -56.0}


def normalize_longitude(values):
    return ((np.asarray(values, dtype=float) + 180.0) % 360.0) - 180.0


def wet_runs(values) -> list[tuple[int, int]]:
    runs = []; start = None
    for index, wet in enumerate(values):
        if wet and start is None:
            start = index
        if start is not None and (not wet or index == len(values) - 1):
            stop = index + 1 if wet and index == len(values) - 1 else index
            runs.append((start, stop)); start = None
    return runs


def candidate_gates(surface_umask, longitude_u, latitude_u, target: dict = TARGET) -> list[dict]:
    wet = np.asarray(surface_umask) > 0
    lon = normalize_longitude(longitude_u); lat = np.asarray(latitude_u, dtype=float)
    if wet.shape != lon.shape or wet.shape != lat.shape or wet.ndim != 2:
        raise ValueError("surface mask and U coordinates must be matching 2D arrays")
    candidates = []
    ny, nx = wet.shape
    for x in range(nx - 1):
        for start, stop in wet_runs(wet[:, x]):
            if start == 0 or stop == ny:
                continue
            run_lat = lat[start:stop, x]; run_lon = lon[start:stop, x]
            if not np.all(np.isfinite(run_lat)) or not np.all(np.isfinite(run_lon)):
                continue
            south = float(run_lat.min()); north = float(run_lat.max()); mean_lon = float(run_lon.mean())
            if south > -62 or north < -58 or stop - start < 12:
                continue
            score = (
                abs(mean_lon - target["longitude_deg"])
                + 0.35 * abs(south - target["south_endpoint_deg"])
                + 0.35 * abs(north - target["north_endpoint_deg"])
            )
            candidates.append({
                "x": x, "y_start": start, "y_stop_exclusive": stop,
                "segment_count": stop - start, "mean_longitude_deg": mean_lon,
                "south_deg": south, "north_deg": north, "score": score,
            })
    return sorted(candidates, key=lambda item: (item["score"], item["x"], item["y_start"]))


def derive(surface_umask, longitude_u, latitude_u, target: dict = TARGET) -> dict:
    lon = normalize_longitude(longitude_u); lat = np.asarray(latitude_u, dtype=float)
    candidates = candidate_gates(surface_umask, longitude_u, latitude_u, target)
    if not candidates:
        raise ValueError("no land-bounded wet U-face run spans the Drake target")
    selected = candidates[0]
    x = selected["x"]; ys = slice(selected["y_start"], selected["y_stop_exclusive"])
    selected = {
        **selected,
        "longitude_deg": [float(value) for value in lon[ys, x]],
        "latitude_deg": [float(value) for value in lat[ys, x]],
        "south_land_neighbor_y": selected["y_start"] - 1,
        "north_land_neighbor_y": selected["y_stop_exclusive"],
        "positive_normal": "native +i / approximately eastward",
    }
    return {"selected": selected, "candidate_count": len(candidates), "target": target}


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def derive_file(mesh_path: pathlib.Path) -> dict:
    with netCDF4.Dataset(mesh_path) as dataset:
        result = derive(
            np.ma.filled(dataset.variables["umask"][0], 0),
            np.ma.filled(dataset.variables["glamu"][:], np.nan),
            np.ma.filled(dataset.variables["gphiu"][:], np.nan),
        )
    return {
        "schema": "oceanlines.osw.m3-drake-native-gate.v1",
        "status": "candidate_native_U_face_gate_not_yet_transport",
        "mesh": {"path": str(mesh_path), "sha256": sha256_file(mesh_path)},
        **result,
        "selection_rule": (
            "Among interior land-bounded surface-wet native U-face runs spanning at least "
            "62°S to 58°S, minimize distance from 67°W and target endpoints 64°S/56°S."
        ),
        "temperature_collocation_pending": True,
        "boundary": (
            "A deterministic grid-aligned candidate gate, not an observational section, unique "
            "Drake definition, volume transport, heat transport, or closed control volume."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-drake-mesh.nc"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-drake-gate.json"))
    args = parser.parse_args()
    result = derive_file(args.mesh)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    selected = result["selected"]
    print(f"wrote {args.output}: x={selected['x']}, y={selected['y_start']}:{selected['y_stop_exclusive']}")


if __name__ == "__main__":
    main()
