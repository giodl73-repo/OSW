"""Extract Fram and two Barents native-face sections from one ORAS5 month."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib

import netCDF4
import numpy as np

try:
    from audit_nemo_face_thickness_reconstruction import reconstruct_t
except ModuleNotFoundError:
    from analysis.audit_nemo_face_thickness_reconstruction import reconstruct_t


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def nullable_flat(values, wet):
    return [float(values[z, segment]) if wet[z, segment] else None for z in range(wet.shape[0]) for segment in range(wet.shape[1])]


def collocate(tracer, velocity, face: dict, method: str):
    y = int(face["y"]); x = int(face["x"])
    if face["face"] == "U":
        negative_side, positive_side = tracer[:, y, x], tracer[:, y, x + 1]
    elif face["face"] == "V":
        negative_side, positive_side = tracer[:, y, x], tracer[:, y + 1, x]
    else:
        raise ValueError(f"unknown native face {face['face']}")
    if method == "mean":
        return 0.5 * (negative_side + positive_side)
    if method == "negative_side":
        return negative_side
    if method == "positive_side":
        return positive_side
    if method == "upwind":
        return np.where(velocity >= 0, negative_side, positive_side)
    raise ValueError("tracer collocation must be mean, negative_side, positive_side, or upwind")


def build_payload(mesh: dict, state: dict, name: str, semantics: str, faces: list[dict], month: str, source: dict, collocation: str = "mean") -> dict:
    reference = np.asarray(mesh["e3t_0"], dtype=float)
    t_thickness, _ = reconstruct_t(reference, mesh["mbathy"], mesh["e3t_ps"])
    columns = []
    masks = []
    widths = []
    velocities = []
    temperatures = []
    salinities = []
    face_records = []
    for index, face in enumerate(faces):
        kind = face["face"]
        y = int(face["y"]); x = int(face["x"])
        sign = int(face.get("sign", face.get("sign_into_barents", 1)))
        if sign not in (-1, 1):
            raise ValueError("face sign must be -1 or +1")
        if kind == "U":
            columns.append(np.minimum(t_thickness[:, y, x], t_thickness[:, y, x + 1]))
            masks.append(np.asarray(mesh["umask"][:, y, x]) > 0)
            widths.append(mesh["e2u"][y, x])
            native_velocity = np.asarray(state["vozocrtx"][:, y, x], dtype=float)
        elif kind == "V":
            columns.append(np.minimum(t_thickness[:, y, x], t_thickness[:, y + 1, x]))
            masks.append(np.asarray(mesh["vmask"][:, y, x]) > 0)
            widths.append(mesh["e1v"][y, x])
            native_velocity = np.asarray(state["vomecrty"][:, y, x], dtype=float)
        else:
            raise ValueError(f"unknown native face {kind}")
        velocities.append(native_velocity * sign)
        temperatures.append(collocate(state["votemper"], native_velocity, face, collocation))
        salinities.append(collocate(state["vosaline"], native_velocity, face, collocation))
        face_records.append({
            "segment": index, "face": kind, "local_y": y, "local_x": x, "normal_sign": sign,
            "longitude_deg": float(face["longitude_deg"]), "latitude_deg": float(face["latitude_deg"]),
        })
    thickness = np.asarray(columns, dtype=float).T
    wet = np.asarray(masks, dtype=bool).T
    width = np.asarray(widths, dtype=float)
    velocity = np.asarray(velocities, dtype=float).T
    temperature = np.asarray(temperatures, dtype=float).T
    salinity = np.asarray(salinities, dtype=float).T
    if np.any((thickness > 0) != wet):
        raise ValueError(f"reconstructed face thickness disagrees with native mask on {name}")
    if np.any(~np.isfinite(width)) or np.any(width <= 0):
        raise ValueError(f"face widths must be finite and positive on {name}")
    for label, values in (("velocity", velocity), ("temperature", temperature), ("salinity", salinity)):
        if np.any(~np.isfinite(values[wet])):
            raise ValueError(f"wet {name} cells contain missing {label}")
    return {
        "schema": "oceanlines.osw.m3-arctic-section-input.v1",
        "status": "candidate native Arctic monthly section input",
        "section": {
            "name": name, "semantics": semantics, "month": month, "segment_count": len(faces),
            "positive_normal": "northward into Arctic" if name == "Fram Strait" else "eastward into Barents Sea",
            "faces": face_records,
        },
        "source": source,
        "shape": [wet.shape[0], wet.shape[1]],
        "segment_width_m": [float(value) for value in width],
        "layer_thickness_m": [float(value) for value in reference],
        "cell_thickness_m": nullable_flat(thickness, wet),
        "wet_fraction": [int(value) for value in wet.ravel()],
        "normal_velocity_m_s": nullable_flat(velocity, wet),
        "potential_temperature_degC": nullable_flat(temperature, wet),
        "practical_salinity_PSU": nullable_flat(salinity, wet),
        "constants": {"density_kg_m3": 1027.0, "heat_capacity_J_kg_K": 3992.0},
        "temperature_contract": f"ORAS5 votemper; adjacent T-cell to native-face collocation={collocation}; no tracer-advection reconstruction",
        "salinity_contract": f"ORAS5 vosaline; same adjacent T-cell collocation={collocation}; retained for joint T/S classification",
        "normal_velocity_contract": "ORAS5 native U/V velocity multiplied by each face's declared section-normal sign",
        "geometry_contract": "Adjacent-minimum reconstructed partial-step T thickness; native e2u/e1v width; native U/V mask",
        "boundary": (
            "One monthly ORAS5 ensemble member and one declared native-face section. Offline adjacent-cell tracer "
            "collocation is explicit. Not a climatology, observational estimate, mass closure, convergence, or Arctic heat budget."
        ),
    }


def section_contracts(readiness: dict, bakeoff: dict):
    fram = readiness["fram"]
    fram_faces = [
        {"face": "V", "y": fram["grid_row"], "x": x, "sign": 1,
         "longitude_deg": fram["longitude_deg"][x - fram["x_start"]],
         "latitude_deg": fram["latitude_deg"][x - fram["x_start"]]}
        for x in range(fram["x_start"], fram["x_stop_exclusive"])
    ]
    return (
        ("fram", "Fram Strait", "land-bounded native V-face gateway", fram_faces),
        ("barents-proxy", bakeoff["observational_proxy"]["name"], bakeoff["observational_proxy"]["semantics"], bakeoff["observational_proxy"]["faces"]),
        ("barents-closure", bakeoff["model_closure"]["name"], bakeoff["model_closure"]["semantics"], bakeoff["model_closure"]["faces"]),
    )


def extract_all(mesh_path: pathlib.Path, state_path: pathlib.Path, readiness_path: pathlib.Path, bakeoff_path: pathlib.Path, collocation: str = "mean"):
    readiness = json.loads(readiness_path.read_text(encoding="utf-8"))
    bakeoff = json.loads(bakeoff_path.read_text(encoding="utf-8"))
    with netCDF4.Dataset(mesh_path) as dataset:
        mesh = {name: np.ma.filled(dataset.variables[name][:], 0) for name in ("e3t_0", "mbathy", "e3t_ps", "umask", "vmask", "e2u", "e1v")}
    with netCDF4.Dataset(state_path) as dataset:
        state = {name: np.ma.filled(dataset.variables[name][:], np.nan) for name in ("votemper", "vosaline", "vozocrtx", "vomecrty")}
        month = str(getattr(dataset, "month"))
    source = {
        "product": "ORAS5 ORCA025 University of Hamburg ICDC ensemble member opa0", "month": month,
        "mesh_path": str(mesh_path), "mesh_sha256": sha256_file(mesh_path),
        "state_path": str(state_path), "state_sha256": sha256_file(state_path),
        "readiness_path": str(readiness_path), "readiness_sha256": sha256_file(readiness_path),
        "bakeoff_path": str(bakeoff_path), "bakeoff_sha256": sha256_file(bakeoff_path),
    }
    return {
        slug: build_payload(mesh, state, name, semantics, faces, month, source, collocation)
        for slug, name, semantics, faces in section_contracts(readiness, bakeoff)
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-arctic-entrances-mesh.nc"))
    parser.add_argument("--state", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-arctic-entrances-state-201802.nc"))
    parser.add_argument("--readiness", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-arctic-gate-readiness.json"))
    parser.add_argument("--bakeoff", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-barents-section-bakeoff.json"))
    parser.add_argument("--output-dir", type=pathlib.Path, default=pathlib.Path("research"))
    parser.add_argument("--collocation", default="mean", choices=("mean", "negative_side", "positive_side", "upwind"))
    args = parser.parse_args()
    results = extract_all(args.mesh, args.state, args.readiness, args.bakeoff, args.collocation)
    for slug, payload in results.items():
        output = args.output_dir / f"osw-m3-oras5-arctic-{slug}-section-input-{payload['section']['month']}.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        print(f"wrote {output}: {payload['shape'][0]} levels x {payload['shape'][1]} segments")


if __name__ == "__main__":
    main()
