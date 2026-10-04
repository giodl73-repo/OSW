"""Pin NOAA LSA Gulf Stream velocity subsets for a small repeat-date audit.

Explicit fetch only. Normal release builds use previously pinned receipts offline.
"""

from __future__ import annotations

import hashlib
import json
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

import netCDF4
import numpy as np

from fetch_noaa_lsa_geostrophic_snapshot import PRODUCT_PAGE, ROOT


DATES = ("2026-09-18", "2026-09-24", "2026-09-26", "2026-09-27")
EXPECTED_SHA256 = {
    "2026-09-18": "c8edda3fc386e91864d72a1a6022db12b808b3383f9c280f436c2852ad4ecec0",
    "2026-09-24": "e01d9929facf1f82a7d8d7eaf857bc5fd62b405c86a0abad9f9c098593941fb6",
    "2026-09-26": "52f1722aac5e63ac7dd0428d5eae92b183652d109836e72cde8ab4e9f68a9a07",
    "2026-09-27": "b3ab4e6d75ca836a2719210791929d2c2afb26bc11dd4b81f8f969af4cbf3a68",
}
URL_ROOT = "https://coastwatch.noaa.gov/data/pub0015/coastwatch/rads/sla/2026/"


def receipt_path(date: str) -> Path:
    return ROOT / "research" / f"noaa-lsa-geostrophic-gulf-stream-{date.replace('-', '')}.json"


def fetch_date(date: str, *, initial_pin: bool = False) -> dict:
    following = (datetime.fromisoformat(date) + timedelta(days=1)).date().isoformat()
    if date not in EXPECTED_SHA256 and not initial_pin:
        raise ValueError("New dates require explicit initial pinning")
    url_root = f"https://coastwatch.noaa.gov/data/pub0015/coastwatch/rads/sla/{date[:4]}/"
    url = url_root + f"rads_global_nrt_sla_{date.replace('-', '')}_{following.replace('-', '')}_001.nc"
    with urllib.request.urlopen(url, timeout=90) as response:
        content = response.read()
    digest = hashlib.sha256(content).hexdigest()
    if date in EXPECTED_SHA256 and digest != EXPECTED_SHA256[date]:
        raise ValueError(f"NOAA source bytes changed for {date}: {digest}; review before replacing receipt")
    output = receipt_path(date)
    if output.exists():
        old = json.loads(output.read_text(encoding="utf-8"))
        if old["source_response_sha256"] != digest:
            raise ValueError(f"NOAA source bytes changed for {date}: {digest}; review before replacing receipt")
    dataset = netCDF4.Dataset("inmemory", memory=content)
    try:
        longitude = np.asarray(dataset.variables["longitude"][:], dtype=float)
        latitude = np.asarray(dataset.variables["latitude"][:], dtype=float)
        if len(longitude) != 1440 or len(latitude) != 720:
            raise ValueError(f"Unexpected NOAA grid on {date}")
        lon_indexes = np.where((longitude >= -80) & (longitude <= -45))[0]
        lat_indexes = np.where((latitude >= 30) & (latitude <= 45))[0]
        if len(lon_indexes) != 140 or len(lat_indexes) != 60:
            raise ValueError(f"Unexpected Gulf Stream subset on {date}")
        time_var = dataset.variables["time"]
        bounds = np.asarray(dataset.variables["time_bnds"][:], dtype=float)
        start = netCDF4.num2date(bounds[0, 0], time_var.units, calendar=time_var.calendar)
        end = netCDF4.num2date(bounds[0, 1], time_var.units, calendar=time_var.calendar)
        if (start.year, start.month, start.day) != tuple(map(int, date.split("-"))) or (end.year, end.month, end.day) != tuple(map(int, following.split("-"))):
            raise ValueError(f"Unexpected NOAA time bounds on {date}")
        fields = {}
        for name in ("ugos", "vgos"):
            variable = dataset.variables[name]
            variable.set_auto_maskandscale(False)
            if variable.units != "m/s" or float(variable.scale_factor) != 0.0001:
                raise ValueError(f"Unexpected NOAA velocity units or scale: {date} {name}")
            fields[name] = np.asarray(variable[0, lat_indexes[0]:lat_indexes[-1] + 1,
                                                       lon_indexes[0]:lon_indexes[-1] + 1], dtype=np.int32).tolist()
        receipt = {
            "schema": "osw.almanac.noaa-lsa-geostrophic-subset.v1",
            "source_provider": "NOAA/NESDIS Laboratory for Satellite Altimetry via NOAA CoastWatch",
            "source_url": url,
            "product_page": PRODUCT_PAGE,
            "source_response_sha256": digest,
            "retrieved_at_utc": old["retrieved_at_utc"] if output.exists() else datetime.now(timezone.utc).isoformat(),
            "source_product_status": dataset.getncattr("cw:product_status"),
            "source_algorithm": dataset.getncattr("cw:processing_algorithm"),
            "source_file_role": "Daily altimetry-derived absolute surface geostrophic velocity; no ageostrophic flow or depth structure",
            "source_time_start": f"{date}T00:00:00Z",
            "source_time_end_exclusive": f"{following}T00:00:00Z",
            "source_grid_shape": [720, 1440],
            "subset_bounds": {"south": 30, "north": 45, "west": -80, "east": -45},
            "subset_shape": [len(lat_indexes), len(lon_indexes)],
            "grid_origin_lon_lat": [float(longitude[lon_indexes[0]]), float(latitude[lat_indexes[0]])],
            "grid_step_degrees": [0.25, 0.25],
            "velocity_scale_m_s_per_raw_unit": 0.0001,
            "raw_fill_value": int(dataset.variables["ugos"]._FillValue),
            "velocity_fields_raw_int32": fields,
            "model_limit": "Altimetry-derived geostrophic surface analysis; a frozen-time streamline is not a particle trajectory or whole-current axis.",
            "attribution": "Altimetry data are provided by the NOAA Laboratory for Satellite Altimetry; acknowledge NOAA CoastWatch.",
        }
    finally:
        dataset.close()
    output.write_text(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    for sample_date in DATES:
        value = fetch_date(sample_date)
        print(sample_date, value["source_response_sha256"], value["subset_shape"])
