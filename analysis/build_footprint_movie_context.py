"""Join dated figure proxy geometry to movie crop rectangles for navigation."""

import math
import re
from shapely.geometry import shape, box
from shapely.ops import unary_union


def build(candidates, geometries, tiles, model_period, snapshot_id):
    years = [int(value) for value in re.findall(r"\d{4}", model_period)]
    if len(years) != 2 or years[0] > years[1]:
        raise ValueError("Movie context requires two declared model years")
    geometry_by_id = {row["id"]: row for row in geometries}
    rows = []
    for candidate in candidates:
        record = geometry_by_id[candidate["geometry_id"]]
        polygon = shape(record["geometry"])
        if not polygon.is_valid or polygon.area <= 0 or polygon.bounds[2] - polygon.bounds[0] > 180:
            raise ValueError("Invalid or ambiguous longitude-seam proxy geometry")
        selected = []
        for tile in tiles:
            west, east = tile["longitude_range_unwrapped"]
            south, north = tile["latitude_range"]
            if not west < east or not south < north or east - west > 360:
                raise ValueError("Invalid crop bounds")
            crop = unary_union([box(west + offset, south, east + offset, north)
                                for offset in (-720, -360, 0, 360, 720)])
            fraction = polygon.intersection(crop).area / polygon.area
            if fraction <= 1e-10:
                continue
            delta_lon = ((polygon.centroid.x - (west + east) / 2 + 180) % 360) - 180
            distance = ((delta_lon * math.cos(math.radians(polygon.centroid.y))) ** 2 +
                        (polygon.centroid.y - (south + north) / 2) ** 2)
            year = int(candidate["observation_date"][:4])
            selected.append({
                "id": "footprint_movie_context:" + candidate["id"] + ":" + tile["tile_id"],
                "entity_id": candidate["entity_id"], "footprint_candidate_id": candidate["id"],
                "geometry_id": record["id"], "geometry_sha256": candidate["geometry_sha256"],
                "tile_id": tile["tile_id"], "zoom": tile["zoom"], "url": tile["url"],
                "longitude_range_unwrapped": tile["longitude_range_unwrapped"],
                "latitude_range": tile["latitude_range"],
                "nominal_angular_overlap_fraction": round(min(1.0, fraction), 9),
                "nominal_complete_view": fraction >= 1 - 1e-9,
                "crop_center_distance_score": round(distance, 9),
                "recommended": False, "observation_date": candidate["observation_date"],
                "movie_model_period": model_period,
                "temporal_alignment_status": "outside_declared_model_years" if not years[0] <= year <= years[1] else "year_in_range_event_alignment_unresolved",
                "event_identity_status": "not_established",
                "source_id": tile["source_id"], "source_snapshot_id": snapshot_id,
                "figure_source_id": candidate["source_id"], "figure_snapshot_source_id": candidate["source_snapshot_id"],
                "support_claim_id": "claim:" + candidate["id"],
                "source_locator": "NASA picker crop " + tile["tile_id"] + "; bounds and movie address in pinned crop ledger",
                "method": "OSW longitude/latitude polygon-to-crop rectangle intersection, with periodic longitude copies; fractions use angular display area. Prefer a nominally complete crop at highest zoom, then smallest wrapped center-distance score and tile ID.",
                "physical_limit": "Geographic movie navigation only. Figure datum is unspecified; crop bounds and contour are approximate. Nominal overlap does not include calibration/segmentation uncertainty and does not identify Kraken or align its observation date with a movie frame.",
            })
        eligible = [row for row in selected if row["nominal_complete_view"]]
        if eligible:
            best = min(eligible, key=lambda row: (-row["zoom"], row["crop_center_distance_score"], row["tile_id"]))
            best["recommended"] = True
        rows.extend(sorted(selected, key=lambda row: (-row["zoom"], -row["nominal_angular_overlap_fraction"], row["crop_center_distance_score"], row["tile_id"])))
    return rows
