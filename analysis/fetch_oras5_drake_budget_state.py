"""Fetch one compact native ORAS5 month containing only the M4 control-box budget state."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib

import netCDF4
import numpy as np

try:
    from analyze_oras5_drake_control_box import BOUNDS
    from fetch_oras5_drake_state_subset import source_urls
except ModuleNotFoundError:
    from analysis.analyze_oras5_drake_control_box import BOUNDS
    from analysis.fetch_oras5_drake_state_subset import source_urls


WINDOWS = {
    "votemper": {"y_start": BOUNDS["south_v_y"], "y_stop_exclusive": BOUNDS["north_v_y"] + 2, "x_start": BOUNDS["west_u_x"], "x_stop_exclusive": BOUNDS["east_u_x"] + 2},
    "vozocrtx": {"y_start": BOUNDS["t_y_start"], "y_stop_exclusive": BOUNDS["t_y_stop_exclusive"], "x_start": BOUNDS["west_u_x"], "x_stop_exclusive": BOUNDS["east_u_x"] + 1},
    "vomecrty": {"y_start": BOUNDS["south_v_y"], "y_stop_exclusive": BOUNDS["north_v_y"] + 1, "x_start": BOUNDS["t_x_start"], "x_stop_exclusive": BOUNDS["t_x_stop_exclusive"]},
}


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def global_window(local_window: dict, mesh_box: dict) -> dict:
    return {
        "y_start": mesh_box["y_start"] + local_window["y_start"],
        "y_stop_exclusive": mesh_box["y_start"] + local_window["y_stop_exclusive"],
        "x_start": mesh_box["x_start"] + local_window["x_start"],
        "x_stop_exclusive": mesh_box["x_start"] + local_window["x_stop_exclusive"],
    }


def subset(variable, window: dict):
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


def fetch(month: str, mesh_receipt_path: pathlib.Path, output: pathlib.Path, receipt_path: pathlib.Path, retrieved_at: str) -> dict:
    mesh_receipt = json.loads(mesh_receipt_path.read_text(encoding="utf-8"))
    mesh_box = mesh_receipt["native_index_box"]
    urls = source_urls(month)
    arrays = {}; metadata = {}
    for name, url in urls.items():
        local = WINDOWS[name]
        remote = global_window(local, mesh_box)
        with netCDF4.Dataset(url) as dataset:
            variable = dataset.variables[name]
            arrays[name] = subset(variable, remote)
            metadata[name] = {"url": url, "local_window": local, "global_window": remote, "units": getattr(variable, "units", None), "long_name": getattr(variable, "long_name", None)}
        expected = (mesh_receipt["shape"][0], local["y_stop_exclusive"] - local["y_start"], local["x_stop_exclusive"] - local["x_start"])
        if arrays[name].shape != expected:
            raise ValueError(f"{name} compact shape {arrays[name].shape} != {expected}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with netCDF4.Dataset(output, "w", format="NETCDF4") as target:
        target.setncattr("month", month)
        target.setncattr("mesh_sha256", mesh_receipt["output"]["sha256"])
        target.setncattr("boundary", "Compact native control-box T/U/V windows only; no complete tendency or flux budget.")
        target.createDimension("z", mesh_receipt["shape"][0])
        for name, array in arrays.items():
            ydim, xdim = f"y_{name}", f"x_{name}"
            target.createDimension(ydim, array.shape[1]); target.createDimension(xdim, array.shape[2])
            variable = target.createVariable(name, array.dtype, ("z", ydim, xdim), zlib=True, complevel=4)
            variable[:] = array
            for attribute in ("units", "long_name"):
                if metadata[name][attribute] is not None:
                    setattr(variable, attribute, metadata[name][attribute])
    result = {
        "schema": "oceanlines.oras5.drake-budget-state.v1", "status": "compact_native_monthly_control_box_state",
        "month": month, "retrieved_at": retrieved_at,
        "mesh_receipt": {"path": str(mesh_receipt_path), "sha256": sha256_file(mesh_receipt_path), "mesh_output_sha256": mesh_receipt["output"]["sha256"]},
        "fields": {name: {**metadata[name], "shape": list(arrays[name].shape)} for name in arrays},
        "output": {"path": str(output), "bytes": output.stat().st_size, "sha256": sha256_file(output)},
        "boundary": "Compact native monthly windows sufficient for the declared control-box storage and offline advective boundaries. No surface, ice, mixing, diffusion, or model-native tracer-budget terms.",
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--month", required=True)
    parser.add_argument("--mesh-receipt", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-drake-mesh.json"))
    parser.add_argument("--output", type=pathlib.Path)
    parser.add_argument("--receipt", type=pathlib.Path)
    parser.add_argument("--retrieved-at")
    args = parser.parse_args()
    output = args.output or pathlib.Path(f"atlas/data/oras5-drake-budget-state-{args.month}.nc")
    receipt = args.receipt or pathlib.Path(f"research/osw-m4-oras5-drake-budget-state-{args.month}.json")
    retrieved_at = args.retrieved_at or dt.datetime.now(dt.timezone.utc).isoformat()
    result = fetch(args.month, args.mesh_receipt, output, receipt, retrieved_at)
    print(f"wrote {output}: {result['output']['bytes']} bytes")


if __name__ == "__main__":
    main()
