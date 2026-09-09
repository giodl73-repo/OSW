"""Render an OSCAR surface-velocity pilot without the OSW zoning overlay."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
from collections import defaultdict
from pathlib import Path

from build_projection_bakeoff import (
    EXPECTED_SOURCE_SHA256,
    SOURCE_COMMIT,
    StateCandidate,
    all_rings,
    projected_polygon_fill,
    pyproj_projector,
    raw_bounds,
    screen_transform,
)


CANVAS = (1200, 980)
MAP_BOX = (48.0, 170.0, 1104.0, 625.0)
MOLLWEIDE = StateCandidate(
    "mollweide-oceanic", "OCEANIC MOLLWEIDE", "Six ocean-emphasis lobes",
    "EQUAL-AREA · INTERRUPTED", "Equal-area ocean view with interrupted seams.",
    "+proj=imoll_o +lon_0=-160 +R=1 +units=m +no_defs",
)
SPEED_CLASSES = (
    (0.10, "#6f9fa3", "&lt; 0.10"),
    (0.25, "#62d7ce", "0.10–0.25"),
    (0.50, "#f0cf70", "0.25–0.50"),
    (1.00, "#f49a62", "0.50–1.00"),
    (float("inf"), "#f05d67", "> 1.00"),
)


def load_payload(path: Path) -> dict:
    source = path.read_text(encoding="utf-8")
    payload = json.loads(source.split("=", 1)[1].strip().removesuffix(";"))
    rows, columns = payload["shape"]
    if len(payload["u_mm_s"]) != rows * columns or len(payload["v_mm_s"]) != rows * columns:
        raise ValueError("OSCAR vector grid shape mismatch")
    return payload


def normalize_longitude(longitude: float) -> float:
    return (longitude + 180.0) % 360.0 - 180.0


def speed_class(speed: float) -> tuple[int, str]:
    for index, (limit, color, _) in enumerate(SPEED_CLASSES):
        if speed < limit:
            return index, color
    raise AssertionError("infinite speed class must match")


def vector_layers(payload: dict, project, screen) -> tuple[str, int]:
    rows, columns = payload["shape"]
    latitudes = payload["latitude_values"]
    longitudes = payload["longitude_values"]
    grouped: dict[int, list[str]] = defaultdict(list)
    count = 0
    for row, latitude in enumerate(latitudes):
        if abs(latitude) > 79.9:
            continue
        cosine = max(0.2, math.cos(math.radians(latitude)))
        for column, longitude_source in enumerate(longitudes):
            index = row * columns + column
            u_encoded, v_encoded = payload["u_mm_s"][index], payload["v_mm_s"][index]
            if u_encoded is None or v_encoded is None:
                continue
            u, v = u_encoded / 1000, v_encoded / 1000
            speed = math.hypot(u, v)
            if speed < 0.015:
                continue
            longitude = normalize_longitude(longitude_source)
            angular_length = 0.9 + min(speed, 1.5) * 3.7
            end_latitude = latitude + v / speed * angular_length
            end_longitude = normalize_longitude(longitude + u / speed * angular_length / cosine)
            if abs(end_latitude) >= 89.0 or abs(end_longitude - longitude) > 40:
                continue
            try:
                start = screen(project(longitude, latitude))
                end = screen(project(end_longitude, end_latitude))
            except Exception:
                continue
            distance = math.hypot(end[0] - start[0], end[1] - start[1])
            if not math.isfinite(distance) or distance < 1.0 or distance > 26.0:
                continue
            bucket, _ = speed_class(speed)
            grouped[bucket].append(f"M{start[0]:.1f},{start[1]:.1f}L{end[0]:.1f},{end[1]:.1f}")
            count += 1
    layers = []
    for bucket, (_, color, _) in enumerate(SPEED_CLASSES):
        commands = grouped.get(bucket, [])
        if commands:
            layers.append(
                f'<path d="{"".join(commands)}" fill="none" stroke="{color}" '
                f'stroke-width="1.15" stroke-opacity=".88" marker-end="url(#arrow-{bucket})"/>'
            )
    return "".join(layers), count


def legend() -> str:
    items = []
    for index, (_, color, label) in enumerate(SPEED_CLASSES):
        x = 62 + index * 145
        items.append(
            f'<path d="M{x} 868H{x + 38}" stroke="{color}" stroke-width="2" marker-end="url(#arrow-{index})"/>'
            f'<text x="{x + 49}" y="872">{label}</text>'
        )
    return "".join(items)


def render(payload: dict, geojson: dict, land_sha256: str) -> str:
    project = pyproj_projector(MOLLWEIDE.proj4)
    bounds = raw_bounds(project)
    screen = screen_transform(bounds, box=MAP_BOX)
    land_path = "".join(
        projected_polygon_fill(ring, MOLLWEIDE, project, bounds, screen)
        for ring in all_rings(geojson)
    )
    vectors, vector_count = vector_layers(payload, project, screen)
    marker_defs = "".join(
        f'<marker id="arrow-{index}" viewBox="0 0 4 4" refX="3.4" refY="2" markerWidth="3.3" markerHeight="3.3" orient="auto"><path d="M0 0L4 2L0 4Z" fill="{color}"/></marker>'
        for index, (_, color, _) in enumerate(SPEED_CLASSES)
    )
    source = html.escape(payload["source"])
    boundary = html.escape(payload["boundary"])
    checksum = html.escape(payload["source_sha256"])
    date = html.escape(payload["date"])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="980" viewBox="0 0 1200 980" role="img" aria-labelledby="title desc" data-motion-level="surface-velocity" data-zoning="off">
  <title id="title">Historical OSCAR surface motion pilot</title>
  <desc id="desc">A zoning-free Oceanic Mollweide map of historical OSCAR zonal and meridional surface-current vectors for {date}. Arrow direction shows diagnosed surface motion; length and color show speed. {boundary}</desc>
  <metadata>Source: {source}. Source SHA-256: {checksum}. Query: {html.escape(payload['query_url'])}. Natural Earth land commit {SOURCE_COMMIT}, SHA-256 {land_sha256}. Projection: {MOLLWEIDE.proj4}. Rendered vectors: {vector_count}. No OSW zones are drawn.</metadata>
  <defs>{marker_defs}
    <clipPath id="motion-map"><rect x="48" y="170" width="1104" height="625" rx="20"/></clipPath>
    <pattern id="quiet-land" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><rect width="9" height="9" fill="#f7f7f4"/><path d="M0 0V9" stroke="#526d70" stroke-width=".55" stroke-opacity=".12"/></pattern>
    <style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.legend text{{fill:#a9bfbe;font:800 10px ui-monospace,Consolas,monospace}}</style>
  </defs>
  <rect width="1200" height="980" fill="#06171c"/>
  <text x="48" y="45" fill="#62d7ce" font-size="14" font-weight="900" letter-spacing="2.5">OSW / MOTION STUDY  ·  M1 HISTORICAL PILOT</text>
  <text x="48" y="88" fill="#eef9f7" font-size="34" font-weight="950">SURFACE WATER IN MOTION</text>
  <text x="48" y="118" fill="#9db3b2" font-size="12">OSCAR third-degree 5-day archive · {date} · nominal 15 m · direction + speed</text>
  <rect x="923" y="38" width="229" height="30" rx="15" fill="#102a30" stroke="#f0cf70" stroke-opacity=".65"/>
  <text x="1037.5" y="58" text-anchor="middle" fill="#f0cf70" font-size="10" font-weight="950" letter-spacing="1.3">ZONING OFF · WATER PRIMARY</text>
  <g clip-path="url(#motion-map)">
    <rect x="48" y="170" width="1104" height="625" fill="#0b252c"/>
    <g aria-label="Surface velocity vectors">{vectors}</g>
    <path d="{land_path}" fill="url(#quiet-land)" fill-rule="evenodd"/>
  </g>
  <rect x="48" y="170" width="1104" height="625" rx="20" fill="none" stroke="#49666b" stroke-width="1.4"/>
  <g class="legend"><text x="48" y="834" fill="#edf8f6" font-size="12" font-weight="900">CURRENT SPEED · m s⁻¹</text>{legend()}</g>
  <g transform="translate(48 905)">
    <text fill="#62d7ce" font-size="10" font-weight="950" letter-spacing="1.2">READ</text>
    <text x="48" fill="#afc3c1" font-size="10.5">surface direction and speed on one historical day</text>
    <text x="455" fill="#f0cf70" font-size="10" font-weight="950" letter-spacing="1.2">DO NOT READ</text>
    <text x="560" fill="#afc3c1" font-size="10.5">full-depth flow · parcel paths · heat transport · convergence</text>
  </g>
  <text x="48" y="954" fill="#667f81" font-size="9">HISTORICAL VISUAL-GRAMMAR PILOT · OLDER OSCAR VERSION 2017.0 · PRODUCTION M1 REQUIRES OSCAR V2.0 · {vector_count} VECTORS</text>
</svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--land-geojson", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    land_raw = args.land_geojson.read_bytes()
    land_sha256 = hashlib.sha256(land_raw).hexdigest()
    if land_sha256 != EXPECTED_SOURCE_SHA256:
        raise SystemExit(f"Natural Earth source checksum mismatch: {land_sha256}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(load_payload(args.data), json.loads(land_raw), land_sha256), encoding="utf-8", newline="\n")
    print(args.output)


if __name__ == "__main__":
    main()
