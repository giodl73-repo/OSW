"""Extract the candidate native U-face Drake gate into the M3 section contract."""

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


def flatten_section(values):
    return [value for level in values for value in level]


def build_payload(mesh_arrays: dict, state_arrays: dict, selected: dict, source: dict, temperature_collocation: str = "mean") -> dict:
    x = selected["x"]; start = selected["y_start"]; stop = selected["y_stop_exclusive"]
    ys = slice(start, stop)
    reference = np.asarray(mesh_arrays["e3t_0"], dtype=float)
    t_thickness, _ = reconstruct_t(reference, mesh_arrays["mbathy"], mesh_arrays["e3t_ps"])
    face_thickness = np.minimum(t_thickness[:, :, x], t_thickness[:, :, x + 1])[:, ys]
    wet = np.asarray(mesh_arrays["umask"][:, ys, x]) > 0
    if np.any((face_thickness > 0) != wet):
        raise ValueError("reconstructed face thickness disagrees with native U mask on gate")
    width = np.asarray(mesh_arrays["e2u"][ys, x], dtype=float)
    if np.any(~np.isfinite(width)) or np.any(width <= 0):
        raise ValueError("gate face widths must be finite and positive")

    temperature = np.asarray(state_arrays["votemper"], dtype=float)
    u_velocity = np.asarray(state_arrays["vozocrtx"], dtype=float)
    face_velocity = u_velocity[:, ys, x]
    west_temperature = temperature[:, ys, x]
    east_temperature = temperature[:, ys, x + 1]
    if temperature_collocation == "mean":
        face_temperature = 0.5 * (west_temperature + east_temperature)
    elif temperature_collocation == "west":
        face_temperature = west_temperature
    elif temperature_collocation == "east":
        face_temperature = east_temperature
    elif temperature_collocation == "upwind":
        face_temperature = np.where(face_velocity >= 0, west_temperature, east_temperature)
    else:
        raise ValueError("temperature collocation must be mean, west, east, or upwind")
    if np.any(~np.isfinite(face_temperature[wet])) or np.any(~np.isfinite(face_velocity[wet])):
        raise ValueError("wet gate contains missing temperature or U velocity")

    def nullable(values):
        return flatten_section([
            [float(values[level, segment]) if wet[level, segment] else None for segment in range(wet.shape[1])]
            for level in range(wet.shape[0])
        ])

    wet_flat = flatten_section([[1 if value else 0 for value in row] for row in wet])
    return {
        "schema": "oceanlines.osw.m3-section-input.v1",
        "status": "candidate native Drake monthly section input",
        "section": {
            "name": "Drake Passage 67.125W native U-face gate",
            "month": source["month"],
            "local_x": x,
            "local_y_start": start,
            "local_y_stop_exclusive": stop,
            "segment_count": stop - start,
            "longitude_deg": selected["longitude_deg"],
            "latitude_deg": selected["latitude_deg"],
            "positive_normal": selected["positive_normal"],
        },
        "source": source,
        "shape": [wet.shape[0], wet.shape[1]],
        "segment_width_m": [float(value) for value in width],
        "layer_thickness_m": [float(value) for value in reference],
        "cell_thickness_m": nullable(face_thickness),
        "wet_fraction": wet_flat,
        "normal_velocity_m_s": nullable(face_velocity),
        "potential_temperature_degC": nullable(face_temperature),
        "constants": {"density_kg_m3": 1027.0, "heat_capacity_J_kg_K": 3992.0},
        "temperature_contract": (
            f"ORAS5 votemper in degrees C; T-to-U collocation={temperature_collocation}; "
            "mean averages adjacent T points, west/east selects one neighbor, and upwind selects "
            "west for positive U and east for negative U; no model tracer-advection reconstruction"
        ),
        "normal_velocity_contract": "ORAS5 native vozocrtx at U faces; positive native +i, approximately eastward",
        "geometry_contract": (
            "Explicit interior U-face thickness is the minimum of adjacent reconstructed partial-step "
            "T thicknesses; width is native e2u; native umask is binary wet support"
        ),
        "boundary": (
            "One candidate grid-aligned gate and one monthly reanalysis member. Temperature face "
            "collocation is a declared offline arithmetic mean. Not a climatology, eddy covariance, "
            "diffusive flux, mass closure, convergence, or Antarctic shelf delivery estimate."
        ),
    }


def extract(mesh_path: pathlib.Path, state_path: pathlib.Path, gate_path: pathlib.Path) -> dict:
    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    with netCDF4.Dataset(mesh_path) as mesh:
        mesh_arrays = {name: np.ma.filled(mesh.variables[name][:], 0) for name in (
            "e3t_0", "mbathy", "e3t_ps", "umask", "e2u"
        )}
    with netCDF4.Dataset(state_path) as state:
        state_arrays = {name: np.ma.filled(state.variables[name][:], np.nan) for name in ("votemper", "vozocrtx")}
        month = getattr(state, "month")
    source = {
        "product": "ORAS5 ORCA025 University of Hamburg ICDC ensemble member opa0",
        "month": month,
        "mesh_path": str(mesh_path), "mesh_sha256": sha256_file(mesh_path),
        "state_path": str(state_path), "state_sha256": sha256_file(state_path),
        "gate_path": str(gate_path), "gate_sha256": sha256_file(gate_path),
    }
    return build_payload(mesh_arrays, state_arrays, gate["selected"], source)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-drake-mesh.nc"))
    parser.add_argument("--state", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-drake-state-201802.nc"))
    parser.add_argument("--gate", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-drake-gate.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-drake-section-input-201802.json"))
    args = parser.parse_args()
    result = extract(args.mesh, args.state, args.gate)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}: {result['shape'][0]} levels x {result['shape'][1]} segments")


if __name__ == "__main__":
    main()
