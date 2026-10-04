"""Describe bounded SANT vertical temperature structure and horizontal-velocity shear."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import netCDF4
import numpy as np

from analyze_ocean_state_interior_pathways import MONTHS, choose_seeds, collocated_velocity
from prepare_ocean_state_interior_current_geometry import rle_decode


ROOT = Path(__file__).resolve().parents[1]
ASSIGNMENT = ROOT / "research" / "ocean-state-interior-sant-current-geometry-assignment-2026-09-12.json"
MESH = ROOT / "atlas" / "data" / "oras5-drake-mesh.nc"
OUTPUT = ROOT / "research" / "ocean-state-interior-sant-vertical-structure-current-geometry-2018.json"
TARGET_DEPTHS_M = (0.0, 100.0, 200.0, 1000.0)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def midpoint_depths(thickness: np.ndarray) -> np.ndarray:
    return np.cumsum(thickness) - thickness / 2


def sample_profile(seed: dict, temperature: np.ndarray, u: np.ndarray, v: np.ndarray, levels: list[dict]) -> dict:
    y, x = seed["y"], seed["x"]
    samples = []
    for level in levels:
        z = level["z"]
        velocity = collocated_velocity(u[z], v[z], y, x)
        temp = float(temperature[z, y, x])
        if velocity is None or not np.isfinite(temp):
            raise ValueError(f"non-finite declared profile support at {seed['id']}, z={z}")
        samples.append({**level, "temperature_c": round(temp, 6), "u_proxy_m_s": round(velocity[0], 8), "v_proxy_m_s": round(velocity[1], 8)})
    interfaces = []
    for upper, lower in zip(samples, samples[1:]):
        dz = lower["midpoint_depth_m"] - upper["midpoint_depth_m"]
        du, dv = lower["u_proxy_m_s"] - upper["u_proxy_m_s"], lower["v_proxy_m_s"] - upper["v_proxy_m_s"]
        interfaces.append({
            "upper_target_depth_m": upper["target_depth_m"], "lower_target_depth_m": lower["target_depth_m"],
            "midpoint_separation_m": round(dz, 6), "upper_minus_lower_temperature_c": round(upper["temperature_c"] - lower["temperature_c"], 6),
            "horizontal_velocity_difference_m_s": round(float(np.hypot(du, dv)), 8),
            "horizontal_velocity_difference_per_m_s_m": round(float(np.hypot(du, dv) / dz), 12),
        })
    return {"seed": seed["id"], "latitude_deg": seed["latitude_deg"], "longitude_deg": seed["longitude_deg"], "levels": samples, "interfaces": interfaces}


def build(assignment_path: Path = ASSIGNMENT, mesh_path: Path = MESH) -> dict:
    assignment_path, mesh_path = Path(assignment_path), Path(mesh_path)
    assignment = load(assignment_path)
    if assignment["status"] != "separate_unjoined_source_family":
        raise ValueError("vertical screen requires the separately versioned assignment")
    if sha256(mesh_path) != assignment["mesh"]["sha256"]:
        raise ValueError("mesh checksum does not match assignment")
    with netCDF4.Dataset(mesh_path) as mesh:
        longitude, latitude = np.asarray(mesh["glamt"][:]), np.asarray(mesh["gphit"][:])
        depths = midpoint_depths(np.asarray(mesh["e3t_0"][:], dtype=float))
    core = rle_decode(assignment["interior_core"]["rle_row_major"], tuple(assignment["mesh"]["shape_yx"]))
    seeds = choose_seeds(core, longitude, latitude)
    levels = [{"target_depth_m": target, "z": int(np.argmin(abs(depths - target))), "midpoint_depth_m": round(float(depths[np.argmin(abs(depths - target))]), 6)} for target in TARGET_DEPTHS_M]
    months = []
    for month in MONTHS:
        state_path = ROOT / "atlas" / "data" / f"oras5-drake-state-{month}.nc"
        with netCDF4.Dataset(state_path) as state:
            temperature, u, v = np.asarray(state["votemper"][:]), np.asarray(state["vozocrtx"][:]), np.asarray(state["vomecrty"][:])
        months.append({"valid_time": f"2018-{month[-2:]}-01/P1M", "state_path": state_path.relative_to(ROOT).as_posix(), "state_sha256": sha256(state_path), "profiles": [sample_profile(seed, temperature, u, v, levels) for seed in seeds]})
    return {
        "schema": "osw-ocean-state-interior-vertical-structure-screen-v1",
        "status": "bounded_vertical_structure_and_shear_screen_not_vertical_transfer",
        "source_family": assignment["source_family"],
        "join_status": "not_joined_to_archived_2018_contents_or_boundary_accounts",
        "address": {"geometry_edition": "longhurst-v4-54", "province": "SANT", "depth_support": "four_nearest_native_T_level_midpoints"},
        "selection": {"frozen_before_field_inspection": True, "seeds": seeds, "target_depths_m": list(TARGET_DEPTHS_M), "native_level_rule": "nearest ORAS5 T-level midpoint calculated from e3t_0", "velocity_rule": "T-cell proxy from two indexed U and two indexed V samples"},
        "membership_source": {"path": assignment_path.relative_to(ROOT).as_posix(), "sha256": sha256(assignment_path)},
        "months": months,
        "boundary": "A local vertical co-occurrence, temperature-gradient, and horizontal-velocity-difference screen. It has no vertical velocity, diapycnal flux, density/salinity class, mixed-layer diagnosis, entrainment term, or closed budget. It therefore does not diagnose vertical transfer, mixing, transformation, vertical heat flux, or causation.",
    }


def validate(payload: dict) -> None:
    if payload["status"] != "bounded_vertical_structure_and_shear_screen_not_vertical_transfer" or not payload["join_status"].startswith("not_joined"):
        raise ValueError("vertical screen scope and non-join status are required")
    for month in payload["months"]:
        if len(month["profiles"]) != 3:
            raise ValueError("every month needs the three predeclared profiles")
        for profile in month["profiles"]:
            if len(profile["levels"]) != 4 or len(profile["interfaces"]) != 3:
                raise ValueError("incomplete vertical profile")
            if not all(np.isfinite(level["temperature_c"]) for level in profile["levels"]):
                raise ValueError("profile temperatures must be finite")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assignment", type=Path, default=ASSIGNMENT)
    parser.add_argument("--mesh", type=Path, default=MESH)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    payload = build(args.assignment, args.mesh)
    validate(payload)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
