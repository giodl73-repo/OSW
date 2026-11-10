"""A provider's regional range is not a seasonal series or velocity-edge width."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = 'research/balearic-socib-2023-regional-width-scope-audit.json'
PIN = 'c4eb5039c0a77ece8e775c50637441d0e0816e2cc401363f85f65effc0f1e203'
ID = 'balearic-socib-2023-regional-width'


def load():
    raw = (ROOT / AUDIT).read_bytes()
    if hashlib.sha256(raw).hexdigest() != PIN:
        raise ValueError('Changed reviewed SOCIB Balearic scope audit')
    return json.loads(raw)


def record():
    row = copy.deepcopy(load()['measurement'])
    row['original_regional_context'].update(audit_file=AUDIT, audit_sha256=PIN)
    return row


def validate_row(row, audit=None):
    expected = load()
    if audit is not None and audit != expected:
        raise ValueError('Changed SOCIB provider range or source supports')
    if row != record():
        raise ValueError('SOCIB regional width differs from reviewed range or scope')
    for kind in ['source_document', 'acquisition', 'protocol']:
        raw = (ROOT / expected[kind + '_file']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected[kind + '_sha256']:
            raise ValueError('Changed SOCIB original or provenance')


def validate_inventory(document):
    rows = [r for r in document['measurements'] if r.get('id') == ID or r.get('current_id') == 'balearic']
    if len(rows) != 1:
        raise ValueError('Missing or duplicated reviewed SOCIB Balearic width')
    validate_row(rows[0])


def svg():
    load()
    ticks = ''.join(f'<text x="{60 + n * 16}" y="210" text-anchor="middle">{n}</text>' for n in [0,10,20,30,40])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 390" role="img" aria-labelledby="title desc">
<title id="title">Balearic Current: SOCIB regional width range</title>
<desc id="desc">Provider-reported 20 to 35 km along the northern Balearic island shelf. No representative midpoint, seasonal endpoint assignment, confidence interval or mapped width edges. Width calculation and sampling period unspecified.</desc>
<rect width="820" height="390" fill="#f7faf9"/>
<g fill="#123541" font-family="sans-serif" font-size="17">
<text x="30" y="45" font-size="23">Balearic Current · reported regional width</text>
<text x="30" y="78">Northern island shelf · SOCIB document version 13 November 2023</text>
<line x1="60" x2="700" y1="185" y2="185" stroke="#7a9299"/>{ticks}
<text x="730" y="210">km</text>
<line x1="380" x2="620" y1="135" y2="135" stroke="#08798b" stroke-width="7"/>
<path d="M380 122v26 M620 122v26" stroke="#08798b" stroke-width="3"/>
<text x="380" y="112" text-anchor="middle">20 km</text><text x="620" y="112" text-anchor="middle">35 km</text>
<text x="30" y="255">Range preserved; no midpoint selected. Width error and dates unknown.</text>
<text x="30" y="283">Autumn maximum is qualitative variability, not a 35 km seasonal width.</text>
<text x="30" y="311">Mean GV 0.2 m/s is not an edge cutoff. No geographic band inferred.</text>
<text x="30" y="348" font-size="14">Source: Juza (2021), SOCIB Regional Estimates, version 2023-11-13, p5 · CC BY 4.0</text>
<text x="30" y="372" font-size="14">Independent OSW graphic; original fields and row-specific boundary method not reproduced.</text>
</g></svg>'''


if __name__ == '__main__':
    validate_inventory(json.loads((ROOT / 'research/ocean-current-width-inventory.json').read_bytes()))
    (ROOT / 'figures/balearic-socib-2023-regional-width.svg').write_text(svg(), encoding='utf-8')
    print('Verified SOCIB 20–35 km regional range; independent graphic written')
