"""Acquire one GEBCO 2026 grid cell at each approximate OSW province seed.

This is an explicit network operation. It preserves the complete ASCII OPeNDAP
response for each request so the committed derived table can be rebuilt offline.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import urllib.request

from build_province_cartogram import PROVINCE_SEEDS


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research" / "gebco-2026-province-seed-depths-source.json"
BASE = "https://dap.ceda.ac.uk/thredds/dodsC/bodc/gebco/global/gebco_2026/ice_surface_elevation/netcdf/GEBCO_2026.nc"
DDS_URL = BASE + ".dds"
TID_BASE = "https://dap.ceda.ac.uk/thredds/dodsC/bodc/gebco/global/gebco_2026/type_identifier_grid/netcdf/gebco_2026_tid.nc"
TID_DDS_URL = TID_BASE + ".dds"
ORIGIN_LON = -179.99791666666667
ORIGIN_LAT = -89.99791666666667
STEP = 1 / 240
DOI = "10.5285/4f68d5c7-45eb-f999-e063-7086abc036fa"
TID_DEFINITIONS = {
    0: "land",
    10: "singlebeam direct measurement", 11: "multibeam direct measurement",
    12: "seismic direct measurement", 13: "isolated sounding",
    14: "ENC sounding", 15: "bathymetric lidar", 16: "optical light sensor",
    17: "combination of direct measurement methods",
    40: "satellite-gravity-guided prediction", 41: "computer-algorithm interpolation",
    42: "digital chart bathymetric contour", 43: "ENC bathymetric contour",
    44: "sounding-constrained grid with satellite-gravity guidance",
    45: "flight-gravity-derived prediction", 46: "grounded-iceberg-draft estimate",
    70: "pre-generated mixed-source grid", 71: "unknown source", 72: "steering point",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def grid_index(value: float, origin: float, maximum: int) -> int:
    """Nearest pixel-center index; exact half-cell ties go north/east."""
    return max(0, min(maximum, math.floor((value - origin) / STEP + 0.5)))


def fetch(url: str, timeout: int = 60) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "OSW/1.0 research acquisition"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def query_one(code: str, longitude: float, latitude: float) -> dict:
    lon_index = grid_index(longitude, ORIGIN_LON, 86399)
    lat_index = grid_index(latitude, ORIGIN_LAT, 43199)
    url = BASE + f".ascii?elevation[{lat_index}:1:{lat_index}][{lon_index}:1:{lon_index}]"
    tid_url = TID_BASE + f".ascii?tid[{lat_index}:1:{lat_index}][{lon_index}:1:{lon_index}]"
    raw = fetch(url)
    tid_raw = fetch(tid_url)
    text = raw.decode("utf-8")
    tid_text = tid_raw.decode("utf-8")
    elevation = re.search(r"^\[0\],\s*(-?\d+)\s*$", text, flags=re.MULTILINE)
    sampled_lat = re.search(r"^elevation\.lat\[1\]\s*\n([^\n]+)", text, flags=re.MULTILINE)
    sampled_lon = re.search(r"^elevation\.lon\[1\]\s*\n([^\n]+)", text, flags=re.MULTILINE)
    if not (elevation and sampled_lat and sampled_lon):
        raise ValueError(f"unrecognized GEBCO response for {code}")
    tid = re.search(r"^\[0\],\s*(\d+)\s*$", tid_text, flags=re.MULTILINE)
    tid_lat = re.search(r"^tid\.lat\[1\]\s*\n([^\n]+)", tid_text, flags=re.MULTILINE)
    tid_lon = re.search(r"^tid\.lon\[1\]\s*\n([^\n]+)", tid_text, flags=re.MULTILINE)
    if not tid or not tid_lat or not tid_lon or int(tid.group(1)) not in TID_DEFINITIONS:
        raise ValueError(f"unrecognized GEBCO TID response for {code}")
    if float(tid_lat.group(1)) != float(sampled_lat.group(1)) or float(tid_lon.group(1)) != float(sampled_lon.group(1)):
        raise ValueError(f"GEBCO elevation/TID coordinates disagree for {code}")
    return {
        "code": code,
        "seed_longitude": longitude,
        "seed_latitude": latitude,
        "lon_index": lon_index,
        "lat_index": lat_index,
        "sampled_longitude": float(sampled_lon.group(1)),
        "sampled_latitude": float(sampled_lat.group(1)),
        "elevation_m": int(elevation.group(1)),
        "query_url": url,
        "response_sha256": sha256(raw),
        "response_ascii": text,
        "tid_code": int(tid.group(1)),
        "tid_definition": TID_DEFINITIONS[int(tid.group(1))],
        "tid_sampled_longitude": float(tid_lon.group(1)),
        "tid_sampled_latitude": float(tid_lat.group(1)),
        "tid_query_url": tid_url,
        "tid_response_sha256": sha256(tid_raw),
        "tid_response_ascii": tid_text,
    }


def acquire(output: Path = OUTPUT, workers: int = 8) -> dict:
    dds = fetch(DDS_URL)
    tid_dds = fetch(TID_DDS_URL)
    records = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(query_one, code, lon, lat): code
            for code, (lon, lat) in sorted(PROVINCE_SEEDS.items())
        }
        for future in as_completed(futures):
            records.append(future.result())
    records.sort(key=lambda item: item["code"])
    payload = {
        "schema": "osw-gebco-province-seed-source-v1",
        "acquired_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "title": "GEBCO_2026 Grid, ice-surface-elevation version",
            "provider": "GEBCO via CEDA OPeNDAP",
            "release": "GEBCO_2026",
            "doi": DOI,
            "base_url": BASE,
            "dds_url": DDS_URL,
            "dds_sha256": sha256(dds),
            "tid_base_url": TID_BASE,
            "tid_dds_url": TID_DDS_URL,
            "tid_dds_sha256": sha256(tid_dds),
            "tid_code_reference": "https://www.gebco.net/gebco-tid-grid",
            "grid": "15 arc-second pixel-center registered geographic latitude/longitude",
            "horizontal_reference": "WGS84 assumption stated by GEBCO",
            "vertical_reference": "heterogeneous source elevations treated by GEBCO as mean sea level; shallow-water exceptions may exist",
            "units": "m elevation; negative below nominal mean sea level",
            "license": "public domain with requested attribution and disclaimer",
        },
        "sampling": {
            "method": "nearest GEBCO pixel center to each approximate OSW display seed",
            "tie_rule": "exact half-cell ties select the north/east center",
            "seed_source": "analysis/build_province_cartogram.py PROVINCE_SEEDS",
            "seed_status": "approximate display placement, not published Longhurst geometry or a province centroid",
            "record_count": len(records),
        },
        "records": records,
        "boundary": "Each value describes one GEBCO grid cell nearest an approximate display seed. It is not a province mean, range, profile, occupancy fraction, navigational sounding, or statement about the whole province.",
    }
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    result = acquire(args.output, args.workers)
    wet = sum(record["elevation_m"] < 0 for record in result["records"])
    print(f"wrote {len(result['records'])} GEBCO seed cells ({wet} wet, {len(result['records']) - wet} non-wet)")


if __name__ == "__main__":
    main()
