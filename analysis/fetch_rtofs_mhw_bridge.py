"""Extract compact surface RTOFS fields around the D10 North Atlantic box."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import urllib.request
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BUCKET = "https://noaa-nws-rtofs-pds.s3.amazonaws.com"
OUTPUT = ROOT / "atlas" / "data" / "rtofs-mhw-bridge-north-atlantic-20260807-20260812.json"
START = dt.date(2026, 8, 7)
END = dt.date(2026, 8, 12)
BOUNDS = {"south": 39.5, "north": 43.5, "west": -52.0, "east": -47.0}
THREE_D = "rtofs_glo_3dz_n024_6hrly_hvr_US_east.nc"
TWO_D = "rtofs_glo_2ds_n024_diag.nc"


def source_url(date: dt.date, filename: str) -> str:
    return f"{BUCKET}/rtofs.{date:%Y%m%d}/{filename}"


def remote_identity(url: str) -> dict:
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "OSW evidence receipt/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return {
            "url": url,
            "content_length_bytes": int(response.headers["Content-Length"]),
            "etag": response.headers.get("ETag", "").strip('"'),
            "last_modified": response.headers.get("Last-Modified"),
        }


def _dependencies():
    try:
        import fsspec
        import h5netcdf
    except ImportError as error:
        raise RuntimeError("RTOFS range extraction requires requirements-observations.txt") from error
    return fsspec, h5netcdf


def _open(url: str):
    fsspec, h5netcdf = _dependencies()
    handle = fsspec.open(url, "rb", block_size=5 * 1024 * 1024, cache_type="blockcache").open()
    return handle, h5netcdf.File(handle, "r")


def _signed_longitude(values):
    values = np.asarray(values, dtype=float)
    return np.where(values > 180, values - 360, values)


def _window(dataset, expected_shape: tuple[int, int]):
    latitudes = np.asarray(dataset["Latitude"][:], dtype=float)
    longitudes = _signed_longitude(dataset["Longitude"][:])
    selected = ((latitudes >= BOUNDS["south"]) & (latitudes <= BOUNDS["north"]) &
                (longitudes >= BOUNDS["west"]) & (longitudes <= BOUNDS["east"]))
    y, x = np.where(selected)
    if len(y) != 4221:
        raise ValueError(f"expected 4,221 RTOFS cells in box, found {len(y)}")
    slices = (slice(int(y.min()), int(y.max()) + 1), slice(int(x.min()), int(x.max()) + 1))
    local_mask = selected[slices]
    if local_mask.shape != expected_shape:
        raise ValueError(f"unexpected rectangular window: {local_mask.shape}")
    return latitudes[slices], longitudes[slices], local_mask, slices


def _encode(values, scale: int, mask: np.ndarray) -> list:
    values = np.ma.asarray(values)
    invalid = np.ma.getmaskarray(values) | ~np.isfinite(np.asarray(values.filled(np.nan), dtype=float)) | ~mask
    encoded = np.rint(np.asarray(values.filled(np.nan), dtype=float) * scale)
    return [[None if invalid[y, x] else int(encoded[y, x]) for x in range(encoded.shape[1])] for y in range(encoded.shape[0])]


def build(output: Path = OUTPUT, retrieved_at: str | None = None) -> dict:
    dates = [START + dt.timedelta(days=offset) for offset in range((END - START).days + 1)]
    rows, files = [], []
    grid = None
    for date in dates:
        print(f"extracting NOAA RTOFS {date}", flush=True)
        url_3d, url_2d = source_url(date, THREE_D), source_url(date, TWO_D)
        identity_3d, identity_2d = remote_identity(url_3d), remote_identity(url_2d)
        handle_3d, dataset_3d = _open(url_3d)
        try:
            latitudes, longitudes, mask, slices_3d = _window(dataset_3d, (67, 63))
            if round(float(dataset_3d["Date"][0])) != int(date.strftime("%Y%m%d")):
                raise ValueError("RTOFS 3-D valid date does not match key date")
            if float(dataset_3d["Depth"][0]) != 0.0:
                raise ValueError("first RTOFS standard depth is not the surface")
            temperature = dataset_3d["temperature"][0, 0, slices_3d[0], slices_3d[1]]
            eastward = dataset_3d["u"][0, 0, slices_3d[0], slices_3d[1]]
            northward = dataset_3d["v"][0, 0, slices_3d[0], slices_3d[1]]
        finally:
            dataset_3d.close(); handle_3d.close()
        handle_2d, dataset_2d = _open(url_2d)
        try:
            latitudes_2d, longitudes_2d, mask_2d, slices_2d = _window(dataset_2d, (67, 63))
            if not (np.allclose(latitudes, latitudes_2d) and np.allclose(longitudes, longitudes_2d) and np.array_equal(mask, mask_2d)):
                raise ValueError("RTOFS 2-D and 3-D subset grids differ")
            if round(float(dataset_2d["Date"][0])) != int(date.strftime("%Y%m%d")):
                raise ValueError("RTOFS 2-D valid date does not match key date")
            mixed_layer = dataset_2d["mixed_layer_thickness"][0, slices_2d[0], slices_2d[1]]
        finally:
            dataset_2d.close(); handle_2d.close()
        if grid is None:
            grid = {
                "shape": [67, 63],
                "valid_box_cells": int(mask.sum()),
                "latitude_degrees_north_e6": np.rint(latitudes * 1_000_000).astype(int).tolist(),
                "longitude_degrees_east_e6": np.rint(longitudes * 1_000_000).astype(int).tolist(),
                "inside_declared_box": mask.astype(int).tolist(),
            }
        rows.append({
            "date": date.isoformat(),
            "temperature_c_milli": _encode(temperature, 1000, mask),
            "eastward_velocity_m_s_e4": _encode(eastward, 10_000, mask),
            "northward_velocity_m_s_e4": _encode(northward, 10_000, mask),
            "mixed_layer_thickness_m_centi": _encode(mixed_layer, 100, mask),
        })
        files.append({"date": date.isoformat(), "three_dimensional": identity_3d, "two_dimensional": identity_2d})
    digest = hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()
    payload = {
        "schema": "osw.rtofs.mhw-bridge-source.v1",
        "status": "assimilative_ocean_analysis_surface_field_cube",
        "source": "NOAA Global Real-Time Ocean Forecast System (RTOFS), HYCOM 93.1",
        "product_page": "https://registry.opendata.aws/noaa-rtofs/",
        "retrieved_at": retrieved_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "window": {"start": START.isoformat(), "end": END.isoformat(), "day_count": len(rows), "valid_time": "00:00 UTC daily", "source_field": "n024 nowcast"},
        "bounds": BOUNDS,
        "grid": grid,
        "variables": {
            "temperature_c_milli": {"source_id": "temperature", "source_units": "degC", "depth_m": 0.0, "scale": 1000},
            "eastward_velocity_m_s_e4": {"source_id": "u", "source_units": "m/s", "depth_m": 0.0, "scale": 10000},
            "northward_velocity_m_s_e4": {"source_id": "v", "source_units": "m/s", "depth_m": 0.0, "scale": 10000},
            "mixed_layer_thickness_m_centi": {"source_id": "mixed_layer_thickness", "source_units": "m", "scale": 100},
        },
        "files": files,
        "rows": rows,
        "extracted_rows_sha256": digest,
        "boundary": "Six 00 UTC surface snapshots from one assimilative operational ocean model. HTTP ETags identify the remote NetCDF objects and the SHA-256 identifies extracted values; range reads do not preserve raw source bytes locally. Surface velocity times a surface-temperature gradient is an Eulerian horizontal-advection diagnostic, not material parcel tracking, full mixed-layer heat transport, model-native tracer tendency, or causal attribution. Mixed-layer thickness is diagnostic and does not close entrainment, vertical advection, diffusion, assimilation increments, or surface forcing.",
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
    print(f"wrote {args.output} ({payload['grid']['valid_box_cells']} cells x {len(payload['rows'])} days)")
    print(f"extracted sha256 {payload['extracted_rows_sha256']}")


if __name__ == "__main__":
    main()
