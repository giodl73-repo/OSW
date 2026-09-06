"""Derive three land-bounded native C-grid paths across the Greenland–Scotland Ridge."""

from __future__ import annotations

import argparse
import json
import pathlib

import netCDF4
import numpy as np

import derive_oras5_barents_section_bakeoff as grid


SECTIONS = (
    {
        "id": "denmark_strait",
        "name": "Denmark Strait",
        "start": {"land": "Greenland", "longitude_deg": -34.5, "latitude_deg": 66.3},
        "stop": {"land": "Iceland", "longitude_deg": -24.0, "latitude_deg": 66.5},
        "bounds": {"west": -40.0, "east": -20.0, "south": 63.0, "north": 69.0},
    },
    {
        "id": "iceland_faroe",
        "name": "Iceland–Faroe",
        "start": {"land": "Iceland", "longitude_deg": -13.5, "latitude_deg": 64.3},
        "stop": {"land": "Faroe", "longitude_deg": -6.8, "latitude_deg": 62.1},
        "bounds": {"west": -17.0, "east": -4.0, "south": 60.0, "north": 66.0},
    },
    {
        "id": "faroe_scotland",
        "name": "Faroe–Scotland",
        "start": {"land": "Faroe", "longitude_deg": -6.8, "latitude_deg": 61.8},
        "stop": {"land": "Scotland", "longitude_deg": -4.5, "latitude_deg": 58.8},
        "bounds": {"west": -10.0, "east": 0.0, "south": 57.0, "north": 64.0},
    },
)

CLOSURE_SECTIONS = (
    SECTIONS[0],
    {
        "id": "iceland_scotland_ridge",
        "name": "Iceland–Scotland Ridge continuous model closure",
        "start": SECTIONS[1]["start"],
        "stop": SECTIONS[2]["stop"],
        "bounds": {"west": -17.0, "east": 0.0, "south": 57.0, "north": 66.0},
    },
    {
        "id": "northern_north_sea",
        "name": "Northern North Sea model closure",
        "start": {"land": "Scotland", "longitude_deg": -1.5, "latitude_deg": 58.6},
        "stop": {"land": "Norway", "longitude_deg": 5.0, "latitude_deg": 58.0},
        "bounds": {"west": -4.0, "east": 8.0, "south": 56.0, "north": 61.0},
    },
)


def package(section, nodes, edges, node_lon, node_lat, ulon, ulat, vlon, vlat):
    signed = grid.signed_faces(nodes, edges, ulon, ulat, vlon, vlat)
    faces = []
    for face in signed:
        face["sign_outward_from_nordic_seas"] = face.pop("sign_into_barents")
        faces.append(face)
    face_ids = [(face["face"], face["y"], face["x"]) for face in faces]
    connected = all(
        sum(abs(a - b) for a, b in zip(nodes[index], nodes[index + 1])) == 1
        for index in range(len(nodes) - 1)
    )
    return {
        "id": section["id"],
        "name": section["name"],
        "semantics": "land-to-land native model section; positive normal points outward, southward from the Nordic Seas room",
        "start_target": section["start"],
        "stop_target": section["stop"],
        "start_node": {
            "y": int(nodes[0][0]), "x": int(nodes[0][1]),
            "longitude_deg": float(node_lon[nodes[0]]), "latitude_deg": float(node_lat[nodes[0]]),
            "modeled_coast": True,
        },
        "stop_node": {
            "y": int(nodes[-1][0]), "x": int(nodes[-1][1]),
            "longitude_deg": float(node_lon[nodes[-1]]), "latitude_deg": float(node_lat[nodes[-1]]),
            "modeled_coast": True,
        },
        "endpoint_offset_km": {
            "start": grid.distance_km(node_lon[nodes[0]], node_lat[nodes[0]], section["start"]["longitude_deg"], section["start"]["latitude_deg"]),
            "stop": grid.distance_km(node_lon[nodes[-1]], node_lat[nodes[-1]], section["stop"]["longitude_deg"], section["stop"]["latitude_deg"]),
        },
        "face_count": len(faces),
        "u_face_count": sum(face["face"] == "U" for face in faces),
        "v_face_count": sum(face["face"] == "V" for face in faces),
        "topology": {
            "connected_corner_chain": connected,
            "unique_faces": len(face_ids) == len(set(face_ids)),
            "corner_duplication_count": len(face_ids) - len(set(face_ids)),
        },
        "faces": faces,
    }


