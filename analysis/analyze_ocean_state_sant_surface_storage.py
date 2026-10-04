"""Aggregate SANT's current-geometry ORAS5 surface forcing and column storage without closing a budget."""

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
METRICS = ROOT / "atlas" / "data" / "oras5-drake-t-metrics.nc"
TERMS = ROOT / "atlas" / "data" / "oras5-drake-current-geometry-surface-terms-2018.nc"
TERMS_RECEIPT = ROOT / "research" / "ocean-state-sant-current-geometry-surface-terms-2018.json"
OUTPUT = ROOT / "research" / "ocean-state-sant-current-geometry-surface-storage-2018.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build(assignment_path: Path = ASSIGNMENT, mesh_path: Path = MESH, metrics_path: Path = METRICS, terms_path: Path = TERMS, terms_receipt_path: Path = TERMS_RECEIPT) -> dict:
    assignment_path, mesh_path, metrics_path, terms_path, terms_receipt_path = map(Path, (assignment_path, mesh_path, metrics_path, terms_path, terms_receipt_path))
    assignment, receipt = load(assignment_path), load(terms_receipt_path)
    if receipt["assignment"]["sha256"] != sha256(assignment_path) or receipt["output"]["sha256"] != sha256(terms_path):
        raise ValueError("surface terms must bind to the pinned assignment and receipt")
    membership = rle_decode(assignment["membership"]["rle_row_major"], tuple(assignment["mesh"]["shape_yx"]))
    with netCDF4.Dataset(metrics_path) as mesh:
        area = np.asarray(mesh["e1t"][:], dtype=float) * np.asarray(mesh["e2t"][:], dtype=float)
    with netCDF4.Dataset(terms_path) as terms:
        months = np.asarray(terms["month"][:], dtype=int)
        heat_flux = np.asarray(np.ma.filled(terms["sohefldo"][:], np.nan), dtype=float)
        water_flux = np.asarray(np.ma.filled(terms["sowaflup"][:], np.nan), dtype=float)
        heat_content = np.asarray(np.ma.filled(terms["sohtcbtm"][:], np.nan), dtype=float)
    records = []
    for index, month in enumerate(months):
        valid = membership & np.isfinite(heat_flux[index]) & np.isfinite(water_flux[index]) & np.isfinite(heat_content[index]) & np.isfinite(area)
        records.append({"month": str(int(month)), "wet_state_area_km2": round(float(area[valid].sum() / 1e6), 6), "state_membership_cells": int(membership.sum()), "valid_cells": int(valid.sum()), "valid_area_fraction": round(float(area[valid].sum() / area[membership & np.isfinite(area)].sum()), 6), "net_downward_surface_heat_power_W": round(float(np.sum(heat_flux[index, valid] * area[valid])), 3), "net_upward_surface_water_mass_flux_kg_s": round(float(np.sum(water_flux[index, valid] * area[valid])), 6), "column_heat_content_J": round(float(np.sum(heat_content[index, valid] * area[valid])), 3)})
    changes = [{"from_month": first["month"], "to_month": second["month"], "column_heat_content_change_J": round(second["column_heat_content_J"] - first["column_heat_content_J"], 3), "boundary": "Difference between archived monthly column heat-content fields. It is not a native tendency and is not compared as a budget residual."} for first, second in zip(records, records[1:])]
    return {"schema": "osw-ocean-state-current-geometry-surface-storage-account-v1", "status": "open_surface_forcing_and_storage_account_no_convergence_or_closure", "source_family": assignment["source_family"], "join_status": "not_joined_to_archived_2018_contents_or_boundary_accounts", "state": assignment["state"], "assignment": {"path": assignment_path.relative_to(ROOT).as_posix(), "sha256": sha256(assignment_path)}, "sources": {"mesh": {"path": mesh_path.relative_to(ROOT).as_posix(), "sha256": sha256(mesh_path)}, "t_metrics": {"path": metrics_path.relative_to(ROOT).as_posix(), "sha256": sha256(metrics_path)}, "surface_terms": {"path": terms_path.relative_to(ROOT).as_posix(), "sha256": sha256(terms_path)}, "surface_terms_receipt": {"path": terms_receipt_path.relative_to(ROOT).as_posix(), "sha256": sha256(terms_receipt_path)}}, "monthly_account": records, "successive_storage_differences": changes, "boundary": "Area-integrated monthly ORAS5 surface forcing and archived column heat content over a geographic state membership. It deliberately omits lateral and vertical fluxes, mixing/diffusion, assimilation/restoring, free-surface/volume terms, and a matched temporal budget convention. It is not heat convergence, freshwater convergence, a closed budget, causal attribution, or evidence of transformation."}


def validate(payload: dict) -> None:
    if payload["status"] != "open_surface_forcing_and_storage_account_no_convergence_or_closure" or not payload["join_status"].startswith("not_joined"):
        raise ValueError("open-account scope and separation required")
    if len(payload["monthly_account"]) != 12 or len(payload["successive_storage_differences"]) != 11:
        raise ValueError("all monthly terms and successive differences required")
    if not all(record["valid_area_fraction"] > 0.99 for record in payload["monthly_account"]):
        raise ValueError("surface account must retain nearly complete state area")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(); payload = build(); validate(payload)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
