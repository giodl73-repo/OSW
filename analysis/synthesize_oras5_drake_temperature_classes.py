"""Partition native Drake section transport into declared temperature classes."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import statistics


MONTHS = ("201802", "201805", "201808", "201811")
EDGES = (-float("inf"), 0.0, 1.0, 2.0, 3.0, 5.0, float("inf"))
LABELS = ("<0°C", "0–1°C", "1–2°C", "2–3°C", "3–5°C", ">5°C")


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def classify(value: float) -> int:
    for index, (lower, upper) in enumerate(zip(EDGES, EDGES[1:])):
        if lower <= value < upper:
            return index
    raise ValueError(f"temperature outside declared classes: {value}")


def calculate_month(section: dict, month: str) -> list[dict]:
    levels, segments = section["shape"]
    widths = section["segment_width_m"]
    nominal = section["layer_thickness_m"]
    explicit = section.get("cell_thickness_m")
    wet = section["wet_fraction"]
    velocity = section["normal_velocity_m_s"]
    temperature = section["potential_temperature_degC"]
    rho = float(section["constants"]["density_kg_m3"])
    cp = float(section["constants"]["heat_capacity_J_kg_K"])
    rows = [{
        "month": month, "class": label, "lower_degC": None if index == 0 else EDGES[index],
        "upper_degC": None if index == len(LABELS) - 1 else EDGES[index + 1],
        "wet_cell_count": 0, "positive_volume_Sv": 0.0, "negative_volume_Sv": 0.0,
        "positive_heat_0C_PW": 0.0, "negative_heat_0C_PW": 0.0,
    } for index, label in enumerate(LABELS)]
    for level in range(levels):
        for segment in range(segments):
            cell = level * segments + segment
            if not wet[cell]:
                continue
            theta = float(temperature[cell])
            thickness = float(explicit[cell]) if explicit is not None else float(nominal[level]) * float(wet[cell])
            area = float(widths[segment]) * thickness
            volume_sv = float(velocity[cell]) * area / 1e6
            heat_pw = rho * cp * volume_sv * theta * 1e-9
            row = rows[classify(theta)]
            row["wet_cell_count"] += 1
            if volume_sv >= 0:
                row["positive_volume_Sv"] += volume_sv
                row["positive_heat_0C_PW"] += heat_pw
            else:
                row["negative_volume_Sv"] += volume_sv
                row["negative_heat_0C_PW"] += heat_pw
    for row in rows:
        row["net_volume_Sv"] = row["positive_volume_Sv"] + row["negative_volume_Sv"]
        row["net_heat_0C_PW"] = row["positive_heat_0C_PW"] + row["negative_heat_0C_PW"]
    return rows


def synthesize(sections: list[dict], transports: list[dict]) -> dict:
    rows = [row for month, section in zip(MONTHS, sections) for row in calculate_month(section, month)]
    summary = []
    for label in LABELS:
        selected = [row for row in rows if row["class"] == label]
        item = {"class": label, "lower_degC": selected[0]["lower_degC"], "upper_degC": selected[0]["upper_degC"]}
        for key in ("wet_cell_count", "positive_volume_Sv", "negative_volume_Sv", "net_volume_Sv", "positive_heat_0C_PW", "negative_heat_0C_PW", "net_heat_0C_PW"):
            values = [row[key] for row in selected]
            item[key] = {"mean": statistics.fmean(values), "minimum": min(values), "maximum": max(values), "range": max(values) - min(values)}
        summary.append(item)
    audits = []
    for month, transport in zip(MONTHS, transports):
        selected = [row for row in rows if row["month"] == month]
        heat0 = next(item["net_PW"] for item in transport["reference_relative_heat_transport"] if item["reference_temperature_degC"] == 0)
        audits.append({
            "month": month,
            "volume_residual_Sv": sum(row["net_volume_Sv"] for row in selected) - transport["volume_transport"]["net_Sv"],
            "heat_0C_residual_PW": sum(row["net_heat_0C_PW"] for row in selected) - heat0,
        })
    return {
        "schema": "oceanlines.osw.m3-drake-temperature-classes.v1",
        "status": "four-sample native-section temperature-class synthesis",
        "months": list(MONTHS), "class_edges_degC": [None, 0, 1, 2, 3, 5, None],
        "temperature_contract": sections[0]["temperature_contract"],
        "rows": rows, "summary": summary, "conservation_audit": audits,
        "boundary": "Potential-temperature classes partition the same collocated section cells. They are not water masses: salinity, density, neutral surfaces, source history, mixing, and model-native tracer flux are not represented.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--research-dir", type=pathlib.Path, default=pathlib.Path("research"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-drake-temperature-classes-2018.json"))
    args = parser.parse_args()
    section_paths = [args.research_dir / f"osw-m3-oras5-drake-section-input-{month}.json" for month in MONTHS]
    transport_paths = [args.research_dir / f"osw-m3-oras5-drake-transport-{month}.json" for month in MONTHS]
    sections = [json.loads(path.read_text(encoding="utf-8")) for path in section_paths]
    transports = [json.loads(path.read_text(encoding="utf-8")) for path in transport_paths]
    result = synthesize(sections, transports)
    result["sources"] = {
        "sections": [{"path": str(path), "sha256": sha256_file(path)} for path in section_paths],
        "transports": [{"path": str(path), "sha256": sha256_file(path)} for path in transport_paths],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
