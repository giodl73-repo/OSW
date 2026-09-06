"""Challenge Barents native-face paths with endpoint and path-cost choices."""

from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib

import netCDF4
import numpy as np


BASE_PATH = pathlib.Path(__file__).with_name("derive_oras5_barents_section_bakeoff.py")
SPEC = importlib.util.spec_from_file_location("barents_base", BASE_PATH)
base = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(base)

CORRIDOR_SCALES_KM = (10.0, 20.0, 40.0)
ENDPOINT_CASES = {
    "baseline": (0.0, 0.0, 0.0, 0.0),
    "west": (-0.5, 0.0, -0.5, 0.0),
    "east": (0.5, 0.0, 0.5, 0.0),
    "shorter": (0.0, 0.25, 0.0, -0.25),
    "longer": (0.0, -0.25, 0.0, 0.25),
    "clockwise": (0.5, 0.0, -0.5, 0.0),
    "counterclockwise": (-0.5, 0.0, 0.5, 0.0),
    "northwest_stop": (0.0, 0.0, -0.5, 0.25),
    "southeast_start": (0.5, -0.25, 0.0, 0.0),
}


def shifted(target, lon_shift, lat_shift):
    return {**target, "longitude_deg": target["longitude_deg"] + lon_shift, "latitude_deg": target["latitude_deg"] + lat_shift}


def face_key(face):
    return face["face"], face["y"], face["x"]


def jaccard_distance(left, right):
    a = {face_key(face) for face in left}; b = {face_key(face) for face in right}
    return 1.0 - len(a & b) / len(a | b)


def summarize(cases, baseline_faces):
    signatures = {tuple(face_key(face) for face in case["faces"]) for case in cases}
    by_endpoint = {
        name: {tuple(face_key(face) for face in case["faces"]) for case in cases if case["endpoint_case"] == name}
        for name in ENDPOINT_CASES
    }
    distances = [(case["endpoint_case"], jaccard_distance(case["faces"], baseline_faces)) for case in cases]
    return {
        "case_count": len(cases),
        "unique_path_count": len(signatures),
        "face_count_range": [min(case["face_count"] for case in cases), max(case["face_count"] for case in cases)],
        "u_face_count_range": [min(case["u_face_count"] for case in cases), max(case["u_face_count"] for case in cases)],
        "v_face_count_range": [min(case["v_face_count"] for case in cases), max(case["v_face_count"] for case in cases)],
        "unique_start_nodes": len({(case["start_node"]["y"], case["start_node"]["x"]) for case in cases}),
        "unique_stop_nodes": len({(case["stop_node"]["y"], case["stop_node"]["x"]) for case in cases}),
        "maximum_face_set_jaccard_distance_from_baseline": max(jaccard_distance(case["faces"], baseline_faces) for case in cases),
        "maximum_distance_endpoint_cases": sorted({name for name, value in distances if np.isclose(value, max(item[1] for item in distances))}),
        "scale_invariant_endpoint_case_count": sum(len(values) == 1 for values in by_endpoint.values()),
        "all_topology_checks_pass": all(
            case["topology"]["connected_corner_chain"]
            and case["topology"]["unique_faces"]
            and case["topology"]["endpoint_degree_one"]
            and case["topology"]["all_internal_degrees_two"]
            and case["topology"]["corner_duplication_count"] == 0
            for case in cases
        ),
    }


def run(mesh_path):
    with netCDF4.Dataset(mesh_path) as dataset:
        tmask = np.asarray(dataset.variables["tmask"][0]) > 0
        umask = np.asarray(dataset.variables["umask"][0]) > 0
        vmask = np.asarray(dataset.variables["vmask"][0]) > 0
        ulon = base.normalize_longitude(dataset.variables["glamu"][:]); ulat = np.asarray(dataset.variables["gphiu"][:], dtype=float)
        vlon = base.normalize_longitude(dataset.variables["glamv"][:]); vlat = np.asarray(dataset.variables["gphiv"][:], dtype=float)
    node_lon, node_lat = base.build_node_coordinates(umask, vmask, ulon, ulat, vlon, vlat)
    valid_nodes = list(zip(*np.where(np.isfinite(node_lon))))
    coast = base.coastal_nodes(tmask, node_lon, node_lat)
    proxy_cases = []; closure_cases = []
    for case_name, (start_lon_shift, start_lat_shift, stop_lon_shift, stop_lat_shift) in ENDPOINT_CASES.items():
        start_target = shifted(base.PROXY_START, start_lon_shift, start_lat_shift)
        stop_target = shifted(base.PROXY_STOP, stop_lon_shift, stop_lat_shift)
        for scale in CORRIDOR_SCALES_KM:
            proxy_start = base.nearest_node(valid_nodes, node_lon, node_lat, start_target)
            proxy_stop = base.nearest_node(valid_nodes, node_lon, node_lat, stop_target)
            nodes, edges = base.shortest_face_path(proxy_start, proxy_stop, umask, vmask, node_lon, node_lat, ulon, ulat, vlon, vlat, start_target, stop_target, scale)
            proxy = base.package_path(case_name, "observational proxy sensitivity", nodes, edges, node_lon, node_lat, ulon, ulat, vlon, vlat, start_target, stop_target, proxy_start in coast, proxy_stop in coast)
            proxy.update({"endpoint_case": case_name, "corridor_scale_km": scale})
            proxy_cases.append(proxy)

            closure_start = base.nearest_node(coast, node_lon, node_lat, start_target)
            closure_stop = base.nearest_node(coast, node_lon, node_lat, stop_target)
            closure_stop_target = {"name": "selected modeled coast", "longitude_deg": float(node_lon[closure_stop]), "latitude_deg": float(node_lat[closure_stop])}
            nodes, edges = base.shortest_face_path(closure_start, closure_stop, umask, vmask, node_lon, node_lat, ulon, ulat, vlon, vlat, start_target, closure_stop_target, scale)
            closure = base.package_path(case_name, "model closure sensitivity", nodes, edges, node_lon, node_lat, ulon, ulat, vlon, vlat, start_target, closure_stop_target, True, True)
            closure.update({"endpoint_case": case_name, "corridor_scale_km": scale})
            closure_cases.append(closure)
    proxy_baseline = next(case for case in proxy_cases if case["endpoint_case"] == "baseline" and case["corridor_scale_km"] == 20.0)
    closure_baseline = next(case for case in closure_cases if case["endpoint_case"] == "baseline" and case["corridor_scale_km"] == 20.0)
    return {
        "schema": "oceanlines.osw.m3-oras5-barents-section-sensitivity.v1",
        "status": "construction_sensitivity_measured_not_physical_uncertainty",
        "design": {"endpoint_cases": ENDPOINT_CASES, "corridor_scales_km": CORRIDOR_SCALES_KM, "cases_per_semantics": len(proxy_cases)},
        "observational_proxy": {"summary": summarize(proxy_cases, proxy_baseline["faces"]), "cases": proxy_cases},
        "model_closure": {"summary": summarize(closure_cases, closure_baseline["faces"]), "cases": closure_cases},
        "baseline_reproduction": {"proxy_face_count": proxy_baseline["face_count"], "closure_face_count": closure_baseline["face_count"]},
        "boundary": "Endpoint and graph-cost sensitivity of surface geometry only. Differences are construction-method sensitivity, not ocean variability, transport uncertainty, observational error, or heat-delivery uncertainty.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-arctic-entrances-mesh.nc"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-barents-section-sensitivity.json"))
    args = parser.parse_args()
    payload = run(args.mesh)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}: 27 proxy + 27 closure cases")


if __name__ == "__main__":
    main()
