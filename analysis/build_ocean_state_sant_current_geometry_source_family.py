"""Bind the pinned SANT geometry to matching ORAS5 T/S/U/V monthly receipts."""

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
MONTHS = ("201802", "201805", "201808", "201811")
OUTPUT = ROOT / "research" / "ocean-state-sant-current-geometry-physical-source-family-2018.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def receipt(path: Path) -> dict:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}


def build(assignment_path: Path = ASSIGNMENT, mesh_path: Path = MESH) -> dict:
    assignment_path, mesh_path = Path(assignment_path), Path(mesh_path)
    assignment = load(assignment_path)
    if assignment["status"] != "separate_unjoined_source_family" or sha256(mesh_path) != assignment["mesh"]["sha256"]:
        raise ValueError("pinned geometry assignment and mesh are required")
    core = rle_decode(assignment["interior_core"]["rle_row_major"], tuple(assignment["mesh"]["shape_yx"]))
    records = []
    for month in MONTHS:
        state_path = ROOT / "atlas" / "data" / f"oras5-drake-state-{month}.nc"
        state_receipt_path = ROOT / "research" / f"osw-m3-oras5-drake-state-{month}.json"
        salinity_path = ROOT / "atlas" / "data" / f"oras5-drake-salinity-current-geometry-{month}.nc"
        salinity_receipt_path = ROOT / "research" / f"ocean-state-interior-sant-salinity-current-geometry-{month}.json"
        state_receipt, salinity_receipt = load(state_receipt_path), load(salinity_receipt_path)
        if state_receipt["mesh_sha256"] != assignment["mesh"]["sha256"] or salinity_receipt["assignment"]["sha256"] != sha256(assignment_path):
            raise ValueError(f"{month} field receipts do not bind to the source family")
        if sha256(state_path) != state_receipt["output"]["sha256"] or sha256(salinity_path) != salinity_receipt["output"]["sha256"]:
            raise ValueError(f"{month} field checksum mismatch")
        with netCDF4.Dataset(salinity_path) as salinity:
            values = np.asarray(salinity["vosaline"][:])
        finite = np.isfinite(values[:, core])
        records.append({
            "month": month,
            "temperature_velocity": {"state": receipt(state_path), "receipt": receipt(state_receipt_path), "fields": ["votemper", "vozocrtx", "vomecrty"]},
            "salinity": {"state": receipt(salinity_path), "receipt": receipt(salinity_receipt_path), "field": "vosaline", "finite_core_voxels": int(finite.sum()), "core_voxels": int(finite.size), "finite_core_fraction": round(float(finite.mean()), 6)},
        })
    return {
        "schema": "osw-ocean-state-current-geometry-physical-source-family-v1",
        "status": "ready_for_density_and_class_structure_screen_not_vertical_transfer_or_budget",
        "source_family": assignment["source_family"],
        "join_status": "not_joined_to_archived_2018_contents_or_boundary_accounts",
        "state": assignment["state"], "assignment": receipt(assignment_path), "mesh": receipt(mesh_path), "months": records,
        "field_capabilities": {
            "available": ["potential_temperature_on_T_cells", "practical_salinity_on_T_cells", "zonal_velocity_on_U_faces", "meridional_velocity_on_V_faces"],
            "not_available_from_probed_ICDC_ORAS5_contract": [{"field": "vovecrtz", "role": "native_vertical_velocity", "attempted_urls": [".../vovecrtz/opa0/vovecrtz_ORAS5_1m_201808_grid_W_02.nc", ".../vovecrtz/opa0/vovecrtz_ORAS5_1m_201808_grid_T_02.nc"], "result": "file_not_found_on_2026-09-12"}],
        },
        "admitted_next_analysis": "A declared T/S density or property-class structure screen at native cells/levels. It must retain practical-salinity provenance, a named equation of state, pressure/depth convention, class thresholds, and no transformation claim without class-volume fluxes.",
        "boundary": "This manifest creates a new, fully receipted geometry-and-T/S/U/V source family for bounded structure diagnostics. It lacks native vertical velocity, model tracer-tendency terms, a complete set of closed-volume faces/surface/storage terms, and independent product support; it cannot establish vertical transfer, transformation flux, convergence, or budget closure.",
    }


def validate(payload: dict) -> None:
    if payload["status"] != "ready_for_density_and_class_structure_screen_not_vertical_transfer_or_budget" or not payload["join_status"].startswith("not_joined"):
        raise ValueError("manifest must preserve its scope and source separation")
    if len(payload["months"]) != 4 or any(record["salinity"]["finite_core_fraction"] <= 0 for record in payload["months"]):
        raise ValueError("all four months require nonempty salinity support")
    if "native_vertical_velocity" not in str(payload["field_capabilities"]["not_available_from_probed_ICDC_ORAS5_contract"]):
        raise ValueError("vertical-velocity limitation must remain visible")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    payload = build()
    validate(payload)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
