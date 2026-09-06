"""Fetch compact native ORAS5 monthly surface heat flux for the M4 Drake box."""

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
except ModuleNotFoundError:
    from analysis.analyze_oras5_drake_control_box import BOUNDS


MONTHS = tuple(f"2018{month:02d}" for month in range(1, 13))
BASE_URL = "https://icdc.cen.uni-hamburg.de/thredds/dodsC/ftpthredds/EASYInit/oras5/ORCA025/sohefldo/opa0"


def source_url(month: str) -> str:
    return f"{BASE_URL}/sohefldo_ORAS5_1m_{month}_grid_T_02.nc"


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def native_window(mesh_receipt: dict) -> dict:
    box = mesh_receipt["native_index_box"]
    return {
        "y_start": box["y_start"] + BOUNDS["t_y_start"],
        "y_stop_exclusive": box["y_start"] + BOUNDS["t_y_stop_exclusive"],
        "x_start": box["x_start"] + BOUNDS["t_x_start"],
        "x_stop_exclusive": box["x_start"] + BOUNDS["t_x_stop_exclusive"],
    }


def fetch(mesh_receipt_path: pathlib.Path, output: pathlib.Path, receipt_path: pathlib.Path, retrieved_at: str) -> dict:
    mesh_receipt = json.loads(mesh_receipt_path.read_text(encoding="utf-8"))
    window = native_window(mesh_receipt)
    selector = (0, slice(window["y_start"], window["y_stop_exclusive"]), slice(window["x_start"], window["x_stop_exclusive"]))
    arrays = []
    sources = []
    metadata = None
    for month in MONTHS:
        url = source_url(month)
        with netCDF4.Dataset(url) as dataset:
            variable = dataset.variables["sohefldo"]
            array = np.ma.filled(variable[selector], np.nan).astype(np.float32)
            if metadata is None:
                metadata = {
                    "units": getattr(variable, "units", None),
                    "long_name": getattr(variable, "long_name", None),
                    "standard_name": getattr(variable, "standard_name", None),
                }
        expected = (window["y_stop_exclusive"] - window["y_start"], window["x_stop_exclusive"] - window["x_start"])
        if array.shape != expected:
            raise ValueError(f"{month} surface-flux shape {array.shape} != {expected}")
        arrays.append(array)
        sources.append({"month": month, "url": url})

    output.parent.mkdir(parents=True, exist_ok=True)
    with netCDF4.Dataset(output, "w", format="NETCDF4") as target:
        target.setncattr("title", "Compact native ORAS5 surface heat flux over the OSW M4 Drake control box")
        target.setncattr("sign_convention", "positive downward into ocean, copied from ORAS5 sohefldo metadata")
        target.createDimension("month", len(MONTHS))
        target.createDimension("y", arrays[0].shape[0])
        target.createDimension("x", arrays[0].shape[1])
        month_var = target.createVariable("month", "i4", ("month",))
        month_var[:] = [int(month) for month in MONTHS]
        flux_var = target.createVariable("sohefldo", "f4", ("month", "y", "x"), zlib=True, complevel=4, fill_value=np.float32(1e20))
        flux_var[:] = np.stack(arrays)
        for name, value in (metadata or {}).items():
            if value is not None:
                setattr(flux_var, name, value)

    result = {
        "schema": "oceanlines.oras5.drake-surface-heat.v1",
        "status": "compact_native_monthly_surface_heat_flux",
        "retrieved_at": retrieved_at,
        "field": "sohefldo",
        "native_window": window,
        "shape": [len(MONTHS), arrays[0].shape[0], arrays[0].shape[1]],
        "metadata": metadata,
        "sources": sources,
        "mesh_receipt": {"path": str(mesh_receipt_path), "sha256": sha256_file(mesh_receipt_path)},
        "output": {"path": str(output), "bytes": output.stat().st_size, "sha256": sha256_file(output)},
        "boundary": "Native ORAS5 monthly-mean net downward surface heat flux. It is model/reanalysis forcing, including the ORAS5 surface-restoring context; it is not a direct observation or a complete tracer-budget diagnostic.",
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh-receipt", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-drake-mesh.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-drake-surface-heat-2018.nc"))
    parser.add_argument("--receipt", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-drake-surface-heat-2018.json"))
    parser.add_argument("--retrieved-at")
    args = parser.parse_args()
    retrieved_at = args.retrieved_at or dt.datetime.now(dt.timezone.utc).isoformat()
    result = fetch(args.mesh_receipt, args.output, args.receipt, retrieved_at)
    print(f"wrote {args.output}: {result['output']['bytes']} bytes")


if __name__ == "__main__":
    main()
