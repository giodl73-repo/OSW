"""Fetch a native ORCA025 Drake mesh subset through public OPeNDAP.

The output preserves geometry inputs only.  It is not an ORAS5 state field,
face-thickness acceptance, section extraction, or transport calculation.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import pathlib

import netCDF4
import numpy as np


SOURCE_URL = "https://icdc.cen.uni-hamburg.de/thredds/dodsC/ftpthredds/EASYInit/oras5/ORCA025/mesh/mesh_mask.nc"
DEFAULT_BOUNDS = {"west": -80.0, "east": -45.0, "south": -70.0, "north": -50.0}
TWO_D = ("glamt", "gphit", "glamu", "gphiu", "glamv", "gphiv", "e2u", "e1v", "mbathy", "e3t_ps")
THREE_D = ("tmask", "umask", "vmask")
ONE_D = ("e3t_0",)


def normalize_longitude(values):
    return ((values + 180.0) % 360.0) - 180.0


def validate_bounds(bounds: dict) -> None:
    if not bounds["west"] < bounds["east"] or not bounds["south"] < bounds["north"]:
        raise ValueError("expected west < east and south < north")
    if not -180 <= bounds["west"] <= 180 or not -180 <= bounds["east"] <= 180:
        raise ValueError("longitude bounds must be in [-180, 180]")
    if not -90 <= bounds["south"] <= 90 or not -90 <= bounds["north"] <= 90:
        raise ValueError("latitude bounds must be in [-90, 90]")


def discover_index_box(longitude, latitude, bounds: dict, stride: int, padding: int = 2, native_shape=None) -> dict:
    validate_bounds(bounds)
    if stride < 1 or padding < 0:
        raise ValueError("stride must be positive and padding nonnegative")
    if longitude.shape != latitude.shape or len(longitude.shape) != 2:
        raise ValueError("longitude and latitude must be matching 2D arrays")
    lon = normalize_longitude(np.asanyarray(longitude))
    lat = np.asanyarray(latitude)
    valid = np.isfinite(lon) & np.isfinite(lat)
    inside = valid & (lon >= bounds["west"]) & (lon <= bounds["east"]) & (lat >= bounds["south"]) & (lat <= bounds["north"])
    rows, columns = np.where(inside)
    if not len(rows):
        raise ValueError("coarse coordinate sample contains no point inside target bounds")
    coarse_y, coarse_x = longitude.shape
    ny, nx = native_shape or (coarse_y * stride, coarse_x * stride)
    expansion = stride * padding
    return {
        "y_start": max(0, int(rows.min() * stride - expansion)),
        "y_stop_exclusive": min(ny, int(rows.max() * stride + stride + expansion)),
        "x_start": max(0, int(columns.min() * stride - expansion)),
        "x_stop_exclusive": min(nx, int(columns.max() * stride + stride + expansion)),
    }


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def strip_time(variable, y_slice=None, x_slice=None):
    dimensions = variable.dimensions
    selectors = []
    for dimension in dimensions:
        if dimension in ("t", "time_counter"):
            selectors.append(0)
        elif dimension == "y":
            selectors.append(y_slice)
        elif dimension == "x":
            selectors.append(x_slice)
        else:
            selectors.append(slice(None))
    return np.asanyarray(variable[tuple(selectors)])


def fetch_subset(source_url: str, output: pathlib.Path, receipt: pathlib.Path, bounds: dict, stride: int, retrieved_at: str, context: str = "drake") -> dict:
    with netCDF4.Dataset(source_url) as source:
        missing = [name for name in (*TWO_D, *THREE_D, *ONE_D) if name not in source.variables]
        if missing:
            raise ValueError(f"source mesh is missing required variables: {', '.join(missing)}")
        full_y = len(source.dimensions["y"]); full_x = len(source.dimensions["x"])
        sampled_lon = strip_time(source.variables["glamt"], slice(0, full_y, stride), slice(0, full_x, stride))
        sampled_lat = strip_time(source.variables["gphit"], slice(0, full_y, stride), slice(0, full_x, stride))
        box = discover_index_box(sampled_lon, sampled_lat, bounds, stride, native_shape=(full_y, full_x))
        ys = slice(box["y_start"], box["y_stop_exclusive"])
        xs = slice(box["x_start"], box["x_stop_exclusive"])
        arrays = {name: strip_time(source.variables[name], ys, xs) for name in TWO_D}
        arrays.update({name: strip_time(source.variables[name], ys, xs) for name in THREE_D})
        arrays.update({name: strip_time(source.variables[name]) for name in ONE_D})
        units = {name: getattr(source.variables[name], "units", None) for name in arrays}

    ny, nx = arrays["glamt"].shape; nz = arrays["e3t_0"].shape[0]
    if any(arrays[name].shape != (nz, ny, nx) for name in THREE_D):
        raise ValueError("unexpected T/U/V mask dimensions after time-axis removal")
    output.parent.mkdir(parents=True, exist_ok=True)
    with netCDF4.Dataset(output, "w", format="NETCDF4") as target:
        target.createDimension("z", nz); target.createDimension("y", ny); target.createDimension("x", nx)
        target.setncattr("source_url", source_url)
        target.setncattr("boundary", "Native mesh subset only; no state, accepted face thickness, section, or transport.")
        for name in ONE_D:
            variable = target.createVariable(name, arrays[name].dtype, ("z",), zlib=True)
            variable[:] = arrays[name]
            if units[name]: variable.units = units[name]
        for name in TWO_D:
            variable = target.createVariable(name, arrays[name].dtype, ("y", "x"), zlib=True)
            variable[:] = arrays[name]
            if units[name]: variable.units = units[name]
        for name in THREE_D:
            variable = target.createVariable(name, arrays[name].dtype, ("z", "y", "x"), zlib=True)
            variable[:] = arrays[name]

    lon = normalize_longitude(np.asanyarray(arrays["glamt"], dtype=float))
    lat = np.asanyarray(arrays["gphit"], dtype=float)
    result = {
        "schema": f"oceanlines.oras5.{context}-mesh-subset.v1",
        "status": "native_mesh_subset_not_yet_accepted_for_transport",
        "source_url": source_url,
        "retrieved_at": retrieved_at,
        "target_bounds_deg": bounds,
        "coarse_discovery_stride": stride,
        "native_index_box": box,
        "shape": [nz, ny, nx],
        "coordinate_extent_deg": {
            "west": float(np.nanmin(lon)), "east": float(np.nanmax(lon)),
            "south": float(np.nanmin(lat)), "north": float(np.nanmax(lat)),
        },
        "variables": {name: {"shape": list(arrays[name].shape), "units": units[name]} for name in arrays},
        "output": {"path": str(output), "bytes": output.stat().st_size, "sha256": sha256_file(output)},
        "next_test": "reconstruct interior U/V thickness and audit mask/depth/face-area conservation",
        "boundary": (
            "Public native-grid mesh subset only. It contains no ORAS5 temperature or velocity, "
            "does not validate the face-thickness reconstruction, and cannot produce transport."
        ),
    }
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-url", default=SOURCE_URL)
    parser.add_argument("--west", type=float, default=DEFAULT_BOUNDS["west"])
    parser.add_argument("--east", type=float, default=DEFAULT_BOUNDS["east"])
    parser.add_argument("--south", type=float, default=DEFAULT_BOUNDS["south"])
    parser.add_argument("--north", type=float, default=DEFAULT_BOUNDS["north"])
    parser.add_argument("--discovery-stride", type=int, default=8)
    parser.add_argument("--retrieved-at")
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-drake-mesh.nc"))
    parser.add_argument("--receipt", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-drake-mesh.json"))
    parser.add_argument("--context", default="drake", choices=("drake", "arctic-entrances", "nordic-seas"))
    args = parser.parse_args()
    bounds = {"west": args.west, "east": args.east, "south": args.south, "north": args.north}
    retrieved_at = args.retrieved_at or dt.datetime.now(dt.timezone.utc).isoformat()
    result = fetch_subset(args.source_url, args.output, args.receipt, bounds, args.discovery_stride, retrieved_at, args.context)
    print(f"wrote {args.output} and {args.receipt}: {result['shape']}")


if __name__ == "__main__":
    main()
