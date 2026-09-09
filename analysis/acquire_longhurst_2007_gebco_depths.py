"""Build a source-aligned Longhurst 2007 × GEBCO 2026 depth screen.

This is an explicit network acquisition. It reads the authoritative Marine
Regions Version 4 WFS geometry and global 0.25-degree GEBCO elevation/TID
samples. Raw provider payloads are checksum-receipted but not redistributed;
the committed products are an OSW crosswalk, a rasterized footprint mask, and
area-weighted province summaries.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
from urllib.request import Request, urlopen

import numpy as np
from shapely import contains_xy, make_valid
from shapely.geometry import shape
from shapely.ops import unary_union
from shapely.validation import explain_validity

from build_gebco_province_seed_depths import deepest_band, tid_class


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "research" / "longhurst-province-reference.csv"
RECEIPT = ROOT / "research" / "longhurst-2007-gebco-2026-source-receipt.json"
OUTPUT = ROOT / "research" / "longhurst-2007-gebco-2026-depths.json"
BROWSER = ROOT / "column" / "province-footprints.js"

GEOMETRY_URL = (
    "https://geo.vliz.be/geoserver/MarineRegions/wfs?service=WFS&version=1.0.0"
    "&request=GetFeature&typeName=MarineRegions:longhurst"
    "&outputFormat=application/json"
)
GEBCO_BASE = (
    "https://dap.ceda.ac.uk/thredds/dodsC/bodc/gebco/global/gebco_2026/"
    "ice_surface_elevation/netcdf/GEBCO_2026.nc"
)
TID_BASE = (
    "https://dap.ceda.ac.uk/thredds/dodsC/bodc/gebco/global/gebco_2026/"
    "type_identifier_grid/netcdf/gebco_2026_tid.nc"
)
GRID_CONSTRAINT = "[30:60:43170][30:60:86370]"
ELEVATION_URL = f"{GEBCO_BASE}.ascii?elevation{GRID_CONSTRAINT}"
TID_URL = f"{TID_BASE}.ascii?tid{GRID_CONSTRAINT}"
GEBCO_DOI = "10.5285/4f68d5c7-45eb-f999-e063-7086abc036fa"
ROWS, COLUMNS = 720, 1440
EARTH_RADIUS_M = 6_371_008.8

# The OSW directory preserves the older 1995 vocabulary. Version 4 is the
# revised 2007 54-province product. These are identity aliases, not geometry
# edits. NPSE and OCAL have no separate Version 4 footprint.
SOURCE_TO_OSW = {
    "CHIL": "HUMB",
    "INDE": "IND E",
    "INDW": "IND W",
    "NASE": "NAST E",
    "NASW": "NAST W",
}
OLDER_ONLY = {"NPSE", "OCAL"}


def fetch(url: str) -> tuple[bytes, dict[str, str | None]]:
    request = Request(url, headers={"User-Agent": "OSW/1.0 scientific-data-acquisition"})
    with urlopen(request, timeout=240) as response:
        raw = response.read()
        headers = {
            "content_type": response.headers.get("Content-Type"),
            "etag": response.headers.get("ETag"),
            "last_modified": response.headers.get("Last-Modified"),
        }
    return raw, headers


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def parse_ascii_grid(raw: bytes, variable: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    text = raw.decode("utf-8")
    match = re.search(
        rf"^{variable}\.{variable}\[{ROWS}\]\[{COLUMNS}\]\n(.*?)\n\n"
        rf"{variable}\.lat\[{ROWS}\]\n([^\n]+)\n\n"
        rf"{variable}\.lon\[{COLUMNS}\]\n([^\n]+)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not match:
        raise ValueError(f"cannot parse {variable} global grid")
    values = np.empty((ROWS, COLUMNS), dtype=np.int16)
    lines = match.group(1).splitlines()
    if len(lines) != ROWS:
        raise ValueError(f"wrong {variable} row count")
    for expected, line in enumerate(lines):
        prefix, payload = line.split("]", 1)
        if int(prefix[1:]) != expected:
            raise ValueError(f"nonsequential {variable} row")
        row = np.fromstring(payload.lstrip(", "), dtype=np.int16, sep=",")
        if row.size != COLUMNS:
            raise ValueError(f"wrong {variable} column count at row {expected}")
        values[expected] = row
    latitudes = np.fromstring(match.group(2), dtype=np.float64, sep=",")
    longitudes = np.fromstring(match.group(3), dtype=np.float64, sep=",")
    if latitudes.size != ROWS or longitudes.size != COLUMNS:
        raise ValueError(f"wrong {variable} coordinate count")
    return values, latitudes, longitudes


def cell_area_by_row(latitudes: np.ndarray, spacing_degrees: float) -> np.ndarray:
    half = spacing_degrees / 2
    south = np.radians(np.maximum(-90, latitudes - half))
    north = np.radians(np.minimum(90, latitudes + half))
    delta_lon = math.radians(spacing_degrees)
    return EARTH_RADIUS_M**2 * delta_lon * (np.sin(north) - np.sin(south))


def encode_runs(assignments: np.ndarray, codes: list[str]) -> list[list[int | str]]:
    runs: list[list[int | str]] = []
    for row_index, row in enumerate(assignments):
        start = 0
        while start < COLUMNS:
            value = int(row[start])
            if value < 0:
                start += 1
                continue
            end = start
            while end + 1 < COLUMNS and int(row[end + 1]) == value:
                end += 1
            runs.append([row_index, start, end, codes[value]])
            start = end + 1
    return runs


def build_crosswalk(source_codes: set[str]) -> list[dict]:
    import csv

    rows = list(csv.DictReader(REFERENCE.open(encoding="utf-8")))
    result = []
    mapped_sources = {SOURCE_TO_OSW.get(code, code): code for code in source_codes}
    for row in rows:
        osw_code = row["code"]
        source_code = mapped_sources.get(osw_code)
        result.append({
            "osw_code": osw_code,
            "osw_name": row["province"],
            "source_code": source_code,
            "status": "older_1995_identity_without_separate_2007_footprint" if osw_code in OLDER_ONLY else "source_aligned_2007",
            "note": (
                "Version 4 merges or reorganizes this older identity; no separate footprint is assigned."
                if osw_code in OLDER_ONLY
                else ("code alias only; geometry is unchanged" if source_code != osw_code else "direct code match")
            ),
        })
    if len(result) != 56 or len([item for item in result if item["source_code"]]) != 54:
        raise ValueError("unexpected 56-to-54 crosswalk cardinality")
    return result


def acquire(receipt_path: Path = RECEIPT, output_path: Path = OUTPUT, browser_path: Path = BROWSER) -> dict:
    geometry_raw, geometry_headers = fetch(GEOMETRY_URL)
    elevation_raw, elevation_headers = fetch(ELEVATION_URL)
    tid_raw, tid_headers = fetch(TID_URL)

    collection = json.loads(geometry_raw)
    if collection.get("type") != "FeatureCollection" or len(collection.get("features", [])) != 54:
        raise ValueError("Marine Regions Longhurst Version 4 must contain 54 features")
    elevations, latitudes, longitudes = parse_ascii_grid(elevation_raw, "elevation")
    tids, tid_latitudes, tid_longitudes = parse_ascii_grid(tid_raw, "tid")
    if not np.array_equal(latitudes, tid_latitudes) or not np.array_equal(longitudes, tid_longitudes):
        raise ValueError("GEBCO elevation and TID coordinates disagree")
    spacing = float(np.median(np.diff(latitudes)))
    if not math.isclose(spacing, 0.25, abs_tol=1e-9):
        raise ValueError("unexpected GEBCO sample spacing")

    features = sorted(collection["features"], key=lambda item: item["properties"]["provcode"])
    source_codes = [item["properties"]["provcode"] for item in features]
    if len(set(source_codes)) != 54:
        raise ValueError("duplicate Longhurst source codes")
    osw_codes = [SOURCE_TO_OSW.get(code, code) for code in source_codes]
    assignments = np.full((ROWS, COLUMNS), -1, dtype=np.int16)
    overlap_count = 0
    lon_mesh, lat_mesh = np.meshgrid(longitudes, latitudes)

    geometry_repairs = []
    for feature_index, feature in enumerate(features):
        geometry = shape(feature["geometry"])
        if not geometry.is_valid:
            reason = explain_validity(geometry)
            original_planar_area = geometry.area
            repaired = make_valid(geometry)
            polygon_parts = [part for part in repaired.geoms if part.geom_type in {"Polygon", "MultiPolygon"}] if repaired.geom_type == "GeometryCollection" else [repaired]
            geometry = unary_union(polygon_parts)
            if geometry.is_empty or not geometry.is_valid or geometry.geom_type not in {"Polygon", "MultiPolygon"}:
                raise ValueError(f"cannot repair source geometry for {source_codes[feature_index]}: {reason}")
            geometry_repairs.append({
                "source_code": source_codes[feature_index],
                "reason": reason,
                "operation": "GEOS make_valid; retain and union polygonal parts",
                "relative_planar_area_change": round((geometry.area - original_planar_area) / original_planar_area, 12),
            })
        inside = contains_xy(geometry, lon_mesh, lat_mesh)
        overlap_count += int(np.count_nonzero(inside & (assignments >= 0)))
        assignments[inside & (assignments < 0)] = feature_index

    row_areas = cell_area_by_row(latitudes, spacing)
    wet = elevations < 0
    assigned = assignments >= 0
    province_summaries = {}
    for feature_index, feature in enumerate(features):
        member = assignments == feature_index
        member_wet = member & wet
        sample_rows, _ = np.nonzero(member_wet)
        weights = row_areas[sample_rows]
        depths = -elevations[member_wet].astype(np.int32)
        member_tids = tids[member_wet].astype(np.int16)
        band_areas = Counter()
        tid_areas = Counter()
        band_counts = Counter()
        tid_counts = Counter()
        for depth, tid, area in zip(depths, member_tids, weights, strict=True):
            band = deepest_band(int(depth))
            source_class = tid_class(int(tid))
            band_counts[band] += 1
            tid_counts[source_class] += 1
            band_areas[band] += float(area)
            tid_areas[source_class] += float(area)
        wet_area = float(weights.sum())
        properties = feature["properties"]
        source_code = source_codes[feature_index]
        osw_code = osw_codes[feature_index]
        province_summaries[osw_code] = {
            "osw_code": osw_code,
            "source_code": source_code,
            "source_name": properties["provdescr"],
            "source_mrgid": int(properties["mrgid"]),
            "source_area_km2": round(float(properties["area_m2"]) / 1_000_000, 2),
            "sampled_footprint_cell_count": int(np.count_nonzero(member)),
            "wet_sample_count": int(depths.size),
            "non_wet_geometry_sample_count": int(np.count_nonzero(member & ~wet)),
            "sampled_wet_area_km2": round(wet_area / 1_000_000, 2),
            "minimum_wet_depth_m": int(depths.min()) if depths.size else None,
            "maximum_wet_depth_m": int(depths.max()) if depths.size else None,
            "counts_by_seafloor_band": dict(sorted(band_counts.items())),
            "wet_area_km2_by_seafloor_band": {key: round(value / 1_000_000, 2) for key, value in sorted(band_areas.items())},
            "wet_area_fraction_by_seafloor_band": {key: round(value / wet_area, 6) for key, value in sorted(band_areas.items())} if wet_area else {},
            "counts_by_tid_class": dict(sorted(tid_counts.items())),
            "wet_area_fraction_by_tid_class": {key: round(value / wet_area, 6) for key, value in sorted(tid_areas.items())} if wet_area else {},
        }

    crosswalk = build_crosswalk(set(source_codes))
    payload = {
        "schema": "osw-longhurst-2007-gebco-2026-depths-v1",
        "geometry_edition": "Marine Regions Longhurst Provinces Version 4, March 2010; revised Longhurst 2007 54-province scheme",
        "geometry_source_sha256": sha256(geometry_raw),
        "gebco_elevation_source_sha256": sha256(elevation_raw),
        "gebco_tid_source_sha256": sha256(tid_raw),
        "grid": {
            "shape": [ROWS, COLUMNS],
            "spacing_degrees": spacing,
            "latitude_start": float(latitudes[0]),
            "longitude_start": float(longitudes[0]),
            "cell_semantics": "GEBCO pixel centers assigned by point-in-polygon to the source geometry; spherical cell-area weighting",
        },
        "crosswalk": crosswalk,
        "provinces": province_summaries,
        "footprint_runs": encode_runs(assignments, osw_codes),
        "coverage": {
            "source_feature_count": len(features),
            "osw_directory_count": len(crosswalk),
            "source_aligned_osw_count": 54,
            "older_only_osw_count": 2,
            "geometry_grid_cell_count": int(np.count_nonzero(assigned)),
            "wet_geometry_grid_cell_count": int(np.count_nonzero(assigned & wet)),
            "non_wet_geometry_grid_cell_count": int(np.count_nonzero(assigned & ~wet)),
            "global_wet_grid_cell_count": int(np.count_nonzero(wet)),
            "wet_cells_outside_geometry_count": int(np.count_nonzero(wet & ~assigned)),
            "overlapping_geometry_grid_cell_count": overlap_count,
            "source_geometry_repair_count": len(geometry_repairs),
        },
        "source_geometry_repairs": geometry_repairs,
        "boundary": "Source-aligned static mean surface ecology, not a current, water mass, material wall, dynamic province diagnosis, heat field, transport, or full-depth occupancy. Bathymetry statistics are 0.25-degree cell-center estimates with spherical area weighting, not exact polygon integrals or navigational products.",
    }
    output_path.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    browser_path.write_text("window.OSW_PROVINCE_FOOTPRINTS = " + json.dumps(payload, separators=(",", ":")) + ";\n", encoding="utf-8", newline="\n")

    receipt = {
        "schema": "osw-longhurst-2007-gebco-2026-source-receipt-v1",
        "acquired_utc": datetime.now(timezone.utc).isoformat(),
        "source_payload_posture": "provider bytes omitted; exact URLs, response metadata, byte counts, and SHA-256 retained; transformed crosswalk, raster mask, and summaries committed",
        "sources": {
            "geometry": {
                "provider": "Flanders Marine Institute (VLIZ), Marine Regions",
                "product": "Longhurst Provinces Version 4, March 2010",
                "url": GEOMETRY_URL,
                "feature_count": 54,
                "crs": "EPSG:4326",
                "license": "CC BY 4.0 under the current Marine Regions license statement; attribution required",
                "citation": f"Flanders Marine Institute (2009). Longhurst Provinces. Available online at https://www.marineregions.org/. Consulted on {datetime.now(timezone.utc).date().isoformat()}.",
                "response_bytes": len(geometry_raw),
                "response_sha256": sha256(geometry_raw),
                "headers": geometry_headers,
            },
            "elevation": {
                "provider": "GEBCO via CEDA OPeNDAP",
                "product": "GEBCO_2026 Grid, ice-surface-elevation version",
                "doi": GEBCO_DOI,
                "url": ELEVATION_URL,
                "response_bytes": len(elevation_raw),
                "response_sha256": sha256(elevation_raw),
                "headers": elevation_headers,
                "license": "public domain with requested attribution and disclaimer",
            },
            "tid": {
                "provider": "GEBCO via CEDA OPeNDAP",
                "product": "GEBCO_2026 Type Identifier Grid",
                "doi": GEBCO_DOI,
                "url": TID_URL,
                "response_bytes": len(tid_raw),
                "response_sha256": sha256(tid_raw),
                "headers": tid_headers,
                "license": "public domain with requested attribution and disclaimer",
            },
        },
        "result": payload["coverage"],
        "boundary": payload["boundary"],
    }
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, default=RECEIPT)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--browser", type=Path, default=BROWSER)
    args = parser.parse_args()
    result = acquire(args.receipt, args.output, args.browser)
    print(json.dumps(result["coverage"], indent=2))


if __name__ == "__main__":
    main()
