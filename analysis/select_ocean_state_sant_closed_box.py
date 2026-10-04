"""Select a geometry-only SANT interior control box and one-cell controls."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import netCDF4
import numpy as np

from prepare_ocean_state_interior_current_geometry import rle_decode


ROOT = Path(__file__).resolve().parents[1]
ASSIGNMENT = ROOT / "research" / "ocean-state-interior-sant-current-geometry-assignment-2026-09-12.json"
MESH = ROOT / "atlas" / "data" / "oras5-drake-mesh.nc"
SIZE = 16
OUTPUT = ROOT / "research" / "ocean-state-sant-closed-box-selection-current-geometry-v1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def candidates(core: np.ndarray, size: int = SIZE) -> list[tuple[int, int]]:
    return [(y, x) for y in range(core.shape[0] - size + 1) for x in range(core.shape[1] - size + 1) if core[y:y + size, x:x + size].all()]


def box_record(identifier: str, y: int, x: int, size: int, longitude: np.ndarray, latitude: np.ndarray) -> dict:
    cy, cx = y + (size - 1) // 2, x + (size - 1) // 2
    return {"id": identifier, "y_start": y, "y_stop_exclusive": y + size, "x_start": x, "x_stop_exclusive": x + size, "cell_count": size * size, "center_latitude_deg": round(float(latitude[cy, cx]), 6), "center_longitude_deg": round(float(longitude[cy, cx]), 6), "latitude_extent_deg": [round(float(latitude[y:y + size, x:x + size].min()), 6), round(float(latitude[y:y + size, x:x + size].max()), 6)], "longitude_extent_deg": [round(float(longitude[y:y + size, x:x + size].min()), 6), round(float(longitude[y:y + size, x:x + size].max()), 6)]}


def build(assignment_path: Path = ASSIGNMENT, mesh_path: Path = MESH) -> dict:
    assignment_path, mesh_path = Path(assignment_path), Path(mesh_path)
    assignment = json.loads(assignment_path.read_text(encoding="utf-8"))
    with netCDF4.Dataset(mesh_path) as mesh:
        longitude, latitude = np.asarray(mesh["glamt"][:]), np.asarray(mesh["gphit"][:])
    core = rle_decode(assignment["interior_core"]["rle_row_major"], tuple(assignment["mesh"]["shape_yx"]))
    eligible = candidates(core)
    target_latitude, target_longitude = float(np.median(latitude[core])), float(np.median(longitude[core]))
    y, x = min(eligible, key=lambda item: (latitude[item[0] + (SIZE - 1) // 2, item[1] + (SIZE - 1) // 2] - target_latitude) ** 2 + (longitude[item[0] + (SIZE - 1) // 2, item[1] + (SIZE - 1) // 2] - target_longitude) ** 2)
    primary = box_record("primary", y, x, SIZE, longitude, latitude)
    controls = []
    for identifier, dy, dx in (("north_control", 1, 0), ("south_control", -1, 0), ("east_control", 0, 1), ("west_control", 0, -1)):
        ny, nx = y + dy, x + dx
        if 0 <= ny and ny + SIZE <= core.shape[0] and 0 <= nx and nx + SIZE <= core.shape[1] and core[ny:ny + SIZE, nx:nx + SIZE].all(): controls.append(box_record(identifier, ny, nx, SIZE, longitude, latitude))
    return {"schema": "osw-ocean-state-closed-box-selection-v1", "status": "geometry_selected_before_flux_outcomes", "source_family": assignment["source_family"], "assignment": {"path": assignment_path.relative_to(ROOT).as_posix(), "sha256": sha256(assignment_path)}, "rule": {"size_native_T_cells": SIZE, "eligibility": "every cell must be in the pinned cardinal interior core", "ordering": "minimum squared distance of box centre to the all-core median latitude/longitude; then row-major order", "prohibited_inputs": ["velocity", "temperature", "salinity", "surface flux", "heat content", "transport", "desired convergence result"]}, "eligible_box_count": len(eligible), "target_core_median": {"latitude_deg": round(target_latitude, 6), "longitude_deg": round(target_longitude, 6)}, "primary": primary, "one_cell_displaced_controls": controls, "boundary": "A fixed native-grid subregion wholly inside SANT's guarded core. It is a horizontal control-box geometry, not a material parcel, water mass, or evidence of closure before its flux terms are evaluated."}


def validate(payload: dict) -> None:
    if payload["status"] != "geometry_selected_before_flux_outcomes" or payload["primary"]["cell_count"] != 256 or len(payload["one_cell_displaced_controls"]) < 1:
        raise ValueError("closed-box selection must retain its fixed geometry and control")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(); payload = build(); validate(payload)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
