"""Explicitly pin one NOAA LSA daily geostrophic-current source subset."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import netCDF4
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
URL = ("https://coastwatch.noaa.gov/data/pub0015/coastwatch/rads/sla/2026/"
       "rads_global_nrt_sla_20260925_20260926_001.nc")
EXPECTED_SHA256 = "53b1c541d4edf529bba2358f255890e2f0c392ef8e57208d04882c732c99f12f"
PRODUCT_PAGE = ("https://coastwatch.noaa.gov/cwn/products/"
                "sea-level-anomaly-and-geostrophic-currents-multi-mission-global-optimal-interpolation.html")
OUTPUT = ROOT / "research" / "noaa-lsa-geostrophic-gulf-stream-20260925.json"


def fetch() -> dict:
    with urllib.request.urlopen(URL, timeout=45) as response:
        content = response.read()
    digest = hashlib.sha256(content).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError(f"Source bytes changed: {digest}; review before replacing the pinned receipt")
    dataset = netCDF4.Dataset("inmemory", memory=content)
    try:
        longitude = np.asarray(dataset.variables["longitude"][:], dtype=float)
        latitude = np.asarray(dataset.variables["latitude"][:], dtype=float)
        if len(longitude) != 1440 or len(latitude) != 720:
            raise ValueError("Unexpected LSA source grid")
        lon_indexes = np.where((longitude >= -80) & (longitude <= -45))[0]
        lat_indexes = np.where((latitude >= 30) & (latitude <= 45))[0]
        if len(lon_indexes) != 140 or len(lat_indexes) != 60:
            raise ValueError("Unexpected Gulf Stream source subset")
        bounds = np.asarray(dataset.variables["time_bnds"][:], dtype=float)
        time_var = dataset.variables["time"]
        start = netCDF4.num2date(bounds[0, 0], time_var.units, calendar=time_var.calendar)
        end = netCDF4.num2date(bounds[0, 1], time_var.units, calendar=time_var.calendar)
        if (start.year, start.month, start.day, end.year, end.month, end.day) != (2026, 9, 25, 2026, 9, 26):
            raise ValueError("Unexpected source time bounds")
        fields = {}
        for name in ("ugos", "vgos"):
            variable = dataset.variables[name]
            variable.set_auto_maskandscale(False)
            if variable.units != "m/s" or float(variable.scale_factor) != 0.0001:
                raise ValueError(f"Unexpected velocity units or scale: {name}")
            values = np.asarray(variable[0, lat_indexes[0]:lat_indexes[-1] + 1,
                                         lon_indexes[0]:lon_indexes[-1] + 1], dtype=np.int32)
            fields[name] = values.tolist()
        receipt = {
            "schema": "osw.almanac.noaa-lsa-geostrophic-subset.v1",
            "source_provider": "NOAA/NESDIS Laboratory for Satellite Altimetry via NOAA CoastWatch",
            "source_url": URL,
            "product_page": PRODUCT_PAGE,
            "source_response_sha256": digest,
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
            "source_product_status": dataset.getncattr("cw:product_status"),
            "source_algorithm": dataset.getncattr("cw:processing_algorithm"),
            "source_file_role": "Daily altimetry-derived absolute surface geostrophic velocity; no ageostrophic flow or depth structure",
            "source_time_start": "2026-09-25T00:00:00Z",
            "source_time_end_exclusive": "2026-09-26T00:00:00Z",
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
    OUTPUT.write_text(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    value = fetch()
    print(f"{OUTPUT}: {value['subset_shape']} {value['source_response_sha256']}")
