"""Pin a native SANT membership derivative from a separately versioned live geometry."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import netCDF4
import numpy as np
from shapely import contains_xy

from acquire_longhurst_2007_adjacency import fetch_geometry, load_geometries, normalized_geometry_sha256


ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "atlas" / "data" / "oras5-drake-mesh.nc"
OUTPUT = ROOT / "research" / "ocean-state-interior-sant-current-geometry-assignment-2026-09-12.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rle_encode(mask: np.ndarray) -> list[list[int]]:
    """Encode a boolean grid as [value, run_length] pairs in row-major order."""
    flat = np.asarray(mask, dtype=np.uint8).ravel()
    runs: list[list[int]] = []
    for value in flat:
        if runs and runs[-1][0] == int(value):
            runs[-1][1] += 1
        else:
            runs.append([int(value), 1])
    return runs


def rle_decode(runs: list[list[int]], shape: tuple[int, int]) -> np.ndarray:
    flat = np.concatenate([np.full(length, value, dtype=bool) for value, length in runs])
    if flat.size != shape[0] * shape[1]:
        raise ValueError("run-length membership size does not match declared mesh shape")
    return flat.reshape(shape)


def build(mesh_path: Path = MESH) -> dict:
    mesh_path = Path(mesh_path)
    raw, headers = fetch_geometry()
    geometries, properties, _ = load_geometries(raw)
    with netCDF4.Dataset(mesh_path) as mesh:
        longitude = np.asarray(mesh["glamt"][:])
        latitude = np.asarray(mesh["gphit"][:])
    membership = contains_xy(geometries["SANT"], longitude, latitude)
    core = membership.copy()
    # A path is only admitted while the current cell and every cardinal neighbor
    # are inside SANT. np.roll is corrected at each outer edge below.
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        neighbor = np.roll(np.roll(membership, dy, axis=0), dx, axis=1)
        if dy == 1:
            neighbor[0, :] = False
        elif dy == -1:
            neighbor[-1, :] = False
        elif dx == 1:
            neighbor[:, 0] = False
        else:
            neighbor[:, -1] = False
        core &= neighbor
    return {
        "schema": "osw-ocean-state-native-membership-v1",
        "source_family": "current_longhurst_geometry_2026-09-12_with_archived_oras5_2018_velocity",
        "status": "separate_unjoined_source_family",
        "state": {"geometry_edition": "longhurst-v4-54", "province": "SANT"},
        "geometry_source": {
            "url": "https://geo.vliz.be/geoserver/MarineRegions/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=MarineRegions:longhurst_v4_2010&outputFormat=application/json",
            "response_bytes": len(raw),
            "response_sha256": hashlib.sha256(raw).hexdigest(),
            "normalized_geometry_sha256": normalized_geometry_sha256(geometries, properties),
            "response_headers": headers,
            "boundary": "The raw mutable WFS response is not bundled. This pinned native membership derivative, its checksums, and the archived mesh make the screen replayable without treating this geometry as the archived 2018 contents geometry.",
        },
        "mesh": {"path": mesh_path.relative_to(ROOT).as_posix(), "sha256": sha256(mesh_path), "shape_yx": list(membership.shape)},
        "membership": {"rule": "shapely contains_xy of native T-cell centres; boundary points are excluded", "cell_count": int(membership.sum()), "rle_row_major": rle_encode(membership)},
        "interior_core": {"rule": "member T cell whose four cardinal T-cell neighbours are also members; outer mesh rolls excluded", "cell_count": int(core.sum()), "rle_row_major": rle_encode(core)},
        "boundary": "This is a geographic assignment only. It establishes neither a water mass, a closed volume, transport, nor a compatibility bridge to the archived 2018 contents or boundary accounts.",
    }


def validate(payload: dict) -> None:
    shape = tuple(payload["mesh"]["shape_yx"])
    membership = rle_decode(payload["membership"]["rle_row_major"], shape)
    core = rle_decode(payload["interior_core"]["rle_row_major"], shape)
    if payload["status"] != "separate_unjoined_source_family":
        raise ValueError("membership must remain explicitly unjoined")
    if membership.sum() != payload["membership"]["cell_count"] or core.sum() != payload["interior_core"]["cell_count"]:
        raise ValueError("membership cell count disagrees with run-length encoding")
    if np.any(core & ~membership):
        raise ValueError("interior core cannot extend beyond state membership")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh", type=Path, default=MESH)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    payload = build(args.mesh)
    validate(payload)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
