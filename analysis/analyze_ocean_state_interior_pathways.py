"""Run a bounded, surface, monthly-mean SANT interior kinematic pathway screen."""

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
OUTPUT = ROOT / "research" / "ocean-state-interior-sant-pathways-current-geometry-2018.json"
MONTHS = ("201802", "201805", "201808", "201811")
EARTH_RADIUS_M = 6_371_000.0
STEP_SECONDS = 6 * 60 * 60
STEPS = 20


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def choose_seeds(core: np.ndarray, longitude: np.ndarray, latitude: np.ndarray) -> list[dict]:
    """Select three geometry-only longitudinal seeds at the median core latitude."""
    yy, xx = np.where(core)
    median_lat = float(np.median(latitude[core]))
    result = []
    for label, quantile in (("western", 0.25), ("central", 0.5), ("eastern", 0.75)):
        target_lon = float(np.quantile(longitude[core], quantile))
        candidate = np.argmin((longitude[core] - target_lon) ** 2 + (latitude[core] - median_lat) ** 2)
        y, x = int(yy[candidate]), int(xx[candidate])
        result.append({"id": label, "quantile": quantile, "y": y, "x": x, "latitude_deg": round(float(latitude[y, x]), 6), "longitude_deg": round(float(longitude[y, x]), 6)})
    return result


def controls(seed: dict, core: np.ndarray) -> list[dict]:
    result = [seed]
    for label, dy, dx in (("north_control", -1, 0), ("south_control", 1, 0), ("west_control", 0, -1), ("east_control", 0, 1)):
        y, x = seed["y"] + dy, seed["x"] + dx
        if 0 <= y < core.shape[0] and 0 <= x < core.shape[1] and core[y, x]:
            result.append({"id": f"{seed['id']}_{label}", "parent_seed": seed["id"], "y": y, "x": x})
    return result


def nearest(values: np.ndarray, target: float) -> int:
    return int(np.argmin(np.abs(values - target)))


def collocated_velocity(u: np.ndarray, v: np.ndarray, y: int, x: int) -> tuple[float, float] | None:
    """T-cell proxy from adjacent native U/V samples; not a native face flux."""
    if y + 1 >= v.shape[0] or x + 1 >= u.shape[1]:
        return None
    samples = (u[y, x], u[y, x + 1], v[y, x], v[y + 1, x])
    if not all(np.isfinite(samples)):
        return None
    return float((samples[0] + samples[1]) / 2), float((samples[2] + samples[3]) / 2)


def integrate(start: dict, u: np.ndarray, v: np.ndarray, temperature: np.ndarray, core: np.ndarray, longitude: np.ndarray, latitude: np.ndarray) -> dict:
    lat_axis, lon_axis = latitude[:, 0], longitude[0, :]
    y, x = start["y"], start["x"]
    position_lat, position_lon = float(latitude[y, x]), float(longitude[y, x])
    points = [{"step": 0, "y": y, "x": x, "latitude_deg": round(position_lat, 6), "longitude_deg": round(position_lon, 6), "monthly_surface_temperature_c": round(float(temperature[y, x]), 6)}]
    status = "completed_interior_screen"
    for step in range(1, STEPS + 1):
        velocity = collocated_velocity(u, v, y, x)
        if velocity is None:
            status = "invalid_velocity_proxy"
            break
        zonal, meridional = velocity
        position_lat += np.degrees(meridional * STEP_SECONDS / EARTH_RADIUS_M)
        position_lon += np.degrees(zonal * STEP_SECONDS / (EARTH_RADIUS_M * np.cos(np.radians(position_lat))))
        y, x = nearest(lat_axis, position_lat), nearest(lon_axis, position_lon)
        points.append({"step": step, "y": y, "x": x, "latitude_deg": round(position_lat, 6), "longitude_deg": round(position_lon, 6), "monthly_surface_temperature_c": round(float(temperature[y, x]), 6)})
        if not core[y, x]:
            status = "left_declared_interior_core"
            break
    return {"id": start["id"], "parent_seed": start.get("parent_seed", start["id"]), "status": status, "steps_completed": len(points) - 1, "points": points}


def distance_km(first: dict, second: dict) -> float:
    lat1, lon1, lat2, lon2 = map(np.radians, (first["latitude_deg"], first["longitude_deg"], second["latitude_deg"], second["longitude_deg"]))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return float(EARTH_RADIUS_M * 2 * np.arcsin(np.sqrt(a)) / 1000)


