"""Join every OSW ocean state to NASA's published Perpetual Ocean 2 crops.

The join uses overlap on the equirectangular atlas display. It supplies video
navigation, not a current, eddy, or state-boundary observation from NASA.
"""

from __future__ import annotations

import json
from pathlib import Path

from shapely.geometry import box
from shapely.ops import unary_union

from build_cartographic_current_state_join import load_states, project
from build_motion_state_join import ROOT


TILES = ROOT / "research" / "nasa-perpetual-ocean-tile-join.json"
RELEASE_MEDIA = ROOT / "research" / "nasa-perpetual-ocean-release-media.json"
OUTPUT = ROOT / "research" / "nasa-perpetual-ocean-state-tile-join.json"


def tile_shape(tile: dict):
    west, east = tile["longitude_range_unwrapped"]
    south, north = tile["latitude_range"]
    boxes = []
    for shift in (-360, 0, 360):
        x0, y0 = project(west + shift, north)
        x1, y1 = project(east + shift, south)
        boxes.append(box(x0, y0, x1, y1))
    return unary_union(boxes)


def main() -> None:
    tile_ledger = json.loads(TILES.read_text(encoding="utf-8"))
    release_media = json.loads(RELEASE_MEDIA.read_text(encoding="utf-8"))
    polar_release = next(item for item in release_media["releases"] if item["release_id"] == "po2-polar")
    polar_movies = {movie["filename"]: movie for movie in polar_release["movies"]}
    north_movie = polar_movies["north_1080.mp4"]
    south_movie = polar_movies["south_1080.mp4"]
    states = load_states()
    prepared = [(tile, tile_shape(tile)) for tile in tile_ledger["tiles"]]
    state_records = {}
    for code, polygon in states.items():
        matches = []
        for tile, rectangle in prepared:
            overlap = polygon.intersection(rectangle).area
            fraction = overlap / polygon.area
            if fraction <= 1e-5:
                continue
            matches.append({
                "tile_id": tile["id"],
                "zoom": tile["zoom"],
                "url": tile["url"],
                "display_coverage_fraction": round(fraction, 5),
                "overlap_display_area_px2": round(overlap, 2),
            })
        matches.sort(key=lambda item: (-item["zoom"], -item["overlap_display_area_px2"], item["tile_id"]))
        best_zoom = max(item["zoom"] for item in matches)
        regional = sorted((item for item in matches if item["zoom"] == best_zoom),
                          key=lambda item: -item["overlap_display_area_px2"])[:3]
        overviews = [item for item in matches if item["zoom"] == 1]
        overview = max(overviews, key=lambda item: item["overlap_display_area_px2"]) if overviews else max(
            (item for item in matches if item["zoom"] == 0), key=lambda item: item["overlap_display_area_px2"])
        centroid_latitude = 90 - (polygon.centroid.y - project(0, 90)[1]) * 180 / 740
        polar_movie = north_movie if centroid_latitude >= 55 else south_movie if centroid_latitude <= -55 else None
        state_records[code] = {
            "regional_zoom": best_zoom,
            "recommended_regional_tiles": [item["tile_id"] for item in regional],
            "overview_tile": overview["tile_id"],
            "polar_perspective": {
                "hemisphere": "north" if centroid_latitude > 0 else "south",
                "url": polar_movie["url"],
                "media_id": polar_movie["media_id"],
                "selection_basis": "OSW state display centroid at or beyond 55 degrees latitude; navigation aid only",
            } if polar_movie else None,
            "matches": matches,
        }
    payload = {
        "schema": "osw.almanac.nasa-state-tile-join.v1",
        "source": tile_ledger["source"],
        "picker": tile_ledger["picker"],
        "tile_ledger": str(TILES.relative_to(ROOT)).replace("\\", "/"),
        "polar_release_media_ledger": str(RELEASE_MEDIA.relative_to(ROOT)).replace("\\", "/"),
        "polar_perspective_rule": "Offer NASA's 1080p polar movie when an OSW state's coast-masked display centroid is at or beyond 55 degrees north or south. This editorial threshold selects a useful alternative view; NASA does not define OSW-state coverage for the polar movies.",
        "state_geometry": "figures/osw-province-atlas-interactive.svg",
        "method": "Intersect coast-masked approximate OSW state polygons and NASA's 70 published equirectangular crop rectangles in the same display projection, allowing 360-degree horizontal wraps. Exclude contacts covering at most 0.001% of a state's display area. Rank each state's regional crops by display overlap at the highest zoom with any overlap. The overview is the level-1 crop with greatest display overlap, or level 0 if unavailable.",
        "evidence_limit": "Display-overlap fractions are navigation measures, not geodesic area fractions. A crop covering a state does not identify a current, eddy, named ring, observed passage, or NASA-endorsed OSW boundary.",
        "state_count": len(state_records),
        "tile_count": len(tile_ledger["tiles"]),
        "states": state_records,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(state_records)} state-to-NASA crop joins")


if __name__ == "__main__":
    main()
