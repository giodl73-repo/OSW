"""Extract 0-50 m RTOFS temperature profiles over the D11 Atlantic box."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

import numpy as np

from fetch_rtofs_mhw_bridge import BOUNDS, END, ROOT, START, THREE_D, _encode, _open, _window, remote_identity, source_url


OUTPUT = ROOT / "atlas" / "data" / "rtofs-mhw-upper-ocean-north-atlantic-20260807-20260812.json"
MAX_DEPTH_M = 50.0


def build(output: Path = OUTPUT, retrieved_at: str | None = None) -> dict:
    dates = [START + dt.timedelta(days=offset) for offset in range((END - START).days + 1)]
    rows, files, grid, depths = [], [], None, None
    for date in dates:
        print(f"extracting NOAA RTOFS upper-ocean temperature {date}", flush=True)
        url = source_url(date, THREE_D)
        identity = remote_identity(url)
        handle, dataset = _open(url)
        try:
            latitude, longitude, mask, slices = _window(dataset, (67, 63))
            source_depths = np.asarray(dataset["Depth"][:], dtype=float)
            depth_indices = np.where(source_depths <= MAX_DEPTH_M)[0]
            local_depths = source_depths[depth_indices]
            if local_depths[0] != 0 or local_depths[-1] != MAX_DEPTH_M or len(local_depths) != 15:
                raise ValueError(f"unexpected RTOFS upper-depth support: {local_depths.tolist()}")
            temperature = dataset["temperature"][0, depth_indices, slices[0], slices[1]]
            eastward = dataset["u"][0, depth_indices, slices[0], slices[1]]
            northward = dataset["v"][0, depth_indices, slices[0], slices[1]]
            if round(float(dataset["Date"][0])) != int(date.strftime("%Y%m%d")):
                raise ValueError("RTOFS valid date does not match key date")
        finally:
            dataset.close(); handle.close()
        if depths is None:
            depths = local_depths.tolist()
        elif not np.array_equal(depths, local_depths):
            raise ValueError("RTOFS standard depths changed across dates")
        if grid is None:
            grid = {
                "shape": [67, 63],
                "valid_box_cells": int(mask.sum()),
                "latitude_degrees_north_e6": np.rint(latitude * 1_000_000).astype(int).tolist(),
                "longitude_degrees_east_e6": np.rint(longitude * 1_000_000).astype(int).tolist(),
                "inside_declared_box": mask.astype(int).tolist(),
            }
        rows.append({
            "date": date.isoformat(),
            "potential_temperature_c_milli_by_depth": [_encode(layer, 1000, mask) for layer in temperature],
            "eastward_velocity_m_s_e4_by_depth": [_encode(layer, 10_000, mask) for layer in eastward],
            "northward_velocity_m_s_e4_by_depth": [_encode(layer, 10_000, mask) for layer in northward],
        })
        files.append({"date": date.isoformat(), "three_dimensional": identity})
    digest = hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()
    payload = {
        "schema": "osw.rtofs.mhw-upper-ocean-source.v1",
        "status": "operational_assimilative_model_standard_depth_temperature_cube",
        "source": "NOAA Global Real-Time Ocean Forecast System (RTOFS), HYCOM 93.1",
        "product_page": "https://registry.opendata.aws/noaa-rtofs/",
        "retrieved_at": retrieved_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "window": {"start": START.isoformat(), "end": END.isoformat(), "day_count": len(rows), "valid_time": "00:00 UTC daily", "source_field": "n024 nowcast"},
        "bounds": BOUNDS,
        "vertical_support": {"standard_depths_m": depths, "maximum_depth_m": MAX_DEPTH_M, "integration_contract": "trapezoidal integration between standard-depth point samples over the fixed 0-50 m column"},
        "grid": grid,
        "variables": {
            "potential_temperature_c_milli_by_depth": {"source_id": "temperature", "standard_name": "sea_water_potential_temperature", "source_units": "degC", "scale": 1000},
            "eastward_velocity_m_s_e4_by_depth": {"source_id": "u", "standard_name": "eastward_sea_water_velocity", "source_units": "m/s", "scale": 10000},
            "northward_velocity_m_s_e4_by_depth": {"source_id": "v", "standard_name": "northward_sea_water_velocity", "source_units": "m/s", "scale": 10000},
        },
        "files": files,
        "rows": rows,
        "extracted_rows_sha256": digest,
        "boundary": "These are standard-depth interpolated snapshots from one operational assimilative ocean model. A fixed 0-50 m potential-temperature integral avoids diagnostic mixed-layer-depth division but remains a heat-storage proxy under declared constant density and heat capacity. Standard-depth velocity and temperature support an offline horizontal-advection screen, not native tracer flux. The cube is not native-layer heat content, observed storage, a mixed-layer budget, or causal attribution.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--retrieved-at")
    args = parser.parse_args()
    payload = build(args.output, args.retrieved_at)
    print(f"wrote {args.output} ({len(payload['vertical_support']['standard_depths_m'])} depths x {len(payload['rows'])} days)")
    print(f"extracted sha256 {payload['extracted_rows_sha256']}")


if __name__ == "__main__":
    main()
