"""Join OSW motion locators to NASA's published Perpetual Ocean 2 crop picker.

The picker contains 70 geographic *movie crops*, not 70 named currents.
Only its public, current SVS URL is used; an older prepublication picker has
broken media links. The output stores NASA's links and an editorial spatial
join. It does not identify a current in any individual video frame.
"""

from __future__ import annotations

import json
import argparse
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "research" / "ocean-current-atlas-index.json"
OBJECTS = ROOT / "research" / "nasa-perpetual-ocean-objects.json"
OUTPUT = ROOT / "research" / "nasa-perpetual-ocean-tile-join.json"
PICKER = "https://svs.gsfc.nasa.gov/vis/a000000/a005500/a005505/PCT_flow_map_ALL_noLabels_beauty.html"
IMAGE_WIDTH = 1638.4
IMAGE_HEIGHT = 512.0
WORLD_WIDTH = 1024.0  # Equirectangular picker: 360 degrees occupy 1024 displayed pixels.


class PickerLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[dict] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        values = dict(attrs)
        tile_id = values.get("title", "")
        if not re.fullmatch(r"level[012]_[A-H]_[1-8]", tile_id):
            return
        style = values.get("style", "")
        dimensions = {}
        for name in ("left", "top", "width", "height"):
            match = re.search(rf"\b{name}:\s*([\d.]+)%", style)
            if not match:
                raise ValueError(f"Missing {name} in {tile_id}")
            dimensions[name] = float(match.group(1)) / 100
        x0 = dimensions["left"] * IMAGE_WIDTH
        x1 = x0 + dimensions["width"] * IMAGE_WIDTH
        y0 = dimensions["top"] * IMAGE_HEIGHT
        y1 = y0 + dimensions["height"] * IMAGE_HEIGHT
        self.links.append({
            "id": tile_id,
            "zoom": int(tile_id[5]),
            "url": urljoin(PICKER, values["href"]),
            "picker_box_px": [round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)],
            "latitude_range": [round(90 - y1 / IMAGE_HEIGHT * 180, 2), round(90 - y0 / IMAGE_HEIGHT * 180, 2)],
            "longitude_range_unwrapped": [round(x0 / WORLD_WIDTH * 360 - 180, 2), round(x1 / WORLD_WIDTH * 360 - 180, 2)],
        })


def candidate_tiles(tiles: list[dict], longitude: float, latitude: float) -> list[dict]:
    x = (longitude + 180) / 360 * WORLD_WIDTH
    y = (90 - latitude) / 180 * IMAGE_HEIGHT
    found = []
    for tile in tiles:
        x0, y0, x1, y1 = tile["picker_box_px"]
        for wrapped_x in (x, x + WORLD_WIDTH):
            if x0 <= wrapped_x <= x1 and y0 <= y <= y1:
                center_distance = abs(wrapped_x - (x0 + x1) / 2) + abs(y - (y0 + y1) / 2)
                found.append((tile["zoom"], -center_distance, tile["id"]))
                break
    return [next(tile for tile in tiles if tile["id"] == tile_id) for _, _, tile_id in sorted(found, reverse=True)]


def main() -> None:
    arguments = argparse.ArgumentParser(description=__doc__)
    arguments.add_argument("--reuse-pinned-tiles", action="store_true",
                           help="recompute locator joins offline using the existing audited crop catalog")
    args = arguments.parse_args()
    if args.reuse_pinned_tiles:
        existing = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if existing["schema"] != "osw.almanac.nasa-perpetual-ocean-tile-join.v1" or existing["picker"] != PICKER:
            raise ValueError("Pinned crop catalog does not match the NASA picker contract")
        tiles = existing["tiles"]
    else:
        request = Request(PICKER, headers={"User-Agent": "OSW-Motion-Atlas/1.0"})
        with urlopen(request, timeout=30) as response:
            html = response.read().decode("utf-8")
        parser = PickerLinks()
        parser.feed(html)
        tiles = parser.links
    if len(tiles) != 70 or len({tile["id"] for tile in tiles}) != 70:
        raise ValueError(f"Expected 70 unique NASA crop links, found {len(tiles)}")
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    joins: dict[str, list[dict]] = {}
    for current_id, item in index["entries"].items():
        matches = []
        for longitude, latitude in item["locators"]:
            candidates = candidate_tiles(tiles, longitude, latitude)
            if not candidates:
                raise ValueError(f"No NASA tile for {current_id} at {longitude},{latitude}")
            best = candidates[0]
            matches.append({"locator": [longitude, latitude], "tile_id": best["id"], "url": best["url"]})
        joins[current_id] = matches
    ring_location = index["named_loop_current_eddies"]["region_locator"]
    ring_tile = candidate_tiles(tiles, *ring_location)[0]
    nasa_objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    object_joins = {}
    for item in nasa_objects["objects"]:
        if item["locator"] is None:
            continue
        best = candidate_tiles(tiles, *item["locator"])[0]
        object_joins[item["id"]] = {"locator": item["locator"], "tile_id": best["id"], "url": best["url"]}
    payload = {
        "schema": "osw.almanac.nasa-perpetual-ocean-tile-join.v1",
        "source": "https://svs.gsfc.nasa.gov/5505",
        "picker": PICKER,
        "series": "Perpetual Ocean 2",
        "model_period": "2021–2023",
        "method": "Point-in-rectangle join of OSW approximate editorial locators to NASA's published equirectangular video crops. Prefer zoom level 2; choose nearest crop center when crops overlap. This proves regional coverage, not that NASA identified or labelled the named feature in a given frame.",
        "projection": "NASA picker repeats 360 degrees every 1024 display pixels; y=0 is 90°N, y=512 is 90°S.",
        "tiles": tiles,
        "current_joins": joins,
        "nasa_object_joins": object_joins,
        "named_loop_current_eddies_region_join": {"locator": ring_location, "tile_id": ring_tile["id"], "url": ring_tile["url"], "claim": "Regional movie crop only; no individual ring positions"},
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(tiles)} NASA tiles and {len(joins)} current joins to {OUTPUT}")


if __name__ == "__main__":
    main()
