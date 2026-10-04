"""Join one NOAA MUNSTER daily eddy contour file to the 56 OSW state shapes.

This gives dated detected eddies with local daily IDs. It does not equate a
NOAA detection with a NASA ECCO model particle pattern or a Horizon eddy name.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.request import Request, urlopen

import netCDF4
import numpy as np
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

from build_motion_state_join import polygon_parts


ROOT = Path(__file__).resolve().parents[1]
PROVINCES = ROOT / "figures" / "osw-province-atlas-interactive.svg"
SOURCE_DIRECTORY = "https://coastwatch.noaa.gov/data/pub0054/coastwatch/products/eddy_tracking/netcdf/munster/eddy_identification/"
FRAME = box(60, 90, 1540, 830)


def source_url(date: str) -> str:
    return SOURCE_DIRECTORY + f"MUNSTER_v1_eddyident_multi_global_daily_s{date}_e{date}.nc"


def cached_source(date: str) -> Path:
    path = Path(tempfile.gettempdir()) / f"osw-munster-{date}.nc"
    if path.exists() and path.stat().st_size > 100_000:
        return path
    request = Request(source_url(date), headers={"User-Agent": "OSW-Motion-Atlas/1.0"})
    temporary = path.with_suffix(".part")
    with urlopen(request, timeout=45) as response, temporary.open("wb") as output:
        while chunk := response.read(1024 * 1024):
            output.write(chunk)
    temporary.replace(path)
    return path


def state_shapes() -> dict[str, object]:
    root = ET.parse(PROVINCES).getroot()
    land = unary_union(polygon_parts(next(item.get("d") for item in root.iter() if item.get("class") == "land-context")))
    states = {}
    for group in root.iter():
        if "province " not in group.get("class", ""):
            continue
        path = next(item.get("d") for item in group if item.tag.endswith("path"))
        states[group.get("data-code")] = unary_union(polygon_parts(path)).difference(land)
    if len(states) != 56:
        raise ValueError("Expected 56 OSW state shapes")
    return states


def contour_shapes(longitudes: np.ndarray, latitudes: np.ndarray) -> list[object]:
    valid = np.isfinite(longitudes) & np.isfinite(latitudes)
    points = list(zip(longitudes[valid].astype(float), latitudes[valid].astype(float)))
    if len(points) < 4:
        return []
    unwrapped = [points[0]]
    for longitude, latitude in points[1:]:
        prior = unwrapped[-1][0]
        while longitude - prior > 180:
            longitude -= 360
        while longitude - prior < -180:
            longitude += 360
        unwrapped.append((longitude, latitude))
    mapped = [(60 + (lon + 180) / 360 * 1480, 90 + (90 - lat) / 180 * 740) for lon, lat in unwrapped]
    polygon = Polygon(mapped)
    if not polygon.is_valid:
        polygon = polygon.buffer(0)
    if polygon.is_empty or polygon.area == 0:
        return []
    pieces = []
    for shift in (-1480, 0, 1480):
        from shapely.affinity import translate
        copy = translate(polygon, xoff=shift)
        if copy.intersects(FRAME):
            pieces.append(copy.intersection(FRAME))
    return pieces


def clean_number(value: object, digits: int = 3) -> float | None:
    number = float(value)
    return round(number, digits) if np.isfinite(number) else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default="20230601", help="One NOAA UTC date in YYYYMMDD format; default overlaps the NASA PO2 period")
    args = parser.parse_args()
    if len(args.date) != 8 or not args.date.isdigit():
        parser.error("--date must be YYYYMMDD")
    source = cached_source(args.date)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    states = state_shapes()
    entries = []
    state_index = {code: {"contained": [], "intersected": []} for code in states}
    with netCDF4.Dataset(source) as dataset:
        for polarity, prefix, dimension in (("anticyclonic", "anticyclonic", "num_anticyclones"), ("cyclonic", "cyclonic", "num_cyclones")):
            centers_lon = dataset[f"{prefix}_center_lon"][:]
            centers_lat = dataset[f"{prefix}_center_lat"][:]
            contours_lon = dataset[f"{prefix}_contour_lon"][:]
            contours_lat = dataset[f"{prefix}_contour_lat"][:]
            radii = dataset[f"{prefix}_radius"][:]
            areas = dataset[f"{prefix}_area"][:]
            amplitudes = dataset[f"{prefix}_amplitude"][:]
            assert dataset[f"{prefix}_radius"].units.strip() == "m"
            assert dataset[f"{prefix}_area"].units.strip() == "m2"
            assert dataset[f"{prefix}_amplitude"].units.strip() == "m"
            for offset in range(len(dataset.dimensions[dimension])):
                daily_id = f"{args.date}-{polarity[:4]}-{offset + 1:04d}"
                shapes = contour_shapes(contours_lon[offset], contours_lat[offset])
                contained = []
                intersected = []
                for code, state in states.items():
                    if not shapes or not any(state.intersects(shape) for shape in shapes):
                        continue
                    if all(state.covers(shape) for shape in shapes):
                        contained.append(code)
                        state_index[code]["contained"].append(daily_id)
                    else:
                        intersected.append(code)
                        state_index[code]["intersected"].append(daily_id)
                entries.append({
                    "id": daily_id,
                    "source_ordinal": offset + 1,
                    "polarity": polarity,
                    "center": [clean_number(centers_lon[offset]), clean_number(centers_lat[offset])],
                    "radius_km": clean_number(radii[offset] / 1000),
                    "area_km2": clean_number(areas[offset] / 1_000_000),
                    "amplitude_cm": clean_number(amplitudes[offset] * 100),
                    "contained_states": contained,
                    "intersected_states": intersected,
                    "name": None,
                    "persistent_track_id": None,
                })
    output = ROOT / "research" / f"noaa-munster-eddy-state-{args.date}.json"
    payload = {
        "schema": "osw.almanac.noaa-munster-eddy-state-snapshot.v1",
        "date": f"{args.date[:4]}-{args.date[4:6]}-{args.date[6:]}",
        "source": source_url(args.date),
        "source_sha256": digest,
        "source_product": "NOAA CoastWatch MUNSTER v1 daily eddy identification",
        "source_documentation": "https://coastwatch.noaa.gov/cwn/products/experimental-eddy-products.html",
        "state_geometry": "figures/osw-province-atlas-interactive.svg",
        "method": "Project NOAA's dated closed contour coordinates onto the OSW equirectangular map. An eddy is contained where the entire contour is covered by a coast-masked approximate state polygon; otherwise it intersects each state polygon it touches. Antimeridian contours are unwrapped and split into visible copies. Relations are valid only for this date and these two products' declared geometry.",
        "identity_limit": "Daily ordinal IDs are local to this file, not persistent NOAA track IDs, NASA model eddy identities, or Horizon Marine names. No named-ring match is inferred.",
        "coverage_limit": "MUNSTER daily field spans approximately 60°S–60°N; no eddy absence is inferred outside that latitude range or from undetected scales.",
        "entries": entries,
        "states": state_index,
    }
    output.write_text(json.dumps(payload, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(entries)} daily detections; {sum(len(v['contained']) for v in state_index.values())} containment and {sum(len(v['intersected']) for v in state_index.values())} intersection relations")


if __name__ == "__main__":
    main()
