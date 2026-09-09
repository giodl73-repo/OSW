"""Render the OSW-D6 split/merge branch-policy bakeoff."""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "research" / "osw-d6-noaa-crw-mhw-branch-sensitivity-2026.json"
DEFAULT_OUTPUT = ROOT / "figures" / "osw-d6-noaa-crw-mhw-branch-sensitivity-2026.svg"


def selected_on(result, candidate_date):
    return next(item["selected"] for item in result["transitions"] if item["candidate_date"] == candidate_date)


def build(input_path=DEFAULT_INPUT, output_path=DEFAULT_OUTPUT):
    payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
    results = payload["results"]
    baseline = results[0]
    fraction = results[2]
    if [item["tracked_window"]["day_count"] for item in results] != [21, 21, 14, 21]:
        raise ValueError("view expects the governed D6 policy outcomes")
    july_main, july_splinter = selected_on(baseline, "2026-07-30"), selected_on(fraction, "2026-07-30")
    august_main, august_splinter = selected_on(baseline, "2026-08-03"), selected_on(fraction, "2026-08-03")
    start, end = date.fromisoformat("2026-07-20"), date.fromisoformat("2026-08-11")
    timeline_x, timeline_w = 330, 760

    def tx(value):
        return timeline_x + (date.fromisoformat(value) - start).days / (end - start).days * timeline_w

    row_labels = ["LARGEST SHARED FOOTPRINT", "BEST IoU", "HIGHEST INHERITED FRACTION", "LARGEST OVERLAPPING COMPONENT"]
    rows = []
    for index, (label, result) in enumerate(zip(row_labels, results)):
        y = 251 + index * 66
        x1 = tx(result["tracked_window"]["start"])
        x2 = tx(result["tracked_window"]["end"]) + timeline_w / (end - start).days
        color = "#b66a3c" if index == 2 else "#267b87"
        rows.append(
            f'<text x="72" y="{y+18}" class="rowlabel">{label}</text>'
            f'<rect x="{timeline_x}" y="{y}" width="{timeline_w}" height="30" rx="4" fill="#e6eeee"/>'
            f'<rect x="{x1:.1f}" y="{y}" width="{x2-x1:.1f}" height="30" rx="4" fill="{color}"/>'
            f'<text x="{x2-10:.1f}" y="{y+20}" text-anchor="end" class="bartext">{result["tracked_window"]["day_count"]} days</text>'
        )
    fork_marks = "".join(
        f'<path d="M{x:.1f} 374v30" stroke="#fff" stroke-width="2"/><circle cx="{x:.1f}" cy="389" r="5" fill="#fff" stroke="#7d3f26" stroke-width="2"/>'
        for x in (tx("2026-07-30"), tx("2026-08-03"))
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800" role="img">
<title>OSW-D6 marine heatwave branch-policy sensitivity</title>
<desc>Three branch rules select the same 21 daily components. Maximizing only the fraction of each candidate inherited selects a 12-cell splinter on July 30 and a one-cell splinter on August 3, ending after 14 days.</desc>
<style>.eyebrow{{font:700 14px Inter,"Segoe UI",sans-serif;letter-spacing:2.2px;fill:#327487}}.title{{font:700 40px Georgia,serif;fill:#112f3b}}.lead{{font:400 18px Inter,"Segoe UI",sans-serif;fill:#49636c}}.section{{font:700 12px Inter,"Segoe UI",sans-serif;letter-spacing:1.4px;fill:#2e7182}}.rowlabel{{font:700 11px Inter,"Segoe UI",sans-serif;letter-spacing:.55px;fill:#294b56}}.bartext{{font:700 12px Inter,"Segoe UI",sans-serif;fill:#fff}}.date{{font:500 11px Inter,"Segoe UI",sans-serif;fill:#667b82}}.cardtitle{{font:700 15px Inter,"Segoe UI",sans-serif;fill:#173d49}}.metric{{font:700 27px Georgia,serif;fill:#153946}}.body{{font:400 13px Inter,"Segoe UI",sans-serif;fill:#506a73}}.small{{font:500 11px Inter,"Segoe UI",sans-serif;fill:#657b82}}</style>
<rect width="1200" height="800" fill="#f8fbfa"/><path d="M0 0H1200V12H0Z" fill="#1f7185"/>
<text x="72" y="61" class="eyebrow">OSW · DETECTED OBJECT 06 · BRANCH IDENTITY</text>
<text x="72" y="113" class="title">A fraction-only rule follows the splinter</text>
<text x="72" y="149" class="lead">Matching lifetimes are not enough; the score’s denominator decides which child inherits the name.</text>
<g transform="translate(72 179)"><rect width="1056" height="43" rx="7" fill="#e2f1f1"/><text x="528" y="27" text-anchor="middle" class="section">3 RULES AGREE CELL FOR CELL FOR 21 DAYS · 1 RULE SELECTS TWO TINY FULLY INHERITED FRAGMENTS</text></g>
{''.join(rows)}{fork_marks}
<text x="{tx('2026-07-21'):.1f}" y="527" text-anchor="middle" class="date">21 JUL</text><text x="{tx('2026-07-30'):.1f}" y="527" text-anchor="middle" class="date">30 JUL</text><text x="{tx('2026-08-03'):.1f}" y="527" text-anchor="middle" class="date">3 AUG</text><text x="{tx('2026-08-10'):.1f}" y="527" text-anchor="middle" class="date">10 AUG</text>
<path d="M72 550H1128" stroke="#c6d6d9"/><text x="72" y="584" class="section">WHY THE FRACTION SCORE BREAKS</text>
<g transform="translate(72 608)"><rect width="326" height="112" rx="7" fill="#e5f2f2"/><text x="18" y="28" class="cardtitle">30 July fork</text><text x="18" y="62" class="metric">{july_main['pixel_count']:,} vs {july_splinter['pixel_count']}</text><text x="18" y="84" class="body">main component vs selected splinter</text><text x="18" y="103" class="small">splinter inherited: {july_splinter['candidate_inherited_fraction']*100:.0f}% · main: {july_main['candidate_inherited_fraction']*100:.0f}%</text></g>
<g transform="translate(437 608)"><rect width="326" height="112" rx="7" fill="#f7eadc"/><text x="18" y="28" class="cardtitle">3 August fork</text><text x="18" y="62" class="metric">{august_main['pixel_count']:,} vs {august_splinter['pixel_count']}</text><text x="18" y="84" class="body">main component vs selected splinter</text><text x="18" y="103" class="small">1 / 1 cell inherited → 100% → lineage stops 4 Aug</text></g>
<g transform="translate(802 608)"><rect width="326" height="112" rx="7" fill="#edf2f2"/><text x="18" y="28" class="cardtitle">The denominator trap</text><text x="18" y="55" class="body">shared cells / candidate size rewards</text><text x="18" y="77" class="body">small fragments nested inside yesterday.</text><text x="18" y="99" class="body">Add scale or two-sided overlap.</text></g>
<text x="72" y="755" class="small">Source: NOAA CRW Marine Heatwave Watch v1.0.1 daily category · native 0.05° grid · 20 Jul–20 Aug 2026.</text>
<text x="72" y="777" class="small">Four-neighbor · any exact overlap · illustrative branch rules · threshold-state identity, not water-parcel or mechanism continuity.</text>
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
