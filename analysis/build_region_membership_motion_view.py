"""Render province-scale motion disagreement inside the frozen 22 regions."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


FAMILY_COLORS = {"POLAR": "#8cc4ff", "PACIFIC": "#62d7ce", "ATLANTIC": "#e76f9f", "INDIAN": "#f0cf70", "SOUTHERN": "#a7d77b"}


def display_code(code: str) -> str:
    return code.replace(" ", "·")


def alignment_color(value: float) -> str:
    if value >= .8:
        return "#62d7ce"
    if value >= .65:
        return "#8cc4ff"
    if value >= .5:
        return "#f0cf70"
    return "#f49a62"


def diverging_bar(x: float, y: float, width: float, value: float | None) -> str:
    if value is None:
        return f'<text x="{x + width / 2}" y="{y + 4}" class="missing" text-anchor="middle">single member</text>'
    center = x + width / 2
    extent = min(1.0, abs(value)) * width / 2
    start = center - extent if value < 0 else center
    color = "#e76f9f" if value < 0 else "#62d7ce"
    return f'<path d="M{center} {y - 8}V{y + 6}" stroke="#49666b" stroke-width=".7"/><rect x="{start:.1f}" y="{y - 4}" width="{extent:.1f}" height="7" rx="3.5" fill="{color}"/>'


def render(membership: dict, passports: dict) -> str:
    state_rows = {item["state_code"]: item for item in membership["states"]}
    passport_rows = {item["region_code"]: item for item in passports["regions"]}
    rows = []
    y = 190.0
    previous_family = None
    for item in membership["regions"]:
        passport = passport_rows[item["region_code"]]
        family = passport["family"]
        if family != previous_family:
            if previous_family is not None:
                y += 8
            rows.append(f'<text x="38" y="{y + 4}" fill="{FAMILY_COLORS[family]}" font-size="8.5" font-weight="950" letter-spacing="1">{family}</text><path d="M38 {y + 11}H1362" stroke="{FAMILY_COLORS[family]}" stroke-width=".7" opacity=".35"/>')
            y += 20
            previous_family = family
        row_fill = "#0c252b" if int(y / 29) % 2 else "#0a2026"
        badges = []
        for index, code in enumerate(item["member_states"]):
            state = state_rows[code]
            x = 356 + index * 49
            color = alignment_color(state["cross_season_alignment"])
            badges.append(f'<rect x="{x}" y="{y - 12}" width="43" height="18" rx="5" fill="{color}" opacity=".9"/><text x="{x + 21.5}" y="{y + 1}" text-anchor="middle" fill="#06171c" font-size="7.5" font-weight="950">{html.escape(display_code(code))}</text><title>{html.escape(state["state"])}: {state["supported_cells"]} cells, alignment {state["cross_season_alignment"]:.2f}, maximum turn {state["maximum_seasonal_turn_degrees"]:.0f}°</title>')
        mean_similarity = item["mean_between_state_direction_similarity"]
        minimum_similarity = item["minimum_between_state_direction_similarity"]
        worst_pair = " ↔ ".join(display_code(code) for code in item["minimum_similarity_pair"]) if item["minimum_similarity_pair"] else "—"
        internal = passport["mean_internal_direction_similarity"]
        mean_markup = diverging_bar(682, y, 132, mean_similarity)
        mean_label = f"{mean_similarity:+.2f}" if mean_similarity is not None else ""
        minimum_markup = diverging_bar(875, y, 132, minimum_similarity)
        minimum_label = f"{minimum_similarity:+.2f}" if minimum_similarity is not None else ""
        rows.append(
            f'<rect x="38" y="{y - 15}" width="1324" height="27" rx="5" fill="{row_fill}"/><text x="54" y="{y + 3}" class="code">{item["region_code"]}</text><text x="103" y="{y + 3}" class="name">{html.escape(item["region"])}</text>{"".join(badges)}'
            f'{mean_markup}<text x="822" y="{y + 3}" class="small">{mean_label}</text>'
            f'{minimum_markup}<text x="1015" y="{y + 3}" class="small">{minimum_label}</text><text x="1062" y="{y + 3}" class="pair">{html.escape(worst_pair)}</text>'
        )
        rows.append(f'{diverging_bar(1250, y, 92, internal)}<text x="1350" y="{y + 3}" class="small">{internal:+.2f}</text>')
        y += 29
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1000" viewBox="0 0 1400 1000" role="img" aria-labelledby="title desc" data-motion-level="region-membership-audit" data-zoning="frozen-comparison"><title id="title">What disagrees inside the frozen 22 regions?</title><desc id="desc">A 22-row matrix shows the 56 province members, province seasonal alignment, mean and minimum between-province directional similarity, worst province pair, and internal cell-neighbor similarity. No split or membership change is proposed.</desc><metadata>Source artifact SHA-256 {membership['source_artifact_sha256']}. {html.escape(membership['boundary'])}</metadata><defs><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.code{{fill:#eef9f7;font-size:11px;font-weight:950}}.name{{fill:#b5c9c7;font-size:10px}}.small{{fill:#789596;font:800 8px ui-monospace,Consolas,monospace}}.pair{{fill:#a9bfbe;font:850 8.5px ui-monospace,Consolas,monospace}}.missing{{fill:#506e72;font:800 7.5px ui-monospace,Consolas,monospace}}</style></defs><rect width="1400" height="1000" fill="#06171c"/><text x="38" y="42" fill="#62d7ce" font-size="14" font-weight="900" letter-spacing="2.5">OSW / MOTION STUDY  ·  M1 MEMBERSHIP AUDIT</text><text x="38" y="84" fill="#eef9f7" font-size="32" font-weight="950">WHAT DISAGREES INSIDE THE 22?</text><text x="38" y="113" fill="#9db3b2" font-size="11.5">56 province signatures · frozen membership · broad all-pairs comparison</text><rect x="1115" y="34" width="247" height="30" rx="15" fill="#102a30" stroke="#f0cf70" stroke-opacity=".7"/><text x="1238.5" y="54" text-anchor="middle" fill="#f0cf70" font-size="10" font-weight="950" letter-spacing="1.3">DIAGNOSIS · NOT A SPLIT ORDER</text><g><text x="54" y="158" class="small">REGION</text><text x="356" y="158" class="small">MEMBER PROVINCES · FILL = SEASON ALIGNMENT</text><text x="682" y="158" class="small">MEAN MEMBER SIM · −1…+1</text><text x="875" y="158" class="small">WORST SIM · −1…+1</text><text x="1062" y="158" class="small">WORST PAIR</text><text x="1250" y="158" class="small">CELL SIM</text></g>{''.join(rows)}<g><path d="M38 929H1362" stroke="#345157"/><text x="38" y="954" fill="#62d7ce" font-size="9.5" font-weight="950">READING</text><text x="102" y="954" fill="#afc3c1" font-size="9.5">cyan bars agree · magenta bars oppose · province fills encode cross-season alignment · singleton regions have no member-pair test</text><text x="38" y="980" fill="#617d80" font-size="8.5">UNWEIGHTED COARSE-CELL PROVINCE MEANS · ALL MEMBER PAIRS, NOT ONLY ADJACENCIES · NOT AREA-WEIGHTED FLOW, BOUNDARY EXCHANGE, HEAT TRANSPORT, OR A SPLIT DECISION</text></g></svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--membership", type=Path, required=True)
    parser.add_argument("--passports", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(json.loads(args.membership.read_text(encoding="utf-8")), json.loads(args.passports.read_text(encoding="utf-8"))), encoding="utf-8", newline="\n")
    print(args.output)


if __name__ == "__main__":
    main()
