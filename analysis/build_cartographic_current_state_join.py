"""Intersect a credited cartographic current-arrow layer with OSW state shapes.

The source polygons are drawn arrows compiled from historical maps. Their
intersections are map relationships, never observed current-core boundaries.
Four published display widths are compared to flag width-sensitive contacts.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

from shapely.geometry import shape
from shapely.ops import transform, unary_union

from build_motion_state_join import ROOT, PROVINCES, polygon_parts


SERVICE = "https://services3.arcgis.com/o98K21Ga5N91Ugjw/ArcGIS/rest/services/Hurricane%20TracksAA/FeatureServer/11"
SCALES = (1_000_000, 5_000_000, 30_000_000, 100_000_000)
NAME_TO_CURRENT = {
    "West Wind Drift / Antarctic Circumpolar": "acc",
    "East Wind Drift / Antarctic Subpolar": "antarctic-coastal",
    "California": "california",
    "Gulf Stream": "gulf-stream",
    "Agulhas": "agulhas",
    "East Australia": "east-australian",
    "Peru": "peru-humboldt",
    "Benguela": "benguela",
    "Canary": "canary",
    "Labrador": "labrador",
    "Brazil": "brazil",
    "North Atlantic": "north-atlantic",
    "Alaska": "alaska",
    "East Greenland": "east-greenland",
    "Falkland": "falkland",
    "Guinea": "guinea",
    "North Equatorial": "north-equatorial",
    "North Pacific": "north-pacific",
    "Norwegian": "norwegian",
    "Oyashio": "oyashio",
    "South Equatorial": "south-equatorial",
    "Western Australia": "west-australian",
    "Caribbean": "caribbean",
    "Eq. Countercurrent": "equatorial-countercurrent",
    "South Atlantic": "south-atlantic",
    "South Indian": "south-indian",
    "South Pacific": "south-pacific",
}
UNMAPPED_REASON = {
    "": "Source arrow has no current name.",
    "Transpolar Drift": "Sea-ice drift is outside this ocean-current ledger.",
    "North Atlantic/Azores": "Combined source label does not identify one current unambiguously.",
    "South Equatorial/South Pacific Gyre": "Combined source label mixes a current and a gyre.",
    "South Indian/Western Australia": "Combined source label does not identify one current unambiguously.",
}
OUTPUT = ROOT / "research" / "cartographic-ocean-current-state-join.json"


def load_source() -> tuple[dict, str]:
    query = urllib.parse.urlencode({
        "where": "1=1",
        "outFields": "OBJECTID,OBJECTID_1,NAME,TEMP,SCALE",
        "outSR": 4326,
        "f": "geojson",
    })
    url = f"{SERVICE}/query?{query}"
    cached = Path(tempfile.gettempdir()) / "osw-current-arrowpolys.geojson"
    if not cached.exists():
        cached.write_bytes(urllib.request.urlopen(url, timeout=60).read())
    raw = cached.read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def project(longitude: float, latitude: float) -> tuple[float, float]:
    return 60 + (longitude + 180) / 360 * 1480, 90 + (90 - latitude) / 180 * 740


def load_states() -> dict:
    root = ET.parse(PROVINCES).getroot()
    land_path = next(item.get("d") for item in root.iter() if item.get("class") == "land-context")
    land = unary_union(polygon_parts(land_path))
    states = {}
    for group in root.iter():
        if "province " not in group.get("class", ""):
            continue
        path = next(item.get("d") for item in group if item.tag.endswith("path"))
        states[group.get("data-code")] = unary_union(polygon_parts(path)).difference(land)
    if len(states) != 56:
        raise ValueError(f"Expected 56 states, found {len(states)}")
    return states


def main() -> None:
    source, source_hash = load_source()
    states = load_states()
    current_index = json.loads((ROOT / "research" / "ocean-current-atlas-index.json").read_text(encoding="utf-8"))
    if not set(NAME_TO_CURRENT.values()) <= set(current_index["entries"]):
        raise ValueError("Cartographic name mapping refers to an unknown OSW current")
    arrow_versions = defaultdict(dict)
    for feature in source["features"]:
        props = feature["properties"]
        original_id = int(props["OBJECTID_1"])
        scale = int(props["SCALE"])
        if scale not in SCALES:
            raise ValueError(f"Unexpected arrow scale {scale}")
        polygon = transform(project, shape(feature["geometry"]))
        if not polygon.is_valid:
            polygon = polygon.buffer(0)
        arrow_versions[original_id][scale] = {
            "name": props["NAME"],
            "temperature_label": props["TEMP"],
            "state_codes": sorted(code for code, state in states.items() if state.intersects(polygon)),
        }
    if len(arrow_versions) != 73 or any(set(versions) != set(SCALES) for versions in arrow_versions.values()):
        raise ValueError("The four cartographic scales do not cover all 73 source arrows")
    arrows = []
    state_stable = defaultdict(set)
    state_sensitive = defaultdict(set)
    for original_id, versions in sorted(arrow_versions.items()):
        names = {item["name"] for item in versions.values()}
        labels = {item["temperature_label"] for item in versions.values()}
        if len(names) != 1 or len(labels) != 1:
            raise ValueError(f"Arrow identity differs between display scales: {original_id}")
        name = names.pop()
        code_sets = [set(versions[scale]["state_codes"]) for scale in SCALES]
        common = set.intersection(*code_sets)
        any_scale = set.union(*code_sets)
        current_id = NAME_TO_CURRENT.get(name)
        normalized_name = name.strip()
        if current_id is None and normalized_name not in UNMAPPED_REASON:
            raise ValueError(f"Unreviewed source-arrow name: {name!r}")
        arrows.append({
            "source_arrow_id": original_id,
            "source_name": name,
            "osw_current_id": current_id,
            "unmapped_reason": None if current_id else UNMAPPED_REASON[normalized_name],
            "source_temperature_label": labels.pop(),
            "stable_state_codes": sorted(common),
            "width_sensitive_state_codes": sorted(any_scale - common),
            "state_codes_by_scale": {str(scale): sorted(versions[scale]["state_codes"]) for scale in SCALES},
        })
        if current_id:
            for code in common:
                state_stable[code].add(current_id)
            for code in any_scale - common:
                state_sensitive[code].add(current_id)
    for code in states:
        state_sensitive[code] -= state_stable[code]
    payload = {
        "schema": "osw.almanac.cartographic-current-state-join.v1",
        "source_layer": SERVICE,
        "source_query": f"{SERVICE}/query?where=1%3D1&outFields=OBJECTID%2COBJECTID_1%2CNAME%2CTEMP%2CSCALE&outSR=4326&f=geojson",
        "source_geojson_sha256": source_hash,
        "source_attribution": "NOAA, National Weather Service, US Army, Maps.com",
        "source_description": "Major wind-driven ocean currents represented by cartographic arrow polygons, compiled from older NOAA National Weather Service and US Army maps. The polygons are optimized for map display and are not observed current footprints or NASA ECCO geometry.",
        "state_geometry": "figures/osw-province-atlas-interactive.svg",
        "scales_compared": list(SCALES),
        "method": "Project all four widths of each source arrow to the OSW equirectangular SVG and intersect coast-masked approximate state polygons. A stable crossing intersects at every width; a width-sensitive contact intersects only at some widths. The OSW name crosswalk is editorial and explicit below.",
        "name_crosswalk": NAME_TO_CURRENT,
        "name_crosswalk_notes": {"East Wind Drift / Antarctic Subpolar": "Reviewed cartographic label mapped to the Antarctic Coastal Current (East Wind Drift), an established westward polar coastal current. The second phrase in the source label is broad; the four arrows are map symbols, not a complete observed coastal path. Source for the current name: https://doi.org/10.1016/j.dsr.2009.06.005."},
        "source_arrow_count": len(arrows),
        "mapped_arrow_count": sum(item["osw_current_id"] is not None for item in arrows),
        "mapped_current_count": len(set(NAME_TO_CURRENT.values())),
        "ledger_currents_without_source_arrow": sorted(set(current_index["entries"]) - set(NAME_TO_CURRENT.values())),
        "unmapped_source_names": sorted({item["source_name"] for item in arrows if item["osw_current_id"] is None}),
        "arrows": arrows,
        "states": {code: {
            "stable_cartographic_current_crossings": sorted(state_stable[code]),
            "width_sensitive_cartographic_contacts": sorted(state_sensitive[code]),
        } for code in states},
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(arrows)} arrows, {payload['mapped_arrow_count']} mapped arrows, {payload['mapped_current_count']} mapped current names")


if __name__ == "__main__":
    main()
