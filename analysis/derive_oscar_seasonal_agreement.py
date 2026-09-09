"""Derive cross-season agreement and turning from the OSCAR seasonal pilot."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import pathlib


def load_payload(path: pathlib.Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    return json.loads(text.split("=", 1)[1].strip().removesuffix(";")), hashlib.sha256(raw).hexdigest()


def derive(source: dict, source_artifact_sha256: str, derived_at: str) -> dict:
    rows, columns = source["shape"]
    seasons = source["season_order"]
    output = {
        "mean_u_mm_s": [], "mean_v_mm_s": [], "mean_speed_mm_s": [],
        "cross_season_alignment_thousandths": [],
        "maximum_seasonal_turn_degrees_tenths": [],
        "mean_within_season_persistence_thousandths": [],
    }
    valid = aligned = turning = diffuse = 0
    for index in range(rows * columns):
        samples = []
        missing = False
        for season in seasons:
            data = source["seasons"][season]
            values = (
                data["mean_u_mm_s"][index], data["mean_v_mm_s"][index],
                data["mean_instantaneous_speed_mm_s"][index],
                data["directional_persistence_thousandths"][index],
            )
            if any(value is None for value in values):
                missing = True
                break
            u, v = values[0] / 1000, values[1] / 1000
            magnitude = math.hypot(u, v)
            if magnitude <= 1e-12:
                missing = True
                break
            samples.append((u, v, values[2] / 1000, values[3] / 1000, u / magnitude, v / magnitude))
        if missing:
            for field in output.values():
                field.append(None)
            continue
        mean_u = sum(item[0] for item in samples) / len(samples)
        mean_v = sum(item[1] for item in samples) / len(samples)
        mean_speed = sum(item[2] for item in samples) / len(samples)
        mean_unit_u = sum(item[4] for item in samples) / len(samples)
        mean_unit_v = sum(item[5] for item in samples) / len(samples)
        alignment = min(1.0, math.hypot(mean_unit_u, mean_unit_v))
        maximum_turn = 0.0
        for left in range(len(samples)):
            for right in range(left + 1, len(samples)):
                dot = samples[left][4] * samples[right][4] + samples[left][5] * samples[right][5]
                maximum_turn = max(maximum_turn, math.degrees(math.acos(max(-1.0, min(1.0, dot)))))
        within = sum(item[3] for item in samples) / len(samples)
        output["mean_u_mm_s"].append(round(mean_u * 1000))
        output["mean_v_mm_s"].append(round(mean_v * 1000))
        output["mean_speed_mm_s"].append(round(mean_speed * 1000))
        output["cross_season_alignment_thousandths"].append(round(alignment * 1000))
        output["maximum_seasonal_turn_degrees_tenths"].append(round(maximum_turn * 10))
        output["mean_within_season_persistence_thousandths"].append(round(within * 1000))
        valid += 1
        if alignment >= 0.75 and within >= 0.5:
            aligned += 1
        elif maximum_turn >= 90 and within >= 0.5:
            turning += 1
        else:
            diffuse += 1
    return {
        "schema": "oceanlines.oscar.seasonal-agreement-pilot.v1",
        "status": "derived historical cross-season surface-motion diagnostic",
        "source": source["source"],
        "source_version": source["source_version"],
        "source_period_start": source["period_start"],
        "source_period_stop": source["period_stop"],
        "source_data_sha256": source["source_sha256"],
        "source_artifact_sha256": source_artifact_sha256,
        "derived_at": derived_at,
        "shape": source["shape"],
        "latitude_values": source["latitude_values"],
        "longitude_values": source["longitude_values"],
        "season_order": seasons,
        **output,
        "diagnostics": {
            "cross_season_alignment": "magnitude of the mean of four seasonal unit-direction vectors; 0 cancels, 1 aligns",
            "maximum_seasonal_turn": "largest pairwise angle between four seasonal mean-velocity directions; degrees from 0 to 180",
            "mean_within_season_persistence": "mean of the four seasonal magnitude(mean velocity)/mean speed ratios",
        },
        "interpretive_bins": {
            "aligned_candidate": "cross-season alignment >= 0.75 and mean within-season persistence >= 0.50",
            "turning_candidate": "maximum seasonal turn >= 90 degrees and mean within-season persistence >= 0.50, unless aligned candidate",
            "diffuse_or_other": "all other valid cells",
        },
        "summary": {
            "valid_cells": valid,
            "aligned_candidate_cells": aligned,
            "turning_candidate_cells": turning,
            "diffuse_or_other_cells": diffuse,
            "missing_cells": rows * columns - valid,
        },
        "boundary": (
            "Cross-season agreement and turning are OSW diagnostics derived from one historical year. "
            "They are not natural boundaries, Lagrangian coherent structures, full-depth flow, or heat transport."
        ),
    }


def write_artifact(payload: dict, output: pathlib.Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "// Generated by analysis/derive_oscar_seasonal_agreement.py; do not edit by hand.\n"
        f"window.OSW_OSCAR_SEASONAL_AGREEMENT={json.dumps(payload, ensure_ascii=False, separators=(',', ':'))};\n",
        encoding="utf-8", newline="\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, required=True)
    parser.add_argument("--derived-at")
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    source, digest = load_payload(args.input)
    derived_at = args.derived_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    payload = derive(source, digest, derived_at)
    write_artifact(payload, args.output)
    print(f"wrote {args.output} ({payload['summary']['valid_cells']} valid cells)")
    print(f"source artifact sha256 {digest}")


if __name__ == "__main__":
    main()

