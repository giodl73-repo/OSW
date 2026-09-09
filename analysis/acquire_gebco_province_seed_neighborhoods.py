"""Acquire 8° × 8° GEBCO elevation/TID neighborhoods around OSW seeds.

Network operation: 33 × 33 samples at 0.25° spacing per approximate display
seed. Complete OPeNDAP ASCII responses are retained for offline derivation.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

from acquire_gebco_province_seed_depths import (
    BASE, TID_BASE, DOI, DDS_URL, TID_DDS_URL, fetch, grid_index, TID_DEFINITIONS,
)
from build_province_cartogram import PROVINCE_SEEDS


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research" / "gebco-2026-province-seed-neighborhoods-source.json"
STRIDE = 60
HALF_WIDTH = 16
SIZE = HALF_WIDTH * 2 + 1


def checksum(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def query_one(code: str, longitude: float, latitude: float) -> dict:
    center_lon = grid_index(longitude, -179.99791666666667, 86399)
    center_lat = grid_index(latitude, -89.99791666666667, 43199)
    lon_start, lon_end = center_lon - HALF_WIDTH * STRIDE, center_lon + HALF_WIDTH * STRIDE
    lat_start, lat_end = center_lat - HALF_WIDTH * STRIDE, center_lat + HALF_WIDTH * STRIDE
    if lon_start < 0 or lon_end > 86399 or lat_start < 0 or lat_end > 43199:
        raise ValueError(f"neighborhood crosses a grid seam for {code}")
    constraint = f"[{lat_start}:{STRIDE}:{lat_end}][{lon_start}:{STRIDE}:{lon_end}]"
    elevation_url = BASE + ".ascii?elevation" + constraint
    tid_url = TID_BASE + ".ascii?tid" + constraint
    elevation_raw, tid_raw = fetch(elevation_url), fetch(tid_url)
    return {
        "code": code,
        "seed_longitude": longitude,
        "seed_latitude": latitude,
        "center_lon_index": center_lon,
        "center_lat_index": center_lat,
        "elevation_url": elevation_url,
        "elevation_response_sha256": checksum(elevation_raw),
        "elevation_response_ascii": elevation_raw.decode("utf-8"),
        "tid_url": tid_url,
        "tid_response_sha256": checksum(tid_raw),
        "tid_response_ascii": tid_raw.decode("utf-8"),
    }


def acquire(output: Path = OUTPUT, workers: int = 8) -> dict:
    elevation_dds, tid_dds = fetch(DDS_URL), fetch(TID_DDS_URL)
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
        "schema": "osw-gebco-province-seed-neighborhood-source-v1",
        "acquired_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "title": "GEBCO_2026 elevation and Type Identifier grids",
            "provider": "GEBCO via CEDA OPeNDAP",
            "release": "GEBCO_2026",
            "doi": DOI,
            "elevation_base_url": BASE,
            "tid_base_url": TID_BASE,
            "elevation_dds_sha256": checksum(elevation_dds),
            "tid_dds_sha256": checksum(tid_dds),
            "tid_definitions": {str(key): value for key, value in TID_DEFINITIONS.items()},
            "license": "public domain with requested attribution and disclaimer",
        },
        "sampling": {
            "record_count": len(records),
            "shape": [SIZE, SIZE],
            "spacing_degrees": STRIDE / 240,
            "nominal_width_degrees": HALF_WIDTH * 2 * STRIDE / 240,
            "method": "regular geographic window centered on the nearest GEBCO pixel center to each approximate OSW display seed",
            "seed_status": "approximate display placement, not published Longhurst geometry or a province centroid",
            "map_geometry": "unweighted longitude/latitude sample grid; cells do not represent equal area",
        },
        "records": records,
        "boundary": "Each neighborhood is an 8° geographic sample window around an approximate display seed. Counts describe sampled grid points, not province area, province occupancy, or equal-area fractions.",
    }
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    return payload


if __name__ == "__main__":
    result = acquire()
    print(f"wrote {len(result['records'])} neighborhoods of {SIZE} × {SIZE} samples")
