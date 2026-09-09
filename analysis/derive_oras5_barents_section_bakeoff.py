"""Build separate Barents observational-proxy and model-closure C-grid paths."""

from __future__ import annotations

import argparse
import hashlib
import heapq
import json
import pathlib

import netCDF4
import numpy as np


PROXY_START = {"name": "Fugloya virtual anchor", "longitude_deg": 20.0, "latitude_deg": 70.5}
PROXY_STOP = {"name": "Bear Island virtual anchor", "longitude_deg": 18.9, "latitude_deg": 74.4}
SEARCH_BOUNDS = {"west": 10.0, "east": 31.0, "south": 69.0, "north": 78.0}


def normalize_longitude(values):
    return ((np.asarray(values, dtype=float) + 180.0) % 360.0) - 180.0


def incident_edges(node, umask, vmask):
    y, x = node
    ny, nx = umask.shape
    if y > 0 and umask[y, x]:
        yield (y - 1, x), ("U", y, x)
    if y + 1 < ny and umask[y + 1, x]:
        yield (y + 1, x), ("U", y + 1, x)
    if x > 0 and vmask[y, x]:
        yield (y, x - 1), ("V", y, x)
    if x + 1 < nx and vmask[y, x + 1]:
        yield (y, x + 1), ("V", y, x + 1)


def build_node_coordinates(umask, vmask, ulon, ulat, vlon, vlat):
    ny, nx = umask.shape
    lon = np.full((ny, nx), np.nan)
    lat = np.full((ny, nx), np.nan)
    for y in range(ny):
        for x in range(nx):
            points = []
            for _, (kind, fy, fx) in incident_edges((y, x), umask, vmask):
                points.append((ulon[fy, fx], ulat[fy, fx]) if kind == "U" else (vlon[fy, fx], vlat[fy, fx]))
            if points:
                lon[y, x] = float(np.mean([point[0] for point in points]))
                lat[y, x] = float(np.mean([point[1] for point in points]))
    return lon, lat


def coastal_nodes(tmask, node_lon, node_lat):
    ny, nx = tmask.shape
    result = []
    for y in range(ny - 1):
        for x in range(nx - 1):
            cells = tmask[y:y + 2, x:x + 2]
            if np.any(cells) and not np.all(cells) and np.isfinite(node_lon[y, x]):
                result.append((y, x))
    return result


def distance_km(lon1, lat1, lon2, lat2):
    scale = np.cos(np.deg2rad((lat1 + lat2) / 2.0))
    return float(111.0 * np.hypot((lon1 - lon2) * scale, lat1 - lat2))


def nearest_node(nodes, node_lon, node_lat, target):
    return min(nodes, key=lambda node: distance_km(node_lon[node], node_lat[node], target["longitude_deg"], target["latitude_deg"]))


def segment_distance_km(lon, lat, start, stop):
    mean_lat = (start["latitude_deg"] + stop["latitude_deg"]) / 2.0
    scale = np.cos(np.deg2rad(mean_lat))
    point = np.array([lon * scale, lat])
    a = np.array([start["longitude_deg"] * scale, start["latitude_deg"]])
    b = np.array([stop["longitude_deg"] * scale, stop["latitude_deg"]])
    delta = b - a
    fraction = np.clip(np.dot(point - a, delta) / np.dot(delta, delta), 0.0, 1.0)
    return float(np.linalg.norm(point - (a + fraction * delta)) * 111.0)


def edge_coordinate(edge, ulon, ulat, vlon, vlat):
    kind, y, x = edge
    return (float(ulon[y, x]), float(ulat[y, x])) if kind == "U" else (float(vlon[y, x]), float(vlat[y, x]))


