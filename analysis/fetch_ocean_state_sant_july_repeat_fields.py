"""Archive the preselected 2016 and 2017 July native box fields."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

import netCDF4
import numpy as np

from fetch_ocean_state_sant_closed_box_monthly_fields import (
    FIELDS, MESH_RECEIPT, ROOT, SELECTION, crop, native_urls, sha256, slab_digest,
)


SELECTION_RULE = ROOT / "research" / "ocean-state-sant-july-repeat-selection-v1.json"
ANNUAL_SOURCE = ROOT / "research" / "ocean-state-sant-closed-box-monthly-fields-2018.json"
OUTPUT = ROOT / "atlas" / "data" / "oras5-sant-closed-box-july-2016-2017.nc"
RECEIPT = ROOT / "research" / "ocean-state-sant-july-repeat-fields-2016-2017.json"
MONTHS = ("201607", "201707")


def fetch() -> tuple[dict, dict]:
    rule = json.loads(SELECTION_RULE.read_text(encoding="utf-8"))
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    annual = json.loads(ANNUAL_SOURCE.read_text(encoding="utf-8"))
    mesh = json.loads(MESH_RECEIPT.read_text(encoding="utf-8"))
    rectangle = crop(selection)
    if rule["status"] != "selected_before_2016_2017_field_inspection" or rectangle != annual["local_crop"] or annual["selection"]["sha256"] != sha256(SELECTION):
        raise ValueError("repeat-year retrieval requires the fixed 2018 box crop")
    nz = mesh["shape"][0]
    ny = rectangle["y_stop_exclusive"] - rectangle["y_start"]
    nx = rectangle["x_stop_exclusive"] - rectangle["x_start"]
    arrays = {name: np.empty((len(MONTHS), nz, ny, nx), dtype="f4") for name in FIELDS}
    records = []
    for index, month in enumerate(MONTHS):
        urls = native_urls(month)
        sources = {}
        for name in FIELDS:
            print(f"fetch {month} {name}", flush=True)
            with netCDF4.Dataset(urls[name]) as dataset:
                variable = dataset[name]
                if variable.dimensions[0] != "time_counter" or variable.shape[1] != nz or float(dataset["time_counter"][0]) != 0:
                    raise ValueError(f"unexpected native source support for {month} {name}")
                y0 = rectangle["y_start"] + mesh["native_index_box"]["y_start"]
                y1 = rectangle["y_stop_exclusive"] + mesh["native_index_box"]["y_start"]
                x0 = rectangle["x_start"] + mesh["native_index_box"]["x_start"]
                x1 = rectangle["x_stop_exclusive"] + mesh["native_index_box"]["x_start"]
                value = np.ma.filled(variable[0, :, y0:y1, x0:x1], np.nan).astype("f4")
                time_units = str(dataset["time_counter"].units)
            if value.shape != (nz, ny, nx) or not np.isfinite(value).any() or not time_units.startswith(f"seconds since {month[:4]}-{month[4:]}-"):
                raise ValueError(f"invalid July native slab for {month} {name}")
            arrays[name][index] = value
            sources[name] = {"url": urls[name], "time_units": time_units, "extracted_slab_sha256": slab_digest(value), "finite_native_voxels": int(np.isfinite(value).sum())}
        if len({item["time_units"] for item in sources.values()}) != 1:
            raise ValueError(f"July {month} fields do not share one time coordinate")
        records.append({"month": month, "fields": sources})
    return arrays, {"schema": "osw-ocean-state-sant-july-repeat-fields-v1",
                    "status": "preselected_two_prior_Julys_compact_native_source_not_budget",
                    "selection_rule": {"path": SELECTION_RULE.relative_to(ROOT).as_posix(), "sha256": sha256(SELECTION_RULE)},
                    "fixed_box": {"path": SELECTION.relative_to(ROOT).as_posix(), "sha256": sha256(SELECTION)},
                    "annual_2018_source": {"path": ANNUAL_SOURCE.relative_to(ROOT).as_posix(), "sha256": sha256(ANNUAL_SOURCE)},
                    "mesh": {"path": MESH_RECEIPT.relative_to(ROOT).as_posix(), "sha256": sha256(MESH_RECEIPT), "output_sha256": mesh["output"]["sha256"]},
                    "local_crop": rectangle, "shape_year_z_y_x": [len(MONTHS), nz, ny, nx], "months": records,
                    "boundary": "Two preselected earlier Julys from the same ICDC ORAS5 ORCA025 opa0 monthly source. This preserves native T/S/U/V box-neighborhood fields only; no independent product, vertical/mixing term, submonthly covariance, or density-class transformation is supplied."}


def write(arrays: dict, receipt: dict, output: Path = OUTPUT, receipt_path: Path = RECEIPT) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with netCDF4.Dataset(output, "w", format="NETCDF4") as dataset:
        for name, size in zip(("year", "z", "y", "x"), receipt["shape_year_z_y_x"]):
            dataset.createDimension(name, size)
        dataset.setncattr("selection_rule_sha256", receipt["selection_rule"]["sha256"])
        dataset.setncattr("mesh_sha256", receipt["mesh"]["output_sha256"])
        for name in FIELDS:
            variable = dataset.createVariable(name, "f4", ("year", "z", "y", "x"), zlib=True, complevel=4, fill_value=np.float32(np.nan))
            variable[:] = arrays[name]
    receipt["output"] = {"path": output.relative_to(ROOT).as_posix(), "bytes": output.stat().st_size, "sha256": sha256(output)}
    receipt["retrieved_at"] = datetime.now(timezone.utc).isoformat()
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--receipt", type=Path, default=RECEIPT)
    args = parser.parse_args()
    arrays, receipt = fetch()
    write(arrays, receipt, args.output, args.receipt)
    print(f"wrote {args.output} and {args.receipt}")


if __name__ == "__main__":
    main()
