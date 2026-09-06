"""Render the OSW-D5 connectivity and overlap sensitivity bakeoff."""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "research" / "osw-d5-noaa-crw-mhw-tracking-sensitivity-2026.json"
DEFAULT_OUTPUT = ROOT / "figures" / "osw-d5-noaa-crw-mhw-tracking-sensitivity-2026.svg"


def build(input_path=DEFAULT_INPUT, output_path=DEFAULT_OUTPUT):
    payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
    results = payload["results"]
    comparison = payload["cross_connectivity_comparison"]
    if not (comparison["tracked_dates_equal"] and comparison["pre_gap_components_equal"] and comparison["post_gap_components_equal"]):
        raise ValueError("view requires matching lifetimes and exact gap components")
    maximum_shape_difference = max(item["symmetric_difference_pixels"] for item in comparison["daily_component_differences"])
    labels = ["ANY TOUCH", "IoU ≥ .10", "IoU ≥ .20", "IoU ≥ .25", "IoU ≥ .50"]
    x0, tile_w, gap = 310, 154, 12
    colors = {21: "#17677a", 18: "#3b8e91", 1: "#b56b3b"}
    tiles = []
    for row_index, result in enumerate(results):
        y = 258 + row_index * 116
        for column, window in enumerate(result["threshold_windows"]):
            x = x0 + column * (tile_w + gap)
            days = window["day_count"]
            duration = f"{days} day" if days == 1 else f"{days} days"
            tiles.append(
                f'<g transform="translate({x} {y})"><rect width="{tile_w}" height="88" rx="7" fill="{colors[days]}"/>'
                f'<text x="16" y="39" class="tilevalue">{duration}</text>'
                f'<text x="16" y="65" class="tiledates">{window["start"][5:].replace("-", "/")}–{window["end"][5:].replace("-", "/")}</text></g>'
            )

    start = date.fromisoformat("2026-07-20")
    end = date.fromisoformat("2026-08-20")
    timeline_x, timeline_w = 154, 892

    def tx(value):
        return timeline_x + (date.fromisoformat(value) - start).days / (end - start).days * timeline_w

    core_x1, core_x2 = tx("2026-07-21"), tx("2026-08-08")
    tail_x1, tail_x2 = tx("2026-08-08"), tx("2026-08-11")
    post_x1, post_x2 = tx("2026-08-12"), tx("2026-08-19")
    seed_x = tx("2026-07-23")
    break_edge = results[0]["threshold_windows"][2]["break_after"]
    gap_bridge = results[0]["gap_bridge"]

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800" role="img">
<title>OSW-D5 marine heatwave tracking sensitivity</title>
<desc>For this North Atlantic case, four-neighbor and eight-neighbor connectivity change some intermediate daily component shapes but give identical lineage lifetimes and gap footprints. Any exact overlap or IoU at least 0.10 gives 21 days. IoU at least 0.20 or 0.25 gives 18 days. IoU at least 0.50 leaves only the seed day. IoU means shared cells divided by the union of both footprints.</desc>
<style>.eyebrow{{font:700 14px Inter,"Segoe UI",sans-serif;letter-spacing:2.2px;fill:#337487}}.title{{font:700 40px Georgia,serif;fill:#112f3b}}.lead{{font:400 18px Inter,"Segoe UI",sans-serif;fill:#47636d}}.column{{font:700 11px Inter,"Segoe UI",sans-serif;letter-spacing:.8px;fill:#58717a}}.rowtitle{{font:700 17px Inter,"Segoe UI",sans-serif;fill:#173c49}}.rownote{{font:400 12px Inter,"Segoe UI",sans-serif;fill:#6a7f86}}.tilevalue{{font:700 25px Georgia,serif;fill:#fff}}.tiledates{{font:600 12px Inter,"Segoe UI",sans-serif;fill:#eaf6f5;letter-spacing:.3px}}.section{{font:700 12px Inter,"Segoe UI",sans-serif;letter-spacing:1.5px;fill:#296b7e}}.body{{font:400 13px Inter,"Segoe UI",sans-serif;fill:#516b74}}.strong{{font:700 14px Inter,"Segoe UI",sans-serif;fill:#173c49}}.small{{font:500 11px Inter,"Segoe UI",sans-serif;fill:#687d84}}</style>
<defs><pattern id="gap" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" fill="#f5f7f6"/><path d="M0 6L6 0" stroke="#aab7b9" stroke-width="1"/></pattern></defs>
<rect width="1200" height="800" fill="#f8fbfa"/><path d="M0 0H1200V12H0Z" fill="#1f7185"/>
<text x="72" y="61" class="eyebrow">OSW · DETECTED OBJECT 05 · ROBUSTNESS</text>
<text x="72" y="113" class="title">Adjacency changes the shape—not the lifetime</text>
<text x="72" y="149" class="lead">Ten controlled policies separate geometric sensitivity from the overlap rule that ends the named lineage.</text>
<g transform="translate(676 172)"><rect width="452" height="43" rx="7" fill="#e2f1f1"/><text x="226" y="27" text-anchor="middle" class="section">{comparison['differing_daily_component_count']} / {comparison['tracked_day_count']} SHAPES DIFFER BY ≤ {maximum_shape_difference} CELL · ALL FIVE LIFETIMES MATCH</text></g>
{''.join(f'<text x="{x0 + i*(tile_w+gap) + tile_w/2}" y="226" text-anchor="middle" class="column">{label}</text>' for i, label in enumerate(labels))}
<g transform="translate(72 274)"><text class="rowtitle">EDGE ONLY</text><text y="24" class="rownote">4-neighbor</text></g>
<g transform="translate(72 390)"><text class="rowtitle">EDGE + CORNER</text><text y="24" class="rownote">8-neighbor</text></g>
{''.join(tiles)}
<path d="M72 484H1128" stroke="#c6d6d9"/>
<text x="72" y="523" class="section">WHAT THE PLATEAU MEANS</text>
<text x="{(core_x1+core_x2)/2:.1f}" y="553" text-anchor="middle" class="small">18-day moderate-threshold plateau</text>
<text x="{(tail_x1+tail_x2)/2:.1f}" y="553" text-anchor="middle" class="small">permissive tail</text>
<text x="{(tx('2026-08-11')+tx('2026-08-12'))/2:.1f}" y="553" text-anchor="middle" class="small">gap</text>
<text x="{(post_x1+post_x2)/2:.1f}" y="553" text-anchor="middle" class="small">post-gap run</text>
<rect x="{timeline_x}" y="563" width="{timeline_w}" height="22" rx="4" fill="#e7eeee"/>
<rect x="{core_x1:.1f}" y="563" width="{core_x2-core_x1:.1f}" height="22" fill="#3b8e91"/>
<rect x="{tail_x1:.1f}" y="563" width="{tail_x2-tail_x1:.1f}" height="22" fill="#d39a4a"/>
<rect x="{tx('2026-08-11'):.1f}" y="563" width="{tx('2026-08-12')-tx('2026-08-11'):.1f}" height="22" fill="url(#gap)"/>
<rect x="{post_x1:.1f}" y="563" width="{post_x2-post_x1:.1f}" height="22" fill="#cbdfe1"/>
<circle cx="{seed_x:.1f}" cy="574" r="5" fill="#fff" stroke="#173c49" stroke-width="2"/>
<path d="M{tx('2026-08-08'):.1f} 550V596" stroke="#9b6534" stroke-width="1.5"/>
<text x="{timeline_x}" y="611" text-anchor="middle" class="small">20 JUL</text><text x="{tx('2026-08-01'):.1f}" y="611" text-anchor="middle" class="small">1 AUG</text><text x="{timeline_x+timeline_w}" y="611" text-anchor="middle" class="small">20 AUG</text>
<g transform="translate(72 645)"><rect width="336" height="91" rx="7" fill="#e5f2f2"/><text x="18" y="28" class="strong">18-day stable plateau</text><text x="18" y="51" class="body">21 Jul–7 Aug survives IoU ≥ .20 and .25.</text><text x="18" y="72" class="body">Both adjacencies give the same lifetime.</text></g>
<g transform="translate(432 645)"><rect width="336" height="91" rx="7" fill="#f6ecdc"/><text x="18" y="28" class="strong">The disputed edge is 7 → 8 Aug</text><text x="18" y="51" class="body">{break_edge['intersection_pixels']} exact cells persist, but IoU = {break_edge['iou']:.3f}.</text><text x="18" y="72" class="body">Large absolute overlap; large simultaneous reshaping.</text></g>
<g transform="translate(792 645)"><rect width="336" height="91" rx="7" fill="#edf2f2"/><text x="18" y="28" class="strong">The temporal bridge is also invariant</text><text x="18" y="51" class="body">{gap_bridge['intersection_pixels']} cells · IoU {gap_bridge['iou']:.3f} · both adjacencies.</text><text x="18" y="72" class="body">Gap permission remains the deciding rule.</text></g>
<text x="72" y="758" class="small">Source: NOAA CRW Marine Heatwave Watch v1.0.1 daily category · native 0.05° grid · 20 Jul–20 Aug 2026 · IoU = shared cells / union.</text>
<text x="72" y="778" class="small">Illustrative threshold sweep · greatest-intersection branch held fixed · no claim of water-parcel, subsurface, mechanism, or impact continuity.</text>
</svg>'''
    Path(output_path).write_text(svg, encoding="utf-8", newline="\n")
    return svg


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    build(args.input, args.output)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
