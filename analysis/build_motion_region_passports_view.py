"""Render 22 frozen-region motion fingerprints without a composite score."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


FAMILY_COLORS = {"POLAR": "#8cc4ff", "PACIFIC": "#62d7ce", "ATLANTIC": "#e76f9f", "INDIAN": "#f0cf70", "SOUTHERN": "#a7d77b"}


def bar(x: float, y: float, width: float, value: float | None, maximum: float, color: str) -> str:
    if value is None:
        return f'<text x="{x + width / 2}" y="{y + 4}" class="missing" text-anchor="middle">—</text>'
    bounded = max(0.0, min(maximum, value))
    return f'<rect x="{x}" y="{y - 5}" width="{width}" height="8" rx="4" fill="#17343a"/><rect x="{x}" y="{y - 5}" width="{width * bounded / maximum:.1f}" height="8" rx="4" fill="{color}"/>'


def diverging_bar(x: float, y: float, width: float, value: float | None, color_negative: str, color_positive: str) -> str:
    if value is None:
        return f'<text x="{x + width / 2}" y="{y + 4}" class="missing" text-anchor="middle">—</text>'
    center = x + width / 2
    extent = min(1.0, abs(value)) * width / 2
    start = center - extent if value < 0 else center
    color = color_negative if value < 0 else color_positive
    return f'<path d="M{center} {y - 7}V{y + 5}" stroke="#49666b" stroke-width=".6"/><rect x="{start:.1f}" y="{y - 4}" width="{extent:.1f}" height="6" rx="3" fill="{color}"/>'


def render(payload: dict) -> str:
    rows = []
    y = 190.0
    previous_family = None
    for item in payload["regions"]:
        family = item["family"]
        if family != previous_family:
            if previous_family is not None:
                y += 8
            rows.append(f'<text x="38" y="{y + 4}" fill="{FAMILY_COLORS[family]}" font-size="8.5" font-weight="950" letter-spacing="1">{family}</text><path d="M38 {y + 11}H1362" stroke="{FAMILY_COLORS[family]}" stroke-width=".7" opacity=".35"/>')
            y += 20
            previous_family = family
        alignment = item["mean_cross_season_alignment"]
        internal = item["mean_internal_direction_similarity"]
        turn = item["mean_maximum_seasonal_turn_degrees"]
        margin = item["screened_weighted_orientation_margin"]
        maximum_cut = item["maximum_screened_cut_through_score"]
        low_fraction = item["low_similarity_internal_fraction"]
        row_fill = "#0c252b" if int(y / 29) % 2 else "#0a2026"
        margin_markup = diverging_bar(1043, y, 112, margin, "#62d7ce", "#f05d67")
        margin_label = f"{margin:+.2f}" if margin is not None else "—"
        cut_markup = bar(1215, y, 82, maximum_cut, 1, "#f05d67")
        cut_label = f"{maximum_cut:.2f}" if maximum_cut is not None else "—"
        rows.append(
            f'<rect x="38" y="{y - 15}" width="1324" height="27" rx="5" fill="{row_fill}"/>'
            f'<text x="54" y="{y + 3}" class="code">{item["region_code"]}</text><text x="103" y="{y + 3}" class="name">{html.escape(item["region"])}</text>'
            f'<text x="445" y="{y + 3}" class="number">{item["supported_cells"]}</text>'
            f'{bar(490, y, 112, alignment, 1, "#62d7ce")}<text x="610" y="{y + 3}" class="small">{alignment:.2f}</text>'
            f'{diverging_bar(672, y, 136, internal, "#e76f9f", "#8cc4ff")}<text x="816" y="{y + 3}" class="small">{internal:+.2f}</text>'
            f'{bar(878, y, 102, turn, 180, "#f49a62")}<text x="988" y="{y + 3}" class="small">{turn:.0f}°</text>'
            f'{margin_markup}<text x="1163" y="{y + 3}" class="small">{margin_label}</text>'
            f'{cut_markup}<text x="1305" y="{y + 3}" class="small">{cut_label}</text>'
        )
        rows.append(f'<text x="1350" y="{y + 3}" class="number">{item["screened_boundaries"]}</text><title>{item["region_code"]}: low-similarity internal fraction {low_fraction:.2f}; {item["provisional_boundaries"]} provisional borders</title>')
        y += 29
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1000" viewBox="0 0 1400 1000" role="img" aria-labelledby="title desc" data-motion-level="region-passports" data-zoning="frozen-comparison"><title id="title">Twenty-two frozen regions, five motion questions</title><desc id="desc">A matrix compares cross-season alignment, internal directional similarity, maximum seasonal turn, screened border orientation, and maximum screened cut-through for every frozen OSW region. Missing screened border evidence is shown as a dash. No composite rank or region revision is produced.</desc><metadata>Source artifact SHA-256 {payload['source_artifact_sha256']}. {html.escape(payload['boundary'])}</metadata><defs><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.code{{fill:#eef9f7;font-size:11px;font-weight:950}}.name{{fill:#b5c9c7;font-size:10px}}.number{{fill:#eef9f7;font:900 10px ui-monospace,Consolas,monospace;text-anchor:end}}.small{{fill:#789596;font:800 8px ui-monospace,Consolas,monospace}}.missing{{fill:#506e72;font:900 12px ui-monospace,Consolas,monospace}}</style></defs><rect width="1400" height="1000" fill="#06171c"/><text x="38" y="42" fill="#62d7ce" font-size="14" font-weight="900" letter-spacing="2.5">OSW / MOTION STUDY  ·  M1 REGION PASSPORTS</text><text x="38" y="84" fill="#eef9f7" font-size="32" font-weight="950">22 REGIONS / FIVE MOTION QUESTIONS</text><text x="38" y="113" fill="#9db3b2" font-size="11.5">frozen geography · comparable diagnostics · missing evidence stays missing</text><rect x="1115" y="34" width="247" height="30" rx="15" fill="#102a30" stroke="#f0cf70" stroke-opacity=".7"/><text x="1238.5" y="54" text-anchor="middle" fill="#f0cf70" font-size="10" font-weight="950" letter-spacing="1.3">NO COMPOSITE SCORE · NO REVISION</text><g aria-label="Column headings"><text x="54" y="158" class="small">REGION</text><text x="445" y="158" class="small" text-anchor="end">CELLS</text><text x="490" y="158" class="small">SEASON ALIGN · 0–1</text><text x="672" y="158" class="small">INTERNAL SIM · −1…+1</text><text x="878" y="158" class="small">MAX TURN · 0–180°</text><text x="1043" y="158" class="small">BORDER MARGIN · ALONG / ACROSS</text><text x="1215" y="158" class="small">MAX CUT · 0–1</text><text x="1350" y="158" class="small" text-anchor="end">S</text></g>{''.join(rows)}<g aria-label="Reading guide"><path d="M38 929H1362" stroke="#345157"/><text x="38" y="954" fill="#62d7ce" font-size="9.5" font-weight="950">READING</text><text x="102" y="954" fill="#afc3c1" font-size="9.5">S = screened incident borders · border margin: cyan leans along, coral leans across · dash = no screened border evidence, not zero</text><text x="38" y="980" fill="#617d80" font-size="8.5">ONE HISTORICAL YEAR · SURFACE DIRECTION ONLY · COLUMNS DELIBERATELY REMAIN SEPARATE · NOT A REGION RANKING, CLIMATOLOGY, OR HEAT-TRANSPORT RESULT</text></g></svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(args.data.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(payload), encoding="utf-8", newline="\n")
    print(args.output)


if __name__ == "__main__":
    main()
