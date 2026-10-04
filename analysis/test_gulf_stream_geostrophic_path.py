"""Check the pinned velocity decoder and the dated path's numerical limits."""

import hashlib
import json
from pathlib import Path

from build_gulf_stream_geostrophic_path import SOURCE, build, load_field, sample_velocity


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    source_bytes = SOURCE.read_bytes()
    source = json.loads(source_bytes)
    fields = load_field(source)
    origin_lon, origin_lat = source["grid_origin_lon_lat"]
    row, column = 24, 27
    lon = origin_lon + column * 0.25
    lat = origin_lat + row * 0.25
    decoded = sample_velocity(source, fields, lon, lat)
    expected = tuple(source["velocity_fields_raw_int32"][name][row][column] * 0.0001
                     for name in ("ugos", "vgos"))
    assert decoded is not None and all(abs(a - b) < 1e-10 for a, b in zip(decoded, expected))
    midpoint = sample_velocity(source, fields, lon + 0.125, lat + 0.125)
    means = tuple(sum(source["velocity_fields_raw_int32"][name][i][j]
                      for i in (row, row + 1) for j in (column, column + 1)) * 0.000025
                  for name in ("ugos", "vgos"))
    assert midpoint is not None and all(abs(a - b) < 1e-10 for a, b in zip(midpoint, means))
    output = json.loads((ROOT / "research" / "gulf-stream-geostrophic-path-20260925.json").read_text(encoding="utf-8"))
    assert output == build()
    assert output["source_subset_sha256"] == hashlib.sha256(source_bytes).hexdigest()
    assert output["representative"]["stop_reason"] == "downstream_longitude_gate"
    assert output["representative"]["seed_lon_lat"] == [-72.875, 36.875]
    assert 2250 < output["representative"]["segment_length_km"] < 2310
    assert {row["state_code"] for row in output["state_relations"]} == {"GFST", "NWCS"}
    assert abs(sum(row["intersection_length_km"] for row in output["state_relations"])
               - output["representative"]["segment_length_km"]) < 0.2
    assert output["adjacent_seed_sensitivity"][0]["stop_reason"] == "downstream_longitude_gate"
    assert output["adjacent_seed_sensitivity"][1]["stop_reason"] == "speed_below_threshold"
    assert all(row["stop_reason"] == "downstream_longitude_gate" and
               abs(row["segment_length_km"] - output["representative"]["segment_length_km"]) < 5
               for row in output["step_size_sensitivity"])
    print("OK: pinned NOAA velocity decoding, dated streamline, sensitivity, and state join")


if __name__ == "__main__":
    main()