def shortest_face_path(start_node, stop_node, umask, vmask, node_lon, node_lat, ulon, ulat, vlon, vlat, reference_start, reference_stop, corridor_scale_km=20.0, search_bounds=None, start_edge=None, stop_edge=None):
    if corridor_scale_km <= 0:
        raise ValueError("corridor_scale_km must be positive")
    bounds = search_bounds or SEARCH_BOUNDS
    queue = [(0.0, start_node)]
    distance = {start_node: 0.0}
    previous = {}
    while queue:
        cost, node = heapq.heappop(queue)
        if cost != distance[node]:
            continue
        if node == stop_node:
            break
        for neighbor, edge in incident_edges(node, umask, vmask):
            if node == start_node and start_edge is not None and edge != start_edge:
                continue
            if neighbor == stop_node and stop_edge is not None and edge != stop_edge:
                continue
            lon, lat = edge_coordinate(edge, ulon, ulat, vlon, vlat)
            if not (bounds["west"] <= lon <= bounds["east"] and bounds["south"] <= lat <= bounds["north"]):
                continue
            offset = segment_distance_km(lon, lat, reference_start, reference_stop)
            step_cost = 1.0 + (offset / corridor_scale_km) ** 2
            # Quantize accumulated costs before comparing them. Equivalent
            # grid routes can otherwise diverge across BLAS/libm platforms at
            # machine precision, changing the pinned face path on Linux versus
            # Windows without a meaningful cost difference.
            candidate = round(cost + step_cost, 10)
            if candidate < distance.get(neighbor, np.inf):
                distance[neighbor] = candidate
                previous[neighbor] = (node, edge)
                heapq.heappush(queue, (candidate, neighbor))
    if stop_node not in distance:
        raise ValueError("no connected wet-face path joins the declared endpoints")
    nodes = [stop_node]
    edges = []
    while nodes[-1] != start_node:
        prior, edge = previous[nodes[-1]]
        edges.append(edge)
        nodes.append(prior)
    nodes.reverse(); edges.reverse()
    return nodes, edges


def signed_faces(nodes, edges, ulon, ulat, vlon, vlat):
    result = []
    for start, stop, edge in zip(nodes[:-1], nodes[1:], edges):
        kind, y, x = edge
        if kind == "U":
            sign = 1 if stop[0] > start[0] else -1
        else:
            sign = -1 if stop[1] > start[1] else 1
        lon, lat = edge_coordinate(edge, ulon, ulat, vlon, vlat)
        result.append({"face": kind, "y": int(y), "x": int(x), "sign_into_barents": sign, "longitude_deg": lon, "latitude_deg": lat})
    return result


def package_path(name, semantics, nodes, edges, node_lon, node_lat, ulon, ulat, vlon, vlat, start_target, stop_target, start_is_coast, stop_is_coast):
    faces = signed_faces(nodes, edges, ulon, ulat, vlon, vlat)
    face_ids = [(face["face"], face["y"], face["x"]) for face in faces]
    node_degrees = {node: 0 for node in nodes}
    for a, b in zip(nodes[:-1], nodes[1:]):
        node_degrees[a] += 1; node_degrees[b] += 1
    connected = all(sum(abs(a - b) for a, b in zip(nodes[index], nodes[index + 1])) == 1 for index in range(len(nodes) - 1))
    topology = {
        "connected_corner_chain": connected,
        "unique_faces": len(face_ids) == len(set(face_ids)),
        "endpoint_degree_one": node_degrees[nodes[0]] == node_degrees[nodes[-1]] == 1,
        "all_internal_degrees_two": all(node_degrees[node] == 2 for node in nodes[1:-1]),
        "corner_duplication_count": len(face_ids) - len(set(face_ids)),
    }
    return {
        "name": name,
        "semantics": semantics,
        "start_target": start_target,
        "stop_target": stop_target,
        "start_node": {"y": int(nodes[0][0]), "x": int(nodes[0][1]), "longitude_deg": float(node_lon[nodes[0]]), "latitude_deg": float(node_lat[nodes[0]]), "modeled_coast": start_is_coast},
        "stop_node": {"y": int(nodes[-1][0]), "x": int(nodes[-1][1]), "longitude_deg": float(node_lon[nodes[-1]]), "latitude_deg": float(node_lat[nodes[-1]]), "modeled_coast": stop_is_coast},
        "face_count": len(faces),
        "u_face_count": sum(face["face"] == "U" for face in faces),
        "v_face_count": sum(face["face"] == "V" for face in faces),
        "topology": topology,
        "faces": faces,
    }


