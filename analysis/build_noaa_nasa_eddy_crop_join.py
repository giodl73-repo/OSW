"""Join dated NOAA eddy centers to NASA PO2 geographic movie crops.

This is a cross-product navigation index, not an eddy identity match.
"""

from __future__ import annotations

import json
from pathlib import Path

from build_nasa_perpetual_ocean_tile_join import candidate_tiles


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
OUTPUT = RESEARCH / "noaa-nasa-eddy-crop-join.json"


def read(name: str) -> dict:
    return json.loads((RESEARCH / name).read_text(encoding="utf-8"))


def build() -> dict:
    manifest = read("noaa-munster-eddy-seasonal-manifest-2021-2023.json")
    timeline = read("nasa-perpetual-ocean-crop-timeline.json")
    crops = read("nasa-perpetual-ocean-tile-join.json")
    tiles = crops["tiles"]
    rows = {}
    total = 0
    for summary in manifest["snapshots"]:
        date = summary["date"]
        if date not in timeline["dates"]:
            continue
        snapshot = read(Path(summary["path"]).name)
        if snapshot["date"] != date or snapshot["source_sha256"] != summary["source_sha256"]:
            raise ValueError(f"NOAA snapshot provenance differs for {date}")
        if len(snapshot["entries"]) != summary["detection_count"]:
            raise ValueError(f"NOAA detection count differs for {date}")
        detections = {}
        for eddy in snapshot["entries"]:
            center = eddy["center"]
            if len(center) != 2 or any(value is None for value in center):
                raise ValueError(f"NOAA detection lacks a center: {eddy['id']}")
            candidates = candidate_tiles(tiles, *center)
            if not candidates:
                raise ValueError(f"No NASA crop covers NOAA center: {eddy['id']} {center}")
            detections[eddy["id"]] = candidates[0]["id"]
        if len(detections) != len(snapshot["entries"]):
            raise ValueError(f"Duplicate NOAA daily ID in {date}")
        rows[date] = {
            "noaa_snapshot": "research/" + Path(summary["path"]).name,
            "noaa_source_sha256": snapshot["source_sha256"],
            "estimated_crop_seconds": timeline["dates"][date]["estimated_crop_seconds"],
            "detection_count": len(detections),
            "detections": detections,
        }
        total += len(detections)
    if not rows:
        raise ValueError("No NOAA sample dates overlap NASA's published date list")
    return {
        "schema": "osw.almanac.noaa-nasa-eddy-crop-join.v1",
        "noaa_manifest": "research/noaa-munster-eddy-seasonal-manifest-2021-2023.json",
        "nasa_crop_ledger": "research/nasa-perpetual-ocean-tile-join.json",
        "nasa_date_index": "research/nasa-perpetual-ocean-crop-timeline.json",
        "nasa_date_list_sha256": timeline["date_list_sha256"],
        "nasa_crop_picker": crops["picker"],
        "date_count": len(rows),
        "detection_count": total,
        "method": "For sampled NOAA days also present in NASA's published date list, put each NOAA detected center in the most detailed NASA equirectangular movie crop. Use the separately inferred crop seek for that model date. The detection ID indexes the NOAA snapshot; the tile ID indexes NASA's geographic crop.",
        "identity_limit": "NOAA satellite-derived detections and NASA ECCO2 model particles are different products. A shared position and model date only select a nearby movie view; they do not identify the same eddy, verify a NASA feature footprint, or supply an individual eddy name. Seek times are cross-release estimates, not verified timestamps.",
        "dates": rows,
    }


def main() -> None:
    result = build()
    OUTPUT.write_text(json.dumps(result, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {result['detection_count']} NOAA center-to-NASA crop routes across {result['date_count']} model dates")


if __name__ == "__main__":
    main()
