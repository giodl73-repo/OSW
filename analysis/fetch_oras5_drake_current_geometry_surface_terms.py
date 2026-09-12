"""Fetch all-2018 native ORAS5 surface/storage terms for the pinned SANT family."""

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
MONTHS = tuple(f"2018{month:02d}" for month in range(1, 13))
FIELDS = {"sohefldo": "W/m2", "sowaflup": "Kg/m2/s", "sohtcbtm": "J/m2"}
OUTPUT = ROOT / "atlas" / "data" / "oras5-drake-current-geometry-surface-terms-2018.nc"
RECEIPT = ROOT / "research" / "ocean-state-sant-current-geometry-surface-terms-2018.json"


def source_url(field: str, month: str) -> str:
    if field not in FIELDS or month not in MONTHS:
        raise ValueError("unsupported surface field or month")
    return f"{BASE}/{field}/opa0/{field}_ORAS5_1m_{month}_grid_T_02.nc"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fetch(mesh_receipt_path: Path = MESH_RECEIPT, assignment_path: Path = ASSIGNMENT, output: Path = OUTPUT, receipt: Path = RECEIPT, retrieved_at: str | None = None) -> dict:
    mesh_receipt_path, assignment_path, output, receipt = map(Path, (mesh_receipt_path, assignment_path, output, receipt))
    mesh, assignment = json.loads(mesh_receipt_path.read_text(encoding="utf-8")), json.loads(assignment_path.read_text(encoding="utf-8"))
    if assignment["status"] != "separate_unjoined_source_family":
        raise ValueError("surface terms require the separate pinned geometry family")
    box = mesh["native_index_box"]
    selector = (0, slice(box["y_start"], box["y_stop_exclusive"]), slice(box["x_start"], box["x_stop_exclusive"]))
    shape = tuple(mesh["shape"][1:])
    arrays, metadata, sources = {}, {}, {}
    for field in FIELDS:
        samples, field_sources = [], []
        for month in MONTHS:
            url = source_url(field, month)
            with netCDF4.Dataset(url) as dataset:
                variable = dataset.variables[field]
                sample = np.ma.filled(variable[selector], np.nan).astype(np.float32)
                if field not in metadata:
                    metadata[field] = {"units": getattr(variable, "units", None), "long_name": getattr(variable, "long_name", None), "standard_name": getattr(variable, "standard_name", None)}
            if sample.shape != shape:
                raise ValueError(f"{field} {month} shape {sample.shape} != {shape}")
            samples.append(sample); field_sources.append({"month": month, "url": url})
        arrays[field], sources[field] = np.stack(samples), field_sources
    output.parent.mkdir(parents=True, exist_ok=True)
    with netCDF4.Dataset(output, "w", format="NETCDF4") as target:
        target.createDimension("month", len(MONTHS)); target.createDimension("y", shape[0]); target.createDimension("x", shape[1])
        target.setncattr("assignment_sha256", sha256(assignment_path)); target.setncattr("mesh_sha256", mesh["output"]["sha256"])
        target.setncattr("boundary", "Native monthly ORAS5 surface heat, freshwater, and column-heat-content terms bound to the separate current-geometry SANT family; no closed budget.")
        month_var = target.createVariable("month", "i4", ("month",)); month_var[:] = [int(month) for month in MONTHS]
        for field, values in arrays.items():
            variable = target.createVariable(field, "f4", ("month", "y", "x"), zlib=True, complevel=4, fill_value=np.float32(np.nan)); variable[:] = values
            for name, value in metadata[field].items():
                if value is not None: setattr(variable, name, value)
    result = {"schema": "osw-ocean-state-current-geometry-surface-terms-v1", "status": "native_monthly_surface_and_storage_terms_not_closed_budget", "source_family": assignment["source_family"], "assignment": {"path": assignment_path.relative_to(ROOT).as_posix(), "sha256": sha256(assignment_path)}, "mesh": {"path": mesh_receipt_path.relative_to(ROOT).as_posix(), "sha256": sha256(mesh_receipt_path), "output_sha256": mesh["output"]["sha256"], "native_index_box": box}, "months": list(MONTHS), "fields": metadata, "sources": sources, "output": {"path": output.relative_to(ROOT).as_posix(), "bytes": output.stat().st_size, "sha256": sha256(output)}, "retrieved_at": retrieved_at or dt.datetime.now(dt.timezone.utc).isoformat(), "boundary": "Monthly reanalysis forcing and archived heat-content state only. Surface heat and freshwater terms do not yield a SANT budget without matched lateral/vertical fluxes; column heat content difference is a storage diagnostic, not a native tracer tendency or causal attribution."}
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh-receipt", type=Path, default=MESH_RECEIPT); parser.add_argument("--assignment", type=Path, default=ASSIGNMENT)
    parser.add_argument("--output", type=Path, default=OUTPUT); parser.add_argument("--receipt", type=Path, default=RECEIPT); parser.add_argument("--retrieved-at")
    args = parser.parse_args(); result = fetch(args.mesh_receipt, args.assignment, args.output, args.receipt, args.retrieved_at)
    print(f"wrote {result['output']['path']}")


if __name__ == "__main__":
    main()
