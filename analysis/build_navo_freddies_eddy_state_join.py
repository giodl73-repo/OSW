"""Intersect pinned NAVO operational eddy polygons with approximate OSW states."""

from __future__ import annotations

import json
from pathlib import Path

from shapely.geometry import Polygon

from build_cartographic_current_state_join import load_states, project


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research" / "navo-freddies-eddy-snapshot-20260925.json"
OUTPUT = ROOT / "research" / "navo-freddies-eddy-state-join-20260925.json"


def build() -> dict:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    if source["observation_date"] != "2026-09-25" or len(source["eddies"]) != 4:
        raise ValueError("Unexpected NAVO source snapshot")
    states = load_states()
    features = []
    for eddy in source["eddies"]:
        polygon = Polygon([project(*point) for point in eddy["source_polygon_lon_lat"]])
        if not polygon.is_valid or polygon.area <= 0:
            raise ValueError(f"Invalid provider polygon: {eddy['provider_code']}")
        relations = []
        for code, state in sorted(states.items()):
            area = polygon.intersection(state).area
            if area <= 1e-9:
                continue
            fraction = area / polygon.area
            relations.append({
                "state_code": code,
                "relation": "contained_in_approximate_state" if fraction >= 1 - 1e-6 else "intersects_approximate_state",
                "display_projection_polygon_area_fraction": round(fraction, 6),
            })
        if not relations:
            raise ValueError(f"No OSW state for {eddy['provider_code']}")
        if sum(row["display_projection_polygon_area_fraction"] for row in relations) > 1.00001:
            raise ValueError("OSW state overlaps duplicate polygon area")
        features.append({
            "id": "navo-freddies:" + source["observation_date"] + ":" + eddy["provider_code"],
            "provider_code": eddy["provider_code"],
            "provider_type": eddy["provider_type"],
            "provider_rotation": eddy["provider_rotation"],
            "provider_center_lon_lat": eddy["provider_center_lon_lat"],
            "display_outline_lon_lat": [[round(x, 6), round(y, 6)] for x, y in
                                        Polygon(eddy["source_polygon_lon_lat"]).simplify(
                                            0.005, preserve_topology=True).exterior.coords],
            "state_relations": relations,
        })
    return {
        "schema": "osw.almanac.navo-freddies-eddy-state-join.v1",
        "observation_date": source["observation_date"],
        "source_receipt": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "source_url": source["source_url"],
        "source_zip_sha256": source["source_zip_sha256"],
        "state_geometry": "figures/osw-province-atlas-interactive.svg",
        "coordinate_reference_status": source["coordinate_reference_status"],
        "identity_limit": source["identity_limit"],
        "relation_limit": "A dated provider polygon is compared with approximate coast-masked OSW display states; containment is for that polygon and date, not a permanent eddy identity or NASA movie event.",
        "display_geometry_limit": "Outlines are simplified to 0.005 degree for rendering only. State intersections use the full source polygon, not the display outline.",
        "features": features,
    }


def main() -> None:
    output = build()
    OUTPUT.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(output['features'])} dated operational eddies in {len({r['state_code'] for f in output['features'] for r in f['state_relations']})} states")


if __name__ == "__main__":
    main()
