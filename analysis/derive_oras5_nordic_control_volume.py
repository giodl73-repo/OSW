"""Join five native sections and land into one Nordic Seas surface control volume."""

from __future__ import annotations

import argparse
from collections import deque
import itertools
import json
import pathlib

import netCDF4
import numpy as np

import derive_oras5_barents_section_bakeoff as grid


def adjacent_cells(face):
    kind, y, x = face["face"], face["y"], face["x"]
    if kind == "U":
        return (y, x), (y, x + 1)
    return (y, x), (y + 1, x)


def remap_fram(mesh_path: pathlib.Path, source: dict) -> dict:
    with netCDF4.Dataset(mesh_path) as dataset:
        mask = np.asarray(dataset.variables["vmask"][0]) > 0
        lon = grid.normalize_longitude(dataset.variables["glamv"][:])
        lat = np.asarray(dataset.variables["gphiv"][:], dtype=float)
    candidates = np.argwhere(mask & (lon >= -25) & (lon <= 20) & (lat >= 76) & (lat <= 81))
    faces = []
    for target_lon, target_lat in zip(source["longitude_deg"], source["latitude_deg"]):
        distances = np.array([
            grid.distance_km(lon[y, x], lat[y, x], target_lon, target_lat)
            for y, x in candidates
        ])
        y, x = candidates[int(np.argmin(distances))]
        faces.append({
            "face": "V", "y": int(y), "x": int(x),
            "sign_outward_from_nordic_seas": 1,
            "longitude_deg": float(lon[y, x]), "latitude_deg": float(lat[y, x]),
            "source_coordinate_offset_km": float(np.min(distances)),
        })
    ids = [(face["y"], face["x"]) for face in faces]
    return {
        "id": "fram_strait",
        "name": "Fram Strait",
        "semantics": "accepted land-bounded V-face row remapped by coordinates; positive native +j points outward into the Arctic",
        "face_count": len(faces),
        "unique_faces": len(ids) == len(set(ids)),
        "land_bounded_at_surface": not mask[faces[0]["y"], faces[0]["x"] - 1] and not mask[faces[-1]["y"], faces[-1]["x"] + 1],
        "maximum_remap_offset_km": max(face["source_coordinate_offset_km"] for face in faces),
        "faces": faces,
    }


def outward_barents(source: dict) -> dict:
    result = {key: value for key, value in source.items() if key != "faces"}
    result["id"] = "norway_svalbard"
    result["faces"] = []
    for original in source["faces"]:
        face = dict(original)
        face["sign_outward_from_nordic_seas"] = face.pop("sign_into_barents")
        result["faces"].append(face)
    return result


def nearest_wet_cell(tmask, lon, lat, target_lon=-5.0, target_lat=70.0):
    distance = 111.0 * np.hypot((lon - target_lon) * np.cos(np.deg2rad(target_lat)), lat - target_lat)
    distance = np.where(tmask, distance, np.inf)
    return tuple(int(value) for value in np.unravel_index(np.argmin(distance), distance.shape))


def flood_inside(tmask, blocked, seed):
    inside = np.zeros_like(tmask, dtype=bool)
    inside[seed] = True
    queue = deque([seed])
    ny, nx = tmask.shape
    while queue:
        y, x = queue.popleft()
        neighbors = (
            ((y, x - 1), ("U", y, x - 1)),
            ((y, x + 1), ("U", y, x)),
            ((y - 1, x), ("V", y - 1, x)),
            ((y + 1, x), ("V", y, x)),
        )
        for (yy, xx), edge in neighbors:
            if 0 <= yy < ny and 0 <= xx < nx and tmask[yy, xx] and not inside[yy, xx] and edge not in blocked:
                inside[yy, xx] = True
                queue.append((yy, xx))
    return inside


