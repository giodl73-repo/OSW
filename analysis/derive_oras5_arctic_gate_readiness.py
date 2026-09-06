"""Audit whether candidate Arctic entrances align with native ORCA025 faces."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib

import netCDF4
import numpy as np


FRAM_TARGET = {"latitude_deg_north": 78.8333333, "west_deg": -20.0, "east_deg": 15.0}
BARENTS_TARGET = {"longitude_deg_east": 20.0, "south_deg": 70.5, "north_deg": 75.0}
BEAR_ISLAND_TARGET = {"longitude_deg_east": 18.9, "latitude_deg_north": 74.4, "role": "approximate representation test, not a surveyed shoreline coordinate"}


def normalize_longitude(values):
    return ((np.asarray(values, dtype=float) + 180.0) % 360.0) - 180.0


def wet_runs(values) -> list[tuple[int, int]]:
    padded = np.r_[False, np.asarray(values, dtype=bool), False]
    edges = np.flatnonzero(padded[1:] != padded[:-1])
    return [(int(start), int(stop)) for start, stop in zip(edges[::2], edges[1::2])]


def derive_fram(surface_vmask, longitude_v, latitude_v, target=FRAM_TARGET) -> dict:
    wet = np.asarray(surface_vmask) > 0
    lon = normalize_longitude(longitude_v)
    lat = np.asarray(latitude_v, dtype=float)
    candidates = []
    for y in range(wet.shape[0]):
        for start, stop in wet_runs(wet[y]):
            if start == 0 or stop == wet.shape[1] or stop - start < 20:
                continue
            run_lon = lon[y, start:stop]
            run_lat = lat[y, start:stop]
            if np.nanmin(run_lon) > -15 or np.nanmax(run_lon) < 10:
                continue
            score = (
                abs(float(np.nanmean(run_lat)) - target["latitude_deg_north"])
                + 0.08 * abs(float(np.nanmin(run_lon)) - target["west_deg"])
                + 0.08 * abs(float(np.nanmax(run_lon)) - target["east_deg"])
            )
            candidates.append((score, y, start, stop))
    if not candidates:
        raise ValueError("no land-bounded native V-face run spans the Fram target")
    score, y, start, stop = min(candidates)
    run_lon = lon[y, start:stop]
    run_lat = lat[y, start:stop]
    return {
        "status": "surface_geometry_ready_for_full_depth_audit",
        "native_face": "V",
        "grid_row": int(y),
        "x_start": int(start),
        "x_stop_exclusive": int(stop),
        "face_count": int(stop - start),
        "land_bounded_at_surface": True,
        "score": float(score),
        "longitude_deg": [float(value) for value in run_lon],
        "latitude_deg": [float(value) for value in run_lat],
        "extent_deg": {
            "west": float(np.nanmin(run_lon)), "east": float(np.nanmax(run_lon)),
            "south": float(np.nanmin(run_lat)), "north": float(np.nanmax(run_lat)),
            "mean_latitude": float(np.nanmean(run_lat)),
        },
        "positive_normal": "native +j / approximately northward into the Arctic",
        "candidate_count": len(candidates),
    }


def derive_barents_single_column(surface_umask, longitude_u, latitude_u, target=BARENTS_TARGET) -> dict:
    wet = np.asarray(surface_umask) > 0
    lon = normalize_longitude(longitude_u)
    lat = np.asarray(latitude_u, dtype=float)
    candidates = []
    for x in range(wet.shape[1]):
        inside = wet[:, x] & (lat[:, x] >= target["south_deg"]) & (lat[:, x] <= target["north_deg"])
        indices = np.flatnonzero(inside)
        if len(indices) < 20 or np.any(np.diff(indices) != 1):
            continue
        start = int(indices[0]); stop = int(indices[-1] + 1)
        run_lon = lon[start:stop, x]
        score = abs(float(np.nanmean(run_lon)) - target["longitude_deg_east"])
        candidates.append((score, x, start, stop))
    if not candidates:
        raise ValueError("no continuous native U-column sample spans the Barents latitude interval")
    score, x, start, stop = min(candidates)
    run_lon = lon[start:stop, x]
    run_lat = lat[start:stop, x]
    south_neighbor_wet = bool(wet[start - 1, x]) if start else False
    north_neighbor_wet = bool(wet[stop, x]) if stop < wet.shape[0] else False
    drift = float(np.nanmax(run_lon) - np.nanmin(run_lon))
    return {
        "status": "single_native_U_column_rejected",
        "native_face_tested": "U",
        "grid_column": int(x),
        "y_start": int(start),
        "y_stop_exclusive": int(stop),
        "face_count": int(stop - start),
        "land_bounded_at_surface": not south_neighbor_wet and not north_neighbor_wet,
        "south_neighbor_wet": south_neighbor_wet,
        "north_neighbor_wet": north_neighbor_wet,
        "score": float(score),
        "longitude_drift_deg": drift,
        "longitude_deg": [float(value) for value in run_lon],
        "latitude_deg": [float(value) for value in run_lat],
        "extent_deg": {
            "west": float(np.nanmin(run_lon)), "east": float(np.nanmax(run_lon)),
            "south": float(np.nanmin(run_lat)), "north": float(np.nanmax(run_lat)),
            "mean_longitude": float(np.nanmean(run_lon)),
        },
        "verdict": "A geographic 20E section cuts obliquely across the curvilinear grid. Build and audit a connected mixed U/V face staircase; do not treat this column as the gate.",
        "candidate_count": len(candidates),
    }


def point_representation(surface_tmask, longitude_t, latitude_t, target: dict) -> dict:
    wet = np.asarray(surface_tmask) > 0
    lon = normalize_longitude(longitude_t)
    lat = np.asarray(latitude_t, dtype=float)
    target_lon = target["longitude_deg_east"]
    target_lat = target["latitude_deg_north"]
    cosine = np.cos(np.deg2rad(target_lat))
    distance = np.sqrt((lat - target_lat) ** 2 + ((lon - target_lon) * cosine) ** 2) * 111.0

    def nearest(mask):
        candidate = np.where(mask & np.isfinite(distance), distance, np.inf)
        y, x = np.unravel_index(np.argmin(candidate), candidate.shape)
        return {
            "y": int(y), "x": int(x), "longitude_deg": float(lon[y, x]),
            "latitude_deg": float(lat[y, x]), "approximate_distance_km": float(candidate[y, x]),
        }

    nearest_any_y, nearest_any_x = np.unravel_index(np.nanargmin(distance), distance.shape)
    return {
        "target": target,
        "nearest_t_cell_is_wet": bool(wet[nearest_any_y, nearest_any_x]),
        "nearest_wet_t_cell": nearest(wet),
        "nearest_dry_t_cell": nearest(~wet),
        "verdict": "Bear Island is not a dry surface T cell in this ORCA025 mesh window. A Fugloya-Bear Island proxy must use an explicit virtual wet endpoint and cannot be called a land-bounded model gateway.",
    }


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def derive_file(mesh_path: pathlib.Path) -> dict:
    with netCDF4.Dataset(mesh_path) as dataset:
        fram = derive_fram(
            np.ma.filled(dataset.variables["vmask"][0], 0),
            np.ma.filled(dataset.variables["glamv"][:], np.nan),
            np.ma.filled(dataset.variables["gphiv"][:], np.nan),
        )
        barents = derive_barents_single_column(
            np.ma.filled(dataset.variables["umask"][0], 0),
            np.ma.filled(dataset.variables["glamu"][:], np.nan),
            np.ma.filled(dataset.variables["gphiu"][:], np.nan),
        )
        bear_island = point_representation(
            np.ma.filled(dataset.variables["tmask"][0], 0),
            np.ma.filled(dataset.variables["glamt"][:], np.nan),
            np.ma.filled(dataset.variables["gphit"][:], np.nan),
            BEAR_ISLAND_TARGET,
        )
    return {
        "schema": "oceanlines.osw.m3-oras5-arctic-gate-readiness.v1",
        "status": "fram_surface_geometry_ready_barents_contract_fork_required",
        "mesh": {"path": str(mesh_path), "sha256": sha256_file(mesh_path)},
        "targets": {"fram": FRAM_TARGET, "barents": BARENTS_TARGET},
        "fram": fram,
        "barents_single_column_test": barents,
        "bear_island_representation": bear_island,
        "barents_contract_fork": {
            "observational_comparison": "Build a mixed U/V face staircase approximating the Fugloya-Bear Island section, terminate at a declared virtual wet endpoint, and label the result an open section proxy that water can bypass in the model.",
            "model_budget_closure": "Build a separate land-to-land Norway-Svalbard boundary and label it a broader model gateway, not the observational Barents Sea Opening section.",
            "never_merge": "Do not compare either transport with observations until their different endpoints and closure meanings are visible.",
        },
        "next_tests": [
            "audit Fram V-face masks and reconstructed partial-cell thickness at every depth",
            "choose observational proxy or broader model closure before constructing the Barents path",
            "verify any mixed-face staircase has no gaps, overlaps, or duplicated corner flux",
            "challenge nearby Fram rows and Barents staircase placements before retrieving state fields",
        ],
        "sources": [
            {"title": "NEMO C-grid and section-path documentation", "url": "https://sites.nemo-ocean.io/user-guide/tools.html"},
            {"title": "Sandø et al. 2010 Barents Sea heat transport", "url": "https://doi.org/10.1029/2009JC005884"},
        ],
        "boundary": "Native surface geometry and representation audit only. It contains no velocity, temperature, salinity, volume transport, heat transport, Atlantic Water classification, or Arctic heat-delivery result. The approximate Bear Island coordinate is a resolution probe, not an exact observational endpoint.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-arctic-entrances-mesh.nc"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-arctic-gate-readiness.json"))
    args = parser.parse_args()
    result = derive_file(args.mesh)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}: {result['status']}")


if __name__ == "__main__":
    main()
