"""Build a four-sample mean latitude-depth field for the native Drake gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib


MONTHS = ("201802", "201805", "201808", "201811")


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def synthesize(payloads: list[dict]) -> dict:
    first = payloads[0]
    geometry_keys = ("shape", "segment_width_m", "layer_thickness_m", "cell_thickness_m", "wet_fraction")
    for payload in payloads[1:]:
        for key in geometry_keys:
            if payload[key] != first[key]:
                raise ValueError(f"section geometry differs across months: {key}")
        if payload["section"]["latitude_deg"] != first["section"]["latitude_deg"]:
            raise ValueError("section latitude coordinate differs across months")
    cells = first["shape"][0] * first["shape"][1]
    temperature = []
    velocity = []
    volume_transport = []
    heat_transport_0c = []
    rho = float(first["constants"]["density_kg_m3"])
    cp = float(first["constants"]["heat_capacity_J_kg_K"])
    for index in range(cells):
        if not first["wet_fraction"][index]:
            temperature.append(None)
            velocity.append(None)
            volume_transport.append(None)
            heat_transport_0c.append(None)
            continue
        temperatures = [float(payload["potential_temperature_degC"][index]) for payload in payloads]
        velocities = [float(payload["normal_velocity_m_s"][index]) for payload in payloads]
        level, segment = divmod(index, first["shape"][1])
        area = float(first["segment_width_m"][segment]) * float(first["cell_thickness_m"][index]) * float(first["wet_fraction"][index])
        monthly_volume = [value * area / 1e6 for value in velocities]
        monthly_heat = [rho * cp * volume * theta * 1e-9 for volume, theta in zip(monthly_volume, temperatures)]
        temperature.append(sum(temperatures) / len(temperatures))
        velocity.append(sum(velocities) / len(velocities))
        volume_transport.append(sum(monthly_volume) / len(monthly_volume))
        heat_transport_0c.append(sum(monthly_heat) / len(monthly_heat))
    depths = []
    depth = 0.0
    for thickness in first["layer_thickness_m"]:
        depths.append({"top_m": depth, "bottom_m": depth + float(thickness), "midpoint_m": depth + float(thickness) / 2})
        depth += float(thickness)
    wet_temperatures = [value for value in temperature if value is not None]
    wet_velocities = [value for value in velocity if value is not None]
    wet_volume = [value for value in volume_transport if value is not None]
    wet_heat = [value for value in heat_transport_0c if value is not None]
    return {
        "schema": "oceanlines.osw.m3-drake-section-field.v1",
        "status": "four-sample mean native latitude-depth gate field",
        "months": list(MONTHS), "shape": first["shape"],
        "longitude_deg": first["section"]["longitude_deg"], "latitude_deg": first["section"]["latitude_deg"],
        "layer_depths": depths, "cell_thickness_m": first["cell_thickness_m"], "wet_fraction": first["wet_fraction"],
        "mean_potential_temperature_degC": temperature, "mean_normal_velocity_m_s": velocity,
        "mean_cell_volume_transport_Sv": volume_transport,
        "mean_cell_heat_transport_PW_at_0C": heat_transport_0c,
        "ranges": {
            "potential_temperature_degC": [min(wet_temperatures), max(wet_temperatures)],
            "normal_velocity_m_s": [min(wet_velocities), max(wet_velocities)],
            "cell_volume_transport_Sv": [min(wet_volume), max(wet_volume)],
            "cell_heat_transport_PW_at_0C": [min(wet_heat), max(wet_heat)],
        },
        "transport_sum_audit": {
            "volume_Sv": sum(wet_volume),
            "heat_transport_PW_at_0C": sum(wet_heat),
        },
        "temperature_contract": first["temperature_contract"], "normal_velocity_contract": first["normal_velocity_contract"],
        "maximum_nominal_model_depth_m": depth,
        "boundary": "Arithmetic mean of February, May, August, and November 2018 native-section cells. The nonlinear display depth scale and sampled velocity marks are visual encodings, not transport integration, water-mass boundaries, an annual mean, or a climatology.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--research-dir", type=pathlib.Path, default=pathlib.Path("research"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-drake-section-field-2018.json"))
    args = parser.parse_args()
    paths = [args.research_dir / f"osw-m3-oras5-drake-section-input-{month}.json" for month in MONTHS]
    payloads = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    result = synthesize(payloads)
    result["sources"] = [{"path": str(path), "sha256": sha256_file(path)} for path in paths]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
