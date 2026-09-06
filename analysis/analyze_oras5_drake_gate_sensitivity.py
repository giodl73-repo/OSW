"""Test Drake transport sensitivity to native gate column and T-to-U collocation."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import statistics

import netCDF4
import numpy as np

try:
    from calculate_section_transport import calculate
    from derive_oras5_drake_gate import candidate_gates, normalize_longitude
    from extract_oras5_drake_section import build_payload
except ModuleNotFoundError:
    from analysis.calculate_section_transport import calculate
    from analysis.derive_oras5_drake_gate import candidate_gates, normalize_longitude
    from analysis.extract_oras5_drake_section import build_payload


MONTHS = ("201802", "201805", "201808", "201811")
OFFSETS = (-8, -4, 0, 4, 8)
COLLOCATIONS = ("mean", "west", "east", "upwind")


def stats(values):
    return {"mean": statistics.fmean(values), "minimum": min(values), "maximum": max(values), "range": max(values) - min(values)}


def summarize(gate_records: list[dict], collocation_records: list[dict], primary_x: int) -> dict:
    gate_summary = []
    for x in sorted({record["x"] for record in gate_records}):
        records = [record for record in gate_records if record["x"] == x]
        gate_summary.append({
            "x": x, "mean_longitude_deg": records[0]["mean_longitude_deg"],
            "south_deg": records[0]["south_deg"], "north_deg": records[0]["north_deg"],
            "net_volume_Sv": stats([record["net_volume_Sv"] for record in records]),
            "net_heat_0C_PW": stats([record["net_heat_0C_PW"] for record in records]),
        })
    primary_by_month = {
        record["month"]: record for record in collocation_records if record["collocation"] == "mean"
    }
    collocation_summary = []
    for scheme in COLLOCATIONS:
        records = [record for record in collocation_records if record["collocation"] == scheme]
        heat_differences = [
            record["net_heat_0C_PW"] - primary_by_month[record["month"]]["net_heat_0C_PW"]
            for record in records
        ]
        collocation_summary.append({
            "collocation": scheme,
            "net_volume_Sv": stats([record["net_volume_Sv"] for record in records]),
            "net_heat_0C_PW": stats([record["net_heat_0C_PW"] for record in records]),
            "heat_difference_from_mean_collocation_PW": stats(heat_differences),
        })
    all_gate_means = [item["net_volume_Sv"]["mean"] for item in gate_summary]
    return {
        "primary_x": primary_x,
        "gate_records": gate_records,
        "gate_summary": gate_summary,
        "across_gate_four_sample_mean_volume_Sv": stats(all_gate_means),
        "collocation_records": collocation_records,
        "collocation_summary": collocation_summary,
    }


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(mesh_path: pathlib.Path, gate_path: pathlib.Path, state_dir: pathlib.Path) -> dict:
    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    primary_x = gate["selected"]["x"]
    with netCDF4.Dataset(mesh_path) as mesh:
        names = ("e3t_0", "mbathy", "e3t_ps", "umask", "e2u", "glamu", "gphiu")
        mesh_arrays = {name: np.ma.filled(mesh.variables[name][:], 0) for name in names}
    candidates = candidate_gates(mesh_arrays["umask"][0], mesh_arrays["glamu"], mesh_arrays["gphiu"])
    by_x = {}
    for candidate in candidates:
        by_x.setdefault(candidate["x"], candidate)
    selected_gates = []
    for x in (primary_x + offset for offset in OFFSETS):
        if x not in by_x:
            raise ValueError(f"no valid sensitivity gate at native x={x}")
        item = dict(by_x[x]); ys = slice(item["y_start"], item["y_stop_exclusive"])
        item.update({
            "longitude_deg": [float(value) for value in normalize_longitude(mesh_arrays["glamu"][ys, x])],
            "latitude_deg": [float(value) for value in mesh_arrays["gphiu"][ys, x]],
            "positive_normal": "native +i / approximately eastward",
        })
        selected_gates.append(item)

    states = {}
    state_sources = []
    for month in MONTHS:
        path = state_dir / f"oras5-drake-state-{month}.nc"
        with netCDF4.Dataset(path) as state:
            states[month] = {
                name: np.ma.filled(state.variables[name][:], np.nan)
                for name in ("votemper", "vozocrtx")
            }
        state_sources.append({"month": month, "path": str(path), "sha256": sha256_file(path)})

    gate_records = []
    for selected in selected_gates:
        for month in MONTHS:
            section = build_payload(mesh_arrays, states[month], selected, {"month": month}, "mean")
            result = calculate(section)
            heat0 = next(case["net_PW"] for case in result["reference_relative_heat_transport"] if case["reference_temperature_degC"] == 0)
            gate_records.append({
                "x": selected["x"], "mean_longitude_deg": selected["mean_longitude_deg"],
                "south_deg": selected["south_deg"], "north_deg": selected["north_deg"],
                "month": month, "net_volume_Sv": result["volume_transport"]["net_Sv"],
                "net_heat_0C_PW": heat0,
            })

    collocation_records = []
    primary = next(item for item in selected_gates if item["x"] == primary_x)
    for scheme in COLLOCATIONS:
        for month in MONTHS:
            section = build_payload(mesh_arrays, states[month], primary, {"month": month}, scheme)
            result = calculate(section)
            heat0 = next(case["net_PW"] for case in result["reference_relative_heat_transport"] if case["reference_temperature_degC"] == 0)
            collocation_records.append({
                "collocation": scheme, "month": month,
                "net_volume_Sv": result["volume_transport"]["net_Sv"],
                "net_heat_0C_PW": heat0,
                "net_temperature_degC": result["transport_weighted_temperature_degC"]["net"],
            })

    synthesis = summarize(gate_records, collocation_records, primary_x)
    return {
        "schema": "oceanlines.osw.m3-drake-method-sensitivity.v1",
        "status": "native gate-position and temperature-collocation sensitivity",
        "months": list(MONTHS),
        "gate_offsets_native_columns": list(OFFSETS),
        "temperature_collocations": list(COLLOCATIONS),
        **synthesis,
        "sources": {
            "mesh": {"path": str(mesh_path), "sha256": sha256_file(mesh_path)},
            "primary_gate": {"path": str(gate_path), "sha256": sha256_file(gate_path)},
            "states": state_sources,
        },
        "boundary": (
            "Five nearby grid-aligned gates and four offline T-to-U collocations over four sampled "
            "2018 months. This is method sensitivity, not observational uncertainty, annual "
            "variability, a unique section, model tracer flux, mass closure, or heat convergence."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-drake-mesh.nc"))
    parser.add_argument("--gate", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-drake-gate.json"))
    parser.add_argument("--state-dir", type=pathlib.Path, default=pathlib.Path("atlas/data"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-drake-method-sensitivity-2018.json"))
    args = parser.parse_args()
    result = run(args.mesh, args.gate, args.state_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    gate_range = result["across_gate_four_sample_mean_volume_Sv"]["range"]
    print(f"wrote {args.output}: across-gate mean-volume range {gate_range:.3f} Sv")


if __name__ == "__main__":
    main()
