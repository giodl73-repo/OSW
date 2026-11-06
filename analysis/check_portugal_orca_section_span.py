"""Keep a source coordinate span distinct from whole-current or seasonal width."""
import copy
import hashlib
import json
from pathlib import Path

from pyproj import Geod

ROOT = Path(__file__).resolve().parents[1]
AUDIT = 'research/portugal-perez-2013-orca-section-span-scope-audit.json'
PIN = '389d77f93a11e2b9cae6be934beba040f143bf7523c442b8bc27a6c491ea1b61'
ID = 'portugal-perez-2009-orca-source-section-span'


def load():
    raw = (ROOT / AUDIT).read_bytes()
    if hashlib.sha256(raw).hexdigest() != PIN:
        raise ValueError('Changed Portugal ORCA reviewed section-span audit')
    audit = json.loads(raw)
    for kind in ['source_event_file', 'protocol', 'figure']:
        path_key = kind if kind == 'source_event_file' else kind + '_file'
        digest_key = kind + '_sha256'
        if hashlib.sha256((ROOT / audit[path_key]).read_bytes()).hexdigest() != audit[digest_key]:
            raise ValueError('Changed Portugal ORCA source/protocol/figure: ' + kind)
    row = audit['measurement']
    context = row['published_section_context']
    event = context['source_event']
    events = json.loads((ROOT / audit['source_event_file']).read_bytes())['entries']
    matching = [r for r in events if r['observation_event_id'] == context['source_event_id']]
    if matching != [event]:
        raise ValueError('Changed or duplicated Portugal ORCA source event')
    a, b = event['reported_section_endpoints_lon_lat']
    distance = Geod(ellps='WGS84').inv(*a, *b)[2] / 1000
    if abs(distance - context['unrounded_geodesic_distance_km']) > 1e-9:
        raise ValueError('Portugal ORCA geodesic calculation changed')
    if round(distance) != row['approximate_width_km']:
        raise ValueError('Portugal ORCA display rounding changed')
    return audit


def record():
    row = copy.deepcopy(load()['measurement'])
    row['published_section_context'].update(audit_file=AUDIT, audit_sha256=PIN)
    return row


def validate_row(row, audit=None):
    expected = load()
    if (audit is not None and audit != expected) or row != record():
        raise ValueError('Portugal ORCA section, calculation, provenance or scope changed')


def validate_inventory(document):
    rows = [r for r in document['measurements'] if r.get('id') == ID]
    if len(rows) != 1:
        raise ValueError('Missing or duplicated Portugal ORCA section span')
    validate_row(rows[0])


def figure():
    return (ROOT / load()['figure_file']).read_text(encoding='utf8')


if __name__ == '__main__':
    validate_row(record())
    print('Verified candidate Portugal ORCA nominal116 km section span; no whole-current or seasonal width inferred')
