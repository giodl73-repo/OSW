"""Check that the five-date audit retains failure cases and pinned evidence."""

import json

from analyze_gulf_stream_geostrophic_repeat import OUTPUT, build


def main() -> None:
    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert stored == build()
    assert stored["dates"] == ["2026-09-18", "2026-09-24", "2026-09-25",
                               "2026-09-26", "2026-09-27"]
    summary = stored["summary"]
    assert summary["date_count"] == 5
    assert summary["daily_selected_seeds_reaching_downstream_gate"] == 4
    assert summary["adjacent_seeds_reaching_downstream_gate"] == 3
    assert summary["adjacent_seed_trace_count"] == 10
    first = stored["observations"][0]
    selected = next(row for row in first["traces"] if "daily_maximum_eastward" in row["seed_role"])
    assert selected["stop_reason"] == "midpoint_speed_below_threshold"
    assert selected["westward_step_count"] > 0
    assert selected["first_eastward_crossing_latitudes"]["-50.0"] is None
    assert all(item["source_response_sha256"] and item["source_subset_sha256"]
               for item in stored["observations"])
    print("OK: pinned five-date Gulf Stream repeat retains seed and temporal failures")


if __name__ == "__main__":
    main()
