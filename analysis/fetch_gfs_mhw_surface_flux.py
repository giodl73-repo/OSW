"""Extract daily GFS surface heat-flux components over the D11 Atlantic box."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import time
import urllib.request
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BUCKET = "https://noaa-gfs-bdp-pds.s3.amazonaws.com"
OUTPUT = ROOT / "atlas" / "data" / "gfs-mhw-surface-flux-north-atlantic-20260807-20260812.json"
START = dt.date(2026, 8, 7)
END = dt.date(2026, 8, 12)  # exclusive forcing endpoint; last interval ends here
BOUNDS = {"south": 39.5, "north": 43.5, "west": -52.0, "east": -47.0}
FORECAST_HOURS = (6, 12, 18, 24)
FIELDS = {
    "latent_heat_flux_upward_w_m2_centi": "LHTFL",
    "sensible_heat_flux_upward_w_m2_centi": "SHTFL",
    "shortwave_downward_w_m2_centi": "DSWRF",
    "longwave_downward_w_m2_centi": "DLWRF",
    "shortwave_upward_w_m2_centi": "USWRF",
    "longwave_upward_w_m2_centi": "ULWRF",
}


def _eccodes():
    try:
        import eccodes
    except ImportError as error:
        raise RuntimeError(
            "GFS GRIB extraction requires eccodes from requirements-observations.txt "
            "and a Python version for which its native wheel is available"
        ) from error
    return eccodes


def source_url(date: dt.date, forecast_hour: int) -> str:
    filename = f"gfs.t00z.sfluxgrbf{forecast_hour:03d}.grib2"
    return f"{BUCKET}/gfs.{date:%Y%m%d}/00/atmos/{filename}"


def request_bytes(url: str, byte_range: tuple[int, int] | None = None):
    headers = {"User-Agent": "OSW evidence receipt/1.0"}
    if byte_range:
        headers["Range"] = f"bytes={byte_range[0]}-{byte_range[1]}"
    for attempt in range(3):
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return response.read(), response.headers
        except OSError:
            if attempt == 2:
                raise
            time.sleep((2, 5)[attempt])


def parse_index(text: str, content_length: int) -> list[dict]:
    lines = text.splitlines()
    parsed = []
    for index, line in enumerate(lines):
        parts = line.split(":")
        offset = int(parts[1])
        end = int(lines[index + 1].split(":")[1]) - 1 if index + 1 < len(lines) else content_length - 1
        parsed.append({"line": line, "offset": offset, "end": end, "variable": parts[3], "level": parts[4], "forecast_time": parts[5]})
    return parsed


def averaged_surface_entry(entries: list[dict], variable: str, forecast_hour: int) -> dict:
    expected = f"{forecast_hour - 6}-{forecast_hour} hour ave fcst"
    matches = [entry for entry in entries if entry["variable"] == variable and entry["level"] == "surface" and entry["forecast_time"] == expected]
    if len(matches) != 1:
        raise ValueError(f"expected one {variable} surface {expected} entry, found {len(matches)}")
    return matches[0]


def decode_message(data: bytes) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    eccodes = _eccodes()
    message = eccodes.codes_new_from_message(data)
    if message is None:
        raise ValueError("ecCodes found no GRIB message in selected byte range")
    try:
        height = int(eccodes.codes_get(message, "Nj"))
        width = int(eccodes.codes_get(message, "Ni"))
        latitude = np.asarray(eccodes.codes_get_array(message, "latitudes"), dtype=float).reshape(height, width)
        longitude = np.asarray(eccodes.codes_get_array(message, "longitudes"), dtype=float).reshape(height, width)
        values = np.asarray(eccodes.codes_get_array(message, "values"), dtype=float).reshape(height, width)
        metadata = {
            "grid_type": eccodes.codes_get(message, "gridType"),
            "ni": width,
            "nj": height,
            "short_name": eccodes.codes_get(message, "shortName"),
            "name": eccodes.codes_get(message, "name"),
            "units": eccodes.codes_get(message, "units"),
            "step_range": str(eccodes.codes_get(message, "stepRange")),
            "type_of_statistical_processing": int(eccodes.codes_get(message, "typeOfStatisticalProcessing")),
        }
    finally:
        eccodes.codes_release(message)
    return latitude, longitude, values, metadata


def subset(latitude: np.ndarray, longitude: np.ndarray, values: np.ndarray):
    signed_longitude = (longitude + 180) % 360 - 180
    selected = ((latitude >= BOUNDS["south"]) & (latitude <= BOUNDS["north"]) &
                (signed_longitude >= BOUNDS["west"]) & (signed_longitude <= BOUNDS["east"]))
    y, x = np.where(selected)
    y_slice = slice(int(y.min()), int(y.max()) + 1)
    x_slice = slice(int(x.min()), int(x.max()) + 1)
    local_mask = selected[y_slice, x_slice]
    if not local_mask.all():
        raise ValueError("GFS bounding-box subset is not rectangular")
    local_latitude = latitude[y_slice, x_slice]
    local_longitude = signed_longitude[y_slice, x_slice]
    return local_latitude, local_longitude, values[y_slice, x_slice]


def encode(values: np.ndarray) -> list[list[int]]:
    return np.rint(values * 100).astype(int).tolist()


def build(output: Path = OUTPUT, retrieved_at: str | None = None) -> dict:
    dates = [START + dt.timedelta(days=offset) for offset in range((END - START).days)]
    rows, files, grid = [], [], None
    for date in dates:
        print(f"extracting NOAA GFS surface flux {date}", flush=True)
        interval_fields = {key: [] for key in FIELDS}
        interval_files = []
        for forecast_hour in FORECAST_HOURS:
            url = source_url(date, forecast_hour)
            index_data, index_headers = request_bytes(url + ".idx")
            content_length = int(index_headers.get("x-amz-meta-size", 0) or 0)
            if not content_length:
                head = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "OSW evidence receipt/1.0"})
                with urllib.request.urlopen(head, timeout=60) as response:
                    content_length = int(response.headers["Content-Length"])
                    remote_headers = dict(response.headers.items())
            else:
                remote_headers = dict(index_headers.items())
            entries = parse_index(index_data.decode("utf-8"), content_length)
            message_receipts = []
            reference_grid = None
            for output_key, variable in FIELDS.items():
                entry = averaged_surface_entry(entries, variable, forecast_hour)
                raw, _ = request_bytes(url, (entry["offset"], entry["end"]))
                latitude, longitude, values, metadata = decode_message(raw)
                local_latitude, local_longitude, local_values = subset(latitude, longitude, values)
                if reference_grid is None:
                    reference_grid = (local_latitude, local_longitude)
                elif not (np.allclose(local_latitude, reference_grid[0]) and np.allclose(local_longitude, reference_grid[1])):
                    raise ValueError("GFS component grids differ within one forecast file")
                interval_fields[output_key].append(local_values)
                message_receipts.append({
                    "variable": variable,
                    "index_line": entry["line"],
                    "byte_range_inclusive": [entry["offset"], entry["end"]],
                    "message_sha256": hashlib.sha256(raw).hexdigest(),
                    "metadata": metadata,
                })
            if grid is None:
                grid = {
                    "shape": list(reference_grid[0].shape),
                    "latitude_degrees_north_e6": np.rint(reference_grid[0] * 1_000_000).astype(int).tolist(),
                    "longitude_degrees_east_e6": np.rint(reference_grid[1] * 1_000_000).astype(int).tolist(),
                }
            elif not (np.allclose(np.asarray(grid["latitude_degrees_north_e6"]) / 1_000_000, reference_grid[0], atol=1e-6) and
                      np.allclose(np.asarray(grid["longitude_degrees_east_e6"]) / 1_000_000, reference_grid[1], atol=1e-6)):
                raise ValueError("GFS subset grid changed across forecast files")
            interval_files.append({
                "forecast_hour": forecast_hour,
                "url": url,
                "content_length_bytes": content_length,
                "etag": remote_headers.get("ETag", "").strip('"'),
                "last_modified": remote_headers.get("Last-Modified"),
                "index_sha256": hashlib.sha256(index_data).hexdigest(),
                "messages": message_receipts,
            })
        row = {"start": date.isoformat(), "end": (date + dt.timedelta(days=1)).isoformat()}
        for key, chunks in interval_fields.items():
            row[key] = encode(np.mean(np.stack(chunks), axis=0))
        rows.append(row)
        files.append({"cycle_date": date.isoformat(), "cycle_hour_utc": 0, "forecast_files": interval_files})
    digest = hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()
    payload = {
        "schema": "osw.gfs.mhw-surface-flux-source.v1",
        "status": "forecast_derived_atmospheric_surface_flux_screen",
        "source": "NOAA Global Forecast System native Gaussian-grid surface-flux product",
        "product_page": "https://registry.opendata.aws/noaa-gfs-bdp-pds/",
        "retrieved_at": retrieved_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "window": {"start": START.isoformat(), "end": END.isoformat(), "interval_count": len(rows), "support": "five consecutive 00:00-00:00 UTC intervals"},
        "bounds": BOUNDS,
        "grid": grid,
        "variables": {key: {"source_id": source_id, "source_units": "W m-2", "scale": 100, "positive_direction": "upward" if "upward" in key else "downward"} for key, source_id in FIELDS.items()},
        "daily_aggregation": "arithmetic mean of four non-overlapping six-hour GFS averages: 0-6, 6-12, 12-18, and 18-24 hours from each 00 UTC cycle",
        "files": files,
        "rows": rows,
        "extracted_rows_sha256": digest,
        "boundary": "GFS is an operational forecast system, not an atmospheric reanalysis or an observed ocean heat budget. The six fields reconstruct a forecast-derived net downward surface flux. Combining this forcing with RTOFS mixed-layer thickness crosses model systems and supports an energetic plausibility screen only; it does not close either model's native heat budget or isolate causality.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--retrieved-at")
    parser.add_argument("--refresh-metadata-only", action="store_true", help="update descriptive metadata in an existing extracted artifact")
    args = parser.parse_args()
    if args.refresh_metadata_only:
        payload = json.loads(args.output.read_text(encoding="utf-8"))
        payload["source"] = "NOAA Global Forecast System native Gaussian-grid surface-flux product"
        args.output.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
        print(f"refreshed metadata in {args.output}")
        return
    payload = build(args.output, args.retrieved_at)
    print(f"wrote {args.output} ({payload['grid']['shape']} x {len(payload['rows'])} intervals)")
    print(f"extracted sha256 {payload['extracted_rows_sha256']}")


if __name__ == "__main__":
    main()
