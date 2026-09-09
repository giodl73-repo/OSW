"""Render whether seasonal surface motion follows or crosses frozen OSW borders."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path

from build_motion_region_audit_view import MAP_BOX, edge_region_pair, load_javascript, motion_glyphs
from build_oscar_motion_view import MOLLWEIDE
from build_projection_bakeoff import (
    EXPECTED_SOURCE_SHA256, SOURCE_COMMIT, all_rings, geographic_state_geometry,
    projected_edge_path, projected_polygon_fill, pyproj_projector, raw_bounds,
    screen_transform,
)


PALETTE = ("#4fd6cf", "#8bc8bd", "#d4bd72", "#ed9863", "#f05d67")


def margin_band(margin: float) -> int:
    if margin <= -.10:
        return 0
    if margin <= -.03:
        return 1
    if margin < .03:
        return 2
    if margin < .10:
        return 3
    return 4


def ranked_rows(items: list[dict], start_y: int, reverse: bool) -> str:
    ranked = sorted(
        (
            item for item in items
            if item["support_class"] == "screened"
            and (item["orientation_margin"] > 0 if reverse else item["orientation_margin"] < 0)
        ),
        key=lambda item: item["orientation_margin"], reverse=reverse,
    )[:5]
    rows = []
    for index, item in enumerate(ranked):
        y = start_y + index * 42
        color = PALETTE[margin_band(item["orientation_margin"])]
        rows.append(
            f'<circle cx="1001" cy="{y - 4}" r="4" fill="{color}"/>'
            f'<text x="1014" y="{y}" class="code">{item["region_a"]}—{item["region_b"]}</text>'
            f'<text x="1194" y="{y}" class="metric">{item["orientation_margin"]:+.2f}</text>'
            f'<text x="1337" y="{y}" class="n">n={item["neighbor_pairs"]}</text>'
            f'<rect x="1014" y="{y + 9}" width="{item["along_border_score"] * 175:.1f}" height="3" fill="#4fd6cf" opacity=".8"><title>along {item["along_border_score"]:.2f}</title></rect>'
            f'<rect x="1198" y="{y + 9}" width="{item["cut_through_score"] * 175:.1f}" height="3" fill="#f05d67" opacity=".8"><title>across {item["cut_through_score"]:.2f}</title></rect>'
        )
    return "".join(rows)


def render(seasonal: dict, audit: dict, geojson: dict, land_sha256: str) -> str:
    project = pyproj_projector(MOLLWEIDE.proj4)
    bounds = raw_bounds(project)
    screen = screen_transform(bounds, box=MAP_BOX)
    land = "".join(projected_polygon_fill(ring, MOLLWEIDE, project, bounds, screen) for ring in all_rings(geojson))
    glyphs, glyph_count = motion_glyphs(seasonal, project, screen)
    scores = {tuple(sorted((item["region_a"], item["region_b"]))): item for item in audit["boundary_pairs"]}
    _, realm_edges, region_edges = geographic_state_geometry()
    grouped = {(band, support): [] for band in range(5) for support in ("sparse", "provisional", "screened")}
    unmatched = 0
    for edge in realm_edges + region_edges:
        item = scores.get(edge_region_pair(edge))
        if item is None:
            unmatched += 1
            grouped[(2, "sparse")].append(edge)
        else:
            grouped[(margin_band(item["orientation_margin"]), item["support_class"])].append(edge)
    borders = "".join(
        f'<path d="{projected_edge_path(edges, MOLLWEIDE, project, bounds, screen)}" fill="none" '
        f'stroke="{PALETTE[band]}" stroke-width="{1.5 if support == "screened" else 1.0 if support == "provisional" else .55}" '
        f'opacity="{.96 if support == "screened" else .72 if support == "provisional" else .32}" '
        f'stroke-dasharray="{"none" if support == "screened" else "5 3" if support == "provisional" else "1 3"}"/>'
        for (band, support), edges in grouped.items() if edges
    )
    followed = ranked_rows(audit["boundary_pairs"], 258, False)
    crossed = ranked_rows(audit["boundary_pairs"], 542, True)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="900" viewBox="0 0 1400 900" role="img" aria-labelledby="title desc" data-motion-level="border-orientation" data-zoning="frozen-audit">
  <title id="title">Where flow leans along and where it leans across OSW borders</title>
  <desc id="desc">A diverging border-orientation audit of the frozen 22-region nearest-seed system. Cyan favors tangential flow along a border, coral favors normal flow across it, and ochre is oblique or mixed. Solid borders have at least eight neighboring cell pairs. No region is revised.</desc>
  <metadata>OSCAR source artifact SHA-256 {audit['source_artifact_sha256']}; Natural Earth commit {SOURCE_COMMIT}, SHA-256 {land_sha256}; {glyph_count} motion glyphs; {unmatched} geometry edges lacked a sampled audit pair. Orientation margin is cut-through score minus along-border score. {html.escape(audit['boundary'])}</metadata>
  <defs><marker id="audit-arrow" viewBox="0 0 4 4" refX="3.5" refY="2" markerWidth="3" markerHeight="3" orient="auto"><path d="M0 0L4 2L0 4Z" fill="#72d8d0"/></marker><pattern id="quiet-land" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><rect width="8" height="8" fill="#fafaf7"/><path d="M0 0V8" stroke="#526d70" stroke-width=".45" stroke-opacity=".10"/></pattern><linearGradient id="orientation-scale"><stop offset="0" stop-color="#4fd6cf"/><stop offset="50%" stop-color="#d4bd72"/><stop offset="100%" stop-color="#f05d67"/></linearGradient><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.code{{fill:#edf8f6;font-size:12px;font-weight:900}}.metric{{fill:#f5d97f;font:900 12px ui-monospace,Consolas,monospace;text-anchor:end}}.n{{fill:#789596;font:800 10px ui-monospace,Consolas,monospace;text-anchor:end}}</style></defs>
  <rect width="1400" height="900" fill="#06171c"/>
  <text x="38" y="42" fill="#62d7ce" font-size="14" font-weight="900" letter-spacing="2.5">OSW / MOTION STUDY  ·  M1 BORDER ORIENTATION</text>
  <text x="38" y="84" fill="#eef9f7" font-size="32" font-weight="950">WHERE FLOW LEANS ALONG / LEANS ACROSS</text>
  <text x="38" y="113" fill="#9db3b2" font-size="11.5">tangential versus normal seasonal surface motion · continuous margin · frozen geometry</text>
  <rect x="1128" y="34" width="234" height="30" rx="15" fill="#102a30" stroke="#f0cf70" stroke-opacity=".7"/><text x="1245" y="54" text-anchor="middle" fill="#f0cf70" font-size="10" font-weight="950" letter-spacing="1.3">COMPARISON · NO REVISION</text>
  <g aria-label="Border-orientation map"><rect x="38" y="150" width="920" height="590" rx="18" fill="#0b252c" stroke="#49666b"/>{glyphs}<path d="{land}" fill="url(#quiet-land)" fill-rule="evenodd"/>{borders}<text x="58" y="718" fill="#617d80" font-size="8">{glyph_count} SEASONAL-MEAN GLYPHS · BORDER COLOR IS ORIENTATION MARGIN · SOLID n≥8 · DASHED n=3–7 · DOTTED SPARSE</text></g>
  <g aria-label="Screened border rankings"><text x="994" y="172" fill="#eef9f7" font-size="18" font-weight="950">LEANING ALONG</text><text x="994" y="198" fill="#789596" font-size="9">NEGATIVE MARGIN AMONG SCREENED BORDERS</text><text x="994" y="218" fill="#789596" font-size="8.5">CYAN BAR = ALONG · CORAL BAR = ACROSS</text>{followed}<text x="994" y="456" fill="#eef9f7" font-size="18" font-weight="950">LEANING ACROSS</text><text x="994" y="482" fill="#789596" font-size="9">POSITIVE MARGIN AMONG SCREENED BORDERS</text><text x="994" y="502" fill="#789596" font-size="8.5">MARGIN = ACROSS − ALONG</text>{crossed}</g>
  <g aria-label="Orientation legend"><text x="38" y="784" fill="#edf8f6" font-size="10" font-weight="900">ORIENTATION MARGIN</text><rect x="194" y="776" width="540" height="9" rx="4.5" fill="url(#orientation-scale)"/><text x="194" y="806" fill="#72d8d0" font-size="9">−1 · FOLLOWS</text><text x="464" y="806" text-anchor="middle" fill="#d4bd72" font-size="9">0 · OBLIQUE / MIXED</text><text x="734" y="806" text-anchor="end" fill="#f49a62" font-size="9">+1 · CROSSES</text></g>
  <text x="38" y="838" fill="#62d7ce" font-size="9.5" font-weight="950">READING</text><text x="102" y="838" fill="#afc3c1" font-size="10">orientation is continuous · “along” does not prove a barrier · “across” does not measure transported heat</text>
  <text x="38" y="866" fill="#617d80" font-size="8.5">ONE HISTORICAL YEAR · FLAT NEAREST-SEED BORDER NORMALS · SPATIALLY DEPENDENT COARSE SAMPLES · NOT CLIMATOLOGY, FULL-DEPTH FLOW, OR HEAT TRANSPORT</text>
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
