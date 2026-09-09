"""Map sampled seasonal-direction agreement across internal province seams."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
from pathlib import Path

from audit_regions_against_motion import nearest_state
from build_motion_region_audit_view import MAP_BOX, load_javascript, motion_glyphs
from build_oscar_motion_view import MOLLWEIDE
from build_projection_bakeoff import (
    EXPECTED_SOURCE_SHA256, SOURCE_COMMIT, all_rings, geographic_state_geometry,
    projected_edge_path, projected_polygon_fill, pyproj_projector, raw_bounds,
    screen_transform,
)


COLORS = ("#e76f9f", "#f0cf70", "#62d7ce")


def similarity_band(value: float) -> int:
    if value < -.25:
        return 0
    if value < .25:
        return 1
    return 2


def edge_state_pair(edge) -> tuple[str, str] | None:
    (x1, y1), (x2, y2) = edge
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length < 1e-9:
        return None
    midpoint = ((x1 + x2) / 2, (y1 + y2) / 2)
    offset = .08
    normal = (-dy / length * offset, dx / length * offset)
    left = nearest_state(midpoint[0] + normal[0], midpoint[1] + normal[1])
    right = nearest_state(midpoint[0] - normal[0], midpoint[1] - normal[1])
    return tuple(sorted((left, right))) if left != right else None


def display_code(code: str) -> str:
    return code.replace(" ", "·")


def owned_internal_edges(states: list[dict], state_region: dict[str, str]):
    owners = {}
    for state in states:
        for piece in state["pieces"]:
            rounded = [(round(x, 5), round(y, 5)) for x, y in piece]
            for start, end in zip(rounded, rounded[1:] + rounded[:1]):
                if start == end:
                    continue
                edge = (start, end) if start < end else (end, start)
                owners.setdefault(edge, set()).add(state["code"])
    result = []
    for edge, codes in owners.items():
        if len(codes) != 2:
            continue
        pair = tuple(sorted(codes))
        if state_region[pair[0]] == state_region[pair[1]]:
            result.append((edge, pair))
    return result


def ranked_rows(items: list[dict], start_y: int, reverse: bool, count: int) -> str:
    selected = sorted(items, key=lambda item: item["mean_direction_similarity"], reverse=reverse)[:count]
    rows = []
    for index, item in enumerate(selected):
        y = start_y + index * 37
        color = COLORS[similarity_band(item["mean_direction_similarity"])]
        rows.append(f'<circle cx="1001" cy="{y - 4}" r="4" fill="{color}"/><text x="1014" y="{y}" class="code">{display_code(item["state_a"])}—{display_code(item["state_b"])}</text><text x="1232" y="{y}" class="value">{item["mean_direction_similarity"]:+.2f}</text><text x="1337" y="{y}" class="n">n={item["neighbor_pairs"]}</text>')
    return "".join(rows)


def render(seasonal: dict, membership: dict, geojson: dict, land_sha256: str) -> str:
    project = pyproj_projector(MOLLWEIDE.proj4)
    bounds = raw_bounds(project)
    screen = screen_transform(bounds, box=MAP_BOX)
    land = "".join(projected_polygon_fill(ring, MOLLWEIDE, project, bounds, screen) for ring in all_rings(geojson))
    glyphs, glyph_count = motion_glyphs(seasonal, project, screen)
    state_region = {state: region["region_code"] for region in membership["regions"] for state in region["member_states"]}
    adjacency = {tuple(sorted((item["state_a"], item["state_b"]))): item for item in membership["sampled_state_adjacencies"]}
    internal = [item for item in membership["sampled_state_adjacencies"] if state_region[item["state_a"]] == state_region[item["state_b"]]]
    states, realm_edges, region_edges = geographic_state_geometry()
    grouped = {(band, support): [] for band in range(3) for support in ("thin", "screened")}
    missing = []
    for edge, pair in owned_internal_edges(states, state_region):
        item = adjacency.get(pair)
        if item is None:
            missing.append(edge)
        else:
            grouped[(similarity_band(item["mean_direction_similarity"]), "screened" if item["neighbor_pairs"] >= 3 else "thin")].append(edge)
    outer = projected_edge_path(realm_edges + region_edges, MOLLWEIDE, project, bounds, screen)
    seam_paths = "".join(f'<path d="{projected_edge_path(edges, MOLLWEIDE, project, bounds, screen)}" fill="none" stroke="{COLORS[band]}" stroke-width="{2.5 if support == "screened" else 1.55}" opacity="{1 if support == "screened" else .8}" stroke-dasharray="{"none" if support == "screened" else "5 3"}"/>' for (band, support), edges in grouped.items() if edges)
    seams = f'<defs><mask id="seam-ocean-mask"><rect width="1400" height="900" fill="white"/><path d="{land}" fill="black" fill-rule="evenodd"/></mask></defs><g mask="url(#seam-ocean-mask)">{seam_paths}</g>'
    missing_path = projected_edge_path(missing, MOLLWEIDE, project, bounds, screen)
    weak = ranked_rows(internal, 257, False, 7)
    strong = ranked_rows(internal, 592, True, 5)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="900" viewBox="0 0 1400 900" role="img" aria-labelledby="title desc" data-motion-level="membership-seams" data-zoning="frozen-comparison"><title id="title">Which internal province seams disagree?</title><desc id="desc">An Oceanic Mollweide map colors sampled province seams inside the frozen 22 regions by seasonal directional similarity. Magenta opposes, ochre is mixed, and cyan agrees. Solid seams have at least three neighboring grid-cell pairs; dashed seams have one or two. No split is proposed.</desc><metadata>OSCAR source artifact SHA-256 {membership['source_artifact_sha256']}; Natural Earth commit {SOURCE_COMMIT}, SHA-256 {land_sha256}; {glyph_count} motion glyphs. {html.escape(membership['boundary'])}</metadata><defs><marker id="audit-arrow" viewBox="0 0 4 4" refX="3.5" refY="2" markerWidth="3" markerHeight="3" orient="auto"><path d="M0 0L4 2L0 4Z" fill="#72d8d0"/></marker><pattern id="quiet-land" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><rect width="8" height="8" fill="#fafaf7"/><path d="M0 0V8" stroke="#526d70" stroke-width=".45" stroke-opacity=".10"/></pattern><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.code{{fill:#eef9f7;font-size:11px;font-weight:950}}.value{{fill:#f5d97f;font:900 11px ui-monospace,Consolas,monospace;text-anchor:end}}.n{{fill:#789596;font:800 9px ui-monospace,Consolas,monospace;text-anchor:end}}</style></defs><rect width="1400" height="900" fill="#06171c"/><text x="38" y="42" fill="#62d7ce" font-size="14" font-weight="900" letter-spacing="2.5">OSW / MOTION STUDY  ·  M1 INTERNAL SEAMS</text><text x="38" y="84" fill="#eef9f7" font-size="32" font-weight="950">WHICH INTERNAL SEAMS DISAGREE?</text><text x="38" y="113" fill="#9db3b2" font-size="11.5">sampled four-neighbor province contacts · seasonal direction similarity · frozen 22-region containers</text><rect x="1128" y="34" width="234" height="30" rx="15" fill="#102a30" stroke="#f0cf70" stroke-opacity=".7"/><text x="1245" y="54" text-anchor="middle" fill="#f0cf70" font-size="10" font-weight="950" letter-spacing="1.3">ADJACENCY · NOT A SPLIT</text><g><rect x="38" y="150" width="920" height="590" rx="18" fill="#0b252c" stroke="#49666b"/>{glyphs}<path d="{land}" fill="url(#quiet-land)" fill-rule="evenodd"/><path d="{outer}" fill="none" stroke="#789596" stroke-width=".65" opacity=".55"/><path d="{missing_path}" fill="none" stroke="#49666b" stroke-width=".5" stroke-dasharray="1 3" opacity=".5"/>{seams}<text x="58" y="718" fill="#617d80" font-size="8">{glyph_count} SEASONAL-MEAN GLYPHS · SOLID SEAM n≥3 · DASHED n=1–2 · DOTTED UNSAMPLED · OUTER REGION BORDERS QUIET</text></g><g><text x="994" y="172" fill="#eef9f7" font-size="18" font-weight="950">LOWEST INTERNAL SEAMS</text><text x="994" y="198" fill="#789596" font-size="9">MEAN FOUR-SEASON DIRECTION SIMILARITY</text><text x="994" y="218" fill="#789596" font-size="8.5">LOCAL SAMPLED CONTACTS ONLY</text>{weak}<text x="994" y="506" fill="#eef9f7" font-size="18" font-weight="950">HIGHEST INTERNAL SEAMS</text><text x="994" y="532" fill="#789596" font-size="9">AGREEMENT DOES NOT PROVE A BARRIER</text>{strong}</g><g><text x="38" y="784" fill="#eef9f7" font-size="10" font-weight="900">SEAM SIMILARITY</text><path d="M180 780H240" stroke="#e76f9f" stroke-width="2"/><text x="250" y="784" fill="#9db3b2" font-size="9">&lt; −0.25 · OPPOSED</text><path d="M408 780H468" stroke="#f0cf70" stroke-width="2"/><text x="478" y="784" fill="#9db3b2" font-size="9">−0.25…+0.25 · MIXED</text><path d="M696 780H756" stroke="#62d7ce" stroke-width="2"/><text x="766" y="784" fill="#9db3b2" font-size="9">≥ +0.25 · ALIGNED</text></g><text x="38" y="838" fill="#62d7ce" font-size="9.5" font-weight="950">READING</text><text x="102" y="838" fill="#afc3c1" font-size="10">the sampled seam replaces the earlier all-pairs shortcut · local disagreement identifies a research target, not a new boundary</text><text x="38" y="866" fill="#617d80" font-size="8.5">ONE HISTORICAL YEAR · COARSE DISPLAY GRID · SCHEMATIC NEAREST-SEED GEOMETRY · NOT VALIDATED PROVINCE BOUNDARIES, EXCHANGE, HEAT TRANSPORT, OR A SPLIT DECISION</text></svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seasonal-data", type=Path, required=True)
    parser.add_argument("--membership", type=Path, required=True)
    parser.add_argument("--land-geojson", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw_land = args.land_geojson.read_bytes()
    digest = hashlib.sha256(raw_land).hexdigest()
    if digest != EXPECTED_SOURCE_SHA256:
        raise SystemExit(f"Natural Earth source checksum mismatch: {digest}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(load_javascript(args.seasonal_data), json.loads(args.membership.read_text(encoding="utf-8")), json.loads(raw_land), digest), encoding="utf-8", newline="\n")
    print(args.output)


if __name__ == "__main__":
    main()
