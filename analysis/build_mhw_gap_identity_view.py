"""Render the OSW-D4 temporal-gap identity bakeoff."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "research" / "osw-d4-noaa-crw-mhw-gap-identity-2026.json"
DEFAULT_OUTPUT = ROOT / "figures" / "osw-d4-noaa-crw-mhw-gap-identity-2026.svg"


def build(input_path=DEFAULT_INPUT, output_path=DEFAULT_OUTPUT):
    payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
    before_rows = payload["pre_gap_footprint"]["component_rows"]
    after_rows = payload["post_gap_lineage"]["daily_footprints"][0]["component_rows"]
    overlap_rows = payload["exact_overlap_rows"]
    west, east, south, north = -51.5, -47.35, 40.0, 43.0
    cosine = math.cos(math.radians((south + north) / 2))
    panel_w, panel_h = 232, 190
    panel_scale = min(panel_w / ((east - west) * cosine), panel_h / (north - south))

    def runs_svg(rows, x0, y0, fill, opacity=1):
        scale = panel_scale
        used_w, used_h = (east - west) * cosine * scale, (north - south) * scale
        ox, oy = x0 + (panel_w - used_w) / 2, y0 + (panel_h - used_h) / 2
        cells = []
        for latitude, runs in rows:
            for run_west, run_east, _category in runs:
                x = ox + (run_west - 0.025 - west) * cosine * scale
                y = oy + (north - latitude - 0.025) * scale
                width = (run_east - run_west + 0.05) * cosine * scale
                cells.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{width:.2f}" height="{0.05*scale:.2f}" fill="{fill}" opacity="{opacity}"/>')
        return "".join(cells)

    x_positions = [72, 332, 592, 852]
    y = 240
    before = runs_svg(before_rows, x_positions[0], y, "#ffc857")
    ghost = runs_svg(before_rows, x_positions[1], y, "url(#ghost)")
    after = runs_svg(after_rows, x_positions[2], y, "#49a9b8")
    overlay_before = runs_svg(before_rows, x_positions[3], y, "#ffc857", 0.85)
    overlay_after = runs_svg(after_rows, x_positions[3], y, "#49a9b8", 0.65)
    overlay_overlap = runs_svg(overlap_rows, x_positions[3], y, "url(#overlap)")
    bridge = payload["bridge_metrics"]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="760" viewBox="0 0 1200 760" role="img">
<title>OSW-D4 marine heatwave gap identity bakeoff</title>
<desc>August 10 and August 12 heatwave footprints share 122 exact native grid locations, although none remains threshold-active on August 11. Daily inheritance splits the lineages; allowing one gap day reconnects them without spatial dilation.</desc>
<style>.eyebrow{{font:700 15px Inter,"Segoe UI",sans-serif;letter-spacing:2.3px;fill:#327184}}.title{{font:700 42px Georgia,serif;fill:#112c38}}.lead{{font:400 18px Inter,"Segoe UI",sans-serif;fill:#425d67}}.paneldate{{font:700 13px Inter,"Segoe UI",sans-serif;fill:#173946;letter-spacing:.7px}}.panelnote{{font:500 12px Inter,"Segoe UI",sans-serif;fill:#61777f}}.metric{{font:700 30px Georgia,serif;fill:#112c38}}.metriclabel{{font:600 11px Inter,"Segoe UI",sans-serif;letter-spacing:.8px;fill:#60747d}}.body{{font:400 13px Inter,"Segoe UI",sans-serif;fill:#536a74}}.join{{font:700 15px Inter,"Segoe UI",sans-serif;fill:#176474}}.split{{font:700 15px Inter,"Segoe UI",sans-serif;fill:#9a3f2b}}</style>
<defs><pattern id="ghost" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" fill="#e7edef"/><path d="M0 6L6 0" stroke="#98a9ae" stroke-width="1"/></pattern><pattern id="overlap" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" fill="#173f52"/><path d="M0 0L6 6M6 0L0 6" stroke="#f8fbfa" stroke-width=".8"/></pattern></defs>
<rect width="1200" height="760" fill="#f8fbfa"/><path d="M0 0H1200V12H0Z" fill="#1f7085"/>
<text x="72" y="66" class="eyebrow">OSW · DETECTED OBJECT 04 · IDENTITY BAKEOFF</text>
<text x="72" y="121" class="title">The gap is temporal, not spatial</text>
<text x="72" y="157" class="lead">Two qualified footprint lineages · one missing threshold day · 122 exact grid locations reactivate</text>
<g fill="#edf5f6" stroke="#b8ccd1">{''.join(f'<rect x="{x}" y="{y}" width="{panel_w}" height="{panel_h}"/>' for x in x_positions)}</g>
{before}{ghost}{after}{overlay_before}{overlay_after}{overlay_overlap}
<path d="M86 {y+168}h{100/111.195*panel_scale:.1f}" stroke="#395660" stroke-width="2"/><text x="{86+(100/111.195*panel_scale)/2:.1f}" y="{y+183}" class="panelnote" text-anchor="middle">100 km</text>
<text x="72" y="221" class="paneldate">10 AUG · BEFORE</text><text x="304" y="221" text-anchor="end" class="panelnote">145 px</text>
<text x="332" y="221" class="paneldate">11 AUG · GAP</text><text x="564" y="221" text-anchor="end" class="panelnote">0 / 145 active</text>
<text x="592" y="221" class="paneldate">12 AUG · AFTER</text><text x="824" y="221" text-anchor="end" class="panelnote">457 px</text>
<text x="852" y="221" class="paneldate">EXACT OVERLAP</text><text x="1084" y="221" text-anchor="end" class="panelnote">122 px</text>
<text x="188" y="456" text-anchor="middle" class="metric">3,323 km²</text><text x="448" y="456" text-anchor="middle" class="metric">threshold off</text><text x="708" y="456" text-anchor="middle" class="metric">10,534 km²</text><text x="968" y="456" text-anchor="middle" class="metric">IoU {bridge['iou']:.3f}</text>
<g transform="translate(72 510)"><rect width="512" height="82" rx="7" fill="#f8e9e4"/><text x="22" y="31" class="split">SPLIT · uninterrupted daily inheritance</text><text x="22" y="57" class="body">No August 11 active component inherits an August 10 pixel.</text></g>
<g transform="translate(616 510)"><rect width="512" height="82" rx="7" fill="#e5f2f2"/><text x="22" y="31" class="join">JOIN · permit one gap day, retain exact overlap</text><text x="22" y="57" class="body">84.1% of prior grid locations reactivate; spatial dilation required: 0 cells.</text></g>
<g transform="translate(72 626)"><text class="metric">{bridge['pre_gap_retained_fraction']*100:.1f}%</text><text x="105" y="-2" class="metriclabel">PRIOR FOOTPRINT RETAINED</text><text x="390" class="metric">{bridge['post_gap_inherited_fraction']*100:.1f}%</text><text x="495" y="-2" class="metriclabel">NEW FOOTPRINT INHERITED</text><text x="790" class="metric">0</text><text x="824" y="-2" class="metriclabel">DILATION CELLS NEEDED</text></g>
<text x="72" y="716" class="body">Local equirectangular · standard parallel 41.5°N. Reconnection is a declared event rule, not continuous threshold evidence or proof of materially identical water.</text>
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
