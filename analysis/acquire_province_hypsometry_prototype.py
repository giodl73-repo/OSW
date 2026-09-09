"""Acquire the representative continuous province-hypsometry prototype.

This explicit network step reuses the declared Version 4 and GEBCO 2026
0.25-degree sources. Provider bytes remain uncommitted; compact curves,
sensitivity summaries, and source receipts are committed for offline use.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from http.client import IncompleteRead
import json
import math
from pathlib import Path
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

import numpy as np
from shapely import contains_xy

from acquire_longhurst_2007_adjacency import load_geometries, normalized_geometry_sha256
from acquire_longhurst_2007_gebco_depths import (
    COLUMNS,
    ELEVATION_URL,
    GEBCO_DOI,
    GEOMETRY_URL,
    ROWS,
    cell_area_by_row,
    parse_ascii_grid,
)


ROOT = Path(__file__).resolve().parents[1]
FOOTPRINTS = ROOT / "research" / "longhurst-2007-gebco-2026-depths.json"
ADJACENCY = ROOT / "research" / "longhurst-2007-province-adjacency.json"
OUTPUT = ROOT / "research" / "longhurst-2007-province-continuous-hypsometry-prototype.json"
RECEIPT = ROOT / "research" / "longhurst-2007-province-continuous-hypsometry-source-receipt.json"
BROWSER = ROOT / "column" / "province-hypsometry.js"
PERCENTILES = tuple(range(101))
ARCHETYPES = {
    "SUND": "shelf-led representative",
    "NADR": "deep-floor-led representative",
    "SPSG": "abyssal-floor-led representative",
    "ANTA": "polar representative",
    "NPPF": "antimeridian-crossing representative",
    "NECS": "small/coastal and repaired-geometry representative",
}


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch(url: str) -> tuple[bytes, dict[str, str | None]]:
    failures = []
    for attempt in range(1, 4):
        request = Request(url, headers={"User-Agent": "OSW/1.0 scientific-data-acquisition"})
        try:
            with urlopen(request, timeout=240) as response:
                raw = response.read()
                headers = {
                    "content_type": response.headers.get("Content-Type"),
                    "etag": response.headers.get("ETag"),
                    "last_modified": response.headers.get("Last-Modified"),
                }
            return raw, headers
        except (IncompleteRead, TimeoutError, URLError) as error:
            failures.append(f"attempt {attempt}: {type(error).__name__}: {error}")
            if attempt < 3:
                time.sleep(attempt)
    raise RuntimeError("source acquisition failed after 3 attempts: " + " | ".join(failures))


def weighted_quantiles(values: np.ndarray, weights: np.ndarray, percentiles=PERCENTILES) -> list[float]:
    if values.size == 0 or values.size != weights.size or np.any(weights <= 0):
        raise ValueError("weighted quantiles require non-empty values and positive matching weights")
    order = np.argsort(values, kind="stable")
    ordered_values = values[order].astype(np.float64)
    ordered_weights = weights[order].astype(np.float64)
    centers = np.cumsum(ordered_weights) - ordered_weights / 2
    targets = np.asarray(percentiles, dtype=np.float64) / 100 * ordered_weights.sum()
    return np.interp(targets, centers, ordered_values, left=ordered_values[0], right=ordered_values[-1]).tolist()


def summarize(depths: np.ndarray, weights: np.ndarray) -> dict:
    total_area = float(weights.sum())
    mean_depth = float(np.sum(depths * weights) / total_area)
    quantiles = weighted_quantiles(depths, weights)
    return {
        "wet_sample_count": int(depths.size),
        "sampled_wet_area_km2": round(total_area / 1_000_000, 2),
        "area_weighted_mean_depth_m": round(mean_depth, 2),
        "minimum_depth_m": int(depths.min()),
        "maximum_depth_m": int(depths.max()),
        "shelf_area_fraction_lt_200m": round(float(weights[depths < 200].sum() / total_area), 6),
        "depth_quantile_percentiles": list(PERCENTILES),
        "depth_quantile_m": [round(value, 2) for value in quantiles],
        "selected_depth_quantiles_m": {
            "p10": round(quantiles[10], 2),
            "p25": round(quantiles[25], 2),
            "p50": round(quantiles[50], 2),
            "p75": round(quantiles[75], 2),
            "p90": round(quantiles[90], 2),
        },
    }


def sample_province(geometry, elevations: np.ndarray, latitudes: np.ndarray, longitudes: np.ndarray, stride: int) -> dict:
    sampled_lats = latitudes[::stride]
    sampled_lons = longitudes[::stride]
    lon_mesh, lat_mesh = np.meshgrid(sampled_lons, sampled_lats)
    inside = contains_xy(geometry, lon_mesh, lat_mesh)
    sampled_elevations = elevations[::stride, ::stride]
    wet = inside & (sampled_elevations < 0)
    rows, _ = np.nonzero(wet)
    spacing = float(np.median(np.diff(sampled_lats)))
    row_areas = cell_area_by_row(sampled_lats, spacing)
    weights = row_areas[rows]
    depths = -sampled_elevations[wet].astype(np.int32)
    return summarize(depths, weights)


def sensitivity(fine: dict, coarse: dict) -> dict:
    keys = ("p10", "p25", "p50", "p75", "p90")
    return {
        "coarse_minus_fine_mean_depth_m": round(coarse["area_weighted_mean_depth_m"] - fine["area_weighted_mean_depth_m"], 2),
        "coarse_minus_fine_shelf_area_fraction": round(coarse["shelf_area_fraction_lt_200m"] - fine["shelf_area_fraction_lt_200m"], 6),
        "coarse_minus_fine_selected_quantiles_m": {
            key: round(coarse["selected_depth_quantiles_m"][key] - fine["selected_depth_quantiles_m"][key], 2)
            for key in keys
        },
    }


def acquire(output_path: Path = OUTPUT, receipt_path: Path = RECEIPT, browser_path: Path = BROWSER) -> dict:
    geometry_raw, geometry_headers = fetch(GEOMETRY_URL)
    elevation_raw, elevation_headers = fetch(ELEVATION_URL)
    geometries, properties, repairs = load_geometries(geometry_raw)
    elevations, latitudes, longitudes = parse_ascii_grid(elevation_raw, "elevation")
    if elevations.shape != (ROWS, COLUMNS):
        raise ValueError("unexpected GEBCO grid shape")
    spacing = float(np.median(np.diff(latitudes)))
    if not math.isclose(spacing, 0.25, abs_tol=1e-9):
        raise ValueError("unexpected GEBCO sample spacing")

    footprints = json.loads(FOOTPRINTS.read_text(encoding="utf-8"))
    adjacency = json.loads(ADJACENCY.read_text(encoding="utf-8"))
    geometry_hash = normalized_geometry_sha256(geometries, properties)
    if geometry_hash != adjacency["normalized_repaired_geometry_sha256"]:
        raise ValueError("fresh normalized Version 4 geometry differs from the adjacency baseline")

    provinces = {}
    compatibility = {}
    for code, rationale in ARCHETYPES.items():
        fine = sample_province(geometries[code], elevations, latitudes, longitudes, 1)
        coarse = sample_province(geometries[code], elevations, latitudes, longitudes, 2)
        prior = footprints["provinces"][code]
        compatible = {
            "wet_sample_count_match": fine["wet_sample_count"] == prior["wet_sample_count"],
            "minimum_depth_match": fine["minimum_depth_m"] == prior["minimum_wet_depth_m"],
            "maximum_depth_match": fine["maximum_depth_m"] == prior["maximum_wet_depth_m"],
            "mean_depth_match": fine["area_weighted_mean_depth_m"] == prior["area_weighted_mean_water_depth_m"],
        }
        if not all(compatible.values()):
            raise ValueError(f"fresh bathymetry summary differs from the committed baseline for {code}: {compatible}")
        compatibility[code] = compatible
        provinces[code] = {
            "osw_code": code,
            "source_code": properties[code]["source_code"],
            "archetype_rationale": rationale,
            "fine_0_25_degree": fine,
            "coarse_0_5_degree_center_screen": coarse,
            "sensitivity": sensitivity(fine, coarse),
        }

    payload = {
        "schema": "osw-longhurst-2007-continuous-hypsometry-prototype-v1",
        "geometry_edition": footprints["geometry_edition"],
        "normalized_repaired_geometry_sha256": geometry_hash,
        "gebco_edition": "GEBCO_2026 ice-surface-elevation grid",
        "source_footprints_path": str(FOOTPRINTS.relative_to(ROOT)).replace("\\", "/"),
        "source_footprints_sha256": sha256_file(FOOTPRINTS),
        "archetype_selection": {
            "status": "frozen before inspecting continuous-curve results",
            "codes": list(ARCHETYPES),
            "rule": "One declared representative each for the existing shelf-led, deep-floor-led, abyssal-floor-led, polar, antimeridian-crossing, and small/coastal repaired-geometry test classes; classes may overlap but each selection has one primary rationale.",
        },
        "method": {
            "fine": "Wet GEBCO 0.25-degree centers inside repaired Version 4 geometry, weighted by spherical cell area.",
            "curve": "Area-weighted empirical seafloor-depth quantiles at every integer percentile from 0 through 100, interpolated at cell-weight centers.",
            "coarse": "Independent 0.5-degree center screen using every second latitude and longitude center and recomputed 0.5-degree spherical cell areas; not an aggregation of the fine result.",
            "shelf": "Area fraction of sampled wet centers with seabed depth less than 200 m.",
        },
        "provinces": provinces,
        "summary": {
            "prototype_province_count": len(provinces),
            "fine_spacing_degrees": 0.25,
            "coarse_spacing_degrees": 0.5,
            "all_fresh_summary_compatibility_checks_pass": all(all(item.values()) for item in compatibility.values()),
        },
        "boundary": "Representative sampled seafloor-depth distributions and one grid-resolution screen, not exact polygon hypsometry, native-resolution bathymetry, uncertainty, geomorphic identity, ecological depth extent, water-mass structure, heat content, transport, or global 54-province completion. The 0.5-degree difference measures declared grid sensitivity only.",
    }
    encoded = json.dumps(payload, separators=(",", ":"))
    output_path.write_text(encoded + "\n", encoding="utf-8", newline="\n")
    browser_path.write_text("window.OSW_PROVINCE_HYPSOMETRY = " + encoded + ";\n", encoding="utf-8", newline="\n")
    receipt = {
        "schema": "osw-longhurst-2007-continuous-hypsometry-source-receipt-v1",
        "acquired_utc": datetime.now(timezone.utc).isoformat(),
        "source_payload_posture": "provider bytes omitted; exact queries, response metadata, byte counts, SHA-256, compatibility checks, and compact derived curves retained",
        "sources": {
            "geometry": {
                "provider": "Flanders Marine Institute (VLIZ), Marine Regions",
                "product": "Longhurst Provinces Version 4, March 2010",
                "url": GEOMETRY_URL,
                "response_bytes": len(geometry_raw),
                "response_sha256": sha256_bytes(geometry_raw),
                "normalized_repaired_geometry_sha256": geometry_hash,
                "headers": geometry_headers,
                "license": "CC BY 4.0 under the current Marine Regions license statement; attribution required",
                "citation": f"Flanders Marine Institute (2009). Longhurst Provinces. Available online at https://www.marineregions.org/. Consulted on {datetime.now(timezone.utc).date().isoformat()}.",
            },
            "elevation": {
                "provider": "GEBCO via CEDA OPeNDAP",
                "product": "GEBCO_2026 Grid, ice-surface-elevation version",
                "url": ELEVATION_URL,
                "doi": GEBCO_DOI,
                "response_bytes": len(elevation_raw),
                "response_sha256": sha256_bytes(elevation_raw),
                "headers": elevation_headers,
                "license": "public domain with requested attribution and disclaimer",
            },
        },
        "compatibility": compatibility,
        "geometry_repairs": repairs,
        "output": str(output_path.relative_to(ROOT)).replace("\\", "/"),
        "output_sha256": sha256_file(output_path),
        "boundary": payload["boundary"],
    }
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--receipt", type=Path, default=RECEIPT)
    parser.add_argument("--browser", type=Path, default=BROWSER)
    args = parser.parse_args()
    result = acquire(args.output, args.receipt, args.browser)
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
