"""Explicitly refresh a pinned NAVO/NCEI operational eddy snapshot.

Requires pyogrio==0.12.1 for the optional shapefile read. The default atlas
build consumes the checked-in JSON receipt and never calls this script.
"""

from __future__ import annotations

import hashlib
import json
import re
import tempfile
import urllib.request
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pyogrio


ROOT = Path(__file__).resolve().parents[1]
URL = "https://www.ncei.noaa.gov/jag/navy/data/satellite_analysis/nafreddy.zip"
LANDING = "https://www.ncei.noaa.gov/products/coastal-surface-analysis-products"


def fetch() -> Path:
    with urllib.request.urlopen(URL, timeout=60) as response:
        archive = response.read()
    digest = hashlib.sha256(archive).hexdigest()
    with tempfile.TemporaryDirectory() as directory:
        folder = Path(directory)
        (folder / "source.zip").write_bytes(archive)
        with zipfile.ZipFile(folder / "source.zip") as source:
            members = source.namelist()
            stems = {Path(name).stem for name in members if name.startswith("nlant_eddies_") and name.endswith(".shp")}
            if len(stems) != 1:
                raise ValueError(f"Expected one North Atlantic eddy shapefile, found {stems}")
            stem = stems.pop()
            expected = [stem + suffix for suffix in (".shp", ".shx", ".dbf")]
            if not all(name in members for name in expected) or "release.txt" not in members:
                raise ValueError("Incomplete NAVO eddy archive")
            release_text = source.read("release.txt").decode("latin-1").strip()
            if "Approved for Public Release" not in release_text:
                raise ValueError("Source public-release statement missing")
            for name in expected:
                (folder / name).write_bytes(source.read(name))
            member_digests = {name: hashlib.sha256(source.read(name)).hexdigest() for name in expected}
        table = pyogrio.read_dataframe(folder / (stem + ".shp"))
        if table.crs is not None:
            raise ValueError(f"Unexpected shapefile CRS metadata: {table.crs}")
        if len(table) != 4 or set(table["Name"]) != {"W26001", "W26002", "C26001", "C26002"}:
            raise ValueError("This source version needs a fresh identity review")
        match = re.fullmatch(r"nlant_eddies_(\d{1,3})_(\d{4})", stem)
        if not match:
            raise ValueError(f"Unexpected NAVO shapefile name: {stem}")
        day_of_year, year = (int(part) for part in match.groups())
        date = (datetime(year, 1, 1) + timedelta(days=day_of_year - 1)).date().isoformat()
        if date[:4] != str(year) or date != "2026-09-25":
            raise ValueError(f"Unexpected NAVO release date: {date}")
        eddies = []
        for _, row in table.sort_values("Name").iterrows():
            polygon = row.geometry
            if polygon.geom_type != "Polygon" or not polygon.is_valid or polygon.interiors:
                raise ValueError(f"Unsupported polygon geometry: {row['Name']}")
            coords = [[float(x), float(y)] for x, y in polygon.exterior.coords]
            if not all(-180 <= x <= 180 and -90 <= y <= 90 for x, y in coords):
                raise ValueError("Coordinates are not longitude/latitude-like")
            eddies.append({
                "provider_code": row["Name"],
                "provider_type": row["Type"],
                "provider_rotation": row["Rotation"],
                "provider_number": row["Number"],
                "provider_origin_year_field": row["Orig_Year"],
                "provider_center_lon_lat": [float(row["Longitude"]), float(row["Latitude"])],
                "source_polygon_lon_lat": coords,
            })
    receipt = {
        "schema": "osw.almanac.navo-freddies-eddy-snapshot.v1",
        "observation_date": date,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_provider": "Naval Oceanographic Office, distributed by NOAA NCEI",
        "source_url": URL,
        "source_landing_page": LANDING,
        "source_zip_sha256": digest,
        "source_member_sha256": member_digests,
        "source_release_text": release_text,
        "source_shapefile": stem,
        "coordinate_reference_status": "No .prj member in source ZIP; numeric coordinates interpreted as longitude/latitude degrees, so exact datum is unspecified.",
        "identity_limit": "Provider W/C codes are dated operational designations; this receipt does not identify any historical named eddy or prove persistence between releases.",
        "geometry_role": "source_operational_eddy_polygon_not_permanent_eddy_extent",
        "eddies": eddies,
    }
    output = ROOT / "research" / f"navo-freddies-eddy-snapshot-{date.replace('-', '')}.json"
    output.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output


if __name__ == "__main__":
    print(fetch())