def derive(mesh_path: pathlib.Path, southern_path: pathlib.Path, barents_path: pathlib.Path, fram_path: pathlib.Path) -> dict:
    southern = json.loads(southern_path.read_text(encoding="utf-8"))
    barents = json.loads(barents_path.read_text(encoding="utf-8"))
    fram_source = json.loads(fram_path.read_text(encoding="utf-8"))["fram"]
    with netCDF4.Dataset(mesh_path) as dataset:
        tmask = np.asarray(dataset.variables["tmask"][0]) > 0
        lon = grid.normalize_longitude(dataset.variables["glamt"][:])
        lat = np.asarray(dataset.variables["gphit"][:], dtype=float)
    fixed_sections = [remap_fram(mesh_path, fram_source), outward_barents(barents["model_closure"])]
    candidate_groups = [southern["endpoint_edge_candidates"][key] for key in ("denmark_strait", "iceland_faroe", "faroe_scotland")]
    selected = None
    selection_score = None
    for candidate_tuple in itertools.product(*candidate_groups):
        trial_sections = [*candidate_tuple, *fixed_sections]
        trial_ids = [(face["face"], face["y"], face["x"]) for section in trial_sections for face in section["faces"]]
        if len(trial_ids) != len(set(trial_ids)):
            continue
        trial_inside = flood_inside(tmask, set(trial_ids), nearest_wet_cell(tmask, lon, lat))
        if np.any(trial_inside[0]) or np.any(trial_inside[-1]) or np.any(trial_inside[:, 0]) or np.any(trial_inside[:, -1]):
            continue
        trial_separates = True
        for section in trial_sections:
            for face in section["faces"]:
                a, b = adjacent_cells(face)
                if bool(trial_inside[a]) == bool(trial_inside[b]):
                    trial_separates = False
                    break
            if not trial_separates:
                break
        if trial_separates:
            score = (sum(section["face_count"] for section in candidate_tuple), tuple(section["candidate_id"] for section in candidate_tuple))
            if selection_score is None or score < selection_score:
                selection_score = score
                selected = list(candidate_tuple)
    three_path_selection = selected
    closure_sections = southern["closure_sections"]
    closure_face_ids = [(face["face"], face["y"], face["x"]) for section in [*closure_sections, *fixed_sections] for face in section["faces"]]
    closure_inside = flood_inside(tmask, set(closure_face_ids), nearest_wet_cell(tmask, lon, lat))
    closure_edge_contact = bool(np.any(closure_inside[0]) or np.any(closure_inside[-1]) or np.any(closure_inside[:, 0]) or np.any(closure_inside[:, -1]))
    if not closure_edge_contact and len(closure_face_ids) == len(set(closure_face_ids)):
        selected = closure_sections
        selected_representation = "three_land_bounded_southern_closures"
    else:
        selected = three_path_selection or southern["sections"]
        selected_representation = "three_named_paths_unclosed"
    sections = [*selected, *fixed_sections]
    face_ids = [(face["face"], face["y"], face["x"]) for section in sections for face in section["faces"]]
    blocked = set(face_ids)
    seed = nearest_wet_cell(tmask, lon, lat)
    inside = flood_inside(tmask, blocked, seed)
    ny, nx = tmask.shape
    edge_contact = bool(np.any(inside[0]) or np.any(inside[-1]) or np.any(inside[:, 0]) or np.any(inside[:, -1]))
    separating = []
    for section in sections:
        count = 0
        for face in section["faces"]:
            a, b = adjacent_cells(face)
            if 0 <= a[0] < ny and 0 <= a[1] < nx and 0 <= b[0] < ny and 0 <= b[1] < nx and bool(inside[a]) != bool(inside[b]):
                count += 1
        separating.append({"id": section["id"], "face_count": section["face_count"], "inside_outside_separating_faces": count})
    interior_indices = np.argwhere(inside)
    return {
        "schema": "osw.oras5.nordic-control-volume.v1",
        "status": "closed_surface_control_volume" if not edge_contact and len(face_ids) == len(blocked) and all(item["face_count"] == item["inside_outside_separating_faces"] for item in separating) else "surface_closure_failed",
        "mesh": {"path": f"atlas/data/{mesh_path.name}", "sha256": grid.sha256_file(mesh_path)},
        "seed": {"y": seed[0], "x": seed[1], "longitude_deg": float(lon[seed]), "latitude_deg": float(lat[seed])},
        "sections": sections,
        "southern_candidate_selection": {
            "method": "enumerate every wet incident start/stop edge at the fixed coastal nodes; retain combinations that create one edge-isolated seed component; choose the shortest deterministic face union",
            "combinations_tested": int(np.prod([len(group) for group in candidate_groups])),
            "three_named_path_closed_combination_found": three_path_selection is not None,
            "three_named_path_selected_candidate_ids": [section["candidate_id"] for section in three_path_selection] if three_path_selection else [],
            "selected_representation": selected_representation,
            "scientific_reason": "ORCA025 does not support two independent land-attached cuts at the fixed Faroe intents; the control-volume boundary therefore uses one continuous Iceland–Scotland Ridge section and an explicit northern North Sea closure because Britain is not joined to continental Europe",
        },
        "topology": {
            "section_count": len(sections),
            "boundary_face_count": len(face_ids),
            "unique_boundary_faces": len(face_ids) == len(blocked),
            "duplicate_boundary_face_count": len(face_ids) - len(blocked),
            "inside_wet_t_cell_count": int(np.sum(inside)),
            "inside_reaches_mesh_edge": edge_contact,
            "every_boundary_face_separates_inside_from_outside": all(item["face_count"] == item["inside_outside_separating_faces"] for item in separating),
            "section_separation": separating,
            "inside_index_extent": {
                "y_min": int(interior_indices[:, 0].min()), "y_max": int(interior_indices[:, 0].max()),
                "x_min": int(interior_indices[:, 1].min()), "x_max": int(interior_indices[:, 1].max()),
            },
            "inside_coordinate_extent_deg": {
                "west": float(np.min(lon[inside])), "east": float(np.max(lon[inside])),
                "south": float(np.min(lat[inside])), "north": float(np.max(lat[inside])),
            },
        },
        "inside_t_cells": [[int(y), int(x)] for y, x in interior_indices],
        "boundary": "Surface-mask topology only. Full-depth southern geometry, state fields, transport, heat, storage, and surface flux remain uncalculated.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-nordic-seas-mesh.nc"))
    parser.add_argument("--southern", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-southern-sections.json"))
    parser.add_argument("--barents", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-barents-section.json"))
    parser.add_argument("--fram", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-arctic-gate-readiness.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-control-volume.json"))
    args = parser.parse_args()
    result = derive(args.mesh, args.southern, args.barents, args.fram)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}: {result['status']}; {result['topology']['inside_wet_t_cell_count']} inside T cells")


if __name__ == "__main__":
    main()
