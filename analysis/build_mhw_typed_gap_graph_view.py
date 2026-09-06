"""Render the OSW-D9 exact-daily versus typed-gap graph."""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "research" / "osw-d9-noaa-crw-mhw-typed-gap-graph-2026.json"
DEFAULT_OUTPUT = ROOT / "figures" / "osw-d9-noaa-crw-mhw-typed-gap-graph-2026.svg"


def build(input_path=DEFAULT_INPUT, output_path=DEFAULT_OUTPUT):
    payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
    bridge = payload["typed_bridge"]
    policies = payload["policy_bakeoff"]
    base = payload["base_family"]
    post = payload["post_gap_primary_lineage"]
    if [(item["node_count"], item["edge_count"]) for item in policies] != [(28, 29), (35, 36)]:
        raise ValueError("view expects the governed D9 graph outcomes")
    start, end = date.fromisoformat("2026-07-21"), date.fromisoformat("2026-08-18")
    x0, width = 88, 1024

    def tx(value):
        return x0 + (date.fromisoformat(value) - start).days / (end - start).days * width

    pre_dates = [date.fromisoformat("2026-07-21").toordinal() + index for index in range(21)]
    post_dates = [date.fromisoformat("2026-08-12").toordinal() + index for index in range(7)]
    pre_nodes = "".join(f'<circle cx="{tx(date.fromordinal(value).isoformat()):.1f}" cy="337" r="6.5" fill="#173f51" stroke="#f8fbfa"/>' for value in pre_dates)
    post_nodes = "".join(f'<circle cx="{tx(date.fromordinal(value).isoformat()):.1f}" cy="337" r="6.5" fill="#267b87" stroke="#f8fbfa"/>' for value in post_dates)
    branch_dates = ["2026-07-28", "2026-07-29", "2026-08-02", "2026-08-04", "2026-08-07"]
    branches = "".join(
        f'<path d="M{tx(value):.1f} 337q10 -42 20 -50" fill="none" stroke="#c17a43" stroke-width="2"/><circle cx="{tx(value)+20:.1f}" cy="287" r="5" fill="#f3b65d" stroke="#8b512e"/>'
        for value in branch_dates
    )
    gap_left, gap_right = tx("2026-08-11") - 12, tx("2026-08-11") + 12
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800" role="img">
<title>OSW-D9 explicitly typed marine heatwave gap edge</title>
<desc>The strict exact-daily graph ends August 10 with 28 nodes and 29 edges. A dashed conditional edge crosses the threshold-inactive August 11 field and joins the August 10 component to a seven-day post-gap primary lineage through August 18, producing 35 nodes and 36 edges. The endpoints share 122 cells, but no inherited cell is active on the gap day.</desc>
<defs><pattern id="gap" width="7" height="7" patternUnits="userSpaceOnUse"><rect width="7" height="7" fill="#f4f6f5"/><path d="M0 7L7 0" stroke="#aab8ba" stroke-width="1"/></pattern></defs>
<style>.eyebrow{{font:700 14px Inter,"Segoe UI",sans-serif;letter-spacing:2.2px;fill:#327487}}.title{{font:700 40px Georgia,serif;fill:#112f3b}}.lead{{font:400 18px Inter,"Segoe UI",sans-serif;fill:#49636c}}.section{{font:700 12px Inter,"Segoe UI",sans-serif;letter-spacing:1.4px;fill:#2e7182}}.legend{{font:600 12px Inter,"Segoe UI",sans-serif;fill:#425f69}}.date{{font:600 11px Inter,"Segoe UI",sans-serif;fill:#60777f}}.metric{{font:700 31px Georgia,serif;fill:#153946}}.metriclabel{{font:700 10px Inter,"Segoe UI",sans-serif;letter-spacing:.7px;fill:#60767e}}.cardtitle{{font:700 15px Inter,"Segoe UI",sans-serif;fill:#173d49}}.body{{font:400 13px Inter,"Segoe UI",sans-serif;fill:#506a73}}.small{{font:500 11px Inter,"Segoe UI",sans-serif;fill:#657b82}}.join{{font:700 15px Inter,"Segoe UI",sans-serif;fill:#176474}}.split{{font:700 15px Inter,"Segoe UI",sans-serif;fill:#9a472e}}</style>
<rect width="1200" height="800" fill="#f8fbfa"/><path d="M0 0H1200V12H0Z" fill="#1f7185"/>
<text x="72" y="61" class="eyebrow">OSW · DETECTED OBJECT 09 · TYPED TEMPORAL EDGE</text>
<text x="72" y="113" class="title">A gap edge is not a daily edge</text>
<text x="72" y="149" class="lead">One dashed policy connector preserves the threshold-inactive day instead of painting it as continuous evidence.</text>
<g transform="translate(72 177)"><path d="M0 8h34" stroke="#267b87" stroke-width="5"/><text x="44" y="12" class="legend">solid · consecutive active days</text><path d="M292 8h34" stroke="#b86d3e" stroke-width="3" stroke-dasharray="7 5"/><text x="337" y="12" class="legend">dashed · one inactive day + endpoint overlap</text><rect x="705" width="20" height="16" fill="url(#gap)" stroke="#aab8ba"/><text x="735" y="12" class="legend">threshold inactive</text></g>
<rect x="72" y="218" width="1056" height="260" rx="8" fill="#edf4f3"/>
<rect x="{gap_left:.1f}" y="239" width="{gap_right-gap_left:.1f}" height="211" fill="url(#gap)" stroke="#aab8ba"/>
<path d="M{tx('2026-07-21'):.1f} 337H{tx('2026-08-10'):.1f}" stroke="#267b87" stroke-width="5"/>
<path d="M{tx('2026-08-12'):.1f} 337H{tx('2026-08-18'):.1f}" stroke="#267b87" stroke-width="5"/>
{branches}{pre_nodes}{post_nodes}
<path d="M{tx('2026-08-10'):.1f} 323C{tx('2026-08-10')+18:.1f} 250 {tx('2026-08-12')-18:.1f} 250 {tx('2026-08-12'):.1f} 323" fill="none" stroke="#b86d3e" stroke-width="3.5" stroke-dasharray="8 6"/>
<text x="{(tx('2026-08-10')+tx('2026-08-12'))/2:.1f}" y="249" text-anchor="middle" class="section">POLICY BRIDGE · 122 SHARED CELLS</text>
<text x="{tx('2026-07-21'):.1f}" y="376" text-anchor="middle" class="date">21 JUL</text><text x="{tx('2026-08-10'):.1f}" y="376" text-anchor="middle" class="date">10 AUG</text><text x="{tx('2026-08-11'):.1f}" y="427" text-anchor="middle" class="date">11 AUG</text><text x="{tx('2026-08-12'):.1f}" y="376" text-anchor="middle" class="date">12 AUG</text><text x="{tx('2026-08-18'):.1f}" y="376" text-anchor="middle" class="date">18 AUG</text>
<text x="{(tx('2026-07-21')+tx('2026-08-10'))/2:.1f}" y="455" text-anchor="middle" class="small">D7 family summary · {base['primary_branch_node_count']} trunk + {base['side_component_count']} side · orange marks = {base['split_node_count']} split dates</text>
<text x="{(tx('2026-08-12')+tx('2026-08-18'))/2:.1f}" y="455" text-anchor="middle" class="small">D4 post-gap primary lineage · {post['day_count']} days · not a complete family</text>
<g transform="translate(72 512)"><rect width="512" height="83" rx="7" fill="#f8e9e4"/><text x="22" y="31" class="split">STOP · adjacent daily exact overlap only</text><text x="22" y="57" class="body">28 nodes · 29 edges · graph ends 10 August.</text></g>
<g transform="translate(616 512)"><rect width="512" height="83" rx="7" fill="#e5f2f2"/><text x="22" y="31" class="join">CONTINUE · permit the typed one-day bridge</text><text x="22" y="57" class="body">35 nodes · 36 edges · primary continuation ends 18 August.</text></g>
<g transform="translate(72 637)"><text class="metric">{bridge['intersection_pixels']}</text><text x="70" y="-3" class="metriclabel">SHARED ENDPOINT CELLS</text><text x="302" class="metric">{bridge['source_retained_fraction']*100:.1f}%</text><text x="408" y="-3" class="metriclabel">PRIOR FOOTPRINT</text><text x="585" class="metric">{bridge['target_inherited_fraction']*100:.1f}%</text><text x="691" y="-3" class="metriclabel">POST-GAP FOOTPRINT</text><text x="891" class="metric">{bridge['active_source_pixels_remaining_on_inactive_date']}</text><text x="923" y="-3" class="metriclabel">ACTIVE ON GAP DAY</text></g>
<text x="72" y="730" class="small">Source: OSW-D7 + OSW-D4 from NOAA CRW Marine Heatwave Watch v1.0.1 · native 0.05° daily category · IoU {bridge['iou']:.3f} · dilation 0 cells.</text>
<text x="72" y="753" class="small">Bridge = event-identity convention. It is not active-threshold evidence or interpolation on 11 August, material continuity, or a physical mechanism.</text>
<text x="72" y="776" class="small">Post-gap addition is one governed primary lineage, not a complete post-gap branch-family expansion.</text>
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
