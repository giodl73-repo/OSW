"""Fetch checksum-bound ORAS5 salinity supplements for the pinned SANT source family."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

import netCDF4
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://icdc.cen.uni-hamburg.de/thredds/dodsC/ftpthredds/EASYInit/oras5/ORCA025"
MESH_RECEIPT = ROOT / "research" / "osw-m3-oras5-drake-mesh.json"
ASSIGNMENT = ROOT / "research" / "ocean-state-interior-sant-current-geometry-assignment-2026-09-12.json"


def source_url(month: str) -> str:
    if len(month) != 6 or not month.isdigit() or not 1 <= int(month[4:]) <= 12:
        raise ValueError("month must be YYYYMM")
    return f"{BASE}/vosaline/opa0/vosaline_ORAS5_1m_{month}_grid_T_02.nc"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def subset(variable, box: dict) -> np.ndarray:
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
    return np.ma.filled(variable[tuple(selectors)], np.nan).astype(np.float32)


def fetch(month: str, mesh_receipt_path: Path = MESH_RECEIPT, assignment_path: Path = ASSIGNMENT, output: Path | None = None, receipt: Path | None = None, retrieved_at: str | None = None) -> dict:
    mesh_receipt_path, assignment_path = Path(mesh_receipt_path), Path(assignment_path)
    output = Path(output or ROOT / "atlas" / "data" / f"oras5-drake-salinity-current-geometry-{month}.nc")
    receipt = Path(receipt or ROOT / "research" / f"ocean-state-interior-sant-salinity-current-geometry-{month}.json")
    mesh, assignment = json.loads(mesh_receipt_path.read_text(encoding="utf-8")), json.loads(assignment_path.read_text(encoding="utf-8"))
    if assignment["status"] != "separate_unjoined_source_family":
        raise ValueError("salinity supplement requires the explicitly separate geometry family")
    box, expected = mesh["native_index_box"], tuple(mesh["shape"])
    url = source_url(month)
    with netCDF4.Dataset(url) as dataset:
        field = dataset.variables["vosaline"]
        values = subset(field, box)
        metadata = {"url": url, "source_dimensions": list(field.dimensions), "units": getattr(field, "units", None), "long_name": getattr(field, "long_name", None)}
    if values.shape != expected or not np.isfinite(values).any():
        raise ValueError("salinity subset has unexpected support")
    output.parent.mkdir(parents=True, exist_ok=True)
    with netCDF4.Dataset(output, "w", format="NETCDF4") as target:
        for dimension, size in zip(("z", "y", "x"), expected):
            target.createDimension(dimension, size)
        target.setncattr("month", month)
        target.setncattr("mesh_sha256", mesh["output"]["sha256"])
        target.setncattr("assignment_sha256", sha256(assignment_path))
        target.setncattr("boundary", "Native ORAS5 salinity supplement bound to the separately versioned current-geometry SANT assignment; no density or transformation diagnosis is implied.")
        variable = target.createVariable("vosaline", "f4", ("z", "y", "x"), zlib=True, complevel=4, fill_value=np.float32(np.nan))
        variable[:] = values
        for name, value in metadata.items():
            if name != "url" and value is not None:
                setattr(variable, name, value)
    result = {
        "schema": "osw-ocean-state-current-geometry-salinity-supplement-v1", "status": "native_monthly_salinity_supplement_not_yet_density_or_transformation", "month": month,
        "source_family": assignment["source_family"], "assignment": {"path": assignment_path.relative_to(ROOT).as_posix(), "sha256": sha256(assignment_path)},
        "mesh": {"path": mesh_receipt_path.relative_to(ROOT).as_posix(), "sha256": sha256(mesh_receipt_path), "output_sha256": mesh["output"]["sha256"], "native_index_box": box, "shape": list(expected)},
        "field": metadata, "output": {"path": output.relative_to(ROOT).as_posix(), "bytes": output.stat().st_size, "sha256": sha256(output)},
        "boundary": "One ORAS5 assimilative-reanalysis member and month. Practical salinity can support a later declared density/class screen, but this receipt is not density, a water-mass classification, a class-volume flux, transformation, transport, or budget.",
    }
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--month", required=True)
    parser.add_argument("--mesh-receipt", type=Path, default=MESH_RECEIPT)
    parser.add_argument("--assignment", type=Path, default=ASSIGNMENT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--retrieved-at", default=dt.datetime.now(dt.timezone.utc).isoformat())
    args = parser.parse_args()
    result = fetch(args.month, args.mesh_receipt, args.assignment, args.output, args.receipt, args.retrieved_at)
    print(f"wrote {result['output']['path']}")


if __name__ == "__main__":
    main()
