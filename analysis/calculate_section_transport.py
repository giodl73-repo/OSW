"""Calculate receipted volume and reference-relative heat transport across a section."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib


def require_finite_number(value, label: str) -> float:
    if not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    return float(value)


def calculate(payload: dict, reference_temperatures: tuple[float, ...] = (-1.9, 0.0, 5.0)) -> dict:
    levels, segments = payload["shape"]
    if not isinstance(levels, int) or not isinstance(segments, int) or levels < 1 or segments < 1:
        raise ValueError("shape must contain positive integer levels and segments")
    cells = levels * segments
    widths = payload["segment_width_m"]
    thicknesses = payload["layer_thickness_m"]
    wet = payload["wet_fraction"]
    cell_thicknesses = payload.get("cell_thickness_m")
    velocity = payload["normal_velocity_m_s"]
    temperature = payload["potential_temperature_degC"]
    if len(widths) != segments or len(thicknesses) != levels:
        raise ValueError("section geometry dimensions do not match shape")
    if any(len(values) != cells for values in (wet, velocity, temperature)):
        raise ValueError("cell arrays do not match shape")
    if cell_thicknesses is not None and len(cell_thicknesses) != cells:
        raise ValueError("cell thickness array does not match shape")
    rho = require_finite_number(payload["constants"]["density_kg_m3"], "density")
    cp = require_finite_number(payload["constants"]["heat_capacity_J_kg_K"], "heat capacity")
    if rho <= 0 or cp <= 0:
        raise ValueError("density and heat capacity must be positive")
    references = tuple(require_finite_number(value, "reference temperature") for value in reference_temperatures)
    if len(set(references)) != len(references):
        raise ValueError("reference temperatures must be unique")

    records = []
    layers = [{
        "volume_m3_s": 0.0, "volume_positive_m3_s": 0.0, "volume_negative_m3_s": 0.0,
        "wet_area_m2": 0.0, "temperature_transport_degC_m3_s": 0.0,
        "temperature_transport_positive_degC_m3_s": 0.0,
        "temperature_transport_negative_degC_m3_s": 0.0,
    } for _ in range(levels)]
    for level in range(levels):
        thickness = require_finite_number(thicknesses[level], f"layer thickness {level}")
        if thickness <= 0:
            raise ValueError("layer thickness must be positive")
        for segment in range(segments):
            index = level * segments + segment
            width = require_finite_number(widths[segment], f"segment width {segment}")
            fraction = require_finite_number(wet[index], f"wet fraction {index}")
            if width <= 0 or not 0 <= fraction <= 1:
                raise ValueError("segment width must be positive and wet fraction must be in [0, 1]")
            if fraction == 0:
                continue
            speed = require_finite_number(velocity[index], f"normal velocity {index}")
            theta = require_finite_number(temperature[index], f"potential temperature {index}")
            cell_thickness = thickness if cell_thicknesses is None else require_finite_number(
                cell_thicknesses[index], f"cell thickness {index}"
            )
            if cell_thickness <= 0:
                raise ValueError("wet-cell thickness must be positive")
            area = width * cell_thickness * fraction
            volume = speed * area
            temperature_transport = volume * theta
            record = {
                "level": level, "segment": segment, "area_m2": area,
                "volume_m3_s": volume, "temperature_degC": theta,
                "temperature_transport_degC_m3_s": temperature_transport,
            }
            records.append(record)
            layers[level]["volume_m3_s"] += volume
            layers[level]["volume_positive_m3_s"] += max(0.0, volume)
            layers[level]["volume_negative_m3_s"] += min(0.0, volume)
            layers[level]["wet_area_m2"] += area
            layers[level]["temperature_transport_degC_m3_s"] += temperature_transport
            if volume >= 0:
                layers[level]["temperature_transport_positive_degC_m3_s"] += temperature_transport
            else:
                layers[level]["temperature_transport_negative_degC_m3_s"] += temperature_transport

    if not records:
        raise ValueError("section contains no wet cells")
    wet_area = sum(record["area_m2"] for record in records)
    volume_positive = sum(max(0.0, record["volume_m3_s"]) for record in records)
    volume_negative = sum(min(0.0, record["volume_m3_s"]) for record in records)
    volume_net = volume_positive + volume_negative
    temperature_transport_net = sum(record["temperature_transport_degC_m3_s"] for record in records)

    heat_cases = []
    for reference in references:
        positive = rho * cp * sum(
            max(0.0, record["volume_m3_s"]) * (record["temperature_degC"] - reference)
            for record in records
        )
        negative = rho * cp * sum(
            min(0.0, record["volume_m3_s"]) * (record["temperature_degC"] - reference)
            for record in records
        )
        heat_cases.append({
            "reference_temperature_degC": reference,
            "positive_PW": positive / 1e15,
            "negative_PW": negative / 1e15,
            "net_PW": (positive + negative) / 1e15,
        })

    reference_audits = []
    for previous, current in zip(heat_cases, heat_cases[1:]):
        expected_change = -rho * cp * volume_net * (
            current["reference_temperature_degC"] - previous["reference_temperature_degC"]
        )
        actual_change = (current["net_PW"] - previous["net_PW"]) * 1e15
        reference_audits.append({
            "from_degC": previous["reference_temperature_degC"],
            "to_degC": current["reference_temperature_degC"],
            "expected_change_W": expected_change,
            "actual_change_W": actual_change,
            "identity_residual_W": actual_change - expected_change,
        })

    layer_output = []
    for level, layer in enumerate(layers):
        layer_output.append({
            "level": level,
            "thickness_m": thicknesses[level],
            "wet_area_m2": layer["wet_area_m2"],
            "positive_volume_Sv": layer["volume_positive_m3_s"] / 1e6,
            "negative_volume_Sv": layer["volume_negative_m3_s"] / 1e6,
            "volume_Sv": layer["volume_m3_s"] / 1e6,
            "positive_temperature_transport_degC_Sv": layer["temperature_transport_positive_degC_m3_s"] / 1e6,
            "negative_temperature_transport_degC_Sv": layer["temperature_transport_negative_degC_m3_s"] / 1e6,
            "temperature_transport_degC_Sv": layer["temperature_transport_degC_m3_s"] / 1e6,
        })

    input_bytes = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "schema": "oceanlines.osw.m3-section-transport.v1",
        "status": "section transport calculation",
        "input_schema": payload["schema"],
        "input_sha256": hashlib.sha256(input_bytes).hexdigest(),
        "section": payload["section"],
        "source": payload["source"],
        "temperature_contract": payload["temperature_contract"],
        "normal_velocity_contract": payload["normal_velocity_contract"],
        "geometry_contract": payload.get(
            "geometry_contract",
            "nominal layer thickness multiplied by wet fraction",
        ),
        "constants": payload["constants"],
        "shape": payload["shape"],
        "wet_cell_count": len(records),
        "wet_area_m2": wet_area,
        "volume_transport": {
            "positive_Sv": volume_positive / 1e6,
            "negative_Sv": volume_negative / 1e6,
            "net_Sv": volume_net / 1e6,
        },
        "transport_weighted_temperature_degC": {
            "positive_branch": None if volume_positive == 0 else sum(
                max(0.0, record["volume_m3_s"]) * record["temperature_degC"] for record in records
            ) / volume_positive,
            "negative_branch": None if volume_negative == 0 else sum(
                min(0.0, record["volume_m3_s"]) * record["temperature_degC"] for record in records
            ) / volume_negative,
            "net": None if abs(volume_net) < 1e-12 else temperature_transport_net / volume_net,
        },
        "reference_relative_heat_transport": heat_cases,
        "reference_change_audit": reference_audits,
        "layers": layer_output,
        "mass_closure": {
            "status": "not_evaluable_from_one_open_section",
            "residual_Sv": None,
            "requirement": "pair with every other open boundary and storage tendency of a closed control volume",
        },
        "boundary": (
            "Advective section transport using declared normal velocity, potential temperature, "
            "wet-face geometry, constant density, and constant heat capacity. Heat transport is "
            "reference-temperature dependent when net volume transport is nonzero. One open section "
            "does not establish mass closure, convergence, eddy covariance, diffusive transport, "
            "ice-shelf delivery, or a complete heat budget."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--reference-temperature", type=float, action="append", dest="references")
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    result = calculate(payload, tuple(args.references or (-1.9, 0.0, 5.0)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}: net {result['volume_transport']['net_Sv']:.6g} Sv")


if __name__ == "__main__":
    main()
