"""Fetch one compact native ORAS5 T/S/U/V month sufficient for the Nordic budget."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib

import netCDF4
import numpy as np

from fetch_oras5_arctic_state_subset import sha256_file, source_urls


def bounding_window(points):
    ys = [point[0] for point in points]; xs = [point[1] for point in points]
    return {"y_start": min(ys), "y_stop_exclusive": max(ys) + 1, "x_start": min(xs), "x_stop_exclusive": max(xs) + 1}


def required_windows(control: dict) -> dict:
    tracer_cells = {tuple(cell) for cell in control["inside_t_cells"]}
    u_faces = set(); v_faces = set()
    for section in control["sections"]:
        for face in section["faces"]:
            y, x = int(face["y"]), int(face["x"])
            if face["face"] == "U":
                u_faces.add((y, x)); tracer_cells.update(((y, x), (y, x + 1)))
            elif face["face"] == "V":
                v_faces.add((y, x)); tracer_cells.update(((y, x), (y + 1, x)))
            else:
                raise ValueError(f"unknown face kind {face['face']}")
    return {
        "votemper": bounding_window(tracer_cells),
        "vosaline": bounding_window(tracer_cells),
        "vozocrtx": bounding_window(u_faces),
        "vomecrty": bounding_window(v_faces),
    }


def global_window(local: dict, mesh_box: dict) -> dict:
    return {
        "y_start": local["y_start"] + mesh_box["y_start"],
        "y_stop_exclusive": local["y_stop_exclusive"] + mesh_box["y_start"],
        "x_start": local["x_start"] + mesh_box["x_start"],
        "x_stop_exclusive": local["x_stop_exclusive"] + mesh_box["x_start"],
    }


def subset(variable, window):
    selectors = []
    for dimension in variable.dimensions:
        if dimension in ("t", "time_counter"):
            selectors.append(0)
        elif dimension == "y":
            selectors.append(slice(window["y_start"], window["y_stop_exclusive"]))
        elif dimension == "x":
            selectors.append(slice(window["x_start"], window["x_stop_exclusive"]))
        else:
            selectors.append(slice(None))
    return np.asanyarray(variable[tuple(selectors)])


def fetch(month: str, mesh_receipt_path: pathlib.Path, control_path: pathlib.Path, output: pathlib.Path, receipt_path: pathlib.Path, retrieved_at: str) -> dict:
    mesh_receipt = json.loads(mesh_receipt_path.read_text(encoding="utf-8"))
    control = json.loads(control_path.read_text(encoding="utf-8"))
    windows = required_windows(control)
    urls = source_urls(month)
    arrays = {}; metadata = {}
    for name, url in urls.items():
        local = windows[name]; remote = global_window(local, mesh_receipt["native_index_box"])
        with netCDF4.Dataset(url) as dataset:
            variable = dataset.variables[name]
            arrays[name] = subset(variable, remote)
            metadata[name] = {"url": url, "local_window": local, "global_window": remote, "units": getattr(variable, "units", None), "long_name": getattr(variable, "long_name", None)}
        expected = (mesh_receipt["shape"][0], local["y_stop_exclusive"] - local["y_start"], local["x_stop_exclusive"] - local["x_start"])
        if arrays[name].shape != expected:
            raise ValueError(f"{name} shape {arrays[name].shape} != {expected}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with netCDF4.Dataset(output, "w", format="NETCDF4") as target:
        target.setncattr("month", month); target.setncattr("mesh_sha256", mesh_receipt["output"]["sha256"])
        target.setncattr("boundary", "Compact native Nordic budget T/S/U/V windows; no transport, storage tendency, or complete heat budget.")
        target.createDimension("z", mesh_receipt["shape"][0])
        for name, array in arrays.items():
            ydim, xdim = f"y_{name}", f"x_{name}"
            target.createDimension(ydim, array.shape[1]); target.createDimension(xdim, array.shape[2])
            variable = target.createVariable(name, array.dtype, ("z", ydim, xdim), zlib=True, complevel=4)
            variable[:] = array
            variable.setncattr("local_y_start", windows[name]["y_start"]); variable.setncattr("local_x_start", windows[name]["x_start"])
            for attribute in ("units", "long_name"):
                if metadata[name][attribute] is not None:
                    setattr(variable, attribute, metadata[name][attribute])
    result = {
        "schema": "osw.oras5.nordic-budget-state.v1",
        "status": "compact_native_monthly_nordic_budget_state",
        "month": month,
        "retrieved_at": retrieved_at,
        "mesh_receipt": {"path": f"research/{mesh_receipt_path.name}", "sha256": sha256_file(mesh_receipt_path), "mesh_output_sha256": mesh_receipt["output"]["sha256"]},
        "control_volume": {"path": f"research/{control_path.name}", "sha256": sha256_file(control_path)},
        "fields": {name: {**metadata[name], "shape": list(arrays[name].shape)} for name in arrays},
        "output": {"path": f"atlas/data/{output.name}", "bytes": output.stat().st_size, "sha256": sha256_file(output)},
        "boundary": "One monthly assimilative-reanalysis member. Windows are sufficient for the exact control-volume storage state and five offline advective boundaries, but contain no surface, ice, mixing, diffusion, assimilation, or model-native tracer-advection terms.",
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--month", required=True)
    parser.add_argument("--mesh-receipt", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-seas-mesh.json"))
    parser.add_argument("--control", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-control-volume.json"))
    parser.add_argument("--output", type=pathlib.Path)
    parser.add_argument("--receipt", type=pathlib.Path)
    parser.add_argument("--retrieved-at")
    args = parser.parse_args()
    output = args.output or pathlib.Path(f"atlas/data/oras5-nordic-budget-state-{args.month}.nc")
    receipt = args.receipt or pathlib.Path(f"research/osw-m4-oras5-nordic-budget-state-{args.month}.json")
    result = fetch(args.month, args.mesh_receipt, args.control, output, receipt, args.retrieved_at or dt.datetime.now(dt.timezone.utc).isoformat())
    print(f"wrote {output}: {result['output']['bytes']} bytes")


if __name__ == "__main__":
    main()
