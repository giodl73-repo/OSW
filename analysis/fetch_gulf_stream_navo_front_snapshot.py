"""Pin one dated NAVO Gulf Stream front bulletin exposed by NOAA OPC.

The local receipt contains parsed coordinates and a response hash, not a copy
of the provider's HTML bulletin. Run explicitly while the requested date is
still the latest bulletin; normal release builds only read the pinned receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = "https://ocean.weather.gov/gulf_stream_text.php"
HEADER = re.compile(r"GULF STREAM (NORTH|SOUTH) WALL DATA FOR (\d{2} [A-Z]{3} \d{2}):")
POINT = re.compile(r"(?<![\w.])(\d{1,2}\.\d)N(\d{1,3}\.\d)W(?![\w.])")


def parse_bulletin(html: bytes, expected_date: str) -> dict:
    page = BeautifulSoup(html, "html.parser")
    pre = page.find("pre")
    if pre is None:
        raise ValueError("The NOAA page has no bulletin <pre> block")
    bulletin = pre.get_text()
    headers = list(HEADER.finditer(bulletin))
    if [match.group(1) for match in headers] != ["NORTH", "SOUTH"]:
        raise ValueError("Expected one north wall and one south wall")
    dates = [datetime.strptime(match.group(2), "%d %b %y").date().isoformat() for match in headers]
    if dates != [expected_date, expected_date]:
        raise ValueError(f"Bulletin date {dates} differs from requested {expected_date}")
    fronts = {}
    for index, match in enumerate(headers):
        end = headers[index + 1].start() if index + 1 < len(headers) else bulletin.index("2.  FRONTAL DATA", match.end())
        block = bulletin[match.end():end]
        coordinates = [[-float(lon), float(lat)] for lat, lon in POINT.findall(block)]
        if len(coordinates) < 100 or len(set(map(tuple, coordinates))) < 100:
            raise ValueError(f"Too few distinct {match.group(1).lower()} wall points")
        residue = POINT.sub("", block)
        if re.search(r"\d+(?:\.\d+)?[NS]\d+(?:\.\d+)?[EW]", residue):
            raise ValueError(f"Unparsed coordinate in {match.group(1).lower()} wall")
        fronts[match.group(1).lower() + "_wall"] = {"geometry": {"type": "LineString", "coordinates": coordinates},
                                                     "point_count": len(coordinates)}
    return {
        "schema": "osw.almanac.navo-gulf-stream-frontal-snapshot.v1",
        "date": expected_date,
        "source_url": SOURCE_URL,
        "source_provider": "Naval Oceanographic Office, provided via NOAA Ocean Prediction Center",
        "source_response_sha256": hashlib.sha256(html).hexdigest(),
        "source_text_role": "Gulf Stream north and south wall frontal analysis",
        "source_method_note": "Bulletin says frontal data are based on maximum surface temperature change over 10 nautical miles in detailed infrared satellite analyses; absolute locations depend on local effects and time since observation.",
        "geometry_role": "dated_analyzed_surface_front_not_current_axis_or_full_footprint",
        "coordinate_reference_system": "OGC:CRS84",
        "coordinate_precision": "0.1 degree as reported",
        "fronts": fronts,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", required=True, help="Expected bulletin date, YYYY-MM-DD")
    args = parser.parse_args()
    target = ROOT / "research" / f"gulf-stream-navo-front-{args.date.replace('-', '')}.json"
    if target.exists():
        raise SystemExit(f"Receipt already exists: {target}")
    response = requests.get(SOURCE_URL, timeout=25)
    response.raise_for_status()
    receipt = parse_bulletin(response.content, args.date)
    target.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Pinned {receipt['date']} NAVO front: "
          f"{receipt['fronts']['north_wall']['point_count']} north, "
          f"{receipt['fronts']['south_wall']['point_count']} south points")


if __name__ == "__main__":
    main()
