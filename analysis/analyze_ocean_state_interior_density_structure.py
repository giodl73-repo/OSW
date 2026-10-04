"""Build a TEOS-10 density-structure screen for the custodial SANT T/S source family."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import gsw
import netCDF4
import numpy as np

from analyze_ocean_state_interior_pathways import MONTHS, choose_seeds
from analyze_ocean_state_interior_vertical_structure import TARGET_DEPTHS_M, midpoint_depths
from prepare_ocean_state_interior_current_geometry import rle_decode


ROOT = Path(__file__).resolve().parents[1]
ASSIGNMENT = ROOT / "research" / "ocean-state-interior-sant-current-geometry-assignment-2026-09-12.json"
FAMILY = ROOT / "research" / "ocean-state-sant-current-geometry-physical-source-family-2018.json"
MESH = ROOT / "atlas" / "data" / "oras5-drake-mesh.nc"
OUTPUT = ROOT / "research" / "ocean-state-interior-sant-density-structure-current-geometry-2018.json"
STRATA = (("below_26_5", -np.inf, 26.5), ("26_5_to_27_0", 26.5, 27.0), ("27_0_to_27_5", 27.0, 27.5), ("at_or_above_27_5", 27.5, np.inf))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def stratum(sigma0: float) -> str:
    return next(name for name, lower, upper in STRATA if lower <= sigma0 < upper)


def profile(seed: dict, temperature: np.ndarray, salinity: np.ndarray, levels: list[dict]) -> dict:
    y, x, longitude, latitude = seed["y"], seed["x"], seed["longitude_deg"], seed["latitude_deg"]
    samples = []
    for level in levels:
        z = level["z"]
        practical_salinity, potential_temperature = float(salinity[z, y, x]), float(temperature[z, y, x])
        if not np.isfinite(practical_salinity) or not np.isfinite(potential_temperature):
            raise ValueError(f"non-finite T/S support at {seed['id']}, z={z}")
        pressure_dbar = float(gsw.p_from_z(-level["midpoint_depth_m"], latitude))
        absolute_salinity = float(gsw.SA_from_SP(practical_salinity, pressure_dbar, longitude, latitude))
        conservative_temperature = float(gsw.CT_from_pt(absolute_salinity, potential_temperature))
        sigma0 = float(gsw.sigma0(absolute_salinity, conservative_temperature))
        samples.append({**level, "practical_salinity_PSU": round(practical_salinity, 6), "absolute_salinity_g_kg": round(absolute_salinity, 6), "potential_temperature_c": round(potential_temperature, 6), "conservative_temperature_c": round(conservative_temperature, 6), "pressure_dbar": round(pressure_dbar, 6), "sigma0_kg_m3": round(sigma0, 6), "numeric_density_stratum": stratum(sigma0)})
    interfaces = [{"upper_target_depth_m": upper["target_depth_m"], "lower_target_depth_m": lower["target_depth_m"], "lower_minus_upper_sigma0_kg_m3": round(lower["sigma0_kg_m3"] - upper["sigma0_kg_m3"], 6), "crosses_numeric_density_stratum": upper["numeric_density_stratum"] != lower["numeric_density_stratum"]} for upper, lower in zip(samples, samples[1:])]
    return {"seed": seed["id"], "latitude_deg": latitude, "longitude_deg": longitude, "levels": samples, "interfaces": interfaces}


def build(assignment_path: Path = ASSIGNMENT, family_path: Path = FAMILY, mesh_path: Path = MESH) -> dict:
    assignment_path, family_path, mesh_path = map(Path, (assignment_path, family_path, mesh_path))
    assignment, family = load(assignment_path), load(family_path)
    if family["assignment"]["sha256"] != sha256(assignment_path) or family["status"] != "ready_for_density_class_and_open_surface_storage_screens_not_vertical_transfer_or_budget":
        raise ValueError("density screen requires the complete current-geometry source family")
    with netCDF4.Dataset(mesh_path) as mesh:
        longitude, latitude = np.asarray(mesh["glamt"][:]), np.asarray(mesh["gphit"][:])
        depths = midpoint_depths(np.asarray(mesh["e3t_0"][:], dtype=float))
    core = rle_decode(assignment["interior_core"]["rle_row_major"], tuple(assignment["mesh"]["shape_yx"]))
    seeds = choose_seeds(core, longitude, latitude)
    levels = [{"target_depth_m": target, "z": int(np.argmin(abs(depths - target))), "midpoint_depth_m": round(float(depths[np.argmin(abs(depths - target))]), 6)} for target in TARGET_DEPTHS_M]
    monthly = []
    for month in MONTHS:
        state_path = ROOT / "atlas" / "data" / f"oras5-drake-state-{month}.nc"
        salinity_path = ROOT / "atlas" / "data" / f"oras5-drake-salinity-current-geometry-{month}.nc"
        with netCDF4.Dataset(state_path) as state, netCDF4.Dataset(salinity_path) as salinity:
            temperature, practical_salinity = np.asarray(state["votemper"][:]), np.asarray(salinity["vosaline"][:])
        monthly.append({"valid_time": f"2018-{month[-2:]}-01/P1M", "temperature_state": {"path": state_path.relative_to(ROOT).as_posix(), "sha256": sha256(state_path)}, "salinity_state": {"path": salinity_path.relative_to(ROOT).as_posix(), "sha256": sha256(salinity_path)}, "profiles": [profile(seed, temperature, practical_salinity, levels) for seed in seeds]})
    return {
        "schema": "osw-ocean-state-interior-density-structure-screen-v1", "status": "bounded_TEOS10_density_and_numeric_class_structure_not_transformation", "source_family": family["source_family"], "join_status": "not_joined_to_archived_2018_contents_or_boundary_accounts",
        "address": {"geometry_edition": "longhurst-v4-54", "province": "SANT", "depth_support": "four_nearest_native_T_level_midpoints"},
        "method": {"equation_of_state": "TEOS-10 GSW 3.6.23", "conversion": "SA_from_SP using local longitude, latitude, and pressure from midpoint depth; CT_from_pt; sigma0", "numeric_strata_sigma0_kg_m3": [{"id": name, "lower_inclusive": None if not np.isfinite(lower) else lower, "upper_exclusive": None if not np.isfinite(upper) else upper} for name, lower, upper in STRATA], "selection_frozen_before_field_inspection": True, "seeds": seeds},
        "source_family_manifest": {"path": family_path.relative_to(ROOT).as_posix(), "sha256": sha256(family_path)}, "months": monthly,
        "boundary": "A local TEOS-10 density and numerical-stratum structure screen from one ORAS5 member. The numerical strata are analysis bins, not named water masses. Density structure and strata do not establish class-volume flux, water-mass transformation, vertical transfer, mixing, transport, convergence, a closed budget, or a numerical bridge to archived contents.",
    }


def validate(payload: dict) -> None:
    if payload["status"] != "bounded_TEOS10_density_and_numeric_class_structure_not_transformation" or not payload["join_status"].startswith("not_joined"):
        raise ValueError("scope and source separation are mandatory")
    if len(payload["months"]) != 4 or len(payload["method"]["numeric_strata_sigma0_kg_m3"]) != 4:
        raise ValueError("four-month, four-stratum screen required")
    for month in payload["months"]:
        for item in month["profiles"]:
            if len(item["levels"]) != 4 or not all(np.isfinite(level["sigma0_kg_m3"]) for level in item["levels"]):
                raise ValueError("finite four-level density profiles required")


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
