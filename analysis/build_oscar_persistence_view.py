"""Render sampled-year OSCAR mean motion with directional persistence."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
from collections import defaultdict
from pathlib import Path

from build_oscar_motion_view import (
    MAP_BOX, MOLLWEIDE, SPEED_CLASSES, normalize_longitude, speed_class,
)
from build_projection_bakeoff import (
    EXPECTED_SOURCE_SHA256, SOURCE_COMMIT, all_rings, projected_polygon_fill,
    pyproj_projector, raw_bounds, screen_transform,
)


PERSISTENCE_BANDS = (
    (0.35, 0.20, 0.85, "LOW · < 0.35"),
    (0.70, 0.55, 1.05, "MIXED · 0.35–0.70"),
    (float("inf"), 0.95, 1.30, "HIGH · > 0.70"),
)


def load_payload(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    payload = json.loads(text.split("=", 1)[1].strip().removesuffix(";"))
    rows, columns = payload["shape"]
    for field in ("mean_u_mm_s", "mean_v_mm_s", "mean_instantaneous_speed_mm_s", "directional_persistence_thousandths"):
        if len(payload[field]) != rows * columns:
            raise ValueError(f"persistence grid shape mismatch: {field}")
    return payload


def persistence_band(value: float) -> int:
    return next(index for index, band in enumerate(PERSISTENCE_BANDS) if value < band[0])


def vector_layers(payload: dict, project, screen) -> tuple[str, int]:
    rows, columns = payload["shape"]
    grouped: dict[tuple[int, int], list[str]] = defaultdict(list)
    count = 0
    for row, latitude in enumerate(payload["latitude_values"]):
        if abs(latitude) > 79.9:
            continue
        cosine = max(0.2, math.cos(math.radians(latitude)))
        for column, longitude_source in enumerate(payload["longitude_values"]):
            index = row * columns + column
            u_encoded = payload["mean_u_mm_s"][index]
            v_encoded = payload["mean_v_mm_s"][index]
            speed_encoded = payload["mean_instantaneous_speed_mm_s"][index]
            persistence_encoded = payload["directional_persistence_thousandths"][index]
            if None in (u_encoded, v_encoded, speed_encoded, persistence_encoded):
                continue
            u, v = u_encoded / 1000, v_encoded / 1000
            resultant = math.hypot(u, v)
            if resultant < 0.008:
                continue
            mean_speed = speed_encoded / 1000
            persistence = persistence_encoded / 1000
            longitude = normalize_longitude(longitude_source)
            angular_length = 0.9 + min(mean_speed, 1.5) * 3.7
            end_latitude = latitude + v / resultant * angular_length
            end_longitude = normalize_longitude(longitude + u / resultant * angular_length / cosine)
            if abs(end_latitude) >= 89 or abs(end_longitude - longitude) > 40:
                continue
            try:
                start = screen(project(longitude, latitude))
                end = screen(project(end_longitude, end_latitude))
            except Exception:
                continue
            distance = math.hypot(end[0] - start[0], end[1] - start[1])
            if not math.isfinite(distance) or distance < 1 or distance > 26:
                continue
            speed_bucket, _ = speed_class(mean_speed)
            grouped[(speed_bucket, persistence_band(persistence))].append(
                f"M{start[0]:.1f},{start[1]:.1f}L{end[0]:.1f},{end[1]:.1f}"
            )
            count += 1
    layers = []
    for (speed_bucket, band), commands in sorted(grouped.items()):
        color = SPEED_CLASSES[speed_bucket][1]
        _, opacity, width, _ = PERSISTENCE_BANDS[band]
        layers.append(
            f'<path d="{"".join(commands)}" fill="none" stroke="{color}" stroke-width="{width}" '
            f'opacity="{opacity}" marker-end="url(#arrow-{speed_bucket})" data-persistence-band="{band}"/>'
        )
    return "".join(layers), count


def speed_legend() -> str:
    items = []
    for index, (_, color, label) in enumerate(SPEED_CLASSES):
        x = 62 + index * 142
        items.append(
            f'<path d="M{x} 862H{x + 36}" stroke="{color}" stroke-width="2" marker-end="url(#arrow-{index})"/>'
            f'<text x="{x + 47}" y="866">{label}</text>'
        )
    return "".join(items)


def persistence_legend() -> str:
    items = []
    for index, (_, opacity, width, label) in enumerate(PERSISTENCE_BANDS):
        x = 785 + index * 122
        items.append(
            f'<path d="M{x} 862H{x + 30}" stroke="#62d7ce" stroke-width="{width + .5}" opacity="{opacity}"/>'
            f'<text x="{x + 39}" y="866">{html.escape(label)}</text>'
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
    vectors, count = vector_layers(payload, project, screen)
    markers = "".join(
        f'<marker id="arrow-{index}" viewBox="0 0 4 4" refX="3.4" refY="2" markerWidth="3.3" markerHeight="3.3" orient="auto"><path d="M0 0L4 2L0 4Z" fill="{color}"/></marker>'
        for index, (_, color, _) in enumerate(SPEED_CLASSES)
    )
    times = len(payload["sample_times"])
    boundary = html.escape(payload["boundary"])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="980" viewBox="0 0 1200 980" role="img" aria-labelledby="title desc" data-motion-level="sampled-persistence" data-zoning="off">
  <title id="title">Where surface motion holds</title>
  <desc id="desc">A zoning-free Oceanic Mollweide map of mean historical OSCAR surface-current vectors from {times} samples between {payload['period_start']} and {payload['period_stop']}. Color shows mean sampled speed and opacity shows directional persistence. {boundary}</desc>
  <metadata>Source: {html.escape(payload['source'])}. Source SHA-256: {payload['source_sha256']}. Query: {html.escape(payload['query_url'])}. Diagnostic: {html.escape(payload['diagnostic_definition'])}. Natural Earth land commit {SOURCE_COMMIT}, SHA-256 {land_sha256}. Projection: {MOLLWEIDE.proj4}. Rendered vectors: {count}. No OSW zones are drawn.</metadata>
  <defs>{markers}
    <clipPath id="motion-map"><rect x="48" y="170" width="1104" height="625" rx="20"/></clipPath>
    <pattern id="quiet-land" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><rect width="9" height="9" fill="#f7f7f4"/><path d="M0 0V9" stroke="#526d70" stroke-width=".55" stroke-opacity=".12"/></pattern>
    <style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.legend text{{fill:#a9bfbe;font:800 9px ui-monospace,Consolas,monospace}}</style>
  </defs>
  <rect width="1200" height="980" fill="#06171c"/>
  <text x="48" y="45" fill="#62d7ce" font-size="14" font-weight="900" letter-spacing="2.5">OSW / MOTION STUDY  ·  M1 PERSISTENCE PILOT</text>
  <text x="48" y="88" fill="#eef9f7" font-size="34" font-weight="950">WHERE SURFACE MOTION HOLDS</text>
  <text x="48" y="118" fill="#9db3b2" font-size="12">{times} sampled historical fields · 2018 · nominal 15 m · speed + directional persistence</text>
  <rect x="923" y="38" width="229" height="30" rx="15" fill="#102a30" stroke="#f0cf70" stroke-opacity=".65"/>
  <text x="1037.5" y="58" text-anchor="middle" fill="#f0cf70" font-size="10" font-weight="950" letter-spacing="1.3">ZONING OFF · STABILITY TEST</text>
  <g clip-path="url(#motion-map)">
    <rect x="48" y="170" width="1104" height="625" fill="#0b252c"/>
    <g aria-label="Mean surface vectors encoded by persistence">{vectors}</g>
    <path d="{land_path}" fill="url(#quiet-land)" fill-rule="evenodd"/>
  </g>
  <rect x="48" y="170" width="1104" height="625" rx="20" fill="none" stroke="#49666b" stroke-width="1.4"/>
  <g class="legend">
    <text x="48" y="828" fill="#edf8f6" font-size="11" font-weight="900">MEAN SAMPLED SPEED · m s⁻¹</text>{speed_legend()}
    <text x="785" y="828" fill="#edf8f6" font-size="11" font-weight="900">DIRECTIONAL PERSISTENCE · 0 CANCELS / 1 ALIGNS</text>{persistence_legend()}
  </g>
  <g transform="translate(48 905)">
    <text fill="#62d7ce" font-size="10" font-weight="950" letter-spacing="1.2">READ</text>
    <text x="48" fill="#afc3c1" font-size="10.5">persistent sampled surface direction · energetic but reversing areas fade</text>
    <text x="590" fill="#f0cf70" font-size="10" font-weight="950" letter-spacing="1.2">DO NOT READ</text>
    <text x="695" fill="#afc3c1" font-size="10.5">natural borders · Lagrangian coherence · heat transport</text>
  </g>
  <text x="48" y="954" fill="#667f81" font-size="9">SAMPLED-YEAR DIAGNOSTIC · {times} TIMES · MINIMUM {payload['minimum_samples']} VALID SAMPLES PER CELL · OLDER OSCAR 2017.0 · {count} VECTORS</text>
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

