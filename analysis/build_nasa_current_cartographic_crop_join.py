"""Join NASA-named currents' independent map arrows to NASA movie crop boxes."""

import json
from collections import defaultdict
from pathlib import Path

from shapely.geometry import box, shape

from build_cartographic_current_state_join import NAME_TO_CURRENT, SCALES, load_source


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
OUTPUT = RESEARCH / "nasa-current-cartographic-crop-join.json"


def read(name):
    return json.loads((RESEARCH / name).read_text(encoding="utf-8"))


def tile_boxes(tile):
    west, east = tile["longitude_range_unwrapped"]
    south, north = tile["latitude_range"]
    return [box(west + shift, south, east + shift, north) for shift in (-360, 0, 360)]


def build():
    source, source_hash = load_source()
    nasa = read("nasa-perpetual-ocean-objects.json")
    tiles = read("nasa-perpetual-ocean-tile-join.json")
    crop_tiles = [tile for tile in tiles["tiles"] if tile["zoom"] == 2]
    direct = [item for item in nasa["objects"] if item.get("almanac_current_id")]
    polygons = defaultdict(lambda: defaultdict(list))
    for feature in source["features"]:
        current_id = NAME_TO_CURRENT.get(feature["properties"]["NAME"])
        if current_id is None:
            continue
        scale = int(feature["properties"]["SCALE"])
        polygons[current_id][scale].append((int(feature["properties"]["OBJECTID_1"]), shape(feature["geometry"])))
    records = []
    for item in direct:
        current_id = item["almanac_current_id"]
        primary = tiles["nasa_object_joins"][item["id"]]["tile_id"]
        matches = []
        for tile in crop_tiles:
            boxes = tile_boxes(tile)
            scales = []
            arrow_ids = set()
            for scale in SCALES:
                overlapping = [arrow_id for arrow_id, polygon in polygons[current_id][scale]
                               if any(polygon.intersection(crop).area > 1e-9 for crop in boxes)]
                if overlapping:
                    scales.append(scale)
                    arrow_ids.update(overlapping)
            if scales:
                matches.append({
                    "tile_id": tile["id"],
                    "url": tile["url"],
                    "map_contact": "all_four_arrow_widths" if len(scales) == len(SCALES) else "width_sensitive",
                    "source_arrow_ids": sorted(arrow_ids),
                    "source_scales": scales,
                    "is_primary_locator_crop": tile["id"] == primary,
                })
        records.append({
            "nasa_object_id": item["id"],
            "current_id": current_id,
            "name": item["name"],
            "primary_locator_crop_id": primary,
            "cartographic_source_arrow_count": len({arrow_id for versions in polygons[current_id].values() for arrow_id, _ in versions}),
            "cartographic_crop_contacts": matches,
            "coverage_status": "cartographic_arrow_join" if any(polygons[current_id].values()) else "no_mapped_source_arrow",
        })
    return {
        "schema": "osw.almanac.nasa-current-cartographic-crop-join.v1",
        "nasa_object_ledger": "research/nasa-perpetual-ocean-objects.json",
        "cartographic_source": "research/cartographic-ocean-current-state-join.json",
        "cartographic_source_geojson_sha256": source_hash,
        "nasa_crop_source": "research/nasa-perpetual-ocean-tile-join.json",
        "method": "Intersect independent cartographic arrow polygons at each of four published display widths with each of NASA's 56 highest-zoom crop rectangles, accounting for 360-degree wrap. A crop contact at all four widths is stable map coverage; fewer widths are sensitive to how the arrow is drawn.",
        "claim_limit": "The arrows are historical map symbols, not measured current boundaries or ECCO model feature footprints. A map-arrow/crop contact is a navigation aid; it does not prove the NASA movie identifies the current in that crop or frame. No arrow means no polygon-based crop claim.",
        "source_scales": list(SCALES),
        "nasa_current_count": len(records),
        "records": records,
    }


if __name__ == "__main__":
    result = build()
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote cartographic crop joins for {len(result['records'])} NASA current records")
