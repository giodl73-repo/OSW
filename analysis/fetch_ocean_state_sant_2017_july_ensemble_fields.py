"""Archive the preselected July 2017 ORAS5 perturbed-member native fields."""

from __future__ import annotations

from datetime import datetime, timezone
import json

import netCDF4
import numpy as np

from fetch_ocean_state_sant_closed_box_monthly_fields import FIELDS, MESH_RECEIPT, ROOT, SELECTION, crop, native_urls, sha256, slab_digest


RULE = ROOT / "research" / "ocean-state-sant-2017-july-ensemble-selection-v1.json"
REFERENCE = ROOT / "research" / "ocean-state-sant-july-repeat-fields-2016-2017.json"
OUTPUT = ROOT / "atlas" / "data" / "oras5-sant-closed-box-july-2017-ensemble.nc"
RECEIPT = ROOT / "research" / "ocean-state-sant-2017-july-ensemble-fields.json"


def member_urls(member: str) -> dict[str, str]:
    if member not in ("opa1", "opa2", "opa3", "opa4"):
        raise ValueError("unexpected ensemble member")
    return {name: url.replace("/opa0/", f"/{member}/") for name, url in native_urls("201707").items()}


def fetch() -> tuple[dict, dict]:
    rule = json.loads(RULE.read_text(encoding="utf-8"))
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    reference = json.loads(REFERENCE.read_text(encoding="utf-8"))
    mesh = json.loads(MESH_RECEIPT.read_text(encoding="utf-8"))
    rectangle = crop(selection)
    members = rule["selected_members"]
    if rule["status"] != "selected_before_perturbed_member_field_inspection" or members != ["opa1", "opa2", "opa3", "opa4"] or rectangle != reference["local_crop"] or reference["fixed_box"]["sha256"] != sha256(SELECTION):
        raise ValueError("ensemble retrieval requires the frozen July geometry and member selection")
    nz = mesh["shape"][0]
    ny = rectangle["y_stop_exclusive"] - rectangle["y_start"]
    nx = rectangle["x_stop_exclusive"] - rectangle["x_start"]
    arrays = {name: np.empty((len(members), nz, ny, nx), dtype="f4") for name in FIELDS}
    records = []
    for index, member in enumerate(members):
        sources = {}
        for name, url in member_urls(member).items():
            print(f"fetch 201707 {member} {name}", flush=True)
            with netCDF4.Dataset(url) as dataset:
                variable = dataset[name]
                if variable.dimensions[0] != "time_counter" or variable.shape[1] != nz or float(dataset["time_counter"][0]) != 0:
                    raise ValueError(f"unexpected native source support for {member} {name}")
                y0 = rectangle["y_start"] + mesh["native_index_box"]["y_start"]
                y1 = rectangle["y_stop_exclusive"] + mesh["native_index_box"]["y_start"]
                x0 = rectangle["x_start"] + mesh["native_index_box"]["x_start"]
                x1 = rectangle["x_stop_exclusive"] + mesh["native_index_box"]["x_start"]
                value = np.ma.filled(variable[0, :, y0:y1, x0:x1], np.nan).astype("f4")
                time_units = str(dataset["time_counter"].units)
            if value.shape != (nz, ny, nx) or not np.isfinite(value).any() or not time_units.startswith("seconds since 2017-07-"):
                raise ValueError(f"invalid native slab for {member} {name}")
            arrays[name][index] = value
            sources[name] = {"url": url, "time_units": time_units, "extracted_slab_sha256": slab_digest(value), "finite_native_voxels": int(np.isfinite(value).sum())}
        if len({item["time_units"] for item in sources.values()}) != 1:
            raise ValueError(f"201707 {member} fields do not share one time coordinate")
        records.append({"member": member, "fields": sources})
    return arrays, {"schema": "osw-ocean-state-sant-2017-july-ensemble-fields-v1",
                    "status": "preselected_four_perturbed_members_compact_native_source_not_independent_products",
                    "selection_rule": {"path": RULE.relative_to(ROOT).as_posix(), "sha256": sha256(RULE)},
                    "fixed_box": {"path": SELECTION.relative_to(ROOT).as_posix(), "sha256": sha256(SELECTION)},
                    "reference_fields": {"path": REFERENCE.relative_to(ROOT).as_posix(), "sha256": sha256(REFERENCE)},
                    "mesh": {"path": MESH_RECEIPT.relative_to(ROOT).as_posix(), "sha256": sha256(MESH_RECEIPT), "output_sha256": mesh["output"]["sha256"]},
                    "local_crop": rectangle, "shape_member_z_y_x": [len(members), nz, ny, nx], "members": records,
                    "boundary": "Four perturbed members of one ORAS5 assimilative product on the same native grid, one monthly mean. This archive supplies no independent product, formal uncertainty interval, submonthly covariance, vertical/mixing term, or density-class transformation."}


def write(arrays: dict, receipt: dict) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with netCDF4.Dataset(OUTPUT, "w", format="NETCDF4") as dataset:
        for name, size in zip(("member", "z", "y", "x"), receipt["shape_member_z_y_x"]):
            dataset.createDimension(name, size)
        dataset.setncattr("selection_rule_sha256", receipt["selection_rule"]["sha256"])
        dataset.setncattr("mesh_sha256", receipt["mesh"]["output_sha256"])
        for name in FIELDS:
            variable = dataset.createVariable(name, "f4", ("member", "z", "y", "x"), zlib=True, complevel=4, fill_value=np.float32(np.nan))
            variable[:] = arrays[name]
    receipt["output"] = {"path": OUTPUT.relative_to(ROOT).as_posix(), "bytes": OUTPUT.stat().st_size, "sha256": sha256(OUTPUT)}
    receipt["retrieved_at"] = datetime.now(timezone.utc).isoformat()
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    write(*fetch())
    print(f"wrote {OUTPUT} and {RECEIPT}")
