"""Synthesize vertical anatomy of four native Drake section calculations."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import statistics


MONTHS = ("201802", "201805", "201808", "201811")
BANDS = ((0, 200), (200, 700), (700, 1500), (1500, 3000), (3000, None))


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def band_label(top: int, bottom: int | None) -> str:
    return f"{top}–{bottom} m" if bottom is not None else f">{top} m"


def synthesize(payloads: list[dict]) -> dict:
    thicknesses = [float(layer["thickness_m"]) for layer in payloads[0]["layers"]]
    if any([float(layer["thickness_m"]) for layer in payload["layers"]] != thicknesses for payload in payloads[1:]):
        raise ValueError("layer thickness coordinates differ across inputs")
    bounds = []
    depth = 0.0
    for thickness in thicknesses:
        bounds.append((depth, depth + thickness, depth + thickness / 2))
        depth += thickness
    rho = float(payloads[0]["constants"]["density_kg_m3"])
    cp = float(payloads[0]["constants"]["heat_capacity_J_kg_K"])
    pw_per_degC_Sv = rho * cp * 1e-9
    rows = []
    for payload, month in zip(payloads, MONTHS):
        for top, bottom in BANDS:
            indices = [i for i, (_, _, midpoint) in enumerate(bounds) if midpoint >= top and (bottom is None or midpoint < bottom)]
            layers = [payload["layers"][i] for i in indices]
            positive = sum(layer["positive_volume_Sv"] for layer in layers)
            negative = sum(layer["negative_volume_Sv"] for layer in layers)
            temp_positive = sum(layer["positive_temperature_transport_degC_Sv"] for layer in layers)
            temp_negative = sum(layer["negative_temperature_transport_degC_Sv"] for layer in layers)
            rows.append({
                "month": month, "band": band_label(top, bottom), "top_m": top, "bottom_m": bottom,
                "level_start": indices[0] if indices else None, "level_stop_exclusive": indices[-1] + 1 if indices else None,
                "positive_volume_Sv": positive, "negative_volume_Sv": negative, "net_volume_Sv": positive + negative,
                "positive_heat_0C_PW": temp_positive * pw_per_degC_Sv,
                "negative_heat_0C_PW": temp_negative * pw_per_degC_Sv,
                "net_heat_0C_PW": (temp_positive + temp_negative) * pw_per_degC_Sv,
            })
    summaries = []
    for top, bottom in BANDS:
        label = band_label(top, bottom)
        selected = [row for row in rows if row["band"] == label]
        summary = {"band": label, "top_m": top, "bottom_m": bottom}
        for key in ("positive_volume_Sv", "negative_volume_Sv", "net_volume_Sv", "positive_heat_0C_PW", "negative_heat_0C_PW", "net_heat_0C_PW"):
            values = [row[key] for row in selected]
            summary[key] = {"mean": statistics.fmean(values), "minimum": min(values), "maximum": max(values), "range": max(values) - min(values)}
        summaries.append(summary)
    audits = []
    for payload, month in zip(payloads, MONTHS):
        selected = [row for row in rows if row["month"] == month]
        heat0 = next(item["net_PW"] for item in payload["reference_relative_heat_transport"] if item["reference_temperature_degC"] == 0)
        audits.append({
            "month": month,
            "volume_residual_Sv": sum(row["net_volume_Sv"] for row in selected) - payload["volume_transport"]["net_Sv"],
            "heat_0C_residual_PW": sum(row["net_heat_0C_PW"] for row in selected) - heat0,
        })
    return {
        "schema": "oceanlines.osw.m3-drake-vertical-anatomy.v1",
        "status": "four-sample native-section depth-stratum synthesis",
        "months": list(MONTHS), "depth_assignment": "nominal model-level midpoint assigned wholly to one declared stratum",
        "maximum_nominal_model_depth_m": depth, "rows": rows, "summary": summaries, "conservation_audit": audits,
        "boundary": "Five declared depth strata summarize native layer contributions. Midpoint binning is descriptive and does not create water masses, neutral-density classes, overturning streamfunctions, convergence, or Antarctic heat delivery.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--research-dir", type=pathlib.Path, default=pathlib.Path("research"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-drake-vertical-2018.json"))
    args = parser.parse_args()
    paths = [args.research_dir / f"osw-m3-oras5-drake-transport-{month}.json" for month in MONTHS]
    payloads = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    result = synthesize(payloads)
    result["sources"] = [{"path": str(path), "sha256": sha256_file(path)} for path in paths]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
