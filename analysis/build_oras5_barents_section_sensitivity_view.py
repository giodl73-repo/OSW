"""Render endpoint-versus-cost sensitivity for the two Barents paths."""

from __future__ import annotations

import argparse
import json
import pathlib


WIDTH = 1400
HEIGHT = 900
ROWS = ("baseline", "west", "east", "shorter", "longer", "clockwise", "counterclockwise", "northwest_stop", "southeast_start")
LABELS = {"baseline": "BASELINE", "west": "BOTH WEST", "east": "BOTH EAST", "shorter": "SHORTER", "longer": "LONGER", "clockwise": "CLOCKWISE", "counterclockwise": "COUNTERCLOCKWISE", "northwest_stop": "NW STOP", "southeast_start": "SE START"}
SCALES = (10.0, 20.0, 40.0)


def face_key(face):
    return face["face"], face["y"], face["x"]


def path_id_map(cases):
    signatures = {}
    result = {}
    for case in cases:
        signature = tuple(face_key(face) for face in case["faces"])
        if signature not in signatures:
            signatures[signature] = len(signatures) + 1
        result[(case["endpoint_case"], case["corridor_scale_km"])] = (signatures[signature], case["face_count"])
    return result


def matrix(cases, x, color):
    ids = path_id_map(cases)
    chunks = []
    for row, name in enumerate(ROWS):
        y = 241 + row * 43
        chunks.append(f'<text x="{x}" y="{y + 20}" class="rowlabel">{LABELS[name]}</text>')
        for column, scale in enumerate(SCALES):
            path_id, count = ids[(name, scale)]
            cx = x + 158 + column * 112
            chunks.append(f'<rect x="{cx}" y="{y}" width="96" height="32" rx="6" fill="{color}" opacity=".13" stroke="{color}"/><text x="{cx + 48}" y="{y + 15}" text-anchor="middle" fill="{color}" font-size="10" font-weight="950">PATH {path_id:02d}</text><text x="{cx + 48}" y="{y + 27}" text-anchor="middle" class="tiny">{count} faces</text>')
    return "".join(chunks)


def build(payload):
    proxy = payload["observational_proxy"]; closure = payload["model_closure"]
    ps = proxy["summary"]; cs = closure["summary"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc" data-motion-level="m3-barents-section-sensitivity"><title id="title">Barents anchors move the line more than the path-cost rule</title><desc id="desc">Fifty-four native geometry cases show scale-invariant paths within each endpoint case but nine proxy paths and six model-closure paths across endpoint perturbations.</desc><metadata>{payload['boundary']}</metadata><defs><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.panel{{fill:#092229;stroke:#36575d}}.body{{fill:#aac0bf;font-size:13px}}.fine{{fill:#78979a;font-size:10px}}.tiny{{fill:#8ca7a7;font-size:8px}}.rowlabel{{fill:#d8e6e2;font-size:9px;font-weight:900;letter-spacing:.5px}}.metric{{fill:#eef8f5;font-size:25px;font-weight:950}}.head{{fill:#eef8f5;font-size:13px;font-weight:950;letter-spacing:1px}}</style></defs><rect width="1400" height="900" fill="#06171c"/><text x="52" y="42" fill="#55ded3" font-size="12" font-weight="950" letter-spacing="2">OSW / BARENTS · CONSTRUCTION SENSITIVITY</text><text x="52" y="86" fill="#eef8f5" font-size="35" font-weight="950">THE COST RULE HOLDS. THE ANCHORS MOVE THE LINE.</text><text x="52" y="117" class="body">Nine endpoint intents × three corridor penalties × two section meanings. These are method choices—not ocean uncertainty.</text>
<rect x="52" y="149" width="620" height="535" rx="14" class="panel"/><rect x="728" y="149" width="620" height="535" rx="14" class="panel"/><text x="72" y="178" class="head">OBSERVATIONAL PROXY</text><text x="748" y="178" class="head">MODEL CLOSURE</text><text x="230" y="211" class="fine">10 KM</text><text x="342" y="211" class="fine">20 KM</text><text x="454" y="211" class="fine">40 KM</text><text x="906" y="211" class="fine">10 KM</text><text x="1018" y="211" class="fine">20 KM</text><text x="1130" y="211" class="fine">40 KM</text>{matrix(proxy['cases'],72,'#55ded3')}{matrix(closure['cases'],748,'#ff9a52')}
<g transform="translate(52 718)"><text class="metric">{ps['unique_path_count']} PATHS · {ps['face_count_range'][0]}–{ps['face_count_range'][1]} FACES</text><text y="28" class="body">maximum baseline face-set replacement: {ps['maximum_face_set_jaccard_distance_from_baseline'] * 100:.0f}%</text><text y="50" class="fine">{ps['unique_start_nodes']} START NODES · {ps['unique_stop_nodes']} STOP NODES · ALL 9 ENDPOINT CASES SCALE-INVARIANT</text></g><g transform="translate(728 718)"><text class="metric">{cs['unique_path_count']} PATHS · {cs['face_count_range'][0]}–{cs['face_count_range'][1]} FACES</text><text y="28" class="body">maximum baseline face-set replacement: {cs['maximum_face_set_jaccard_distance_from_baseline'] * 100:.0f}%</text><text y="50" class="fine">{cs['unique_start_nodes']} START NODES · {cs['unique_stop_nodes']} STOP NODE · ALL 9 ENDPOINT CASES SCALE-INVARIANT</text></g>
<rect x="52" y="802" width="1296" height="48" rx="10" fill="#102a30" stroke="#36575d"/><text x="72" y="832" fill="#ffbd71" font-size="14" font-weight="950">VERDICT: PROMOTE ENDPOINT PLACEMENT TO A REQUIRED SENSITIVITY; RETAIN 20 KM ONLY AS A REPRODUCIBLE PATH-COST DEFAULT.</text><text x="52" y="881" class="fine">54 SURFACE-GEOMETRY CASES · ALL TOPOLOGY CHECKS PASS · NO VELOCITY, TRANSPORT, HEAT, OBSERVATIONAL ERROR, OR PHYSICAL UNCERTAINTY</text></svg>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-barents-section-sensitivity.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m3-oras5-barents-section-sensitivity.svg"))
    args = parser.parse_args(); payload = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(build(payload), encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
