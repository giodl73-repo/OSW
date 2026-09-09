"""Build the Stage 3 model-screened ocean-state hydrography pilot.

This is an explicit network operation because it reacquires the source-edition
Longhurst geometry. It combines that geometry with the four already-custodied
2018 ORAS5 Drake native-grid subsets. The compact JSON derivative is committed;
provider geometry bytes are not.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import netCDF4
import numpy as np
from shapely import contains_xy

try:
    from acquire_longhurst_2007_adjacency import (
        fetch_geometry,
        load_geometries,
        normalized_geometry_sha256,
        sha256_bytes,
    )
except ImportError:  # pragma: no cover - package-style test imports
    from analysis.acquire_longhurst_2007_adjacency import (
        fetch_geometry,
        load_geometries,
        normalized_geometry_sha256,
        sha256_bytes,
    )


ROOT = Path(__file__).resolve().parents[1]
BROWSER = ROOT / "exchange" / "hydrography.js"
MONTHS = ("201802", "201805", "201808", "201811")
DEPTH_BANDS = (
    ("0-200m", 0.0, 200.0),
    ("200-1000m", 200.0, 1_000.0),
    ("1000-4000m", 1_000.0, 4_000.0),
    ("4000-6000m", 4_000.0, 6_000.0),
    ("6000m+", 6_000.0, float("inf")),
)
QUANTILES = (0.10, 0.25, 0.50, 0.75, 0.90)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_text_file(path: Path) -> str:
    """Hash repository text with canonical LF endings on every host OS."""
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def portable_path(root: Path, stored: str) -> Path:
    return root.joinpath(*Path(stored.replace("\\", "/")).parts)


def t_cell_geometry(mesh: netCDF4.Dataset) -> tuple[np.ndarray, np.ndarray]:
    """Return reconstructed T-cell thickness and midpoint depth arrays."""
    reference = np.asarray(mesh.variables["e3t_0"][:], dtype=float)
    mbathy = np.asarray(mesh.variables["mbathy"][:], dtype=int)
    partial = np.asarray(mesh.variables["e3t_ps"][:], dtype=float)
    levels, rows, columns = len(reference), *mbathy.shape
    thickness = np.zeros((levels, rows, columns), dtype=np.float32)
    for level in range(levels):
        active = mbathy > level
        bottom = mbathy == level + 1
        thickness[level, active] = reference[level]
        bottom_values = np.where(partial > 0, partial, reference[level])
        thickness[level, bottom] = bottom_values[bottom]
    top = np.cumsum(thickness, axis=0, dtype=np.float64) - thickness
    midpoint = top + thickness / 2
    midpoint[thickness <= 0] = np.nan
    return thickness, midpoint


def assign_provinces(longitude: np.ndarray, latitude: np.ndarray, geometries: dict) -> tuple[np.ndarray, dict]:
    assignments = np.full(longitude.shape, "", dtype="U8")
    overlaps = np.zeros(longitude.shape, dtype=np.uint8)
    for code in sorted(geometries):
        inside = contains_xy(geometries[code], longitude, latitude)
        overlaps += inside.astype(np.uint8)
        assignments[(assignments == "") & inside] = code
    return assignments, {
        "assigned_horizontal_cells": int(np.count_nonzero(assignments != "")),
        "unassigned_horizontal_cells": int(np.count_nonzero(assignments == "")),
        "overlap_cell_count": int(np.count_nonzero(overlaps > 1)),
    }


def summarize(values: np.ndarray) -> dict:
    values = np.asarray(values, dtype=float)
    quantiles = np.quantile(values, QUANTILES)
    return {
        "sample_count": int(values.size),
        "mean_degC": round(float(np.mean(values)), 6),
        "standard_deviation_degC": round(float(np.std(values)), 6),
        "minimum_degC": round(float(np.min(values)), 6),
        "p10_degC": round(float(quantiles[0]), 6),
        "p25_degC": round(float(quantiles[1]), 6),
        "median_degC": round(float(quantiles[2]), 6),
        "p75_degC": round(float(quantiles[3]), 6),
        "p90_degC": round(float(quantiles[4]), 6),
        "maximum_degC": round(float(np.max(values)), 6),
    }


def build(root: Path = ROOT, acquired_at: str | None = None) -> dict:
    root = Path(root)
    acquired_at = acquired_at or datetime.now(timezone.utc).isoformat()
    raw, headers = fetch_geometry()
    geometries, properties, repairs = load_geometries(raw)
    geometry_hash = normalized_geometry_sha256(geometries, properties)

    mesh_receipt_path = root / "research/osw-m3-oras5-drake-mesh.json"
    mesh_receipt = json.loads(mesh_receipt_path.read_text(encoding="utf-8"))
    mesh_path = portable_path(root, mesh_receipt["output"]["path"])
    if sha256_file(mesh_path) != mesh_receipt["output"]["sha256"]:
        raise ValueError("ORAS5 mesh does not match its receipt")

    with netCDF4.Dataset(mesh_path) as mesh:
        longitude = np.asarray(mesh.variables["glamt"][:], dtype=float)
        latitude = np.asarray(mesh.variables["gphit"][:], dtype=float)
        mbathy = np.asarray(mesh.variables["mbathy"][:], dtype=int)
        _, midpoint = t_cell_geometry(mesh)
    assignments, assignment_audit = assign_provinces(longitude, latitude, geometries)
    supported_codes = sorted(set(assignments.ravel()) - {""})

    passports = []
    sample_cache = {}
    state_sources = []
    for month in MONTHS:
        receipt_path = root / f"research/osw-m3-oras5-drake-state-{month}.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        state_path = portable_path(root, receipt["output"]["path"])
        if sha256_file(state_path) != receipt["output"]["sha256"]:
            raise ValueError(f"ORAS5 {month} state does not match its receipt")
        state_sources.append({
            "month": month,
            "path": state_path.relative_to(root).as_posix(),
            "sha256": receipt["output"]["sha256"],
            "receipt_path": receipt_path.relative_to(root).as_posix(),
            "receipt_sha256": sha256_text_file(receipt_path),
            "source_url": receipt["fields"]["votemper"]["url"],
            "retrieved_at": receipt["retrieved_at"],
        })
        with netCDF4.Dataset(state_path) as state:
            temperature = np.ma.asarray(state.variables["votemper"][:])
        raw_values = np.asarray(temperature.filled(np.nan), dtype=float)
        valid_temperature = np.isfinite(raw_values) & ~np.ma.getmaskarray(temperature)
        for code in supported_codes:
            horizontal = assignments == code
            for band, lower, upper in DEPTH_BANDS:
                support = horizontal[None, :, :] & (midpoint >= lower) & (midpoint < upper) & (mbathy[None, :, :] > np.arange(midpoint.shape[0])[:, None, None])
                expected = int(np.count_nonzero(support))
                valid = support & valid_temperature
                count = int(np.count_nonzero(valid))
                if not count:
                    continue
                samples = raw_values[valid]
                sample_cache[(month, code, band)] = samples
                record = {
                    "address": {"geometry_edition": "longhurst-v4-54", "province": code, "depth_support": band},
                    "valid_time": f"{month[:4]}-{month[4:]}-01/P1M",
                    "seasonal_sample": month,
                    "property": "sea_water_potential_temperature",
                    "units": "degC",
                    "evidence_class": "assimilative_reanalysis_model_screen",
                    "method_version": "osw-hydrography-pilot-v1",
                    "support": {
                        "expected_native_t_cells": expected,
                        "valid_native_t_cells": count,
                        "fraction": round(count / expected, 6) if expected else 0.0,
                        "weighting": "unweighted_native_T_cell_level_samples",
                    },
                    "distribution": summarize(samples),
                    "uncertainty": {
                        "status": "not_estimated",
                        "reason": "one ORAS5 ensemble member and four monthly snapshots; distribution spread is not measurement or model uncertainty",
                    },
                    "revision_lineage": {"supersedes": None, "method_compatibility": "initial_version"},
                }
                passports.append(record)

    province_summary = []
    for code in supported_codes:
        records = [item for item in passports if item["address"]["province"] == code]
        province_summary.append({
            **properties[code],
            "horizontal_native_t_cells": int(np.count_nonzero(assignments == code)),
            "passport_count": len(records),
            "minimum_support_fraction": min((item["support"]["fraction"] for item in records), default=0.0),
        })

    adjacency_path = root / "research/longhurst-2007-province-adjacency.json"
    adjacency = json.loads(adjacency_path.read_text(encoding="utf-8"))
    adjacent_contrasts = []
    for edge in adjacency["edges"]:
        first, second = edge["provinces"]
        if first not in supported_codes or second not in supported_codes:
            continue
        for month in MONTHS:
            for band, _, _ in DEPTH_BANDS:
                left = sample_cache.get((month, first, band))
                right = sample_cache.get((month, second, band))
                if left is None or right is None:
                    continue
                left_summary, right_summary = summarize(left), summarize(right)
                pooled = np.sqrt((float(np.var(left)) + float(np.var(right))) / 2)
                adjacent_contrasts.append({
                    "edge_id": edge["edge_id"],
                    "provinces": [first, second],
                    "valid_time": f"{month[:4]}-{month[4:]}-01/P1M",
                    "seasonal_sample": month,
                    "depth_support": band,
                    "first_minus_second_mean_degC": round(float(np.mean(left) - np.mean(right)), 6),
                    "first_minus_second_median_degC": round(left_summary["median_degC"] - right_summary["median_degC"], 6),
                    "standardized_mean_difference": round(float((np.mean(left) - np.mean(right)) / pooled), 6) if pooled else None,
                    "interquartile_overlap_degC": round(max(0.0, min(left_summary["p75_degC"], right_summary["p75_degC"]) - max(left_summary["p25_degC"], right_summary["p25_degC"])), 6),
                    "sample_counts": [int(left.size), int(right.size)],
                    "inference": "descriptive_model_screen_no_independence_or_significance_claim",
                })

    return {
        "schema": "osw-ocean-state-hydrography-pilot-v1",
        "status": "stage_3_temperature_only_model_screen",
        "acquired_at": acquired_at,
        "geometry": {
            "edition": "Marine Regions Longhurst Provinces Version 4, March 2010; revised Longhurst 2007 54-province scheme",
            "source_url": "https://geo.vliz.be/geoserver/MarineRegions/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=MarineRegions:longhurst_v4_2010&outputFormat=application/json",
            "response_bytes": len(raw),
            "response_sha256": sha256_bytes(raw),
            "normalized_repaired_geometry_sha256": geometry_hash,
            "response_headers": headers,
            "repair_count": len(repairs),
            "license": "CC BY 4.0 under the Marine Regions data license; attribution required",
            "citation": "Flanders Marine Institute (2009). Longhurst Provinces. Available online at https://www.marineregions.org/. Consulted on 2026-09-08.",
        },
        "grid": {
            "source": "ORAS5 ORCA025 native Drake subset",
            "mesh_path": mesh_path.relative_to(root).as_posix(),
            "mesh_sha256": mesh_receipt["output"]["sha256"],
            "shape": mesh_receipt["shape"],
            "coordinate_extent_deg": mesh_receipt["coordinate_extent_deg"],
            "assignment": "source polygon containment at native T-cell centers",
            **assignment_audit,
        },
        "source_custody": {
            "provider": "ECMWF ORAS5 via the University of Hamburg ICDC native ORCA025 THREDDS mirror",
            "product_doi": "10.24381/cds.67e8eeb7",
            "license": "Copernicus Climate Data Store CC-BY licence for ORAS5; attribution required",
            "redistribution": "OSW commits bounded native subsets and compact derivatives with source URLs and checksums",
        },
        "admitted_properties": ["sea_water_potential_temperature"],
        "unsupported_properties": [
            {"property": "sea_water_salinity", "reason": "not present in the already-custodied Drake state subsets"},
            {"property": "sea_water_density", "reason": "salinity and a declared equation-of-state method are unavailable"},
            {"property": "moles_of_oxygen_per_unit_mass_in_sea_water", "reason": "not present in the source subsets"},
            {"property": "heat_content", "reason": "T-cell horizontal metrics and a complete density/heat-capacity convention are not admitted"},
        ],
        "time_support": {"year": 2018, "months": list(MONTHS), "interpretation": "four monthly means sampled across seasons, not a climatology or annual mean"},
        "depth_bands": [{"id": name, "lower_m": lower, "upper_m": None if np.isinf(upper) else upper} for name, lower, upper in DEPTH_BANDS],
        "state_sources": state_sources,
        "provinces": province_summary,
        "property_passports": passports,
        "adjacency_source": {"path": adjacency_path.relative_to(root).as_posix(), "sha256": sha256_text_file(adjacency_path)},
        "adjacent_contrasts": adjacent_contrasts,
        "multiple_comparison_boundary": "No significance test or global rank is reported. Native samples are spatially and vertically autocorrelated and unequal in area and volume.",
        "boundary": "Temperature distributions are unweighted ORAS5 native T-cell-level model screens inside static source polygons. They are not observations, volume-weighted inventories, heat content, water masses, uncertainty estimates, transport, or proof that a province is physically coherent.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "research/ocean-state-hydrography-pilot-2018.json")
    parser.add_argument("--browser-output", type=Path, default=BROWSER)
    parser.add_argument("--acquired-at")
    args = parser.parse_args()
    payload = build(acquired_at=args.acquired_at)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    args.browser_output.parent.mkdir(parents=True, exist_ok=True)
    compact = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    args.browser_output.write_text(f"window.OSW_HYDROGRAPHY = {compact};\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}: {len(payload['provinces'])} provinces, {len(payload['property_passports'])} passports")


if __name__ == "__main__":
    main()
