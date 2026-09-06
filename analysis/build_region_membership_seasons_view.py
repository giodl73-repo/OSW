"""Render seasonal stability of sampled internal province seams."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path

from build_oscar_motion_view import MOLLWEIDE, SPEED_CLASSES
from build_oscar_seasonal_view import PANELS, SEASON_CONTEXT, load_payload, vector_layers
from build_projection_bakeoff import (
    EXPECTED_SOURCE_SHA256, SOURCE_COMMIT, all_rings, geographic_state_geometry,
    projected_edge_path, projected_polygon_fill, pyproj_projector, raw_bounds,
    screen_transform,
)
from build_region_membership_seams_view import COLORS, owned_internal_edges, similarity_band


def internal_adjacencies(membership: dict) -> tuple[dict, dict]:
    state_region = {state: region["region_code"] for region in membership["regions"] for state in region["member_states"]}
    items = {
        tuple(sorted((item["state_a"], item["state_b"]))): item
        for item in membership["sampled_state_adjacencies"]
        if state_region[item["state_a"]] == state_region[item["state_b"]]
    }
    return state_region, items


def stability_summary(items: dict) -> dict:
    stable = opposed = aligned = 0
    for item in items.values():
        bands = [similarity_band(item[f"direction_similarity_{season}"]) for season in ("DJF", "MAM", "JJA", "SON")]
        if len(set(bands)) == 1:
            stable += 1
            opposed += bands[0] == 0
            aligned += bands[0] == 2
    return {"internal": len(items), "stable": stable, "opposed": opposed, "aligned": aligned}


def panel(payload: dict, membership: dict, season: str, geojson: dict, project, bounds, states, outer_edges, state_region, adjacency) -> str:
    x, y, width, height = PANELS[season]
    screen = screen_transform(bounds, box=(x + 12, y + 50, width - 24, height - 65))
    land = "".join(projected_polygon_fill(ring, MOLLWEIDE, project, bounds, screen) for ring in all_rings(geojson))
    vectors, vector_count = vector_layers(payload, season, project, screen)
    grouped = {(band, support): [] for band in range(3) for support in ("thin", "screened")}
    missing = []
    for edge, pair in owned_internal_edges(states, state_region):
        item = adjacency.get(pair)
        if item is None:
            missing.append(edge)
        else:
            grouped[(similarity_band(item[f"direction_similarity_{season}"]), "screened" if item["neighbor_pairs"] >= 3 else "thin")].append(edge)
    seam_paths = "".join(f'<path d="{projected_edge_path(edges, MOLLWEIDE, project, bounds, screen)}" fill="none" stroke="{COLORS[band]}" stroke-width="{2.0 if support == "screened" else 1.25}" opacity="{1 if support == "screened" else .76}" stroke-dasharray="{"none" if support == "screened" else "5 3"}"/>' for (band, support), edges in grouped.items() if edges)
    outer = projected_edge_path(outer_edges, MOLLWEIDE, project, bounds, screen)
    missing_path = projected_edge_path(missing, MOLLWEIDE, project, bounds, screen)
    values = [item[f"direction_similarity_{season}"] for item in adjacency.values()]
    counts = [sum(similarity_band(value) == band for value in values) for band in range(3)]
    return f'''<g aria-label="{season} internal seams"><rect x="{x}" y="{y}" width="{width}" height="{height}" rx="18" fill="#0b252c" stroke="#49666b"/><text x="{x + 18}" y="{y + 28}" fill="#eef9f7" font-size="19" font-weight="950">{season} · {html.escape(payload['seasons'][season]['name'].upper())}</text><text x="{x + width - 18}" y="{y + 27}" text-anchor="end" fill="#7e9b9d" font-size="8.5">{SEASON_CONTEXT[season]}</text><g>{vectors}<path d="{outer}" fill="none" stroke="#789596" stroke-width=".55" opacity=".45"/><path d="{missing_path}" fill="none" stroke="#49666b" stroke-width=".45" stroke-dasharray="1 3" opacity=".35"/><defs><mask id="land-mask-{season}"><rect width="1400" height="1050" fill="white"/><path d="{land}" fill="black" fill-rule="evenodd"/></mask></defs><g mask="url(#land-mask-{season})">{seam_paths}</g><path d="{land}" fill="url(#quiet-land)" fill-rule="evenodd"/></g><text x="{x + 18}" y="{y + height - 10}" fill="#617d80" font-size="8">{vector_count} VECTORS · {counts[0]} OPPOSED · {counts[1]} MIXED · {counts[2]} ALIGNED SAMPLED SEAMS</text></g>'''


def render(payload: dict, membership: dict, geojson: dict, land_sha256: str) -> str:
    project = pyproj_projector(MOLLWEIDE.proj4)
    bounds = raw_bounds(project)
    states, realm_edges, region_edges = geographic_state_geometry()
    state_region, adjacency = internal_adjacencies(membership)
    panels = [panel(payload, membership, season, geojson, project, bounds, states, realm_edges + region_edges, state_region, adjacency) for season in payload["season_order"]]
    summary = stability_summary(adjacency)
    markers = "".join(f'<marker id="arrow-{index}" viewBox="0 0 4 4" refX="3.4" refY="2" markerWidth="3" markerHeight="3" orient="auto"><path d="M0 0L4 2L0 4Z" fill="{color}"/></marker>' for index, (_, color, _) in enumerate(SPEED_CLASSES))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1050" viewBox="0 0 1400 1050" role="img" aria-labelledby="title desc" data-motion-level="membership-seasons" data-zoning="frozen-comparison"><title id="title">Do the internal province seams persist across seasons?</title><desc id="desc">Four matched Oceanic Mollweide panels color sampled internal province seams by DJF, MAM, JJA, and SON direction similarity. None of the sampled seams remains opposed in all four seasons. No split is proposed.</desc><metadata>OSCAR source artifact SHA-256 {membership['source_artifact_sha256']}; Natural Earth commit {SOURCE_COMMIT}, SHA-256 {land_sha256}. {html.escape(membership['boundary'])}</metadata><defs>{markers}<pattern id="quiet-land" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><rect width="8" height="8" fill="#f7f7f4"/><path d="M0 0V8" stroke="#526d70" stroke-width=".5" stroke-opacity=".12"/></pattern><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}</style></defs><rect width="1400" height="1050" fill="#06171c"/><text x="38" y="42" fill="#62d7ce" font-size="14" font-weight="900" letter-spacing="2.5">OSW / MOTION STUDY  ·  M1 SEAM SEASONS</text><text x="38" y="84" fill="#eef9f7" font-size="32" font-weight="950">DO THE INTERNAL SEAMS PERSIST?</text><text x="38" y="113" fill="#9db3b2" font-size="11.5">same owned province seams · four seasonal direction fields · support styling preserved</text><rect x="1133" y="34" width="229" height="30" rx="15" fill="#102a30" stroke="#f0cf70" stroke-opacity=".65"/><text x="1247.5" y="54" text-anchor="middle" fill="#f0cf70" font-size="10" font-weight="950" letter-spacing="1.3">TIME TEST · NOT A SPLIT</text>{''.join(panels)}<g><text x="38" y="945" fill="#eef9f7" font-size="10.5" font-weight="900">SEAM SIMILARITY</text><path d="M180 941H240" stroke="#e76f9f" stroke-width="2"/><text x="250" y="945" fill="#9db3b2" font-size="9">&lt; −0.25 · OPPOSED</text><path d="M430 941H490" stroke="#f0cf70" stroke-width="2"/><text x="500" y="945" fill="#9db3b2" font-size="9">MIXED</text><path d="M620 941H680" stroke="#62d7ce" stroke-width="2"/><text x="690" y="945" fill="#9db3b2" font-size="9">≥ +0.25 · ALIGNED</text><text x="920" y="945" fill="#f0cf70" font-size="11" font-weight="950">{summary['opposed']} PERSISTENTLY OPPOSED</text><text x="1103" y="945" fill="#62d7ce" font-size="11" font-weight="950">{summary['aligned']} PERSISTENTLY ALIGNED</text></g><text x="38" y="1000" fill="#62d7ce" font-size="9.5" font-weight="950">RESULT</text><text x="100" y="1000" fill="#afc3c1" font-size="10">{summary['stable']} of {summary['internal']} sampled seams stay in one class across all four seasons · none stay opposed</text><text x="38" y="1028" fill="#617d80" font-size="8.5">ONE HISTORICAL YEAR · COARSE GRID · SCHEMATIC SEAMS · SEASONAL STABILITY IS NOT INTERANNUAL PERSISTENCE, BOUNDARY EXCHANGE, HEAT TRANSPORT, OR A SPLIT DECISION</text></svg>'''


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
    args.output.write_text(render(load_payload(args.seasonal_data), json.loads(args.membership.read_text(encoding="utf-8")), json.loads(raw_land), digest), encoding="utf-8", newline="\n")
    print(args.output)


if __name__ == "__main__":
    main()
