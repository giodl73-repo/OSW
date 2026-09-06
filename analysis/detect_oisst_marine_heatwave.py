"""Detect marine heatwaves in OSW's checksum-pinned OISST point series."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "atlas" / "data" / "oisst-mhw-point-north-atlantic-1991-2026.json"
DEFAULT_OUTPUT = ROOT / "research" / "osw-d1-oisst-mhw-point-2026.json"


def canonical_doy(date):
    """Return day on a 366-day calendar, leaving a slot for February 29."""
    day = date.timetuple().tm_yday
    leap = date.year % 4 == 0 and (date.year % 100 != 0 or date.year % 400 == 0)
    return day + (not leap and date.month >= 3)


def percentile(values, percentile_value):
    """R/NumPy-compatible Type 7 linear sample quantile."""
    ordered = sorted(values)
    if not ordered:
        raise ValueError("cannot calculate a percentile from no values")
    position = (len(ordered) - 1) * percentile_value / 100
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (position - lower) * (ordered[upper] - ordered[lower])


def circular_mean(values, width):
    if width % 2 != 1:
        raise ValueError("smoothing width must be odd")
    half = width // 2
    return [sum(values[(index + offset) % len(values)] for offset in range(-half, half + 1)) / width for index in range(len(values))]


def build_climatology(rows, percentile_value=90, window_half_width=5, smoothing_width=31):
    parsed = [(dt.date.fromisoformat(date), value / 100) for date, value in rows]
    means, thresholds = [], []
    for target in range(1, 367):
        pool = [
            value
            for date, value in parsed
            if min(abs(canonical_doy(date) - target), 366 - abs(canonical_doy(date) - target)) <= window_half_width
        ]
        means.append(sum(pool) / len(pool))
        thresholds.append(percentile(pool, percentile_value))
    return circular_mean(means, smoothing_width), circular_mean(thresholds, smoothing_width)


def qualifying_runs(exceedance, minimum_duration=5, maximum_gap=2):
    runs = []
    start = None
    for index, exceeds in enumerate(exceedance + [False]):
        if exceeds and start is None:
            start = index
        elif not exceeds and start is not None:
            if index - start >= minimum_duration:
                runs.append([start, index - 1])
            start = None
    merged = []
    for run in runs:
        if merged and run[0] - merged[-1][1] - 1 <= maximum_gap:
            merged[-1][1] = run[1]
        else:
            merged.append(run)
    return merged


def detect(event_rows, seasonal_mean, threshold, minimum_duration=5, maximum_gap=2):
    records = []
    for date_text, hundredths in event_rows:
        date = dt.date.fromisoformat(date_text)
        day = canonical_doy(date) - 1
        temperature = hundredths / 100
        records.append({
            "date": date_text,
            "temperature_c": temperature,
            "seasonal_mean_c": seasonal_mean[day],
            "threshold_c": threshold[day],
            "exceeds": temperature > threshold[day],
        })
    events = []
    for start, end in qualifying_runs([record["exceeds"] for record in records], minimum_duration, maximum_gap):
        span = records[start : end + 1]
        intensities = [record["temperature_c"] - record["threshold_c"] for record in span]
        anomalies = [record["temperature_c"] - record["seasonal_mean_c"] for record in span]
        peak = max(range(len(span)), key=lambda index: intensities[index])
        events.append({
            "start_date": span[0]["date"],
            "end_date": span[-1]["date"],
            "duration_days": len(span),
            "peak_date": span[peak]["date"],
            "maximum_intensity_above_threshold_c": round(intensities[peak], 3),
            "mean_intensity_above_threshold_c": round(sum(intensities) / len(intensities), 3),
            "cumulative_intensity_above_threshold_c_days": round(sum(intensities), 3),
            "mean_anomaly_above_seasonal_mean_c": round(sum(anomalies) / len(anomalies), 3),
            "left_censored": start == 0,
            "right_censored": end == len(records) - 1,
        })
    return records, events


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(source_path=DEFAULT_SOURCE, output_path=DEFAULT_OUTPUT):
    source_path, output_path = Path(source_path), Path(output_path)
    source = json.loads(source_path.read_text(encoding="utf-8"))
    if source.get("status") != "observational_analysis_point_series":
        raise ValueError("source acquisition is not complete")
    seasonal_mean, threshold = build_climatology(source["series"]["baseline"])
    records, events = detect(source["series"]["event"], seasonal_mean, threshold)
    payload = {
        "schema": "osw.detected-ocean-object.v1",
        "detection_id": "OSW-D1",
        "status": "detected_object" if events else "no_event_detected",
        "object_id": "OBJ046",
        "object_name": "marine heatwave",
        "evidence_origin": "observational_analysis",
        "source_artifact": source_path.relative_to(ROOT).as_posix(),
        "source_artifact_sha256": sha256(source_path),
        "coordinate": source["coordinate"],
        "method": {
            "baseline": "1991-01-01 through 2020-12-31",
            "percentile": 90,
            "seasonal_pool": "11-day circular window centered on each canonical day of year",
            "climatology_smoothing": "31-day circular moving mean",
            "minimum_duration_days": 5,
            "join_events_across_gaps_days": 2,
            "threshold_operator": "strictly greater than",
            "algorithm_order": "retain contiguous exceedance runs of at least five days, then join retained events across gaps of at most two days",
        },
        "event_window": {"start": records[0]["date"], "end": records[-1]["date"], "day_count": len(records)},
        "event_count": len(events),
        "events": events,
        "identity_evaluation": {
            "result": "pass" if events else "fail",
            "test": "SST exceeds a seasonally varying local high-percentile threshold for the required duration under a declared gap rule.",
            "finding": f"{len(events)} qualifying event(s) detected at the declared OISST cell." if events else "No qualifying event was detected in the declared window.",
        },
        "daily_series": records,
        "boundary": "A time-bounded detection at one objectively analyzed surface grid cell. It is not a spatial footprint, subsurface heatwave, ocean heat content, heat transport, causal attribution, or ecological-impact estimate. Events touching either window edge are explicitly censored.",
    }
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build(args.source, args.output)
    print(f'wrote {args.output}: {payload["status"]}, {payload["event_count"]} event(s)')


if __name__ == "__main__":
    main()