def derive(mesh_path: pathlib.Path) -> dict:
    with netCDF4.Dataset(mesh_path) as dataset:
        tmask = np.asarray(dataset.variables["tmask"][0]) > 0
        umask = np.asarray(dataset.variables["umask"][0]) > 0
        vmask = np.asarray(dataset.variables["vmask"][0]) > 0
        ulon = grid.normalize_longitude(dataset.variables["glamu"][:])
        ulat = np.asarray(dataset.variables["gphiu"][:], dtype=float)
        vlon = grid.normalize_longitude(dataset.variables["glamv"][:])
        vlat = np.asarray(dataset.variables["gphiv"][:], dtype=float)
    node_lon, node_lat = grid.build_node_coordinates(umask, vmask, ulon, ulat, vlon, vlat)
    coast = grid.coastal_nodes(tmask, node_lon, node_lat)
    terminal_coast = [node for node in coast if len(list(grid.incident_edges(node, umask, vmask))) == 1]
    paths = []
    endpoint_edge_candidates = {}
    for section in SECTIONS:
        start = grid.nearest_node(coast, node_lon, node_lat, section["start"])
        stop = grid.nearest_node(coast, node_lon, node_lat, section["stop"])
        nodes, edges = grid.shortest_face_path(
            start, stop, umask, vmask, node_lon, node_lat, ulon, ulat, vlon, vlat,
            section["start"], section["stop"], corridor_scale_km=20.0,
            search_bounds=section["bounds"],
        )
        paths.append(package(section, nodes, edges, node_lon, node_lat, ulon, ulat, vlon, vlat))
        candidates = []
        for start_edge in sorted(edge for _, edge in grid.incident_edges(start, umask, vmask)):
            for stop_edge in sorted(edge for _, edge in grid.incident_edges(stop, umask, vmask)):
                try:
                    candidate_nodes, candidate_edges = grid.shortest_face_path(
                        start, stop, umask, vmask, node_lon, node_lat, ulon, ulat, vlon, vlat,
                        section["start"], section["stop"], corridor_scale_km=20.0,
                        search_bounds=section["bounds"], start_edge=start_edge, stop_edge=stop_edge,
                    )
                except ValueError:
                    continue
                candidate = package(section, candidate_nodes, candidate_edges, node_lon, node_lat, ulon, ulat, vlon, vlat)
                candidate["candidate_id"] = f"start-{start_edge[0]}-{start_edge[1]}-{start_edge[2]}__stop-{stop_edge[0]}-{stop_edge[1]}-{stop_edge[2]}"
                candidate["endpoint_edges"] = {"start": list(start_edge), "stop": list(stop_edge)}
                candidates.append(candidate)
        endpoint_edge_candidates[section["id"]] = candidates
    closure_sections = []
    for section in CLOSURE_SECTIONS:
        start = grid.nearest_node(terminal_coast, node_lon, node_lat, section["start"])
        stop = grid.nearest_node(terminal_coast, node_lon, node_lat, section["stop"])
        nodes, edges = grid.shortest_face_path(
            start, stop, umask, vmask, node_lon, node_lat, ulon, ulat, vlon, vlat,
            section["start"], section["stop"], corridor_scale_km=20.0,
            search_bounds=section["bounds"],
        )
        closure_sections.append(package(section, nodes, edges, node_lon, node_lat, ulon, ulat, vlon, vlat))
    all_faces = [(face["face"], face["y"], face["x"]) for path in paths for face in path["faces"]]
    return {
        "schema": "osw.oras5.nordic-southern-sections.v1",
        "status": "three_native_land_bounded_paths_derived_closure_not_yet_proven",
        "mesh": {"path": f"atlas/data/{mesh_path.name}", "sha256": grid.sha256_file(mesh_path)},
        "orientation": "each path runs west-to-east along the ridge; stored signs point to its right, outward from the Nordic Seas",
        "sections": paths,
        "endpoint_edge_candidates": endpoint_edge_candidates,
        "closure_sections": closure_sections,
        "representation_fork": {
            "three_named_paths": "geographically legible, but the fixed Faroe endpoints do not produce a closed surface cut on this ORCA025 mask",
            "control_volume_closures": "Denmark Strait plus one continuous Iceland–Scotland Ridge path ending at degree-one modeled coastal nodes; gateway subreporting requires a later virtual waypoint convention",
            "north_sea_requirement": "Britain and continental Europe are separated by water; a northern North Sea section is required unless the domain extends south to an explicit English Channel closure",
        },
        "union_topology": {
            "section_count": len(paths),
            "face_count": len(all_faces),
            "unique_faces": len(all_faces) == len(set(all_faces)),
            "duplicate_face_count": len(all_faces) - len(set(all_faces)),
        },
        "boundary": "Native surface paths only. Full-depth geometry and whole-room T-cell closure remain untested; no state, transport, heat, or delivery result is calculated.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-nordic-seas-mesh.nc"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-southern-sections.json"))
    args = parser.parse_args()
    result = derive(args.mesh)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print("wrote", args.output, [(item["id"], item["face_count"]) for item in result["sections"]])


if __name__ == "__main__":
    main()