def summarize_relative_motion(seeds: list[dict], tracks: list[dict]) -> list[dict]:
    """Compare each seed with its predeclared cardinal controls, not a volume divergence."""
    by_id = {track["id"]: track for track in tracks}
    summary = []
    for seed in seeds:
        focal = by_id[seed["id"]]
        controls_for_seed = [track for track in tracks if track.get("parent_seed") == seed["id"] and track["id"] != seed["id"]]
        initial_distances = [distance_km(focal["points"][0], control["points"][0]) for control in controls_for_seed]
        final_distances = [distance_km(focal["points"][-1], control["points"][-1]) for control in controls_for_seed]
        initial_temperature_contrasts = [abs(focal["points"][0]["monthly_surface_temperature_c"] - control["points"][0]["monthly_surface_temperature_c"]) for control in controls_for_seed]
        final_temperature_contrasts = [abs(focal["points"][-1]["monthly_surface_temperature_c"] - control["points"][-1]["monthly_surface_temperature_c"]) for control in controls_for_seed]
        summary.append({
            "seed": seed["id"],
            "control_count": len(controls_for_seed),
            "mean_initial_control_separation_km": round(float(np.mean(initial_distances)), 6),
            "mean_final_control_separation_km": round(float(np.mean(final_distances)), 6),
            "mean_control_separation_change_km": round(float(np.mean(final_distances) - np.mean(initial_distances)), 6),
            "mean_initial_temperature_contrast_c": round(float(np.mean(initial_temperature_contrasts)), 6),
            "mean_final_temperature_contrast_c": round(float(np.mean(final_temperature_contrasts)), 6),
            "boundary": "A relative-motion and co-located-temperature contrast among a seed and one-cell displaced controls. Negative separation change is local kinematic contraction in this screen, not horizontal convergence, accumulation, mixing, or a flux divergence diagnosis.",
        })
    return summary


def build(assignment_path: Path = ASSIGNMENT, mesh_path: Path = MESH) -> dict:
    assignment_path, mesh_path = Path(assignment_path), Path(mesh_path)
    assignment = load(assignment_path)
    if assignment["status"] != "separate_unjoined_source_family":
        raise ValueError("only the explicitly separate membership source family is admissible")
    with netCDF4.Dataset(mesh_path) as mesh:
        longitude, latitude = np.asarray(mesh["glamt"][:]), np.asarray(mesh["gphit"][:])
    if sha256(mesh_path) != assignment["mesh"]["sha256"]:
        raise ValueError("mesh checksum does not match pinned membership assignment")
    core = rle_decode(assignment["interior_core"]["rle_row_major"], tuple(assignment["mesh"]["shape_yx"]))
    seeds = choose_seeds(core, longitude, latitude)
    all_starts = [item for seed in seeds for item in controls(seed, core)]
    monthly = []
    for month in MONTHS:
        state_path = ROOT / "atlas" / "data" / f"oras5-drake-state-{month}.nc"
        with netCDF4.Dataset(state_path) as state:
            u, v, temperature = np.asarray(state["vozocrtx"][0]), np.asarray(state["vomecrty"][0]), np.asarray(state["votemper"][0])
        tracks = [integrate(start, u, v, temperature, core, longitude, latitude) for start in all_starts]
        monthly.append({"valid_time": f"2018-{month[-2:]}-01/P1M", "state_path": state_path.relative_to(ROOT).as_posix(), "state_sha256": sha256(state_path), "tracks": tracks, "relative_motion": summarize_relative_motion(seeds, tracks), "completed_track_count": sum(track["status"] == "completed_interior_screen" for track in tracks)})
    return {
        "schema": "osw-ocean-state-interior-pathway-screen-v1",
        "status": "bounded_kinematic_screen_not_transport_or_budget",
        "source_family": assignment["source_family"],
        "join_status": "not_joined_to_archived_2018_contents_or_boundary_accounts",
        "address": {"geometry_edition": "longhurst-v4-54", "province": "SANT", "depth_support": "surface_model_layer"},
        "selection": {"frozen_before_velocity_inspection": True, "seeds": seeds, "controls": "each available cardinal one-cell core neighbor", "time_samples": list(MONTHS), "integration": {"velocity_support": "ORAS5 z=0 monthly mean", "t_cell_proxy": "mean of two indexed U samples and two indexed V samples", "temperature_support": "ORAS5 z=0 monthly temperature sampled at the nearest T cell after each kinematic step", "step_hours": 6, "step_count": STEPS, "nominal_duration_days": 5}},
        "membership_source": {"path": assignment_path.relative_to(ROOT).as_posix(), "sha256": sha256(assignment_path), "core_cell_count": assignment["interior_core"]["cell_count"]},
        "months": monthly,
        "boundary": "A screen of gridded, monthly-mean surface kinematics with co-located Eulerian temperature samples. It is not an observed Lagrangian trajectory, parcel thermodynamics, a material pathway, a transport estimate, a vertical transfer, a water-mass diagnosis, convergence, transformation, a closed budget, or a result compatible for numerical joining with the archived 2018 state-contents account.",
    }


def validate(payload: dict) -> None:
    if payload["status"] != "bounded_kinematic_screen_not_transport_or_budget" or not payload["join_status"].startswith("not_joined"):
        raise ValueError("screen scope and non-join status are required")
    if len(payload["selection"]["seeds"]) != 3 or len(payload["months"]) != 4:
        raise ValueError("declared three-seed, four-month screen is incomplete")
    for month in payload["months"]:
        if not month["tracks"]:
            raise ValueError("each month requires tracks")
        if len(month["relative_motion"]) != 3:
            raise ValueError("each month requires one relative-motion result per primary seed")
        for track in month["tracks"]:
            if track["status"] not in {"completed_interior_screen", "left_declared_interior_core", "invalid_velocity_proxy"}:
                raise ValueError("unknown track status")
            if track["points"][0]["step"] != 0:
                raise ValueError("track must retain its declared starting point")
            if not all(np.isfinite(point["monthly_surface_temperature_c"]) for point in track["points"]):
                raise ValueError("track must retain finite co-located temperature samples")


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
