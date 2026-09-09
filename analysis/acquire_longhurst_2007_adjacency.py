"""Acquire and derive the source-backed Longhurst Version 4 adjacency graph.

This is an explicit network acquisition. Provider geometry bytes are not
committed. The compact graph, rejected-contact log, browser payload, and source
receipt are committed and remain reproducible offline from fixtures and their
recorded source identities.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
from http.client import IncompleteRead
import itertools
import json
import math
from pathlib import Path
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

import numpy as np
from shapely import contains_xy, make_valid
from shapely.geometry import LineString, MultiLineString, mapping, shape
from shapely.ops import unary_union
from shapely.validation import explain_validity

from acquire_longhurst_2007_gebco_depths import (
    COLUMNS,
    EARTH_RADIUS_M,
    GEOMETRY_URL,
    ROWS,
    SOURCE_TO_OSW,
)


ROOT = Path(__file__).resolve().parents[1]
FOOTPRINTS = ROOT / "research" / "longhurst-2007-gebco-2026-depths.json"
OUTPUT = ROOT / "research" / "longhurst-2007-province-adjacency.json"
REJECTED = ROOT / "research" / "longhurst-2007-province-adjacency-rejected.json"
RECEIPT = ROOT / "research" / "longhurst-2007-province-adjacency-source-receipt.json"
BROWSER = ROOT / "column" / "province-adjacency.js"
CONTACT_EPSILON_DEGREES = 1e-8
NEAR_MISS_TOLERANCES_DEGREES = (1e-6, 1e-4, 1e-3, 1e-2)


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch_geometry(url: str = GEOMETRY_URL) -> tuple[bytes, dict[str, str | None]]:
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
    raise RuntimeError("geometry acquisition failed after 3 attempts: " + " | ".join(failures))


def repair_polygon(geometry, source_code: str) -> tuple[object, dict | None]:
    if geometry.is_valid:
        return geometry, None
    reason = explain_validity(geometry)
    original_planar_area = geometry.area
    repaired = make_valid(geometry)
    parts = (
        [part for part in repaired.geoms if part.geom_type in {"Polygon", "MultiPolygon"}]
        if repaired.geom_type == "GeometryCollection"
        else [repaired]
    )
    geometry = unary_union(parts)
    if geometry.is_empty or not geometry.is_valid or geometry.geom_type not in {"Polygon", "MultiPolygon"}:
        raise ValueError(f"cannot repair source geometry for {source_code}: {reason}")
    return geometry, {
        "source_code": source_code,
        "reason": reason,
        "operation": "GEOS make_valid; retain and union polygonal parts",
        "relative_planar_area_change": round((geometry.area - original_planar_area) / original_planar_area, 12),
    }


def load_geometries(raw: bytes) -> tuple[dict[str, object], dict[str, dict], list[dict]]:
    collection = json.loads(raw)
    features = collection.get("features", [])
    if collection.get("type") != "FeatureCollection" or len(features) != 54:
        raise ValueError("Marine Regions Longhurst Version 4 must contain 54 features")
    geometries: dict[str, object] = {}
    properties: dict[str, dict] = {}
    repairs = []
    for feature in sorted(features, key=lambda item: item["properties"]["provcode"]):
        source_code = feature["properties"]["provcode"]
        osw_code = SOURCE_TO_OSW.get(source_code, source_code)
        if osw_code in geometries:
            raise ValueError(f"duplicate mapped province code: {osw_code}")
        geometry, repair = repair_polygon(shape(feature["geometry"]), source_code)
        geometries[osw_code] = geometry
        properties[osw_code] = {
            "osw_code": osw_code,
            "source_code": source_code,
            "source_name": feature["properties"]["provdescr"],
            "source_mrgid": int(feature["properties"]["mrgid"]),
        }
        if repair:
            repairs.append(repair)
    return geometries, properties, repairs


def iter_lines(geometry):
    if isinstance(geometry, LineString):
        yield geometry
    elif isinstance(geometry, MultiLineString) or geometry.geom_type == "GeometryCollection":
        for part in geometry.geoms:
            yield from iter_lines(part)


def great_circle_line_length_km(geometry) -> float:
    total_m = 0.0
    for line in iter_lines(geometry):
        coordinates = list(line.coords)
        for first, second in zip(coordinates, coordinates[1:]):
            lon1, lat1 = map(math.radians, first[:2])
            lon2, lat2 = map(math.radians, second[:2])
            delta_lon = (lon2 - lon1 + math.pi) % (2 * math.pi) - math.pi
            delta_lat = lat2 - lat1
            haversine = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
            total_m += 2 * EARTH_RADIUS_M * math.asin(min(1.0, math.sqrt(haversine)))
    return total_m / 1_000


def normalized_geometry_sha256(geometries: dict[str, object], properties: dict[str, dict]) -> str:
    records = [
        {
            "osw_code": code,
            "source_code": properties[code]["source_code"],
            "source_mrgid": properties[code]["source_mrgid"],
            "geometry": mapping(geometries[code]),
        }
        for code in sorted(geometries)
    ]
    encoded = json.dumps(records, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(encoded)


def classify_contacts(geometries: dict[str, object]) -> tuple[list[dict], list[dict]]:
    edges = []
    rejected = []
    for first, second in itertools.combinations(sorted(geometries), 2):
        first_boundary = geometries[first].boundary
        second_boundary = geometries[second].boundary
        intersection = first_boundary.intersection(second_boundary)
        shared_length_km = great_circle_line_length_km(intersection)
        distance_degrees = float(first_boundary.distance(second_boundary))
        if shared_length_km > 0:
            edges.append({
                "edge_id": f"{first}--{second}",
                "provinces": [first, second],
                "contact_class": "shared_source_edge",
                "shared_boundary_length_km": round(shared_length_km, 3),
                "source_intersection_type": intersection.geom_type,
                "physical_boundary_class": "undetermined_reference_edge",
            })
        elif distance_degrees <= CONTACT_EPSILON_DEGREES:
            rejected.append({
                "candidate_id": f"{first}--{second}",
                "provinces": [first, second],
                "disposition": "rejected_point_only_contact",
                "minimum_planar_distance_degrees": round(distance_degrees, 12),
                "source_intersection_type": intersection.geom_type,
                "reason": "The source polygons touch only at one or more points and do not share a measurable edge.",
            })
        elif distance_degrees <= max(NEAR_MISS_TOLERANCES_DEGREES):
            reached = next(value for value in NEAR_MISS_TOLERANCES_DEGREES if distance_degrees <= value)
            rejected.append({
                "candidate_id": f"{first}--{second}",
                "provinces": [first, second],
                "disposition": "rejected_tolerance_only_near_miss",
                "minimum_planar_distance_degrees": round(distance_degrees, 12),
                "first_included_tolerance_degrees": reached,
                "source_intersection_type": intersection.geom_type,
                "reason": "The source polygons do not touch; buffering would invent the contact.",
            })
    return edges, rejected


def decode_footprint_runs(payload: dict) -> tuple[np.ndarray, list[str]]:
    codes = sorted(payload["provinces"])
    code_index = {code: index for index, code in enumerate(codes)}
    assignments = np.full((ROWS, COLUMNS), -1, dtype=np.int16)
    for row, start, end, code in payload["footprint_runs"]:
        assignments[row, start:end + 1] = code_index[code]
    return assignments, codes


def sampled_neighbor_pairs(assignments: np.ndarray, codes: list[str]) -> tuple[set[tuple[str, str]], Counter]:
    pair_counts: Counter = Counter()
    comparisons = (
        (assignments[:, :-1], assignments[:, 1:]),
        (assignments[:-1, :], assignments[1:, :]),
        (assignments[:, -1:], assignments[:, :1]),
    )
    for first, second in comparisons:
        valid = (first >= 0) & (second >= 0) & (first != second)
        for left, right in zip(first[valid], second[valid], strict=True):
            pair = tuple(sorted((codes[int(left)], codes[int(right)])))
            pair_counts[pair] += 1
    return set(pair_counts), pair_counts


def rasterize_geometries(geometries: dict[str, object], codes: list[str], footprint_payload: dict) -> np.ndarray:
    grid = footprint_payload["grid"]
    spacing = float(grid["spacing_degrees"])
    latitudes = float(grid["latitude_start"]) + spacing * np.arange(ROWS)
    longitudes = float(grid["longitude_start"]) + spacing * np.arange(COLUMNS)
    lon_mesh, lat_mesh = np.meshgrid(longitudes, latitudes)
    assignments = np.full((ROWS, COLUMNS), -1, dtype=np.int16)
    for index, code in enumerate(codes):
        inside = contains_xy(geometries[code], lon_mesh, lat_mesh)
        if np.any(inside & (assignments >= 0)):
            raise ValueError(f"fresh source geometry overlaps an earlier province at sampled centers: {code}")
        assignments[inside] = index
    return assignments


def derive(
    raw: bytes,
    headers: dict[str, str | None],
    output_path: Path = OUTPUT,
    rejected_path: Path = REJECTED,
    receipt_path: Path = RECEIPT,
    browser_path: Path = BROWSER,
) -> dict:
    footprints = json.loads(FOOTPRINTS.read_text(encoding="utf-8"))
    geometries, properties, repairs = load_geometries(raw)
    codes = sorted(geometries)
    committed_assignments, committed_codes = decode_footprint_runs(footprints)
    if codes != committed_codes:
        raise ValueError("fresh geometry codes do not match the committed 54-province footprint edition")
    fresh_assignments = rasterize_geometries(geometries, codes, footprints)
    matching_cells = int(np.count_nonzero(fresh_assignments == committed_assignments))
    total_cells = int(fresh_assignments.size)
    if matching_cells != total_cells:
        raise ValueError(f"fresh Version 4 geometry changes {total_cells - matching_cells} committed grid assignments")

    edges, rejected = classify_contacts(geometries)
    sampled_pairs, sampled_counts = sampled_neighbor_pairs(committed_assignments, codes)
    source_pairs = {tuple(edge["provinces"]) for edge in edges}
    for edge in edges:
        pair = tuple(edge["provinces"])
        edge["sampled_grid_cross_edge_pair_count"] = int(sampled_counts[pair])
        edge["sampled_grid_support"] = pair in sampled_pairs

    sampled_only = sorted(sampled_pairs - source_pairs)
    for pair in sampled_only:
        rejected.append({
            "candidate_id": f"{pair[0]}--{pair[1]}",
            "provinces": list(pair),
            "disposition": "rejected_sampled_grid_only_neighbor",
            "sampled_grid_cross_edge_pair_count": int(sampled_counts[pair]),
            "reason": "Neighboring 0.25-degree assigned centers do not establish a shared source-polygon edge.",
        })

    degree = Counter()
    shared_km = Counter()
    for edge in edges:
        for code in edge["provinces"]:
            degree[code] += 1
            shared_km[code] += edge["shared_boundary_length_km"]
    nodes = []
    for code in codes:
        node = dict(properties[code])
        node.update({
            "degree": degree[code],
            "shared_boundary_length_km": round(shared_km[code], 3),
            "neighbors": sorted(other for edge in edges if code in edge["provinces"] for other in edge["provinces"] if other != code),
        })
        nodes.append(node)

    source_sha256 = sha256_bytes(raw)
    geometry_sha256 = normalized_geometry_sha256(geometries, properties)
    payload = {
        "schema": "osw-longhurst-2007-province-adjacency-v1",
        "geometry_edition": footprints["geometry_edition"],
        "source_response_sha256": source_sha256,
        "normalized_repaired_geometry_sha256": geometry_sha256,
        "committed_footprint_source_response_sha256": footprints["geometry_source_sha256"],
        "committed_footprint_path": str(FOOTPRINTS.relative_to(ROOT)).replace("\\", "/"),
        "committed_footprint_sha256": sha256_file(FOOTPRINTS),
        "contract": {
            "accepted_contact": "non-zero geodesic length in the exact shared source-boundary intersection after declared validity repair",
            "point_contact": "source-boundary distance no greater than 1e-8 degrees with zero shared linear length; rejected from the edge graph",
            "near_miss_tolerances_degrees": list(NEAR_MISS_TOLERANCES_DEGREES),
            "longitude_seam": "Source multipolygons remain in EPSG:4326; exact shared coordinates are tested on both encoded sides of the antimeridian, and the committed raster comparison wraps first and last longitude columns.",
            "grid_support": "0.25-degree source-assignment centers are a separate support diagnostic, not the adjacency identity test.",
            "mask": "Topology uses source polygons independent of GEBCO wet/non-wet status; physical coastline, ice, gateway, and transport classes remain undetermined.",
        },
        "summary": {
            "node_count": len(nodes),
            "accepted_shared_edge_count": len(edges),
            "source_edges_with_sampled_grid_support": sum(edge["sampled_grid_support"] for edge in edges),
            "source_edges_without_sampled_grid_support": sum(not edge["sampled_grid_support"] for edge in edges),
            "rejected_candidate_count": len(rejected),
            "rejected_counts_by_disposition": dict(sorted(Counter(item["disposition"] for item in rejected).items())),
            "minimum_degree": min(degree.values()),
            "maximum_degree": max(degree.values()),
            "mean_degree": round(sum(degree.values()) / len(nodes), 6),
            "fresh_to_committed_assignment_matching_cells": matching_cells,
            "fresh_to_committed_assignment_total_cells": total_cells,
        },
        "nodes": nodes,
        "edges": edges,
        "boundary": "A deterministic graph of shared static Version 4 polygon edges. It does not identify a material wall, current, front, gateway, water mass, ecological interaction, volume exchange, heat transport, retention, causation, or full-depth coherence. Shared-edge length is spherical great-circle segment length of the encoded common source boundary, not navigational or coast-resolution geometry.",
    }
    rejected_payload = {
        "schema": "osw-longhurst-2007-province-adjacency-rejected-v1",
        "source_adjacency_sha256": None,
        "contract": payload["contract"],
        "candidates": sorted(rejected, key=lambda item: (item["candidate_id"], item["disposition"])),
        "boundary": "Rejected candidates are retained for audit. Point contacts, tolerance-only proximity, and sampled-grid neighbors are not promoted to shared source edges.",
    }
    encoded = json.dumps(payload, separators=(",", ":"))
    output_path.write_text(encoded + "\n", encoding="utf-8", newline="\n")
    rejected_payload["source_adjacency_sha256"] = sha256_file(output_path)
    rejected_path.write_text(json.dumps(rejected_payload, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    browser_path.write_text("window.OSW_PROVINCE_ADJACENCY = " + encoded + ";\n", encoding="utf-8", newline="\n")
    receipt = {
        "schema": "osw-longhurst-2007-province-adjacency-source-receipt-v1",
        "acquired_utc": datetime.now(timezone.utc).isoformat(),
        "source_payload_posture": "provider bytes omitted; exact URL, response metadata, byte count, SHA-256, normalized topology derivative, and full committed-grid equivalence retained",
        "source": {
            "provider": "Flanders Marine Institute (VLIZ), Marine Regions",
            "product": "Longhurst Provinces Version 4, March 2010",
            "url": GEOMETRY_URL,
            "feature_count": 54,
            "crs": "EPSG:4326",
            "license": "CC BY 4.0 under the current Marine Regions license statement; attribution required",
            "citation": f"Flanders Marine Institute (2009). Longhurst Provinces. Available online at https://www.marineregions.org/. Consulted on {datetime.now(timezone.utc).date().isoformat()}.",
            "response_bytes": len(raw),
            "response_sha256": source_sha256,
            "normalized_repaired_geometry_sha256": geometry_sha256,
            "headers": headers,
        },
        "compatibility": {
            "earlier_raw_response_sha256": footprints["geometry_source_sha256"],
            "raw_response_bytes_match": source_sha256 == footprints["geometry_source_sha256"],
            "full_assignment_grid_match": matching_cells == total_cells,
            "matching_cells": matching_cells,
            "total_cells": total_cells,
            "interpretation": "The mutable WFS response bytes differ from the earlier receipt, while all 1,036,800 Version 4 assignments on the committed 0.25-degree analysis grid are identical. This establishes grid-level geometry compatibility, not byte identity or native-coordinate identity.",
        },
        "geometry_repairs": repairs,
        "outputs": {
            "adjacency": str(output_path.relative_to(ROOT)).replace("\\", "/"),
            "adjacency_sha256": sha256_file(output_path),
            "rejected": str(rejected_path.relative_to(ROOT)).replace("\\", "/"),
            "rejected_sha256": sha256_file(rejected_path),
        },
        "boundary": payload["boundary"],
    }
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    return payload


def acquire(
    output_path: Path = OUTPUT,
    rejected_path: Path = REJECTED,
    receipt_path: Path = RECEIPT,
    browser_path: Path = BROWSER,
) -> dict:
    raw, headers = fetch_geometry()
    return derive(raw, headers, output_path, rejected_path, receipt_path, browser_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--rejected", type=Path, default=REJECTED)
    parser.add_argument("--receipt", type=Path, default=RECEIPT)
    parser.add_argument("--browser", type=Path, default=BROWSER)
    args = parser.parse_args()
    result = acquire(args.output, args.rejected, args.receipt, args.browser)
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
