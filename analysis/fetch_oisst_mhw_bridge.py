"""Fetch a compact OISST field cube around the D4 marine-heatwave bridge."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

import netCDF4
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = "https://psl.noaa.gov/thredds/dodsC/Datasets/noaa.oisst.v2.highres/sst.day.mean.2026.nc"
OUTPUT = ROOT / "atlas" / "data" / "oisst-mhw-bridge-north-atlantic-20260807-20260812.json"
START = dt.date(2026, 8, 7)
END = dt.date(2026, 8, 12)
BOUNDS = {"south": 40.125, "north": 42.875, "west": -51.375, "east": -47.375}


def _dates(values, units, calendar):
    return [dt.date(value.year, value.month, value.day) for value in netCDF4.num2date(values, units, calendar=calendar)]


def build(output: Path = OUTPUT, retrieved_at: str | None = None, source_url: str = SOURCE_URL) -> dict:
    with netCDF4.Dataset(source_url) as dataset:
        time = dataset.variables["time"]
        dates = _dates(time[:], time.units, getattr(time, "calendar", "standard"))
        time_indices = [dates.index(START + dt.timedelta(days=offset)) for offset in range((END - START).days + 1)]
        latitudes = np.asarray(dataset.variables["lat"][:], dtype=float)
        longitudes = np.asarray(dataset.variables["lon"][:], dtype=float)
        latitude_indices = np.flatnonzero((latitudes >= BOUNDS["south"]) & (latitudes <= BOUNDS["north"]))
        west_360, east_360 = BOUNDS["west"] % 360, BOUNDS["east"] % 360
        longitude_indices = np.flatnonzero((longitudes >= west_360) & (longitudes <= east_360))
        if not len(latitude_indices) or not len(longitude_indices):
            raise ValueError("declared bridge box selects no OISST cells")
        cube = np.ma.asarray(dataset.variables["sst"][time_indices, latitude_indices[0] : latitude_indices[-1] + 1, longitude_indices[0] : longitude_indices[-1] + 1])
        if cube.shape != (6, len(latitude_indices), len(longitude_indices)):
            raise ValueError(f"unexpected OISST cube shape: {cube.shape}")
        if np.ma.getmaskarray(cube).any():
            raise ValueError("bridge box unexpectedly contains missing OISST cells")
        values = np.rint(np.asarray(cube, dtype=float) * 100).astype(int).tolist()
        variable = dataset.variables["sst"]

    rows = [[date.isoformat(), field] for date, field in zip((START + dt.timedelta(days=i) for i in range(6)), values)]
    extracted_sha256 = hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()
    payload = {
        "schema": "osw.oisst.mhw-bridge-source.v1",
        "status": "observational_analysis_surface_field_cube",
        "source": "NOAA/NCEI OISST v2.1 via NOAA PSL OPeNDAP mirror",
        "source_url": source_url,
        "request": {
            "variable": "sst",
            "time_indices": [int(index) for index in time_indices],
            "latitude_index_range_inclusive": [int(latitude_indices[0]), int(latitude_indices[-1])],
            "longitude_index_range_inclusive": [int(longitude_indices[0]), int(longitude_indices[-1])],
            "opendap_hyperslab": f"sst[{time_indices[0]}:1:{time_indices[-1]}][{latitude_indices[0]}:1:{latitude_indices[-1]}][{longitude_indices[0]}:1:{longitude_indices[-1]}]",
        },
        "doi": "https://doi.org/10.25921/RE9P-PT57",
        "retrieved_at": retrieved_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "window": {"start": START.isoformat(), "end": END.isoformat(), "day_count": 6},
        "variable": {"id": "sst", "long_name": getattr(variable, "long_name", "sea surface temperature"), "units": getattr(variable, "units", "degree_C")},
        "native_resolution_degrees": 0.25,
        "bounds_cell_centers": BOUNDS,
        "latitude_degrees_north": [round(float(latitudes[index]), 3) for index in latitude_indices],
        "longitude_degrees_east": [round(float(longitudes[index] - 360), 3) for index in longitude_indices],
        "value_encoding": "daily fields of integer hundredths degree C, ordered [latitude][longitude]",
        "rows": rows,
        "extracted_slice_sha256": extracted_sha256,
        "boundary": "Six daily objectively analyzed 0.25-degree surface-temperature fields over one fixed North Atlantic box. The checksum covers extracted date/value content, not DAP transport bytes. OISST is a separate analysis from the 0.05-degree CoralTemp-derived threshold object, but the products may share observing inputs. OISST does not provide surface flux, currents, mixed-layer depth, heat content, or causal attribution.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--retrieved-at")
    parser.add_argument("--source-url", default=SOURCE_URL)
    args = parser.parse_args()
    payload = build(args.output, args.retrieved_at, args.source_url)
    print(f"wrote {args.output} ({len(payload['latitude_degrees_north'])} x {len(payload['longitude_degrees_east'])} x 6)")
    print(f"extracted sha256 {payload['extracted_slice_sha256']}")


if __name__ == "__main__":
    main()
