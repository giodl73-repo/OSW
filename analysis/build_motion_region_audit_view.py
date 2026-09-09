"""Render the frozen OSW region system as an audit overlay on seasonal motion."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
from pathlib import Path

from audit_regions_against_motion import cell_seasons, cell_structure, region_code
from build_oscar_motion_view import MOLLWEIDE, normalize_longitude
from build_projection_bakeoff import (
    EXPECTED_SOURCE_SHA256, SOURCE_COMMIT, all_rings, geographic_state_geometry,
    projected_edge_path, projected_polygon_fill, pyproj_projector, raw_bounds,
    screen_transform,
)


CANVAS = (1400, 900)
MAP_BOX = (38.0, 150.0, 920.0, 590.0)
SCORE_COLORS = ("#50777b", "#f0cf70", "#f49a62", "#f05d67")


def load_javascript(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8").split("=", 1)[1].strip().removesuffix(";"))


def score_band(score: float, count: int) -> int:
    if count < 3:
        return 0
    if score >= .50:
        return 3
    if score >= .40:
        return 2
    if score >= .28:
        return 1
    return 0


def edge_region_pair(edge) -> tuple[str, str] | None:
    (x1, y1), (x2, y2) = edge
    midpoint = ((x1 + x2) / 2, (y1 + y2) / 2)
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length < 1e-9:
        return None
    # Sampling on both sides identifies the nearest-seed regions that own the edge.
    offset = .08
    normal = (-dy / length * offset, dx / length * offset)
    left = region_code(midpoint[0] + normal[0], midpoint[1] + normal[1])
    right = region_code(midpoint[0] - normal[0], midpoint[1] - normal[1])
    return tuple(sorted((left, right))) if left != right else None


def motion_glyphs(payload: dict, project, screen) -> tuple[str, int]:
    rows, columns = payload["shape"]
    paths = []
    count = 0
    for row, latitude in enumerate(payload["latitude_values"]):
        if abs(latitude) > 79.9:
            continue
        cosine = max(.2, math.cos(math.radians(latitude)))
        for column, source_longitude in enumerate(payload["longitude_values"]):
            index = row * columns + column
            seasons = cell_seasons(payload, index)
            if not seasons:
                continue
            mean_u = sum(item[0] for item in seasons) / len(seasons)
            mean_v = sum(item[1] for item in seasons) / len(seasons)
            speed = math.hypot(mean_u, mean_v)
            alignment, _ = cell_structure(seasons)
            if speed < .008:
                continue
            longitude = normalize_longitude(source_longitude)
            angular = 1.2 + min(speed, 1.4) * 3.2
            end_latitude = latitude + mean_v / speed * angular
            end_longitude = normalize_longitude(longitude + mean_u / speed * angular / cosine)
            if abs(end_latitude) >= 89 or abs(end_longitude - longitude) > 40:
                continue
            start = screen(project(longitude, latitude))
            end = screen(project(end_longitude, end_latitude))
            distance = math.hypot(end[0] - start[0], end[1] - start[1])
            if not math.isfinite(distance) or distance < .6 or distance > 20:
                continue
            opacity = .12 + .48 * alignment
            paths.append(
                f'<path d="M{start[0]:.1f},{start[1]:.1f}L{end[0]:.1f},{end[1]:.1f}" '
                f'stroke="#72d8d0" stroke-width=".85" opacity="{opacity:.2f}" marker-end="url(#audit-arrow)"/>'
            )
            count += 1
    return "".join(paths), count


def render(seasonal: dict, audit: dict, geojson: dict, land_sha256: str) -> str:
    project = pyproj_projector(MOLLWEIDE.proj4)
    bounds = raw_bounds(project)
    screen = screen_transform(bounds, box=MAP_BOX)
    land = "".join(projected_polygon_fill(ring, MOLLWEIDE, project, bounds, screen) for ring in all_rings(geojson))
    glyphs, glyph_count = motion_glyphs(seasonal, project, screen)

    scores = {
        tuple(sorted((item["region_a"], item["region_b"]))): item
        for item in audit["boundary_pairs"]
    }
    _, realm_edges, region_edges = geographic_state_geometry()
    grouped = {(band, support): [] for band in range(4) for support in ("sparse", "provisional", "screened")}
    unmatched = 0
    for edge in realm_edges + region_edges:
        pair = edge_region_pair(edge)
        item = scores.get(pair) if pair else None
        if item is None:
            unmatched += 1
            grouped[(0, "sparse")].append(edge)
        else:
            grouped[(score_band(item["cut_through_score"], item["neighbor_pairs"]), item["support_class"])].append(edge)
    borders = "".join(
        f'<path d="{projected_edge_path(edges, MOLLWEIDE, project, bounds, screen)}" fill="none" '
        f'stroke="{SCORE_COLORS[band]}" stroke-width="{(.55, 1.0, 1.45, 2.0)[band]}" '
        f'opacity="{(.42, .78, .9, 1)[band]}" stroke-dasharray="{("1 3" if support == "sparse" else "5 3" if support == "provisional" else "none")}"/>'
        for (band, support), edges in grouped.items() if edges
    )

    screened = [item for item in audit["boundary_pairs"] if item["support_class"] == "screened"][:6]
    provisional = [item for item in audit["boundary_pairs"] if item["support_class"] == "provisional"][:3]
    supported = screened + provisional
    boundary_rows = []
    for index, item in enumerate(supported):
        y = 260 + index * 35
        band = score_band(item["cut_through_score"], item["neighbor_pairs"])
        season_cells = []
        for season_index, season in enumerate(("DJF", "MAM", "JJA", "SON")):
            season_score = item[f"cut_through_{season}"]
            season_band = score_band(season_score, 99)
            x = 1170 + season_index * 30
            season_cells.append(
                f'<rect x="{x}" y="{y - 12}" width="23" height="10" rx="3" fill="{SCORE_COLORS[season_band]}" opacity="{.48 + .52 * season_score:.2f}">'
                f'<title>{season} cut-through {season_score:.2f}</title></rect>'
            )
        boundary_rows.append(
            f'<circle cx="1001" cy="{y - 4}" r="4" fill="{SCORE_COLORS[band]}"/>'
            f'<text x="1014" y="{y}" class="code">{item["region_a"]}—{item["region_b"]}</text>'
            f'<text x="1154" y="{y}" class="value">{item["cut_through_score"]:.2f}</text>'
            f'{"".join(season_cells)}'
            f'<text x="1337" y="{y}" class="n">{item["support_class"][0].upper()} · n={item["neighbor_pairs"]}</text>'
        )

    coherent = [item for item in audit["regions"] if item["internal_neighbor_pairs"] >= 3][:7]
    region_rows = []
    for index, item in enumerate(coherent):
        y = 638 + index * 30
        region_rows.append(
            f'<text x="994" y="{y}" class="code">{item["region_code"]}</text>'
            f'<text x="1042" y="{y}" class="region">{html.escape(item["region"])}</text>'
            f'<text x="1337" y="{y}" class="n">{item["mean_internal_direction_similarity"]:+.2f}</text>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="900" viewBox="0 0 1400 900" role="img" aria-labelledby="title desc" data-motion-level="boundary-audit" data-zoning="frozen-audit">
  <title id="title">Do the provisional OSW region borders hold?</title>
  <desc id="desc">A diagnostic overlay compares the frozen 22-region nearest-seed system with one historical year of seasonal OSCAR surface motion. Warm borders are stronger cut-through warnings; four small cells show DJF, MAM, JJA, and SON scores; and a ranked panel identifies regions with low internal directional similarity. No region is revised.</desc>
  <metadata>OSCAR source artifact SHA-256 {audit['source_artifact_sha256']}; Natural Earth commit {SOURCE_COMMIT}, SHA-256 {land_sha256}; {glyph_count} motion glyphs; {unmatched} geometry edges lacked a sampled audit pair. {html.escape(audit['boundary'])}</metadata>
  <defs><marker id="audit-arrow" viewBox="0 0 4 4" refX="3.5" refY="2" markerWidth="3" markerHeight="3" orient="auto"><path d="M0 0L4 2L0 4Z" fill="#72d8d0"/></marker><pattern id="quiet-land" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><rect width="8" height="8" fill="#fafaf7"/><path d="M0 0V8" stroke="#526d70" stroke-width=".45" stroke-opacity=".10"/></pattern><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.code{{fill:#edf8f6;font-size:12px;font-weight:900}}.value{{fill:#f5d97f;font:900 12px ui-monospace,Consolas,monospace;text-anchor:end}}.n{{fill:#789596;font:800 10px ui-monospace,Consolas,monospace;text-anchor:end}}.region{{fill:#a9bfbe;font-size:10px}}</style></defs>
  <rect width="1400" height="900" fill="#06171c"/>
  <text x="38" y="42" fill="#62d7ce" font-size="14" font-weight="900" letter-spacing="2.5">OSW / MOTION STUDY  ·  M1 BOUNDARY AUDIT</text>
  <text x="38" y="84" fill="#eef9f7" font-size="32" font-weight="950">DO THESE BORDERS HOLD?</text>
  <text x="38" y="113" fill="#9db3b2" font-size="11.5">frozen 22-region overlay · seasonal surface motion · screening evidence, not a redraw</text>
  <rect x="1128" y="34" width="234" height="30" rx="15" fill="#102a30" stroke="#f0cf70" stroke-opacity=".7"/><text x="1245" y="54" text-anchor="middle" fill="#f0cf70" font-size="10" font-weight="950" letter-spacing="1.3">AUDIT OVERLAY · NO REVISION</text>
  <g aria-label="Motion and border audit map"><rect x="38" y="150" width="920" height="590" rx="18" fill="#0b252c" stroke="#49666b"/>{glyphs}<path d="{land}" fill="url(#quiet-land)" fill-rule="evenodd"/>{borders}<text x="58" y="718" fill="#617d80" font-size="8">{glyph_count} SEASONAL-MEAN GLYPHS · GLYPH OPACITY IS CROSS-SEASON ALIGNMENT · BORDERS REMAIN SCHEMATIC</text></g>
  <g aria-label="Ranked audit results"><text x="994" y="172" fill="#eef9f7" font-size="18" font-weight="950">BORDERS CROSSED</text><text x="994" y="198" fill="#789596" font-size="9">CUT-THROUGH = NORMAL FLOW × RESCALED DIRECTION SIMILARITY</text><text x="994" y="218" fill="#789596" font-size="8.2">S n≥8 · P n=3–7 · D/M/J/S = DJF/MAM/JJA/SON</text><text x="1154" y="238" class="n">MEAN</text><text x="1181" y="238" class="n">D</text><text x="1211" y="238" class="n">M</text><text x="1241" y="238" class="n">J</text><text x="1271" y="238" class="n">S</text><text x="1337" y="238" class="n">SUPPORT</text>{''.join(boundary_rows)}<text x="994" y="574" fill="#eef9f7" font-size="18" font-weight="950">INTERIORS THAT DISAGREE</text><text x="994" y="600" fill="#789596" font-size="9">LOWEST MEAN DIRECTIONAL SIMILARITY WITHIN A REGION</text>{''.join(region_rows)}</g>
  <g aria-label="Border legend"><text x="38" y="784" fill="#edf8f6" font-size="10" font-weight="900">CUT-THROUGH SCREEN</text>{''.join(f'<path d="M{190 + i * 158} 780H{238 + i * 158}" stroke="{color}" stroke-width="{(.55,1,1.45,2)[i]}"/><text x="250" y="784" transform="translate({i * 158} 0)" fill="#9db3b2" font-size="9">{("LOW / UNSAMPLED", "0.28–0.39", "0.40–0.49", "≥ 0.50")[i]}</text>' for i, color in enumerate(SCORE_COLORS))}</g>
  <text x="38" y="838" fill="#62d7ce" font-size="9.5" font-weight="950">WHAT THIS CAN SAY</text><text x="166" y="838" fill="#afc3c1" font-size="10">where the present schematic deserves investigation · whether a border and its neighboring surface motion agree</text>
  <text x="38" y="866" fill="#617d80" font-size="8.5">ONE HISTORICAL YEAR · COARSE GRID · FLAT NEAREST-SEED BORDER NORMAL · SUPPORT IS NOT STATISTICAL INDEPENDENCE · NOT CLIMATOLOGY, TRAJECTORIES, FULL-DEPTH FLOW, OR HEAT TRANSPORT</text>
</svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seasonal-data", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--land-geojson", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw_land = args.land_geojson.read_bytes()
    digest = hashlib.sha256(raw_land).hexdigest()
    if digest != EXPECTED_SOURCE_SHA256:
        raise SystemExit(f"Natural Earth source checksum mismatch: {digest}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(load_javascript(args.seasonal_data), json.loads(args.audit.read_text(encoding="utf-8")), json.loads(raw_land), digest), encoding="utf-8", newline="\n")
    print(args.output)


if __name__ == "__main__":
    main()
