"""Calculate boundary fluxes around a small native Drake control box."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import statistics

import netCDF4
import numpy as np

try:
    from audit_nemo_face_thickness_reconstruction import reconstruct_t
except ModuleNotFoundError:
    from analysis.audit_nemo_face_thickness_reconstruction import reconstruct_t


MONTHS = ("201802", "201805", "201808", "201811")
REFERENCES = (-1.9, 0.0, 5.0)
BOUNDS = {"west_u_x": 56, "east_u_x": 72, "south_v_y": 53, "north_v_y": 139, "t_x_start": 57, "t_x_stop_exclusive": 73, "t_y_start": 54, "t_y_stop_exclusive": 140}


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def boundary_transport(velocity, temperature, thickness, width, mask, outward_sign, rho=1027.0, cp=3992.0) -> dict:
    velocity = np.asarray(velocity, dtype=float)
    temperature = np.asarray(temperature, dtype=float)
    thickness = np.asarray(thickness, dtype=float)
    width = np.asarray(width, dtype=float)
    mask = np.asarray(mask) > 0
    if velocity.shape != temperature.shape or velocity.shape != thickness.shape or velocity.shape != mask.shape:
        raise ValueError("boundary level/segment arrays must share shape")
    if width.shape != (velocity.shape[1],):
        raise ValueError("boundary width must have one value per segment")
    if np.any(~np.isfinite(velocity[mask])) or np.any(~np.isfinite(temperature[mask])):
        raise ValueError("wet boundary state must be finite")
    signed_volume = outward_sign * velocity * thickness * width[None, :]
    signed_volume = np.where(mask, signed_volume, 0.0)
    volume_m3_s = float(signed_volume.sum())
    heat = []
    for reference in REFERENCES:
        watts = float((rho * cp * signed_volume * (temperature - reference))[mask].sum())
        heat.append({"reference_temperature_degC": reference, "net_PW": watts / 1e15})
    return {
        "wet_face_count": int(mask.sum()),
        "volume_Sv": volume_m3_s / 1e6,
        "heat_transport_PW": heat,
    }


def calculate_month(mesh: dict, state: dict, month: str, bounds: dict | None = None) -> dict:
    b = BOUNDS if bounds is None else bounds
    t_thickness, _ = reconstruct_t(mesh["e3t_0"], mesh["mbathy"], mesh["e3t_ps"])
    u_thickness = np.minimum(t_thickness[:, :, :-1], t_thickness[:, :, 1:])
    v_thickness = np.minimum(t_thickness[:, :-1, :], t_thickness[:, 1:, :])
    temperature = state["votemper"]
    u = state["vozocrtx"]
    v = state["vomecrty"]
    ys = slice(b["t_y_start"], b["t_y_stop_exclusive"])
    xs = slice(b["t_x_start"], b["t_x_stop_exclusive"])
    definitions = (
        ("west", u[:, ys, b["west_u_x"]], .5 * (temperature[:, ys, b["west_u_x"]] + temperature[:, ys, b["west_u_x"] + 1]), u_thickness[:, ys, b["west_u_x"]], mesh["e2u"][ys, b["west_u_x"]], mesh["umask"][:, ys, b["west_u_x"]], -1),
        ("east", u[:, ys, b["east_u_x"]], .5 * (temperature[:, ys, b["east_u_x"]] + temperature[:, ys, b["east_u_x"] + 1]), u_thickness[:, ys, b["east_u_x"]], mesh["e2u"][ys, b["east_u_x"]], mesh["umask"][:, ys, b["east_u_x"]], 1),
        ("south", v[:, b["south_v_y"], xs], .5 * (temperature[:, b["south_v_y"], xs] + temperature[:, b["south_v_y"] + 1, xs]), v_thickness[:, b["south_v_y"], xs], mesh["e1v"][b["south_v_y"], xs], mesh["vmask"][:, b["south_v_y"], xs], -1),
        ("north", v[:, b["north_v_y"], xs], .5 * (temperature[:, b["north_v_y"], xs] + temperature[:, b["north_v_y"] + 1, xs]), v_thickness[:, b["north_v_y"], xs], mesh["e1v"][b["north_v_y"], xs], mesh["vmask"][:, b["north_v_y"], xs], 1),
    )
    boundaries = []
    for name, velocity, face_temperature, thickness, width, mask, sign in definitions:
        item = boundary_transport(velocity, face_temperature, thickness, width, mask, sign)
        item["name"] = name
        item["positive_direction"] = "outward"
        boundaries.append(item)
    volume = sum(item["volume_Sv"] for item in boundaries)
    heat = []
    for reference in REFERENCES:
        heat.append({
            "reference_temperature_degC": reference,
            "net_boundary_PW": sum(next(case["net_PW"] for case in item["heat_transport_PW"] if case["reference_temperature_degC"] == reference) for item in boundaries),
        })
    audits = []
    for previous, current in zip(heat, heat[1:]):
        expected = -1027.0 * 3992.0 * volume * 1e6 * (current["reference_temperature_degC"] - previous["reference_temperature_degC"])
        actual = (current["net_boundary_PW"] - previous["net_boundary_PW"]) * 1e15
        audits.append({"from_degC": previous["reference_temperature_degC"], "to_degC": current["reference_temperature_degC"], "identity_residual_W": actual - expected})
    return {"month": month, "boundaries": boundaries, "net_outward_volume_Sv": volume, "net_outward_heat_PW": heat, "reference_change_audit": audits}


def stats(values) -> dict:
    return {"mean": statistics.fmean(values), "minimum": min(values), "maximum": max(values), "range": max(values) - min(values)}


def summarize(months: list[dict]) -> dict:
    boundary_summary = []
    for name in ("west", "east", "south", "north"):
        selected = [next(item for item in month["boundaries"] if item["name"] == name) for month in months]
        item = {"name": name, "volume_Sv": stats([boundary["volume_Sv"] for boundary in selected])}
        item["heat_transport_PW"] = [
            {"reference_temperature_degC": reference, "net_PW": stats([
                next(case["net_PW"] for case in boundary["heat_transport_PW"] if case["reference_temperature_degC"] == reference)
                for boundary in selected
            ])} for reference in REFERENCES
        ]
        boundary_summary.append(item)
    reference_summary = []
    for reference in REFERENCES:
        reference_summary.append({
            "reference_temperature_degC": reference,
            "net_outward_PW": stats([next(item["net_boundary_PW"] for item in month["net_outward_heat_PW"] if item["reference_temperature_degC"] == reference) for month in months]),
        })
    mean_by_reference = [item["net_outward_PW"]["mean"] for item in reference_summary]
    return {
        "boundaries": boundary_summary,
        "net_outward_volume_Sv": stats([month["net_outward_volume_Sv"] for month in months]),
        "net_outward_heat_PW": reference_summary,
        "across_reference_mean_heat_range_PW": max(mean_by_reference) - min(mean_by_reference),
    }


def run(mesh_path: pathlib.Path, state_dir: pathlib.Path) -> dict:
    with netCDF4.Dataset(mesh_path) as dataset:
        mesh = {name: np.ma.filled(dataset.variables[name][:], 0) for name in ("e3t_0", "mbathy", "e3t_ps", "umask", "vmask", "e2u", "e1v", "glamu", "gphiu", "glamv", "gphiv")}
    months = []
    state_sources = []
    for month in MONTHS:
        path = state_dir / f"oras5-drake-state-{month}.nc"
        with netCDF4.Dataset(path) as dataset:
            state = {name: np.ma.filled(dataset.variables[name][:], np.nan) for name in ("votemper", "vozocrtx", "vomecrty")}
        months.append(calculate_month(mesh, state, month))
        state_sources.append({"month": month, "path": str(path), "sha256": sha256_file(path)})
    b = BOUNDS
    geometry = {
        **b,
        "west_mean_longitude_deg": float(np.mean(mesh["glamu"][b["t_y_start"]:b["t_y_stop_exclusive"], b["west_u_x"]])),
        "east_mean_longitude_deg": float(np.mean(mesh["glamu"][b["t_y_start"]:b["t_y_stop_exclusive"], b["east_u_x"]])),
        "south_mean_latitude_deg": float(np.mean(mesh["gphiv"][b["south_v_y"], b["t_x_start"]:b["t_x_stop_exclusive"]])),
        "north_mean_latitude_deg": float(np.mean(mesh["gphiv"][b["north_v_y"], b["t_x_start"]:b["t_x_stop_exclusive"]])),
    }
    return {
        "schema": "oceanlines.osw.m4-drake-control-box.v1",
        "status": "native four-boundary control-box flux pilot",
        "geometry": geometry, "months": months, "summary": summarize(months),
        "sources": {"mesh": {"path": str(mesh_path), "sha256": sha256_file(mesh_path)}, "states": state_sources},
        "boundary": "Signed outward advective boundary flux around one small grid-aligned box. Without matched storage tendency, surface freshwater/heat flux, diffusion, and other model budget terms, net boundary flux is not closure, accumulation, convergence attribution, or Antarctic heat delivery.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-drake-mesh.nc"))
    parser.add_argument("--state-dir", type=pathlib.Path, default=pathlib.Path("atlas/data"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-drake-control-box-2018.json"))
    args = parser.parse_args()
    result = run(args.mesh, args.state_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
