"""Render the OSW-D8 family-pruning scale ladder."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "research" / "osw-d8-noaa-crw-mhw-family-pruning-2026.json"
DEFAULT_OUTPUT = ROOT / "figures" / "osw-d8-noaa-crw-mhw-family-pruning-2026.svg"


def build(input_path=DEFAULT_INPUT, output_path=DEFAULT_OUTPUT):
    payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
    results = payload["results"]
    expected = [7, 4, 4, 2, 1, 0]
    if [item["side_component_count"] for item in results] != expected:
        raise ValueError("view expects the governed D8 pruning ladder")
    labels = ["NO CUTOFF", "≥ 25 km²", "≥ 250 km²", "≥ 500 km²", "≥ 1,000 km²", "≥ 1,500 km²"]
    fills = ["#b86c3e", "#c47c48", "#c47c48", "#d49b59", "#dfbd82", "#d9e7e7"]
    cards = []
    for index, (label, result) in enumerate(zip(labels, results)):
        x = 72 + index * 176
        side = result["side_component_count"]
        split_count = result["split_node_count"]
        merge_count = result["merge_node_count"]
        split_text = f"{split_count} split" if split_count == 1 else f"{split_count} splits"
        merge_text = f"{merge_count} merge" if merge_count == 1 else f"{merge_count} merges"
        value_color = "#fff" if side else "#183e4b"
        detail_color = "#fff4e8" if side else "#557079"
        cards.append(
            f'<g transform="translate({x} 236)"><rect width="160" height="154" rx="8" fill="{fills[index]}"/>'
            f'<text x="16" y="27" class="cardlabel" fill="{value_color}">{label}</text>'
            f'<text x="16" y="74" class="cardvalue" fill="{value_color}">{side}</text>'
            f'<text x="16" y="96" class="cardunit" fill="{detail_color}">SIDE COMPONENTS</text>'
            f'<text x="16" y="124" class="carddetail" fill="{detail_color}">{split_text} · {merge_text}</text>'
            f'<text x="16" y="143" class="carddetail" fill="{detail_color}">21 trunk nodes</text></g>'
        )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800" role="img">
<title>OSW-D8 marine heatwave lineage-family pruning sensitivity</title>
<desc>The 21-node primary trunk survives every tested daily-area threshold from zero through 1,500 square kilometres. Side components decline from seven to four, four, two, one, and zero. Split and merge topology disappears as small components are pruned.</desc>
<style>.eyebrow{{font:700 14px Inter,"Segoe UI",sans-serif;letter-spacing:2.2px;fill:#327487}}.title{{font:700 40px Georgia,serif;fill:#112f3b}}.lead{{font:400 18px Inter,"Segoe UI",sans-serif;fill:#49636c}}.section{{font:700 12px Inter,"Segoe UI",sans-serif;letter-spacing:1.4px;fill:#2e7182}}.cardlabel{{font:700 12px Inter,"Segoe UI",sans-serif;letter-spacing:.8px}}.cardvalue{{font:700 42px Georgia,serif}}.cardunit{{font:700 10px Inter,"Segoe UI",sans-serif;letter-spacing:.7px}}.carddetail{{font:600 12px Inter,"Segoe UI",sans-serif}}.stephead{{font:700 15px Inter,"Segoe UI",sans-serif;fill:#183f4b}}.body{{font:400 13px Inter,"Segoe UI",sans-serif;fill:#506a73}}.small{{font:500 11px Inter,"Segoe UI",sans-serif;fill:#657b82}}</style>
<rect width="1200" height="800" fill="#f8fbfa"/><path d="M0 0H1200V12H0Z" fill="#1f7185"/>
<text x="72" y="61" class="eyebrow">OSW · DETECTED OBJECT 08 · SCALE SENSITIVITY</text>
<text x="72" y="113" class="title">The trunk survives every tested cutoff. The family does not.</text>
<text x="72" y="149" class="lead">Minimum daily area progressively removes side topology without changing the 21-day primary lineage.</text>
<g transform="translate(72 177)"><rect width="1056" height="39" rx="7" fill="#e2f1f1"/><text x="528" y="25" text-anchor="middle" class="section">AREA CUTOFF APPLIED TO EVERY NODE · RECOMPUTE ANCHOR REACHABILITY, SPLITS, MERGES, AND TERMINALS</text></g>
{''.join(cards)}
<path d="M72 426H1128" stroke="#c6d6d9"/>
<text x="72" y="462" class="section">WHICH SIDE COMPONENTS CROSS EACH LINE</text>
<g transform="translate(72 488)"><rect width="246" height="116" rx="7" fill="#f8eadf"/><text x="18" y="29" class="stephead">25 km² removes three</text><text x="18" y="56" class="body">Three one-cell components</text><text x="18" y="77" class="body">at 23.1–23.7 km² vanish.</text><text x="18" y="99" class="small">7 → 4 side components</text></g>
<g transform="translate(342 488)"><rect width="246" height="116" rx="7" fill="#f4ecdf"/><text x="18" y="29" class="stephead">250 km² is a plateau</text><text x="18" y="56" class="body">No additional component</text><text x="18" y="77" class="body">falls between 25 and 250.</text><text x="18" y="99" class="small">4 → 4 side components</text></g>
<g transform="translate(612 488)"><rect width="246" height="116" rx="7" fill="#edf1eb"/><text x="18" y="29" class="stephead">500 km² removes the merge</text><text x="18" y="56" class="body">279 and 465 km² branches go;</text><text x="18" y="77" class="body">the merge-back topology goes too.</text><text x="18" y="99" class="small">4 → 2 side components</text></g>
<g transform="translate(882 488)"><rect width="246" height="116" rx="7" fill="#e7efef"/><text x="18" y="29" class="stephead">1,500 km² leaves the trunk</text><text x="18" y="56" class="body">559 km² goes at 1,000;</text><text x="18" y="77" class="body">1,254 km² goes at 1,500.</text><text x="18" y="99" class="small">2 → 1 → 0 side components</text></g>
<g transform="translate(72 638)"><rect width="1056" height="82" rx="7" fill="#e5f2f2"/><text x="22" y="28" class="stephead">What is robust?</text><text x="22" y="51" class="body">The primary trunk is scale-stable across this diagnostic ladder. The number of branches, splits, and merges is not.</text><text x="22" y="70" class="body">Small does not mean false; it means the topology needs an explicit minimum-scale convention.</text></g>
<text x="72" y="756" class="small">Source: OSW-D7 from NOAA CRW Marine Heatwave Watch v1.0.1 · native 0.05° grid · daily component area.</text>
<text x="72" y="778" class="small">Illustrative thresholds · no primary-trunk override · representation sensitivity, not evidence that removed components are erroneous or physically unimportant.</text>
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
