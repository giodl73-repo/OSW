"""Fetch native ORCA025 T-cell horizontal metrics for the existing Drake subset."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib

import netCDF4
import numpy as np


SOURCE_URL = "https://icdc.cen.uni-hamburg.de/thredds/dodsC/ftpthredds/EASYInit/oras5/ORCA025/mesh/mesh_mask.nc"
VARIABLES = ("e1t", "e2t")


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def strip_time(variable, ys, xs):
    selectors = [0 if dimension in ("t", "time_counter") else ys if dimension == "y" else xs if dimension == "x" else slice(None) for dimension in variable.dimensions]
    return np.asanyarray(variable[tuple(selectors)])


def validate_arrays(arrays: dict, expected_shape: tuple[int, int]) -> dict:
    for name in VARIABLES:
        values = np.asarray(arrays[name], dtype=float)
        if values.shape != expected_shape:
            raise ValueError(f"{name} shape does not match existing subset")
        if np.any(~np.isfinite(values)) or np.any(values <= 0):
            raise ValueError(f"{name} must be finite and positive")
    area = np.asarray(arrays["e1t"], dtype=float) * np.asarray(arrays["e2t"], dtype=float)
    return {"minimum_m2": float(area.min()), "maximum_m2": float(area.max()), "all_finite_positive": True}


def fetch(source_url: str, mesh_receipt_path: pathlib.Path, output: pathlib.Path, receipt_path: pathlib.Path, retrieved_at: str, context: str = "drake") -> dict:
    mesh_receipt = json.loads(mesh_receipt_path.read_text(encoding="utf-8"))
    box = mesh_receipt["native_index_box"]
    expected_shape = tuple(mesh_receipt["shape"][1:])
    ys = slice(box["y_start"], box["y_stop_exclusive"])
    xs = slice(box["x_start"], box["x_stop_exclusive"])
    with netCDF4.Dataset(source_url) as source:
        arrays = {name: strip_time(source.variables[name], ys, xs) for name in VARIABLES}
        units = {name: getattr(source.variables[name], "units", None) for name in VARIABLES}
    area_audit = validate_arrays(arrays, expected_shape)
    output.parent.mkdir(parents=True, exist_ok=True)
    with netCDF4.Dataset(output, "w", format="NETCDF4") as target:
        target.createDimension("y", expected_shape[0]); target.createDimension("x", expected_shape[1])
        target.setncattr("source_url", source_url)
        target.setncattr("boundary", f"Native T-cell horizontal metrics for {context} only; no state, heat content, storage tendency, or budget closure.")
        for name in VARIABLES:
            variable = target.createVariable(name, arrays[name].dtype, ("y", "x"), zlib=True)
            variable[:] = arrays[name]
            if units[name]:
                variable.units = units[name]
    result = {
        "schema": f"oceanlines.oras5.{context}-t-metrics.v1", "status": "native_t_cell_metric_companion",
        "source_url": source_url, "retrieved_at": retrieved_at, "native_index_box": box,
        "shape": list(expected_shape), "variables": {name: {"shape": list(arrays[name].shape), "units": units[name]} for name in VARIABLES},
        "t_cell_area_m2": area_audit,
        "mesh_receipt": {"path": str(mesh_receipt_path), "sha256": sha256_file(mesh_receipt_path), "mesh_output_sha256": mesh_receipt["output"]["sha256"]},
        "output": {"path": str(output), "bytes": output.stat().st_size, "sha256": sha256_file(output)},
        "boundary": f"Native T-cell horizontal metrics aligned to the existing {context} subset. They provide area geometry but do not establish heat-content tendency, complete tracer-budget closure, or heat delivery.",
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-url", default=SOURCE_URL)
    parser.add_argument("--mesh-receipt", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-drake-mesh.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-drake-t-metrics.nc"))
    parser.add_argument("--receipt", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-drake-t-metrics.json"))
    parser.add_argument("--retrieved-at")
    parser.add_argument("--context", default="drake")
    args = parser.parse_args()
    retrieved_at = args.retrieved_at or dt.datetime.now(dt.timezone.utc).isoformat()
    result = fetch(args.source_url, args.mesh_receipt, args.output, args.receipt, retrieved_at, args.context)
    print(f"wrote {args.output} and {args.receipt}: {result['shape']}")


if __name__ == "__main__":
    main()
