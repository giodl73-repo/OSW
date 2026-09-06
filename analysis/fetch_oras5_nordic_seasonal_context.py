"""Fetch ORAS5 ice concentration, ice thickness, and mixed-layer depth for the Nordic room."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib

import netCDF4
import numpy as np

from fetch_oras5_drake_surface_heat import MONTHS, sha256_file


BASE_URL = "https://icdc.cen.uni-hamburg.de/thredds/dodsC/ftpthredds/EASYInit/oras5/ORCA025"
FIELDS = {
    "ileadfra": "icemod_02",
    "iicethic": "icemod_02",
    "somxl010": "grid_T_02",
}


def source_url(field: str, month: str) -> str:
    return f"{BASE_URL}/{field}/opa0/{field}_ORAS5_1m_{month}_{FIELDS[field]}.nc"


def fetch(mesh_receipt_path: pathlib.Path, output: pathlib.Path, receipt_path: pathlib.Path, retrieved_at: str) -> dict:
    mesh_receipt = json.loads(mesh_receipt_path.read_text(encoding="utf-8"))
    box = mesh_receipt["native_index_box"]
    window = {key: box[key] for key in ("y_start", "y_stop_exclusive", "x_start", "x_stop_exclusive")}
    selector = (0, slice(window["y_start"], window["y_stop_exclusive"]), slice(window["x_start"], window["x_stop_exclusive"]))
    expected = tuple(mesh_receipt["shape"][1:])
    field_arrays, metadata, sources = {}, {}, []
    for field in FIELDS:
        arrays = []
        for month in MONTHS:
            url = source_url(field, month)
            with netCDF4.Dataset(url) as dataset:
                variable = dataset.variables[field]
                array = np.ma.filled(variable[selector], np.nan).astype(np.float32)
                if field not in metadata:
                    metadata[field] = {name: getattr(variable, name, None) for name in ("units", "long_name", "standard_name")}
            if array.shape != expected:
                raise ValueError(f"{month} {field} shape {array.shape} != {expected}")
            arrays.append(array)
            sources.append({"field": field, "month": month, "url": url})
        field_arrays[field] = np.stack(arrays)

    output.parent.mkdir(parents=True, exist_ok=True)
    with netCDF4.Dataset(output, "w", format="NETCDF4") as target:
        target.setncattr("title", "Native ORAS5 seasonal context over the OSW Nordic Seas mesh")
        target.setncattr("ice_naming_note", "ICDC folder/variable ileadfra carries NetCDF long_name Ice concentration")
        target.createDimension("month", len(MONTHS)); target.createDimension("y", expected[0]); target.createDimension("x", expected[1])
        target.createVariable("month", "i4", ("month",))[:] = [int(month) for month in MONTHS]
        for field, arrays in field_arrays.items():
            variable = target.createVariable(field, "f4", ("month", "y", "x"), zlib=True, complevel=4, fill_value=np.float32(1e20))
            variable[:] = arrays
            for name, value in metadata[field].items():
                if value is not None:
                    setattr(variable, name, value)
    result = {
        "schema": "osw.oras5.nordic-seasonal-context.v1",
        "status": "native_monthly_ice_and_mixed_layer_context",
        "retrieved_at": retrieved_at,
        "fields": metadata,
        "native_window": window,
        "shape_per_field": [len(MONTHS), *expected],
        "sources": sources,
        "mesh_receipt": {"path": f"research/{mesh_receipt_path.name}", "sha256": sha256_file(mesh_receipt_path)},
        "output": {"path": f"atlas/data/{output.name}", "bytes": output.stat().st_size, "sha256": sha256_file(output)},
        "boundary": "Monthly ORAS5 reanalysis state context. Ice concentration, ice thickness, and mixed-layer depth are not heat-budget tendencies and cannot causally identify the unresolved remainder.",
    }
    receipt_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh-receipt", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-seas-mesh.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-nordic-seasonal-context-2018.nc"))
    parser.add_argument("--receipt", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-seasonal-context-source-2018.json"))
    parser.add_argument("--retrieved-at")
    args = parser.parse_args()
    result = fetch(args.mesh_receipt, args.output, args.receipt, args.retrieved_at or dt.datetime.now(dt.timezone.utc).isoformat())
    print(f"wrote {args.output}: {result['shape_per_field']}")


if __name__ == "__main__":
    main()
