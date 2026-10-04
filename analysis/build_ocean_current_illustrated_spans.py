"""Rank the visible span of named current arrows, not physical current lengths.

The source polylines are empty as of 2026-09-29. Its cartographic arrow
polygons are available at four display widths. Half of a narrow arrow's
geodesic perimeter is a reproducible *illustrated span* proxy. Arrowheads,
curvature, branching and editorial endpoints make it unsuitable as a measured
current length. For multiple arrows, use the longest single symbol rather
than summing potentially overlapping or differently scoped symbols.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from pyproj import Geod
from shapely.geometry import shape

from build_cartographic_current_state_join import ROOT, SCALES, load_source


OUTPUT = ROOT / "research" / "ocean-current-illustrated-spans.json"
ARROW_JOIN = ROOT / "research" / "cartographic-ocean-current-state-join.json"
CURRENT_INDEX = ROOT / "research" / "ocean-current-atlas-index.json"
CURRENT_LEDGER = ROOT / "research" / "ocean-current-almanac.json"
SOURCE_LINE_LAYER = "https://services3.arcgis.com/o98K21Ga5N91Ugjw/ArcGIS/rest/services/Hurricane%20TracksAA/FeatureServer/6"
GEOD = Geod(ellps="WGS84")


def arrow_span_km(geometry: dict) -> float:
    polygon = shape(geometry)
    assert polygon.is_valid and polygon.area > 0
    return GEOD.geometry_length(polygon.boundary) / 2000


def main() -> None:
    source, digest = load_source()
    joined = json.loads(ARROW_JOIN.read_text(encoding="utf-8"))
    index = json.loads(CURRENT_INDEX.read_text(encoding="utf-8"))["entries"]
    ledger = json.loads(CURRENT_LEDGER.read_text(encoding="utf-8"))
    names = {item["id"]: item["name"] for item in ledger["entries"]}
    assert digest == joined["source_geojson_sha256"]
    by_id: dict[int, dict[int, float]] = defaultdict(dict)
    for feature in source["features"]:
        properties = feature["properties"]
        arrow_id = int(properties["OBJECTID_1"])
        scale = int(properties["SCALE"])
        assert scale in SCALES and scale not in by_id[arrow_id]
        by_id[arrow_id][scale] = arrow_span_km(feature["geometry"])
    assert len(by_id) == joined["source_arrow_count"]
    assert all(set(versions) == set(SCALES) for versions in by_id.values())

    by_current: dict[str, list[dict]] = defaultdict(list)
    for arrow in joined["arrows"]:
        current_id = arrow["osw_current_id"]
        if current_id is None:
            continue
        versions = by_id[arrow["source_arrow_id"]]
        by_current[current_id].append({
            "source_arrow_id": arrow["source_arrow_id"],
            "source_name": arrow["source_name"],
            "illustrated_span_km": round(versions[1_000_000]),
            "display_width_span_range_km": [round(min(versions.values())), round(max(versions.values()))],
        })
    assert len(by_current) == joined["mapped_current_count"]

    entries = []
    for current_id in sorted(names):
        arrows = sorted(by_current.get(current_id, []), key=lambda item: (-item["illustrated_span_km"], item["source_arrow_id"]))
        identity = index[current_id]["identity_level"]
        rank_eligible = bool(arrows) and identity != "family"
        entries.append({
            "current_id": current_id,
            "name": names[current_id],
            "identity_level": identity,
            "map_coverage": "source_arrow" if arrows else "none",
            "illustrated_span_rank_eligible": rank_eligible,
            "longest_arrow_span_km": arrows[0]["illustrated_span_km"] if arrows else None,
            "source_arrow_count": len(arrows),
            "arrows": arrows,
            "scope_note": (
                "Family name spans separate basin currents; do not assign one family length."
                if arrows and identity == "family" else
                "Longest single drawn arrow only; other symbols are not summed, and the symbol may cover only part of the flow or combine segments."
                if arrows else "No mapped arrow; no cartographic span proxy available."
            ),
        })
    ranked = sorted((item for item in entries if item["illustrated_span_rank_eligible"]),
                    key=lambda item: (-item["longest_arrow_span_km"], item["name"]))
    for position, item in enumerate(ranked, 1):
        item["illustrated_span_rank"] = position
    for item in entries:
        if "illustrated_span_rank" not in item:
            item["illustrated_span_rank"] = None
    output = {
        "schema": "osw.almanac.current-illustrated-spans.v1",
        "as_of": "2026-09-29",
        "source_layer": joined["source_layer"],
        "source_geojson_sha256": digest,
        "source_line_layer": SOURCE_LINE_LAYER,
        "source_line_layer_record_count_observed": 0,
        "metric": "Half the WGS84 geodesic perimeter of the source's narrowest (1:1,000,000 display) arrow polygon; rounded to a whole kilometre.",
        "ranking_rule": "Order the longest single mapped arrow for each non-family current. Do not sum separate arrow symbols. This ranks illustrated map spans, not physical current lengths or lower bounds. Family labels across basins and currents without a source arrow remain unranked.",
        "uncertainty": "The four display-width values show sensitivity to drawn arrow thickness only. They are not physical confidence intervals. Arrowheads, bends, symbol endpoints, and labels that combine flows can create larger unknown errors.",
        "counts": {
            "named_currents": len(entries),
            "mapped_currents": len(by_current),
            "ranked_illustrated_spans": len(ranked),
            "excluded_multi_basin_families": sum(bool(item["arrows"]) and item["identity_level"] == "family" for item in entries),
            "without_arrow": sum(not item["arrows"] for item in entries),
        },
        "entries": sorted(entries, key=lambda item: (item["illustrated_span_rank"] is None,
                                                       item["illustrated_span_rank"] or 0, item["name"])),
    }
    OUTPUT.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(ranked)} illustrated-span ranks among {len(entries)} named currents")


if __name__ == "__main__":
    main()
