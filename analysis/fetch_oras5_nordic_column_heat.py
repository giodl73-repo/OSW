"""Fetch native ORAS5 total-column heat content over the Nordic Seas mesh."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib

import netCDF4
import numpy as np

from fetch_oras5_drake_surface_heat import MONTHS, sha256_file


BASE_URL = "https://icdc.cen.uni-hamburg.de/thredds/dodsC/ftpthredds/EASYInit/oras5/ORCA025/sohtcbtm/opa0"


def source_url(month: str) -> str:
    return f"{BASE_URL}/sohtcbtm_ORAS5_1m_{month}_grid_T_02.nc"


def fetch(mesh_receipt_path: pathlib.Path, output: pathlib.Path, receipt_path: pathlib.Path, retrieved_at: str) -> dict:
    mesh_receipt = json.loads(mesh_receipt_path.read_text(encoding="utf-8"))
    box = mesh_receipt["native_index_box"]
    window = {key: box[key] for key in ("y_start", "y_stop_exclusive", "x_start", "x_stop_exclusive")}
    selector = (0, slice(window["y_start"], window["y_stop_exclusive"]), slice(window["x_start"], window["x_stop_exclusive"]))
    expected = tuple(mesh_receipt["shape"][1:])
    arrays, sources = [], []
    metadata = None
    for month in MONTHS:
        url = source_url(month)
        with netCDF4.Dataset(url) as dataset:
            variable = dataset.variables["sohtcbtm"]
            array = np.ma.filled(variable[selector], np.nan).astype(np.float64)
            if metadata is None:
                metadata = {name: getattr(variable, name, None) for name in ("units", "long_name", "standard_name")}
        if array.shape != expected:
            raise ValueError(f"{month} column-heat shape {array.shape} != {expected}")
        arrays.append(array)
        sources.append({"month": month, "url": url})

    output.parent.mkdir(parents=True, exist_ok=True)
    with netCDF4.Dataset(output, "w", format="NETCDF4") as target:
        target.setncattr("title", "Native ORAS5 total-column heat content over the OSW Nordic Seas mesh")
        target.createDimension("month", len(MONTHS))
        target.createDimension("y", expected[0])
        target.createDimension("x", expected[1])
        target.createVariable("month", "i4", ("month",))[:] = [int(month) for month in MONTHS]
        heat = target.createVariable("sohtcbtm", "f8", ("month", "y", "x"), zlib=True, complevel=4, fill_value=np.float64(1e20))
        heat[:] = np.stack(arrays)
        for name, value in (metadata or {}).items():
            if value is not None:
                setattr(heat, name, value)

    result = {
        "schema": "osw.oras5.nordic-column-heat.v1",
        "status": "native_monthly_total_column_heat_content",
        "retrieved_at": retrieved_at,
        "field": "sohtcbtm",
        "native_window": window,
        "shape": [len(MONTHS), *expected],
        "metadata": metadata,
        "sources": sources,
        "mesh_receipt": {"path": f"research/{mesh_receipt_path.name}", "sha256": sha256_file(mesh_receipt_path)},
        "output": {"path": f"atlas/data/{output.name}", "bytes": output.stat().st_size, "sha256": sha256_file(output)},
        "boundary": "Archived ORAS5 monthly-mean total-column heat content. It independently checks storage but is not a temperature tendency, native tracer-advection term, or complete heat budget.",
    }
    receipt_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh-receipt", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-seas-mesh.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-nordic-column-heat-2018.nc"))
    parser.add_argument("--receipt", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-column-heat-source-2018.json"))
    parser.add_argument("--retrieved-at")
    args = parser.parse_args()
    result = fetch(args.mesh_receipt, args.output, args.receipt, args.retrieved_at or dt.datetime.now(dt.timezone.utc).isoformat())
    print(f"wrote {args.output}: {result['shape']}")


if __name__ == "__main__":
    main()
