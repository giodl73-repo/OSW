"""Synthesize four sampled 2018 ORAS5 Drake section calculations."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import statistics


SEASONS = {"201802": "February", "201805": "May", "201808": "August", "201811": "November"}


def summarize(payloads: list[dict]) -> dict:
    if len(payloads) != 4:
        raise ValueError("expected exactly four seasonal payloads")
    months = [payload["section"]["month"] for payload in payloads]
    if months != list(SEASONS):
        raise ValueError(f"expected ordered months {list(SEASONS)}, got {months}")
    section_keys = ("local_x", "local_y_start", "local_y_stop_exclusive", "segment_count", "positive_normal")
    contract = tuple(payloads[0]["section"][key] for key in section_keys)
    if any(tuple(payload["section"][key] for key in section_keys) != contract for payload in payloads[1:]):
        raise ValueError("seasonal calculations do not share one gate contract")
    if any(payload["geometry_contract"] != payloads[0]["geometry_contract"] for payload in payloads[1:]):
        raise ValueError("seasonal calculations do not share one geometry contract")

    rows = []
    for payload in payloads:
        heat = {
            str(case["reference_temperature_degC"]): case["net_PW"]
            for case in payload["reference_relative_heat_transport"]
        }
        rows.append({
            "month": payload["section"]["month"],
            "label": SEASONS[payload["section"]["month"]],
            "positive_Sv": payload["volume_transport"]["positive_Sv"],
            "negative_Sv": payload["volume_transport"]["negative_Sv"],
            "net_Sv": payload["volume_transport"]["net_Sv"],
            "positive_temperature_degC": payload["transport_weighted_temperature_degC"]["positive_branch"],
            "negative_temperature_degC": payload["transport_weighted_temperature_degC"]["negative_branch"],
            "net_temperature_degC": payload["transport_weighted_temperature_degC"]["net"],
            "net_heat_PW_by_reference_degC": heat,
            "input_sha256": payload["input_sha256"],
        })

    def stats(values):
        return {"mean": statistics.fmean(values), "minimum": min(values), "maximum": max(values), "range": max(values) - min(values)}

    references = list(rows[0]["net_heat_PW_by_reference_degC"])
    return {
        "schema": "oceanlines.osw.m3-drake-seasonal-synthesis.v1",
        "status": "four sampled monthly native-section calculations",
        "gate": {key: payloads[0]["section"][key] for key in section_keys},
        "rows": rows,
        "summary": {
            "net_volume_Sv": stats([row["net_Sv"] for row in rows]),
            "positive_volume_Sv": stats([row["positive_Sv"] for row in rows]),
            "negative_volume_Sv": stats([row["negative_Sv"] for row in rows]),
            "net_temperature_degC": stats([row["net_temperature_degC"] for row in rows]),
            "net_heat_PW_by_reference_degC": {
                reference: stats([row["net_heat_PW_by_reference_degC"][reference] for row in rows])
                for reference in references
            },
        },
        "benchmark_context": {
            "older_canonical_mean_Sv": 134.0,
            "older_canonical_standard_deviation_Sv": 11.2,
            "newer_cDrake_mean_Sv": 173.3,
            "newer_cDrake_uncertainty_Sv": 10.7,
            "interpretation": "Noncontemporaneous, method-different context only; not validation targets.",
        },
        "boundary": (
            "Four sampled 2018 monthly means from one assimilative-reanalysis member and one "
            "grid-aligned gate. Not an annual mean, climatology, ensemble uncertainty, mass closure, "
            "eddy heat flux, convergence, or Antarctic heat-delivery estimate."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--research-dir", type=pathlib.Path, default=pathlib.Path("research"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-drake-seasons-2018.json"))
    args = parser.parse_args()
    paths = [args.research_dir / f"osw-m3-oras5-drake-transport-{month}.json" for month in SEASONS]
    payloads = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    result = summarize(payloads)
    result["sources"] = [{"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in paths]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    volume = result["summary"]["net_volume_Sv"]
    print(f"wrote {args.output}: mean {volume['mean']:.3f} Sv, range {volume['range']:.3f} Sv")


if __name__ == "__main__":
    main()
