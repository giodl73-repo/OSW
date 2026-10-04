"""Audit Figure 2 red curves and the 29 May blue SSH loop against OSW states.

This optional source-audit script requires a local copy of the pinned NOAA-hosted
paper PDF. It traces a source-image SSH contour proxy, not the authors'
scientific boundary coordinates or a whole-ring lifetime footprint.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import itertools
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import cv2
import pymupdf
import shapely
from PIL import Image
from shapely.geometry import Polygon
from shapely.ops import unary_union

from build_motion_state_join import polygon_parts


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research" / "kraken-2013-figure2-state-audit.json"
MAP = ROOT / "figures" / "osw-province-atlas-interactive.svg"
SOURCE_URL = "https://repository.library.noaa.gov/view/noaa/18748/noaa_18748_DS1.pdf"
PDF_SHA256 = "bba7a3b04adcafdc3c78bbe80c72aa0f906fe358ca6047cf0b048180489ed438"
FIGURE_SHA256 = "b07f073dadda7d8bb8660184b43aa981a719d4944a647ac02bff84e28812015b"
PANELS = (
    ("2013-05-29", (108, 313, 57, 661), (440, 690, 165, 425)),
    ("2013-08-01", (426, 630, 471, 1074), (650, 950, 585, 850)),
    ("2013-10-12", (742, 947, 883, 1488), (850, 1180, 1050, 1300)),
)


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def state_shapes() -> dict:
    root = ET.parse(MAP).getroot()
    land = unary_union(polygon_parts(next(item.get("d") for item in root.iter()
                                           if item.get("class") == "land-context")))
    states = {}
    for group in root.iter():
        if "province " not in group.get("class", ""):
            continue
        path = next(item.get("d") for item in group if item.tag.endswith("path"))
        states[group.get("data-code")] = unary_union(polygon_parts(path)).difference(land)
    assert len(states) == 56
    return states


def xy_to_svg(pixel_x: np.ndarray, pixel_y: np.ndarray,
              axes: tuple[int, int, int, int]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    x98, x936, y31, y18 = axes
    longitude = -98 + (pixel_x - x98) * 4.4 / (x936 - x98)
    latitude = 31 - (pixel_y - y31) * 13 / (y18 - y31)
    svg_x = 60 + (longitude + 180) / 360 * 1480
    svg_y = 90 + (90 - latitude) / 180 * 740
    return longitude, latitude, svg_x, svg_y


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, required=True, help="local copy of the pinned paper PDF")
    args = parser.parse_args()
    blob = args.pdf.read_bytes()
    if sha256(blob) != PDF_SHA256:
        raise ValueError("Kraken paper PDF SHA-256 differs from pinned source bytes")
    document = pymupdf.open(stream=blob, filetype="pdf")
    if len(document) != 12:
        raise ValueError("Unexpected Kraken PDF page count")
    figure_image = document[3].get_images(full=True)
    if len(figure_image) != 1:
        raise ValueError("Expected one embedded image on Figure 2 PDF page")
    image_bytes = document.extract_image(figure_image[0][0])["image"]
    if sha256(image_bytes) != FIGURE_SHA256:
        raise ValueError("Figure 2 embedded JPEG bytes differ from pinned source")
    pixels = np.asarray(Image.open(io.BytesIO(image_bytes)).convert("RGB"), dtype=np.int16)
    if pixels.shape != (1574, 1650, 3):
        raise ValueError("Unexpected Figure 2 pixel grid")
    red = ((pixels[:, :, 0] > 120) &
           (pixels[:, :, 0] > pixels[:, :, 1] * 1.8) &
           (pixels[:, :, 0] > pixels[:, :, 2] * 1.4))
    shapes = state_shapes()
    rows = []
    for date, axes, (left, right, top, bottom) in PANELS:
        local_y, local_x = np.where(red[top:bottom, left:right])
        pixel_x, pixel_y = local_x + left, local_y + top
        if len(pixel_x) < 1000:
            raise ValueError(f"Too few red boundary pixels in {date} panel")
        lon, lat, svg_x, svg_y = xy_to_svg(pixel_x, pixel_y, axes)
        nominal_points = shapely.points(svg_x, svg_y)
        nominal_counts = {code: int(np.count_nonzero(shapely.covers(shape, nominal_points)))
                          for code, shape in shapes.items()}
        nominal_counts = {code: count for code, count in nominal_counts.items() if count}
        sensitivity = []
        for shifts in itertools.product((-3, 3), repeat=4):
            perturbed = tuple(value + delta for value, delta in zip(axes, shifts))
            _, _, shifted_x, shifted_y = xy_to_svg(pixel_x, pixel_y, perturbed)
            points = shapely.points(shifted_x, shifted_y)
            sensitivity.append(int(np.count_nonzero(shapely.covers(shapes["CAMR"], points))))
        rows.append({
            "observation_date": date,
            "figure_panel_axis_pixels": {"x_98W": axes[0], "x_93_6W": axes[1],
                                         "y_31N": axes[2], "y_18N": axes[3]},
            "red_pixel_search_box_xyxy": [left, top, right, bottom],
            "selected_red_pixel_count": len(pixel_x),
            "selected_pixel_bounds_xyxy": [int(pixel_x.min()), int(pixel_y.min()),
                                           int(pixel_x.max()), int(pixel_y.max())],
            "figure_derived_lon_lat_envelope": [round(float(lon.min()), 3),
                                                round(float(lat.min()), 3),
                                                round(float(lon.max()), 3),
                                                round(float(lat.max()), 3)],
            "nominal_selected_pixel_state_counts": nominal_counts,
            "axis_calibration_sensitivity_pixels": 3,
            "axis_calibration_sensitivity_cases": len(sensitivity),
            "camr_covered_red_pixel_count_range": [min(sensitivity), max(sensitivity)],
            "state_interpretation": "figure_red_boundary_pixels_only_not_whole_ring_footprint",
        })
    result = {
        "schema": "osw.almanac.kraken-figure-state-audit.v1",
        "source_url": SOURCE_URL,
        "source_doi": "10.1038/s41598-018-29582-5",
        "source_pdf_sha256": PDF_SHA256,
        "source_pdf_page_index": 3,
        "source_figure": "Figure 2",
        "embedded_figure_sha256": FIGURE_SHA256,
        "source_license": "CC BY 4.0, stated on the paper PDF final page; figure is credited to the article authors",
        "state_geometry_path": MAP.relative_to(ROOT).as_posix(),
        "state_geometry_sha256": sha256(MAP.read_bytes()),
        "method": "Extract the article's embedded Figure 2 JPEG; select visually red pixels within each dated panel using fixed RGB thresholds; linearly georeference pixel positions from manually read 98.0W, 93.6W, 31.0N, and 18.0N axis ticks; project into the OSW equirectangular map and test coast-masked state polygon coverage. Repeat with each axis tick shifted independently by ±3 source pixels.",
        "claim_limit": "Red pixels depict the paper's solid coherent-core and dashed short-term shielding curves, not the whole instantaneous SSH eddy footprint. JPEG anti-aliasing, tick reading, curve thickness, and OSW's approximate state boundaries remain uncertainties. Pixel counts are not area fractions; this artifact does not digitize a closed scientific boundary or verify whole-eddy containment, NASA identity, or persistence between the three dates.",
        "panels": rows,
    }
    if (len(rows) != 3 or any(row["nominal_selected_pixel_state_counts"] !=
                             {"CAMR": row["selected_red_pixel_count"]} for row in rows)):
        raise ValueError("Figure red pixels no longer support the nominal CAMR candidate")
    min_sensitivity_fraction = min(row["camr_covered_red_pixel_count_range"][0] /
                                   row["selected_red_pixel_count"] for row in rows)
    if min_sensitivity_fraction < 0.999:
        raise ValueError("Figure calibration sensitivity no longer supports the CAMR candidate")
    result["state_candidate"] = {
        "id": "published:kraken-2013",
        "state_code": "CAMR",
        "observation_dates": [row["observation_date"] for row in rows],
        "evidence_status": "figure_derived_red_curve_candidate",
        "minimum_axis_sensitivity_red_pixel_fraction_in_state": round(min_sensitivity_fraction, 6),
        "source_locator": "Figure 2 red solid and dashed curves; panels dated 29 May, 1 August, and 12 October 2013",
        "physical_relation": "red_curve_pixel_locations_near_or_in_approximate_state_whole_ring_containment_unresolved",
        "review_status": "not_individually_reviewed",
        "source_pdf_sha256": PDF_SHA256,
        "embedded_figure_sha256": FIGURE_SHA256,
        "state_geometry_sha256": result["state_geometry_sha256"],
        "panel_evidence": rows,
        "method": result["method"],
        "claim_limit": result["claim_limit"],
    }
    # Only the 29 May blue line is an instantaneous SSH contour in the paper.
    # The August and October blue curves are advected material, so they cannot
    # be used as dated Eulerian footprints.
    left, right, top, bottom = 480, 660, 185, 400
    region = pixels[top:bottom, left:right]
    blue_cases = []
    nominal_geometry = None
    nominal_pixel_ring = None
    for blue_min, blue_red_ratio, blue_green_ratio in (
        (60, 1.25, 1.10), (70, 1.35, 1.20), (90, 1.45, 1.30)
    ):
        mask = ((region[:, :, 2] > blue_min) &
                (region[:, :, 2] > region[:, :, 0] * blue_red_ratio) &
                (region[:, :, 2] > region[:, :, 1] * blue_green_ratio)).astype("uint8")
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        if (hierarchy is None or hierarchy[0, 0, 2] < 0 or
                cv2.contourArea(contours[0]) < 18000 or
                sum(cv2.contourArea(part) >= 10 for part in contours) != 2):
            raise ValueError("29 May blue contour is no longer one closed, hollow loop")
        contour = contours[0][:, 0, :].astype(float)
        pixel_x, pixel_y = contour[:, 0] + left, contour[:, 1] + top
        if blue_min == 70:
            longitude, latitude, _, _ = xy_to_svg(pixel_x, pixel_y, PANELS[0][1])
            ring = [[round(float(lon), 7), round(float(lat), 7)] for lon, lat in zip(longitude, latitude)]
            ring.append(ring[0])
            nominal_geometry = {"type": "Polygon", "coordinates": [ring]}
            nominal_pixel_ring = [[int(x), int(y)] for x, y in zip(pixel_x, pixel_y)]
            nominal_pixel_ring.append(nominal_pixel_ring[0])
        _, _, nominal_x, nominal_y = xy_to_svg(pixel_x, pixel_y, PANELS[0][1])
        nominal = Polygon(np.column_stack((nominal_x, nominal_y)))
        nominal_overlaps = {code: round(nominal.intersection(shape).area / nominal.area, 6)
                            for code, shape in shapes.items() if nominal.intersects(shape)}
        cases = []
        for shifts in itertools.product((-3, 3), repeat=4):
            axes = tuple(value + delta for value, delta in zip(PANELS[0][1], shifts))
            _, _, svg_x, svg_y = xy_to_svg(pixel_x, pixel_y, axes)
            footprint = Polygon(np.column_stack((svg_x, svg_y)))
            if not footprint.is_valid or footprint.area <= 0:
                raise ValueError("29 May blue footprint geometry is invalid")
            overlaps = {code: round(footprint.intersection(shape).area / footprint.area, 6)
                        for code, shape in shapes.items() if footprint.intersects(shape)}
            cases.append(overlaps)
        blue_cases.append({
            "rgb_threshold": {"blue_min": blue_min, "blue_to_red_min_ratio": blue_red_ratio,
                              "blue_to_green_min_ratio": blue_green_ratio},
            "selected_pixel_count": int(mask.sum()),
            "contour_vertex_count": len(contour),
            "selected_pixel_bounds_xyxy": [int(pixel_x.min()), int(pixel_y.min()),
                                           int(pixel_x.max()), int(pixel_y.max())],
            "axis_sensitivity_cases": len(cases),
            "nominal_footprint_area_fraction_by_state": nominal_overlaps,
            "camr_footprint_area_fraction_range": [min(case.get("CAMR", 0) for case in cases),
                                                   max(case.get("CAMR", 0) for case in cases)],
            "carb_footprint_area_fraction_range": [min(case.get("CARB", 0) for case in cases),
                                                   max(case.get("CARB", 0) for case in cases)],
            "carb_intersection_axis_sensitivity_cases": sum(case.get("CARB", 0) > 0 for case in cases),
            "other_state_codes_any_case": sorted(set().union(*(set(case) - {"CAMR"} for case in cases))),
        })
    if any(case["camr_footprint_area_fraction_range"][0] < 0.90 for case in blue_cases):
        raise ValueError("29 May SSH contour no longer robustly intersects CAMR")
    result["dated_ssh_footprint_candidate"] = {
        "id": "published:kraken-2013",
        "observation_date": "2013-05-29",
        "nominal_state_codes": sorted(set().union(*(set(case["nominal_footprint_area_fraction_by_state"])
                                                  for case in blue_cases))),
        "sensitivity_state_codes": sorted(set().union(*(set(case["other_state_codes_any_case"]) | {"CAMR"}
                                                      for case in blue_cases))),
        "evidence_status": "figure_derived_dated_ssh_contour_candidate",
        "source_locator": "Figure 2, 29 May 2013 panel, outermost closed blue instantaneous SSH contour",
        "blue_pixel_search_box_xyxy": [left, top, right, bottom],
        "axis_calibration_sensitivity_pixels": 3,
        "segmentation_sensitivity_cases": blue_cases,
        "minimum_axis_and_segmentation_sensitivity_camr_footprint_area_fraction":
            min(case["camr_footprint_area_fraction_range"][0] for case in blue_cases),
        "method": "Segment the single closed blue loop by three RGB thresholds; trace its outside pixel contour; linearly georeference from the manually read panel ticks; intersect the enclosed polygon with the coast-masked approximate OSW state shapes under 16 independent ±3-pixel axis-tick perturbations per threshold.",
        "claim_limit": "Dated 2-D instantaneous SSH contour proxy only. Axis-tick sensitivity can place part of this near-boundary contour in CARB, so whole-footprint CAMR containment is unresolved. This is not the material coherent-core curve, a 3-D ring volume, or a claim for August/October. Source JPEG quality, manual axis reading, line thickness, and schematic OSW state geometry limit precision.",
        "review_status": "not_individually_reviewed",
        "source_pdf_sha256": PDF_SHA256,
        "embedded_figure_sha256": FIGURE_SHA256,
        "state_geometry_sha256": result["state_geometry_sha256"],
        "nominal_geometry": nominal_geometry,
        "source_pixel_ring": nominal_pixel_ring,
        "source_panel_axes_pixels": list(PANELS[0][1]),
        "nominal_segmentation_case_index": 1,
        "coordinate_reference_system": "figure_axis_lon_lat_degrees_unspecified_datum",
        "coordinate_reference_status": "Longitude/latitude inferred from figure axes; source figure does not specify a geodetic datum. Decimal output precision does not imply survey accuracy.",
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print([(row["observation_date"], row["nominal_selected_pixel_state_counts"],
            row["camr_covered_red_pixel_count_range"], row["selected_red_pixel_count"])
           for row in rows])


if __name__ == "__main__":
    main()
