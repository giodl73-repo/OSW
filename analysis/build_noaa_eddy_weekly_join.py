"""Join a MUNSTER daily eddy snapshot to the overlapping NOAA weekly tracks.

The weekly product's trajectory_id variable is not used as a persistent ID:
in the inspected 2023-06-01 file nearly all its values are zero. Match day-one
center and radius instead, then retain a reference scoped to this weekly file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import tempfile
import urllib.request
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from pathlib import Path

from netCDF4 import Dataset


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = "https://coastwatch.noaa.gov/data/pub0054/coastwatch/products/eddy_tracking/netcdf/munster/eddy_tracks"


def cache_file(date: str, end: str) -> Path:
    return Path(tempfile.gettempdir()) / f"osw-munster-tracks-{date}-{end}.nc"


def read_tracks(source: Path, daily: dict, date: str, end: str) -> dict:
    matches = {}
    with Dataset(source) as nc:
        days = [datetime.fromtimestamp(int(value), UTC).strftime("%Y-%m-%d") for value in nc.variables["time"][:]]
        assert days == [(datetime.strptime(date, "%Y%m%d") + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
        for polarity, prefix in (("anticyclonic", "anti"), ("cyclonic", "cyclo")):
            lon = nc.variables[f"{prefix}_lon_center"][:]
            lat = nc.variables[f"{prefix}_lat_center"][:]
            radius = nc.variables[f"{prefix}_radius"][:]
            by_center = defaultdict(list)
            for column in range(lon.shape[1]):
                if math.isfinite(float(lon[0, column])) and math.isfinite(float(lat[0, column])):
                    by_center[(float(lon[0, column]), float(lat[0, column]))].append(column)
            used = set()
            for item in daily["entries"]:
                if item["polarity"] != polarity:
                    continue
                candidates = by_center.get(tuple(item["center"]), [])
                if not candidates:
                    raise ValueError(f"No weekly center for {item['id']}")
                column = min(candidates, key=lambda j: abs(float(radius[0, j]) / 1000 - item["radius_km"]))
                mismatch_km = abs(float(radius[0, column]) / 1000 - item["radius_km"])
                if mismatch_km > 0.001 or column in used:
                    raise ValueError(f"Ambiguous weekly match for {item['id']}: {mismatch_km} km")
                used.add(column)
                positions = []
                for day_index, day in enumerate(days):
                    longitude = float(lon[day_index, column])
                    latitude = float(lat[day_index, column])
                    if math.isfinite(longitude) and math.isfinite(latitude):
                        if not (-180 <= longitude <= 180 and -90 <= latitude <= 90):
                            raise ValueError(f"Bad track coordinate for {item['id']}")
                        positions.append({"date": day, "center": [round(longitude, 3), round(latitude, 3)]})
                matches[item["id"]] = {
                    "file_scoped_track_ref": f"{date}-{end}-{prefix}-column-{column + 1:04d}",
                    "weekly_column_ordinal": column + 1,
                    "positions": positions,
                }
    if set(matches) != {item["id"] for item in daily["entries"]}:
        raise ValueError("Weekly join did not cover the complete daily snapshot")
    return matches


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default="20230601", help="Start date YYYYMMDD; requires a matching daily OSW snapshot")
    args = parser.parse_args()
    date = args.date
    start = datetime.strptime(date, "%Y%m%d")
    end = (start + timedelta(days=6)).strftime("%Y%m%d")
    daily_path = ROOT / "research" / f"noaa-munster-eddy-state-{date}.json"
    daily = json.loads(daily_path.read_text(encoding="utf-8"))
    if daily["date"] != start.strftime("%Y-%m-%d"):
        raise ValueError("Daily snapshot date does not match requested week")
    filename = f"MUNSTER_v1_eddytraject_multi_global_7days_s{date}_e{end}.nc"
    url = f"{SOURCE_ROOT}/{filename}"
    source = cache_file(date, end)
    if not source.exists():
        urllib.request.urlretrieve(url, source)
    sha256 = hashlib.sha256(source.read_bytes()).hexdigest()
    matches = read_tracks(source, daily, date, end)
    payload = {
        "schema": "osw.almanac.noaa-munster-weekly-join.v1",
        "start_date": start.strftime("%Y-%m-%d"),
        "end_date": (start + timedelta(days=6)).strftime("%Y-%m-%d"),
        "source": url,
        "source_sha256": sha256,
        "daily_join": str(daily_path.relative_to(ROOT)).replace("\\", "/"),
        "daily_source_sha256": daily["source_sha256"],
        "matching_rule": "Same polarity and exact NOAA day-one center; disambiguate any duplicate center with radius within 0.001 km of the rounded daily snapshot. Every daily eddy must match one distinct weekly column.",
        "identity_limit": "The track reference is the column ordinal in this seven-day NOAA file. It is not a persistent inter-week ID, a NASA ECCO particle identity, or a historical named eddy. The provider trajectory_id variable was not used because its values in this file do not identify the columns.",
        "matched_daily_eddies": len(matches),
        "tracks": matches,
    }
    output = ROOT / "research" / f"noaa-munster-eddy-weekly-join-{date}-{end}.json"
    output.write_text(json.dumps(payload, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(matches)} daily-to-weekly track joins to {output}")


if __name__ == "__main__":
    main()
