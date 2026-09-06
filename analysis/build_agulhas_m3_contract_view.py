"""Render the M2-to-M3 Agulhas leakage experiment contract."""

from __future__ import annotations

import argparse
import html
import json
import pathlib


WIDTH, HEIGHT = 1400, 960


def gap_row(item: dict, y: int) -> str:
    verdict = "GEOMETRY ACQUIRED" if item["verdict"] == "resolved_for_replication" else "NOT PROMOTED"
    verdict_class = "resolved" if item["verdict"] == "resolved_for_replication" else "fail"
    return f'''<g transform="translate(50 {y})"><rect width="1300" height="82" rx="12" class="row"/><text x="20" y="25" class="dimension">{item['dimension'].upper()}</text><text x="205" y="25" class="m2">{html.escape(item['m2'])}</text><path d="M632 18h35" class="arrow"/><text x="700" y="25" class="m3">{html.escape(item['m3'])}</text><text x="20" y="56" class="{verdict_class}">{verdict}</text><text x="205" y="56" class="small">CURRENT M2 EVIDENCE</text><text x="700" y="56" class="small">REQUIRED M3 CONTRACT</text></g>'''


def build(payload: dict) -> str:
    rows = "".join(gap_row(item, 154 + index * 94) for index, item in enumerate(payload["m2_gap_audit"]))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc" data-motion-level="m3-agulhas-contract"><title id="title">Agulhas M3 experiment contract</title><desc id="desc">Five failed promotion checks and one acquired geometry separate the current surface-pathway pilot from a full-depth, transport-weighted, four-year Agulhas leakage experiment.</desc><metadata>{html.escape(payload['boundary'])} Schmidt et al. 2021 doi:10.5194/os-17-1067-2021. Schwarzkopf et al. 2022 doi:10.1038/s43247-022-00643-y. Daher et al. 2020 doi:10.1029/2019JC015753.</metadata><defs><marker id="arrowhead" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L8 4L0 8Z" fill="#58777b"/></marker><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.row{{fill:#0d272e;stroke:#38585e}}.dimension{{fill:#eef9f7;font-size:11px;font-weight:950;letter-spacing:1px}}.m2{{fill:#d995a3;font-size:11px;font-weight:750}}.m3{{fill:#79ded6;font-size:11px;font-weight:800}}.small{{fill:#58777b;font-size:7px;font-weight:900;letter-spacing:1px}}.fail{{fill:#e26f86;font-size:7px;font-weight:950;letter-spacing:1px}}.resolved{{fill:#54d8d0;font-size:7px;font-weight:950;letter-spacing:1px}}.arrow{{stroke:#58777b;stroke-width:1.2;marker-end:url(#arrowhead)}}.note{{fill:#a7bdbc;font-size:10px}}.fine{{fill:#587477;font-size:8px}}</style></defs><rect width="1400" height="960" fill="#06171c"/><text x="50" y="42" fill="#54d8d0" font-size="14" font-weight="900" letter-spacing="2.4">OSW / AGULHAS · M3 EXPERIMENT CONTRACT</text><text x="50" y="86" fill="#eef9f7" font-size="35" font-weight="950">SURFACE PATHS ARE NOT YET LEAKAGE TRANSPORT.</text><text x="50" y="117" fill="#9db3b2" font-size="12">Six promotion checks derived from published Lagrangian experiment design</text><rect x="1058" y="37" width="297" height="30" rx="15" fill="#102a30" stroke="#e26f86"/><text x="1206.5" y="57" fill="#e26f86" text-anchor="middle" font-size="9.5" font-weight="950" letter-spacing="1">REFERENCE GEOMETRY ACQUIRED · RAW 3-D OPEN</text><g transform="translate(255 139)"><text class="small">M2</text><text x="445" class="small">M3</text></g>{rows}<rect x="50" y="730" width="1300" height="165" rx="14" fill="#0b242a" stroke="#38585e"/><text x="72" y="758" fill="#eef9f7" font-size="14" font-weight="950">THE TARGET EXPERIMENT</text><text x="72" y="786" fill="#54d8d0" font-size="18" font-weight="950">32°S FULL WIDTH + DEPTH</text><path d="M344 780h82" class="arrow"/><text x="458" y="786" fill="#54d8d0" font-size="18" font-weight="950">5-DAY RELEASES × 1 YEAR</text><path d="M748 780h82" class="arrow"/><text x="862" y="786" fill="#54d8d0" font-size="18" font-weight="950">3-D TRACKS × 4 YEARS</text><text x="72" y="821" class="note">Each particle carries native-cell volume transport. Every GoodHope crossing retains time and direction.</text><text x="72" y="845" fill="#ffad55" font-size="12" font-weight="900">ALL CROSSINGS</text><text x="200" y="845" class="note">exchange and thermohaline transformation</text><text x="620" y="845" fill="#d78cff" font-size="12" font-weight="900">ODD CROSSINGS</text><text x="755" y="845" class="note">water remaining in the South Atlantic for overturning questions</text><text x="72" y="874" class="fine">PUBLISHED 55-RECORD GOODHOPE COMPOSITE ACQUIRED · NEW RUN MUST MAP IT TO THE TARGET GRID · 32°S / ACT RELEASE SENSITIVITY REQUIRED · HEAT REMAINS A SEPARATE CONVENTION</text><text x="50" y="928" class="fine">CONTRACT + ATTRIBUTED REPLICATION · NO RAW 3-D VELOCITY DOWNLOADED · NO LEAKAGE, VOLUME, HEAT, OR AMOC ESTIMATE · SOURCES AND ACCEPTANCE TESTS IN THE JSON RECEIPT</text></svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m3-agulhas-experiment-contract.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m3-agulhas-experiment-contract.svg"))
    args = parser.parse_args()
    svg = build(json.loads(args.input.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg, encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
