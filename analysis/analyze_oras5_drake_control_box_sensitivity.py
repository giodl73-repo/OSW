"""Challenge M4 Drake advective divergence with nested control-box geometries."""

from __future__ import annotations

import argparse
import json
import pathlib
import statistics

import netCDF4
import numpy as np

try:
    from analyze_oras5_drake_control_box import MONTHS, REFERENCES, BOUNDS, calculate_month, sha256_file
except ModuleNotFoundError:
    from analysis.analyze_oras5_drake_control_box import MONTHS, REFERENCES, BOUNDS, calculate_month, sha256_file


EAST_BOUNDARIES = (60, 64, 68, 72)
NORTH_BOUNDARIES = (74, 96, 118, 139)


def stats(values) -> dict:
    return {"mean": statistics.fmean(values), "minimum": min(values), "maximum": max(values), "range": max(values) - min(values)}


def summarize_variant(name: str, family: str, bounds: dict, months: list[dict], mesh: dict) -> dict:
    heat_by_reference = []
    for reference in REFERENCES:
        values = [next(item["net_boundary_PW"] for item in month["net_outward_heat_PW"] if item["reference_temperature_degC"] == reference) for month in months]
        heat_by_reference.append({"reference_temperature_degC": reference, "net_outward_PW": stats(values)})
    means = [item["net_outward_PW"]["mean"] for item in heat_by_reference]
    b = bounds
    return {
        "name": name, "family": family, "bounds": bounds,
        "extent": {
            "west_mean_longitude_deg": float(np.mean(mesh["glamu"][b["t_y_start"]:b["t_y_stop_exclusive"], b["west_u_x"]])),
            "east_mean_longitude_deg": float(np.mean(mesh["glamu"][b["t_y_start"]:b["t_y_stop_exclusive"], b["east_u_x"]])),
            "south_mean_latitude_deg": float(np.mean(mesh["gphiv"][b["south_v_y"], b["t_x_start"]:b["t_x_stop_exclusive"]])),
            "north_mean_latitude_deg": float(np.mean(mesh["gphiv"][b["north_v_y"], b["t_x_start"]:b["t_x_stop_exclusive"]])),
        },
        "net_outward_volume_Sv": stats([month["net_outward_volume_Sv"] for month in months]),
        "net_outward_heat_PW": heat_by_reference,
        "across_reference_mean_heat_range_PW": max(means) - min(means),
    }


def variants() -> list[tuple[str, str, dict]]:
    output = []
    for east in EAST_BOUNDARIES:
        bounds = dict(BOUNDS)
        bounds.update({"east_u_x": east, "t_x_stop_exclusive": east + 1})
        output.append((f"east-x{east}", "eastward_extent", bounds))
    for north in NORTH_BOUNDARIES:
        bounds = dict(BOUNDS)
        bounds.update({"north_v_y": north, "t_y_stop_exclusive": north + 1})
        output.append((f"north-y{north}", "northward_extent", bounds))
    return output


def run(mesh_path: pathlib.Path, state_dir: pathlib.Path) -> dict:
    with netCDF4.Dataset(mesh_path) as dataset:
        mesh = {name: np.ma.filled(dataset.variables[name][:], 0) for name in ("e3t_0", "mbathy", "e3t_ps", "umask", "vmask", "e2u", "e1v", "glamu", "gphiu", "glamv", "gphiv")}
    states = {}
    sources = []
    for month in MONTHS:
        path = state_dir / f"oras5-drake-state-{month}.nc"
        with netCDF4.Dataset(path) as dataset:
            states[month] = {name: np.ma.filled(dataset.variables[name][:], np.nan) for name in ("votemper", "vozocrtx", "vomecrty")}
        sources.append({"month": month, "path": str(path), "sha256": sha256_file(path)})
    records = []
    for name, family, bounds in variants():
        months = [calculate_month(mesh, states[month], month, bounds) for month in MONTHS]
        records.append(summarize_variant(name, family, bounds, months, mesh))
    family_summary = []
    for family in ("eastward_extent", "northward_extent"):
        selected = [item for item in records if item["family"] == family]
        heat_means = [next(case["net_outward_PW"]["mean"] for case in item["net_outward_heat_PW"] if case["reference_temperature_degC"] == 0) for item in selected]
        volume_maxima = [max(abs(item["net_outward_volume_Sv"]["minimum"]), abs(item["net_outward_volume_Sv"]["maximum"])) for item in selected]
        family_summary.append({"family": family, "heat_0C_mean_PW_across_boxes": stats(heat_means), "maximum_absolute_monthly_volume_imbalance_Sv": max(volume_maxima)})
    return {
        "schema": "oceanlines.osw.m4-drake-control-box-sensitivity.v1",
        "status": "nested native control-box geometry sensitivity",
        "variants": records, "family_summary": family_summary,
        "sources": {"mesh": {"path": str(mesh_path), "sha256": sha256_file(mesh_path)}, "states": sources},
        "boundary": "Nested eastward-extent and northward-extent boxes test geometric dependence of offline advective boundary divergence. They do not quantify observational uncertainty, storage tendency, surface flux, diffusion, native tracer-budget closure, or Antarctic heat delivery.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-drake-mesh.nc"))
    parser.add_argument("--state-dir", type=pathlib.Path, default=pathlib.Path("atlas/data"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-drake-control-box-sensitivity-2018.json"))
    args = parser.parse_args()
    result = run(args.mesh, args.state_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
