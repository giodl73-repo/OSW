"""Select the first province-edge exchange pilot without reading outcomes.

The selector may inspect geometry, masks, dimensions, and finite-value support.
It deliberately never summarizes or ranks velocity or temperature values.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

import netCDF4
import numpy as np
from shapely.geometry import shape

try:
    from acquire_longhurst_2007_adjacency import SOURCE_TO_OSW, fetch_geometry, normalized_geometry_sha256, repair_polygon, sha256_bytes
    from acquire_ocean_state_hydrography_pilot import assign_provinces, portable_path, sha256_file, sha256_text_file
except ImportError:  # pragma: no cover
    from analysis.acquire_longhurst_2007_adjacency import SOURCE_TO_OSW, fetch_geometry, normalized_geometry_sha256, repair_polygon, sha256_bytes
    from analysis.acquire_ocean_state_hydrography_pilot import assign_provinces, portable_path, sha256_file, sha256_text_file


ROOT = Path(__file__).resolve().parents[1]
MONTHS = ("201802", "201805", "201808", "201811")
MIN_MATCHED_FACES = 8
MAX_PAIRED_FACES = 2_000
REGIONAL_GEOMETRY_URL = (
    "https://geo.vliz.be/geoserver/MarineRegions/wfs?service=WFS&version=1.0.0"
    "&request=GetFeature&typeName=MarineRegions:longhurst"
    "&outputFormat=application/json&bbox=-83.25,-71.1,-39.5,-46.5,EPSG:4326"
)


def load_regional_geometries(raw: bytes) -> tuple[dict, dict]:
    collection = json.loads(raw)
    features = collection.get("features", [])
    if collection.get("type") != "FeatureCollection" or not features:
        raise ValueError("regional Longhurst WFS response has no features")
    geometries, properties = {}, {}
    for feature in sorted(features, key=lambda item: item["properties"]["provcode"]):
        source_code = feature["properties"]["provcode"]
        code = SOURCE_TO_OSW.get(source_code, source_code)
        geometry, _ = repair_polygon(shape(feature["geometry"]), source_code)
        geometries[code] = geometry
        properties[code] = {
            "osw_code": code,
            "source_code": source_code,
            "source_name": feature["properties"]["provdescr"],
            "source_mrgid": int(feature["properties"]["mrgid"]),
        }
    return geometries, properties


def boundary_faces(assignments: np.ndarray) -> dict[str, list[dict]]:
    """Return native interior faces whose adjacent T centers have different states."""
    found: dict[str, list[dict]] = {}
    rows, columns = assignments.shape
    for y in range(rows):
        for x in range(columns - 1):
            negative, positive = assignments[y, x], assignments[y, x + 1]
            if not negative or not positive or negative == positive:
                continue
            first, second = sorted((negative, positive))
            sign = 1 if negative == first else -1
            found.setdefault(f"{first}--{second}", []).append({"face": "U", "y": y, "x": x, "sign_first_to_second": sign})
    for y in range(rows - 1):
        for x in range(columns):
            negative, positive = assignments[y, x], assignments[y + 1, x]
            if not negative or not positive or negative == positive:
                continue
            first, second = sorted((negative, positive))
            sign = 1 if negative == first else -1
            found.setdefault(f"{first}--{second}", []).append({"face": "V", "y": y, "x": x, "sign_first_to_second": sign})
    return found


def displaced_control(face: dict, first: str, assignments: np.ndarray) -> dict | None:
    """Move a face one T cell into the lexicographic first province."""
    y, x, sign = face["y"], face["x"], face["sign_first_to_second"]
    rows, columns = assignments.shape
    if face["face"] == "U":
        cx = x - 1 if sign == 1 else x + 1
        if cx < 0 or cx + 1 >= columns or assignments[y, cx] != first or assignments[y, cx + 1] != first:
            return None
        return {"face": "U", "y": y, "x": cx, "sign_parallel_to_first_to_second": sign}
    cy = y - 1 if sign == 1 else y + 1
    if cy < 0 or cy + 1 >= rows or assignments[cy, x] != first or assignments[cy + 1, x] != first:
        return None
    return {"face": "V", "y": cy, "x": x, "sign_parallel_to_first_to_second": sign}


def wet_mask(face: dict, umask: np.ndarray, vmask: np.ndarray) -> np.ndarray:
    source = umask if face["face"] == "U" else vmask
    return source[:, face["y"], face["x"]]


def field_support(face: dict, states: dict[str, dict], umask: np.ndarray, vmask: np.ndarray) -> bool:
    wet = wet_mask(face, umask, vmask)
    if not np.any(wet):
        return False
    y, x = face["y"], face["x"]
    for arrays in states.values():
        velocity = arrays["u"][:, y, x] if face["face"] == "U" else arrays["v"][:, y, x]
        negative = arrays["temperature"][:, y, x]
        positive = arrays["temperature"][:, y, x + 1] if face["face"] == "U" else arrays["temperature"][:, y + 1, x]
        if not (np.all(np.isfinite(velocity[wet])) and np.all(np.isfinite(negative[wet])) and np.all(np.isfinite(positive[wet]))):
            return False
    return True


def build(root: Path = ROOT, acquired_at: str | None = None) -> dict:
    root = Path(root)
    acquired_at = acquired_at or datetime.now(timezone.utc).isoformat()
    graph_path = root / "research/longhurst-2007-province-adjacency.json"
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    raw, headers = fetch_geometry(REGIONAL_GEOMETRY_URL)
    geometries, properties = load_regional_geometries(raw)
    geometry_hash = normalized_geometry_sha256(geometries, properties)
    nodes = {item["osw_code"]: item for item in graph["nodes"]}
    if not geometries or any(
        code not in nodes
        or properties[code]["source_mrgid"] != nodes[code]["source_mrgid"]
        or properties[code]["source_code"] != nodes[code]["source_code"]
        for code in geometries
    ):
        raise ValueError("regional WFS identities differ from the frozen graph")

    mesh_receipt_path = root / "research/osw-m3-oras5-drake-mesh.json"
    mesh_receipt = json.loads(mesh_receipt_path.read_text(encoding="utf-8"))
    mesh_path = portable_path(root, mesh_receipt["output"]["path"])
    audit_path = root / "research/osw-m3-oras5-face-thickness-audit.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    with netCDF4.Dataset(mesh_path) as mesh:
        lon = np.asarray(mesh.variables["glamt"][:], dtype=float)
        lat = np.asarray(mesh.variables["gphit"][:], dtype=float)
        umask = np.asarray(mesh.variables["umask"][:], dtype=bool)
        vmask = np.asarray(mesh.variables["vmask"][:], dtype=bool)
    assignments, assignment_audit = assign_provinces(lon, lat, geometries)
    faces_by_edge = boundary_faces(assignments)

    states: dict[str, dict] = {}
    state_sources = []
    for month in MONTHS:
        receipt_path = root / f"research/osw-m3-oras5-drake-state-{month}.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        state_path = portable_path(root, receipt["output"]["path"])
        with netCDF4.Dataset(state_path) as state:
            states[month] = {
                "temperature": np.asarray(np.ma.filled(state.variables["votemper"][:], np.nan), dtype=float),
                "u": np.asarray(np.ma.filled(state.variables["vozocrtx"][:], np.nan), dtype=float),
                "v": np.asarray(np.ma.filled(state.variables["vomecrty"][:], np.nan), dtype=float),
            }
        state_sources.append({"month": month, "path": state_path.relative_to(root).as_posix(), "sha256": sha256_file(state_path)})

    candidates = []
    eligible = []
    for edge in graph["edges"]:
        edge_id = edge["edge_id"]
        first = edge["provinces"][0]
        native_faces = faces_by_edge.get(edge_id, [])
        supported_faces = [face for face in native_faces if field_support(face, states, umask, vmask)]
        paired = []
        for face in supported_faces:
            control = displaced_control(face, first, assignments)
            if control is None or not field_support(control, states, umask, vmask):
                continue
            if not np.array_equal(wet_mask(face, umask, vmask), wet_mask(control, umask, vmask)):
                continue
            paired.append({"boundary": face, "control": control})
        in_domain = bool(native_faces)
        gates = {
            "identity": True,
            "native_grid_geometry": in_domain,
            "compatible_fields": bool(supported_faces),
            "source_and_license_custody": in_domain,
            "matched_control": len(paired) >= MIN_MATCHED_FACES,
            "testable_numerics": in_domain and audit["status"] == "candidate_passes_native_geometry_consistency",
            "bounded_resource_scope": 0 < len(paired) <= MAX_PAIRED_FACES,
        }
        passes = all(gates.values())
        record = {
            "edge_id": edge_id,
            "provinces": edge["provinces"],
            "shared_boundary_length_km": edge["shared_boundary_length_km"],
            "native_boundary_face_count": len(native_faces),
            "complete_field_face_count": len(supported_faces),
            "exact_wet_mask_matched_control_face_count": len(paired),
            "matched_control_fraction": round(len(paired) / len(supported_faces), 6) if supported_faces else 0.0,
            "committed_0_25_degree_edge_support": edge["sampled_grid_support"],
            "eligibility": gates,
            "disposition": "eligible" if passes else "ineligible",
            "failure_reasons": [name for name, passed in gates.items() if not passed],
        }
        candidates.append(record)
        if passes:
            eligible.append((record, paired))

    if not eligible:
        raise ValueError("no candidate passes the frozen gates")
    eligible.sort(key=lambda item: (-item[0]["matched_control_fraction"], -item[0]["exact_wet_mask_matched_control_face_count"], not item[0]["committed_0_25_degree_edge_support"], item[0]["edge_id"]))
    selected, selected_pairs = eligible[0]
    attractive = next((item for item in candidates if item["edge_id"] == "ANTA--SANT" and item["edge_id"] != selected["edge_id"]), next(item for item in candidates if item["disposition"] == "ineligible"))
    return {
        "schema": "osw-ocean-state-exchange-pilot-selection-v1",
        "status": "pilot_selected_before_transport_outcomes",
        "selected_at": acquired_at,
        "candidate_source": {"path": graph_path.relative_to(root).as_posix(), "sha256": sha256_text_file(graph_path), "candidate_count": len(candidates)},
        "geometry_source": {"url": REGIONAL_GEOMETRY_URL, "content_location": headers.get("content_location"), "response_sha256": sha256_bytes(raw), "regional_normalized_repaired_geometry_sha256": geometry_hash, "identity_match_to_frozen_graph": True},
        "native_grid": {"path": mesh_path.relative_to(root).as_posix(), "sha256": sha256_file(mesh_path), "assignment_audit": assignment_audit, "face_thickness_audit": {"path": audit_path.relative_to(root).as_posix(), "sha256": sha256_text_file(audit_path), "status": audit["status"]}},
        "state_sources": state_sources,
        "frozen_thresholds": {"minimum_exact_wet_mask_matched_control_faces": MIN_MATCHED_FACES, "maximum_paired_faces_for_repository_scope": MAX_PAIRED_FACES, "field_support": "all wet velocity and both adjacent T-cell temperature values finite in all four months", "control_support": "one-cell displacement into first province with identical vertical wet mask"},
        "ordering": ["source_payload_already_under_valid_osw_custody", "native_grid_face_geometry_already_audited", "complete_vertical_and_seasonal_support", "matched_control_fraction_descending", "matched_control_face_count_descending", "committed_0_25_degree_edge_support", "stable_edge_id"],
        "prohibited_selection_inputs": ["velocity_magnitude", "transport_sign", "transport_magnitude", "temperature_contrast", "heat_transport", "desired_zoning_result"],
        "candidates": candidates,
        "eligible_edge_count": len(eligible),
        "selected_edge": selected,
        "selected_face_pairs": selected_pairs,
        "control_geometry": "Each retained boundary face is paired one-for-one with the same U/V orientation displaced one native T cell into the lexicographic first province; paired faces have identical vertical wet masks and complete four-month fields.",
        "attractive_rejected_or_lower_ranked_candidate": {"edge_id": attractive["edge_id"], "disposition": attractive["disposition"], "failure_reasons": attractive["failure_reasons"], "reason": "Not selected under the frozen lexicographic control-strength ordering; no transport outcome was inspected." if attractive["disposition"] == "eligible" else "Failed one or more frozen eligibility gates."},
        "boundary": "Selection tests one regional method. It does not validate this source edge as a front or barrier, equate it with Drake Passage, establish exchange, authorize global processing, or support a zoning revision.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=Path("research/ocean-state-exchange-pilot-selection-v1.json"))
    parser.add_argument("--acquired-at")
    args = parser.parse_args()
    result = build(args.root, args.acquired_at)
    output = args.output if args.output.is_absolute() else args.root / args.output
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"selected": result["selected_edge"]["edge_id"], "eligible": result["eligible_edge_count"], "paired_faces": len(result["selected_face_pairs"])}, indent=2))


if __name__ == "__main__":
    main()
