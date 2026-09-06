"""Fetch one native 2018 ORAS5 Drake T/U/V monthly state subset from ICDC."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib

import netCDF4
import numpy as np


BASE = "https://icdc.cen.uni-hamburg.de/thredds/dodsC/ftpthredds/EASYInit/oras5/ORCA025"
FIELDS = {
    "votemper": ("votemper", "opa0", "grid_T"),
    "vozocrtx": ("vozocrtx", "opa0", "grid_U"),
    "vomecrty": ("vomecrty", "opa0", "grid_V"),
}


def source_urls(month: str, base: str = BASE) -> dict[str, str]:
    if len(month) != 6 or not month.isdigit() or not 1 <= int(month[4:]) <= 12:
        raise ValueError("month must be YYYYMM")
    if not 1979 <= int(month[:4]) <= 2018:
        raise ValueError("this fixed ICDC archive contract covers 1979 through 2018")
    return {
        output: f"{base}/{folder}/{member}/{output}_ORAS5_1m_{month}_{grid}_02.nc"
        for output, (folder, member, grid) in FIELDS.items()
    }


def strip_and_subset(variable, box: dict):
    selectors = []
    for dimension in variable.dimensions:
        if dimension in ("t", "time_counter"):
            selectors.append(0)
        elif dimension == "y":
            selectors.append(slice(box["y_start"], box["y_stop_exclusive"]))
        elif dimension == "x":
            selectors.append(slice(box["x_start"], box["x_stop_exclusive"]))
        else:
            selectors.append(slice(None))
    return np.asanyarray(variable[tuple(selectors)])


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fetch(month: str, mesh_receipt: pathlib.Path, output: pathlib.Path, receipt: pathlib.Path, retrieved_at: str, base: str = BASE) -> dict:
    mesh = json.loads(mesh_receipt.read_text(encoding="utf-8"))
    box = mesh["native_index_box"]
    expected_shape = tuple(mesh["shape"])
    urls = source_urls(month, base)
    arrays = {}; metadata = {}
    for name, url in urls.items():
        with netCDF4.Dataset(url) as dataset:
            if name not in dataset.variables:
                raise ValueError(f"{url} does not contain {name}")
            variable = dataset.variables[name]
            arrays[name] = strip_and_subset(variable, box)
            metadata[name] = {
                "url": url,
                "source_dimensions": list(variable.dimensions),
                "units": getattr(variable, "units", None),
                "long_name": getattr(variable, "long_name", None),
            }
    for name, array in arrays.items():
        if array.shape != expected_shape:
            raise ValueError(f"{name} shape {array.shape} does not align with mesh {expected_shape}")

    output.parent.mkdir(parents=True, exist_ok=True)
    nz, ny, nx = expected_shape
    with netCDF4.Dataset(output, "w", format="NETCDF4") as target:
        target.createDimension("z", nz); target.createDimension("y", ny); target.createDimension("x", nx)
        target.setncattr("month", month)
        target.setncattr("mesh_sha256", mesh["output"]["sha256"])
        target.setncattr("boundary", "Native monthly T/U/V subset only; no accepted section or transport.")
        for name, array in arrays.items():
            variable = target.createVariable(name, array.dtype, ("z", "y", "x"), zlib=True, complevel=4)
            variable[:] = array
            for attribute in ("units", "long_name"):
                if metadata[name][attribute] is not None:
                    setattr(variable, attribute, metadata[name][attribute])

    result = {
        "schema": "oceanlines.oras5.drake-state-subset.v1",
        "status": "native_monthly_state_subset_not_yet_sectioned",
        "month": month,
        "source": "University of Hamburg ICDC ORAS5 ORCA025 ensemble member opa0",
        "retrieved_at": retrieved_at,
        "mesh_receipt": str(mesh_receipt),
        "mesh_sha256": mesh["output"]["sha256"],
        "native_index_box": box,
        "shape": list(expected_shape),
        "fields": metadata,
        "output": {"path": str(output), "bytes": output.stat().st_size, "sha256": sha256_file(output)},
        "next_test": "define a native-face Drake section and collocate T-point temperature to its U/V faces",
        "boundary": (
            "One monthly assimilative-reanalysis member on the native grid. This is not an "
            "observation-only field, climatology, section transport, mass closure, or heat budget."
        ),
    }
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--month", default="201802")
    parser.add_argument("--mesh-receipt", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-drake-mesh.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-drake-state-201802.nc"))
    parser.add_argument("--receipt", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-drake-state-201802.json"))
    parser.add_argument("--retrieved-at")
    parser.add_argument("--base", default=BASE)
    args = parser.parse_args()
    retrieved_at = args.retrieved_at or dt.datetime.now(dt.timezone.utc).isoformat()
    result = fetch(args.month, args.mesh_receipt, args.output, args.receipt, retrieved_at, args.base)
    print(f"wrote {args.output} and {args.receipt}: {result['shape']}")


if __name__ == "__main__":
    main()
