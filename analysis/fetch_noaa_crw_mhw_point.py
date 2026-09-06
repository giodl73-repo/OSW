"""Extract one auditable point series from NOAA's daily Marine Heatwave Watch files."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import tempfile
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://www.star.nesdis.noaa.gov/pub/socd/mecb/crw/data/marine_heatwave/v1.0.1/category/nc"
DEFAULT_OUTPUT = ROOT / "atlas" / "data" / "noaa-crw-mhw-point-north-atlantic-2026.json"
START = dt.date(2026, 7, 20)
END = dt.date(2026, 8, 20)


def file_url(date):
    stamp = date.strftime("%Y%m%d")
    return f"{BASE_URL}/{date.year}/noaa-crw_mhw_v1.0.1_category_{stamp}.nc"


def download(url, target, attempts=4):
    request = urllib.request.Request(url, headers={"User-Agent": "OSW evidence receipt/1.0"})
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(request, timeout=60) as response, target.open("wb") as handle:
                while chunk := response.read(1024 * 1024):
                    handle.write(chunk)
            return
        except (OSError, TimeoutError):
            if attempt == attempts:
                raise
            time.sleep(2 ** (attempt - 1))


def extract(path, expected_date, latitude=42.125, longitude=-49.875):
    try:
        from netCDF4 import Dataset
    except ImportError as error:
        raise RuntimeError("CRW point acquisition requires requirements-observations.txt") from error
    with Dataset(path) as dataset:
        latitudes = dataset.variables["lat"][:]
        longitudes = dataset.variables["lon"][:]
        latitude_index = int(abs(latitudes - latitude).argmin())
        longitude_index = int(abs(longitudes - longitude).argmin())
        actual_latitude = float(latitudes[latitude_index])
        actual_longitude = float(longitudes[longitude_index])
        if round(actual_latitude, 3) != latitude or round(actual_longitude, 3) != longitude:
            raise ValueError(f"unexpected nearest coordinate: {(actual_latitude, actual_longitude)}")
        if dataset.time_coverage_start[:8] != expected_date.strftime("%Y%m%d"):
            raise ValueError(f"unexpected file date: {dataset.time_coverage_start}")
        category = int(dataset.variables["heatwave_category"][0, latitude_index, longitude_index])
        mask = int(dataset.variables["mask"][0, latitude_index, longitude_index])
        metadata = {
            "product_version": dataset.product_version,
            "source": dataset.source,
            "date_issued": dataset.date_issued,
        }
    return category, mask, metadata


def build(output=DEFAULT_OUTPUT, retrieved_at=None, start=START, end=END):
    rows, files = [], []
    with tempfile.TemporaryDirectory(prefix="osw-crw-mhw-") as temporary:
        date = start
        while date <= end:
            url = file_url(date)
            path = Path(temporary) / url.rsplit("/", 1)[-1]
            print(f"fetching NOAA CRW {date}", flush=True)
            download(url, path)
            raw_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
            category, mask, metadata = extract(path, date)
            rows.append([date.isoformat(), category, mask])
            files.append({"date": date.isoformat(), "url": url, "raw_file_sha256": raw_sha256, **metadata})
            date += dt.timedelta(days=1)
    payload = {
        "schema": "osw.noaa-crw.mhw-point-source.v1",
        "status": "derived_observation_product_point_series",
        "source": "NOAA Coral Reef Watch Daily Global 5km Satellite Marine Heatwave Watch v1.0.1",
        "product_page": "https://coralreefwatch.noaa.gov/product/marine_heatwave/",
        "retrieved_at": retrieved_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "coordinate": {"latitude_degrees_north": 42.125, "longitude_degrees_east": -49.875},
        "window": {"start": start.isoformat(), "end": end.isoformat(), "day_count": len(rows)},
        "series_encoding": "[ISO date, marine heatwave category, mask]",
        "category_meanings": {"0": "none", "1": "moderate", "2": "strong", "3": "severe", "4": "extreme", "5": "beyond extreme"},
        "rows": rows,
        "files": files,
        "boundary": "One exact 0.05-degree surface pixel extracted from daily global derived-product files. Raw-file checksums identify every downloaded NetCDF source. Category exceedance alone is not treated as a duration-qualified event; OSW applies that test separately. This is not an OISST field, subsurface event, heat content, transport, cause, or impact estimate.",
    }
    Path(output).write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--retrieved-at")
    args = parser.parse_args()
    payload = build(args.output, args.retrieved_at)
    print(f'wrote {args.output} ({len(payload["rows"])} days)')


if __name__ == "__main__":
    main()