def sha256_file(path):
    digest = hashlib.sha256()
    with pathlib.Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def derive_file(mesh_path: pathlib.Path) -> dict:
    with netCDF4.Dataset(mesh_path) as dataset:
        tmask = np.asarray(dataset.variables["tmask"][0]) > 0
        umask = np.asarray(dataset.variables["umask"][0]) > 0
        vmask = np.asarray(dataset.variables["vmask"][0]) > 0
        ulon = normalize_longitude(dataset.variables["glamu"][:]); ulat = np.asarray(dataset.variables["gphiu"][:], dtype=float)
        vlon = normalize_longitude(dataset.variables["glamv"][:]); vlat = np.asarray(dataset.variables["gphiv"][:], dtype=float)
    node_lon, node_lat = build_node_coordinates(umask, vmask, ulon, ulat, vlon, vlat)
    valid_nodes = list(zip(*np.where(np.isfinite(node_lon))))
    coast = coastal_nodes(tmask, node_lon, node_lat)
    proxy_start = nearest_node(valid_nodes, node_lon, node_lat, PROXY_START)
    proxy_stop = nearest_node(valid_nodes, node_lon, node_lat, PROXY_STOP)
    proxy_nodes, proxy_edges = shortest_face_path(proxy_start, proxy_stop, umask, vmask, node_lon, node_lat, ulon, ulat, vlon, vlat, PROXY_START, PROXY_STOP)
    closure_start = nearest_node(coast, node_lon, node_lat, PROXY_START)
    closure_stop = nearest_node(coast, node_lon, node_lat, PROXY_STOP)
    closure_reference_stop = {"name": "nearest represented northern coast", "longitude_deg": float(node_lon[closure_stop]), "latitude_deg": float(node_lat[closure_stop])}
    closure_nodes, closure_edges = shortest_face_path(closure_start, closure_stop, umask, vmask, node_lon, node_lat, ulon, ulat, vlon, vlat, PROXY_START, closure_reference_stop)
    proxy = package_path("Fugloya-Bear observational proxy", "open virtual-endpoint comparison section; model water may bypass either endpoint", proxy_nodes, proxy_edges, node_lon, node_lat, ulon, ulat, vlon, vlat, PROXY_START, PROXY_STOP, proxy_start in coast, proxy_stop in coast)
    closure = package_path("Norway-Svalbard model closure", "land-to-land model-grid boundary; not the observational Fugloya-Bear section", closure_nodes, closure_edges, node_lon, node_lat, ulon, ulat, vlon, vlat, PROXY_START, closure_reference_stop, True, True)
    return {
        "schema": "oceanlines.osw.m3-oras5-barents-section-bakeoff.v1",
        "status": "two_topologically_valid_sections_with_noninterchangeable_semantics",
        "mesh": {"path": str(mesh_path), "sha256": sha256_file(mesh_path)},
        "observational_proxy": proxy,
        "model_closure": closure,
        "comparison": {
            "same_start_node": proxy["start_node"]["y"] == closure["start_node"]["y"] and proxy["start_node"]["x"] == closure["start_node"]["x"],
            "proxy_stop_is_modeled_coast": proxy["stop_node"]["modeled_coast"],
            "closure_stop_distance_from_bear_target_km": distance_km(closure["stop_node"]["longitude_deg"], closure["stop_node"]["latitude_deg"], PROXY_STOP["longitude_deg"], PROXY_STOP["latitude_deg"]),
            "interpretation": "Topology can validate both paths, but cannot make their endpoints or measured domains equivalent.",
        },
        "boundary": "Surface face-path geometry only. No state variables, face thickness, transport, heat, Atlantic Water class, observational agreement, or Arctic delivery is calculated.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-arctic-entrances-mesh.nc"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-barents-section-bakeoff.json"))
    args = parser.parse_args()
    result = derive_file(args.mesh)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}: proxy={result['observational_proxy']['face_count']} faces; closure={result['model_closure']['face_count']} faces")


if __name__ == "__main__":
    main()
