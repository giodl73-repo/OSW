"""Fetch a minimal NOAA OISST point series for a marine-heatwave test."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import time
from pathlib import Path


DATASET_ID = "noaa.oisst.v2.highres/sst.day.mean.YEAR.nc"
PSL_DAP = "https://psl.noaa.gov/thredds/dodsC/Datasets/noaa.oisst.v2.highres"
DOI = "https://doi.org/10.25921/RE9P-PT57"
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "atlas" / "data" / "oisst-mhw-point-north-atlantic-1991-2026.json"


def build_query(year, start_index=0, stop_index=None, latitude_index=528, longitude_index=1240):
    days = 366 if dt.date(year, 12, 31).timetuple().tm_yday == 366 else 365
    stop_index = days - 1 if stop_index is None else stop_index
    dataset = f"{PSL_DAP}/sst.day.mean.{year}.nc"
    hyperslab = f"sst[{start_index}:1:{stop_index}][{latitude_index}][{longitude_index}]"
    return dataset, hyperslab


def fetch_slice(year, start_index=0, stop_index=None, latitude_index=528, longitude_index=1240, attempts=5):
    try:
        from netCDF4 import Dataset
    except ImportError as error:
        raise RuntimeError("OISST point acquisition requires requirements-observations.txt") from error
    dataset_url, hyperslab = build_query(year, start_index, stop_index, latitude_index, longitude_index)
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            with Dataset(dataset_url) as dataset:
                resolved_stop = len(dataset.variables["time"]) - 1 if stop_index is None else stop_index
                latitude = float(dataset.variables["lat"][latitude_index])
                longitude = float(dataset.variables["lon"][longitude_index])
                if (latitude, longitude) != (42.125, 310.125):
                    raise ValueError(f"unexpected point coordinate: {(latitude, longitude)}")
                raw_values = dataset.variables["sst"][start_index : resolved_stop + 1, latitude_index, longitude_index]
                if getattr(raw_values, "mask", False) is not False and any(raw_values.mask.flat):
                    raise ValueError("point series contains missing values")
                values = [round(float(value) * 100) for value in raw_values]
            break
        except (OSError, RuntimeError) as error:
            last_error = error
            if attempt == attempts:
                raise RuntimeError(f"OISST DAP failed for {year} after {attempts} attempts") from error
            time.sleep(2 ** (attempt - 1))
    start_date = dt.date(year, 1, 1) + dt.timedelta(days=start_index)
    rows = [[(start_date + dt.timedelta(days=index)).isoformat(), value] for index, value in enumerate(values)]
    digest = hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()
    return rows, {"dataset_url": dataset_url, "hyperslab": hyperslab, "extracted_slice_sha256": digest, "day_count": len(rows)}


def load_checkpoint(output):
    path = Path(output)
    if not path.exists():
        return {}, {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "osw.oisst.mhw-point-source.v1":
        return {}, {}
    cached_rows = {request["year"]: rows for request, rows in zip(payload.get("requests", {}).get("baseline", []), payload.get("series", {}).get("baseline_by_year", []))}
    cached_requests = {request["year"]: request for request in payload.get("requests", {}).get("baseline", [])}
    return cached_rows, cached_requests


def write_checkpoint(output, retrieved_at, baseline_by_year, baseline_requests):
    payload = {
        "schema": "osw.oisst.mhw-point-source.v1",
        "status": "acquisition_incomplete",
        "retrieved_at": retrieved_at,
        "coordinate": {"latitude_degrees_north": 42.125, "longitude_degrees_east": 310.125},
        "requests": {"baseline": baseline_requests},
        "series_encoding": "[ISO date, integer hundredths degree C]",
        "series": {"baseline_by_year": baseline_by_year},
        "boundary": "Incomplete resumable acquisition checkpoint; not scientific evidence.",
    }
    Path(output).write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")


def build(output=DEFAULT_OUTPUT, retrieved_at=None):
    retrieved_at = retrieved_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    cached_rows, cached_requests = load_checkpoint(output)
    baseline_by_year = []
    baseline_requests = []
    for year in range(1991, 2021):
        if year in cached_rows:
            rows, request = cached_rows[year], cached_requests[year]
            print(f"using cached OISST {year}", flush=True)
        else:
            print(f"fetching OISST {year}", flush=True)
            rows, request = fetch_slice(year)
        expected = 366 if dt.date(year, 12, 31).timetuple().tm_yday == 366 else 365
        if len(rows) != expected:
            raise ValueError(f"baseline {year} has {len(rows)} rows; expected {expected}")
        baseline_by_year.append(rows)
        baseline_requests.append({"year": year, **request})
        write_checkpoint(output, retrieved_at, baseline_by_year, baseline_requests)

    baseline = [row for rows in baseline_by_year for row in rows]

    event_start, event_stop = dt.date(2026, 6, 1), dt.date(2026, 8, 20)
    start_index = event_start.timetuple().tm_yday - 1
    stop_index = event_stop.timetuple().tm_yday - 1
    print("fetching OISST 2026 event window", flush=True)
    event, event_request = fetch_slice(2026, start_index, stop_index)
    expected_event = (event_stop - event_start).days + 1
    if len(event) != expected_event:
        raise ValueError(f"event window has {len(event)} rows; expected {expected_event}")

    payload = {
        "schema": "osw.oisst.mhw-point-source.v1",
        "status": "observational_analysis_point_series",
        "source": "NOAA/NCEI OISST v2.1 via NOAA PSL OPeNDAP mirror",
        "dataset_id": DATASET_ID,
        "doi": DOI,
        "retrieved_at": retrieved_at,
        "coordinate": {"latitude_degrees_north": 42.125, "longitude_degrees_east": 310.125},
        "variable": "sea surface temperature",
        "units": "degree_C",
        "precision": 0.01,
        "requests": {
            "baseline": baseline_requests,
            "event": {"year": 2026, **event_request},
        },
        "series_encoding": "[ISO date, integer hundredths degree C]",
        "series": {"baseline": baseline, "event": event},
        "boundary": "One objectively analyzed 0.25-degree surface grid cell. Checksums identify extracted date/value slices, not raw DAP transport bytes. This is not a spatial heatwave footprint, subsurface event, heat content, transport, attribution, or biological-impact estimate.",
    }
    Path(output).write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--retrieved-at")
    args = parser.parse_args()
    payload = build(args.output, args.retrieved_at)
    print(f'wrote {args.output} ({len(payload["series"]["baseline"])} baseline + {len(payload["series"]["event"])} event days)')


if __name__ == "__main__":
    main()
