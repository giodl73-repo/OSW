"""Archive compact native T/S/U/V fields for the fixed SANT box and controls."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import netCDF4
import numpy as np

from fetch_oras5_drake_state_subset import source_urls
from fetch_oras5_drake_current_geometry_salinity import source_url as salinity_url


ROOT = Path(__file__).resolve().parents[1]
SELECTION = ROOT / "research" / "ocean-state-sant-closed-box-selection-current-geometry-v1.json"
FAMILY = ROOT / "research" / "ocean-state-sant-current-geometry-physical-source-family-2018.json"
MESH_RECEIPT = ROOT / "research" / "osw-m3-oras5-drake-mesh.json"
TEMPORAL = ROOT / "research" / "ocean-state-sant-temporal-support-audit-2018.json"
OUTPUT = ROOT / "atlas" / "data" / "oras5-sant-closed-box-monthly-fields-2018.nc"
RECEIPT = ROOT / "research" / "ocean-state-sant-closed-box-monthly-fields-2018.json"
MONTHS = tuple(f"2018{month:02d}" for month in range(1, 13))
FIELDS = ("votemper", "vosaline", "vozocrtx", "vomecrty")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def crop(selection: dict) -> dict:
    boxes = [selection["primary"], *selection["one_cell_displaced_controls"]]
    # Include both T cells adjacent to every outer native U/V boundary face.
    return {"y_start": min(box["y_start"] for box in boxes) - 1,
            "y_stop_exclusive": max(box["y_stop_exclusive"] for box in boxes) + 1,
            "x_start": min(box["x_start"] for box in boxes) - 1,
            "x_stop_exclusive": max(box["x_stop_exclusive"] for box in boxes) + 1}


def native_urls(month: str) -> dict[str, str]:
    urls = source_urls(month)
    urls["vosaline"] = salinity_url(month)
    return urls


def slab_digest(array: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(array, dtype="<f4").tobytes()).hexdigest()


def fetch() -> tuple[dict, dict]:
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    family = json.loads(FAMILY.read_text(encoding="utf-8"))
    mesh_receipt = json.loads(MESH_RECEIPT.read_text(encoding="utf-8"))
    temporal = json.loads(TEMPORAL.read_text(encoding="utf-8"))
    if selection["assignment"]["sha256"] != family["assignment"]["sha256"] or temporal["source_family"]["sha256"] != sha256(FAMILY):
        raise ValueError("source-family or temporal custody mismatch")
    rectangle = crop(selection)
    mesh_box = mesh_receipt["native_index_box"]
    ny = rectangle["y_stop_exclusive"] - rectangle["y_start"]
    nx = rectangle["x_stop_exclusive"] - rectangle["x_start"]
    z = mesh_receipt["shape"][0]
    arrays = {name: np.empty((12, z, ny, nx), dtype="f4") for name in FIELDS}
    records = []
    baseline = {entry["month"]: entry for entry in family["months"]}
    provider_time = {entry["month"]: entry for entry in temporal["months"]}
    for index, month in enumerate(MONTHS):
        urls = native_urls(month)
        sources = {}
        for name in FIELDS:
            path = None
            if month in baseline:
                bound = baseline[month]["salinity" if name == "vosaline" else "temperature_velocity"]["state"]
                path = ROOT / bound["path"]
                if sha256(path) != bound["sha256"] or provider_time[month]["fields"][name]["source_url"] != urls[name]:
                    raise ValueError(f"cached {month} {name} is incompatible with bound family")
                with netCDF4.Dataset(path) as dataset:
                    value = np.ma.filled(dataset[name][:, rectangle["y_start"]:rectangle["y_stop_exclusive"], rectangle["x_start"]:rectangle["x_stop_exclusive"]], np.nan).astype("f4")
                time_units = provider_time[month]["fields"][name]["time_units"]
            else:
                print(f"fetch {month} {name}", flush=True)
                with netCDF4.Dataset(urls[name]) as dataset:
                    variable = dataset[name]
                    if variable.dimensions[0] != "time_counter" or variable.shape[1] != z:
                        raise ValueError(f"unexpected source dimensions for {month} {name}")
                    y0, y1 = rectangle["y_start"] + mesh_box["y_start"], rectangle["y_stop_exclusive"] + mesh_box["y_start"]
                    x0, x1 = rectangle["x_start"] + mesh_box["x_start"], rectangle["x_stop_exclusive"] + mesh_box["x_start"]
                    value = np.ma.filled(variable[0, :, y0:y1, x0:x1], np.nan).astype("f4")
                    time = dataset["time_counter"]
                    if float(time[0]) != 0:
                        raise ValueError(f"unexpected source time value for {month} {name}")
                    time_units = str(time.units)
            if value.shape != (z, ny, nx) or not np.isfinite(value).any():
                raise ValueError(f"invalid native slab for {month} {name}")
            arrays[name][index] = value
            sources[name] = {"url": urls[name], "time_units": time_units, "extracted_slab_sha256": slab_digest(value),
                             "finite_native_voxels": int(np.isfinite(value).sum()),
                             "archive": None if path is None else {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}}
        if len({item["time_units"] for item in sources.values()}) != 1:
            raise ValueError(f"monthly provider fields not coindexed for {month}")
        if not next(iter(sources.values()))["time_units"].startswith(f"seconds since {month[:4]}-{month[4:]}-"):
            raise ValueError(f"provider time coordinate points outside {month}")
        records.append({"month": month, "fields": sources})
    return arrays, {"schema": "osw-ocean-state-sant-closed-box-monthly-fields-v1",
                    "status": "compact_native_monthly_2018_screen_source_not_full_state_or_budget",
                    "selection": {"path": SELECTION.relative_to(ROOT).as_posix(), "sha256": sha256(SELECTION)},
                    "source_family": {"path": FAMILY.relative_to(ROOT).as_posix(), "sha256": sha256(FAMILY)},
                    "temporal_audit": {"path": TEMPORAL.relative_to(ROOT).as_posix(), "sha256": sha256(TEMPORAL)},
                    "mesh": {"path": MESH_RECEIPT.relative_to(ROOT).as_posix(), "sha256": sha256(MESH_RECEIPT), "output_sha256": mesh_receipt["output"]["sha256"]},
                    "local_crop": rectangle, "native_crop": {key: rectangle[key] + mesh_box["y_start" if key.startswith("y_") else "x_start"] for key in rectangle},
                    "shape_month_z_y_x": [12, z, ny, nx], "months": records,
                    "boundary": "A compact 2018 native-grid box neighborhood for monthly horizontal screens. Monthly mean T/S/U/V products do not preserve submonthly velocity-tracer covariance, vertical flux, mixing, assimilation, or a matched class-volume tendency."}


def write(arrays: dict, receipt: dict, output: Path = OUTPUT, receipt_path: Path = RECEIPT) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with netCDF4.Dataset(output, "w", format="NETCDF4") as dataset:
        for name, size in zip(("month", "z", "y", "x"), receipt["shape_month_z_y_x"]):
            dataset.createDimension(name, size)
        dataset.setncattr("selection_sha256", receipt["selection"]["sha256"])
        dataset.setncattr("mesh_sha256", receipt["mesh"]["output_sha256"])
        for name in FIELDS:
            variable = dataset.createVariable(name, "f4", ("month", "z", "y", "x"), zlib=True, complevel=4, fill_value=np.float32(np.nan))
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
