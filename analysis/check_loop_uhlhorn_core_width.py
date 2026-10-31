"""Keep a prestorm geostrophic core distinct from loop size and seasonal widths."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = 'research/loop-uhlhorn-2008-core-width-scope-audit.json'
PIN = 'd96a85769d521a858d6975a66fdfed10be47989daa1010d805e61146581d8ae9'
ID = 'loop-uhlhorn-2008-prelili-geostrophic-core'


def load():
    raw = (ROOT / AUDIT).read_bytes()
    if hashlib.sha256(raw).hexdigest() != PIN:
        raise ValueError('Changed frozen Loop Current core source definitions')
    return json.loads(raw)


def record():
    row = copy.deepcopy(load()['measurement'])
    row['original_regional_context'].update(audit_file=AUDIT, audit_sha256=PIN)
    return row


def validate_row(row, audit=None):
    expected = load()
    if (audit is not None and audit != expected) or row != record():
        raise ValueError('Loop core differs from original threshold, dates or support')
    for kind in ['acquisition', 'protocol', 'integrity_contract']:
        raw = (ROOT / expected[kind + '_file']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected[kind + '_sha256']:
            raise ValueError('Changed Loop core provenance')
    from uhlhorn_thesis_source import resolve_source
    resolve_source()


def validate_inventory(document):
    rows = [r for r in document['measurements'] if r.get('id') == ID or r.get('current_id') == 'loop']
    if len(rows) != 1:
        raise ValueError('Missing, duplicated or reassigned Loop core width')
    validate_row(rows[0])


def svg():
    load()
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 500" role="img" aria-labelledby="title desc">
<title id="title">Loop Current: pre-Lili geostrophic core width</title>
<desc id="desc">Author-reported approximate100 km cross-stream span for geostrophic speed at least0.4 m/s, prestorm fields19-23September2002. Zero-reference level at750 m or local bottom. This is not a current footprint, uniform depth layer, seasonal range or width-error interval. No velocity curve reconstructed.</desc>
<rect width="960" height="500" fill="#f7faf9"/>
<g fill="#123541" font-family="sans-serif" font-size="18">
<text x="32" y="42" font-size="25">Loop Current · published geostrophic core span</text>
<text x="32" y="78">19–23 September 2002 · southeastern Gulf of Mexico</text>
<text x="32" y="111">Fixed speed cutoff: at least 0.4 m/s · author-labeled cross-stream section</text>
<line x1="90" x2="790" y1="220" y2="220" stroke="#7a9299"/>
<path d="M90 210v20 M440 210v20 M790 210v20" stroke="#7a9299"/>
<text x="90" y="253" text-anchor="middle">0</text><text x="440" y="253" text-anchor="middle">50</text>
<text x="790" y="253" text-anchor="middle">100 km</text>
<line x1="90" x2="790" y1="178" y2="178" stroke="#08798b" stroke-width="7"/>
<path d="M90 165v26 M790 165v26" stroke="#08798b" stroke-width="3"/>
<text x="440" y="156" text-anchor="middle">About 100 km · reported span, no edge locations inferred</text>
<text x="32" y="303">Thermal-wind density analysis · zero reference at 750 m or local bottom.</text>
<text x="32" y="337">Upper 300 m core context does not define a uniform width layer.</text>
<text x="32" y="371">Source e-folding wording is not adopted as a relative boundary rule.</text>
<text x="32" y="405">No width error, seasonal interval, annual extrema or whole-current width.</text>
<text x="32" y="451" font-size="15">Source: Uhlhorn (2008), University of Miami dissertation, §2.5.2, p36; Figure2.28, p38.</text>
<text x="32" y="477" font-size="15">Independent OSW graphic; source curves and geographic edges not reproduced.</text>
</g></svg>'''


if __name__ == '__main__':
    validate_row(record())
    (ROOT / 'figures/loop-uhlhorn-2008-core-width.svg').write_bytes(svg().encode())
    print('Verified original Loop Current100 km core definition and drew independent graphic')
