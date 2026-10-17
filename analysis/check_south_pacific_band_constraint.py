"""Freeze the original March1990 relative-geostrophic band constraint."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = 'research/south-pacific-stramma-1995-width-constraint-scope-audit.json'
PIN = '5d86b40f0c1029535542b843dd5b1451d6111b1ddcd16e82a6a02d438d1c7578'
ID = 'south-pacific-stramma-1990-03-relative-band-constraint'


def load():
    raw = (ROOT/AUDIT).read_bytes()
    if hashlib.sha256(raw).hexdigest() != PIN:
        raise ValueError('Changed reviewed South Pacific band constraint audit')
    audit = json.loads(raw)
    for kind in ['source_document', 'acquisition', 'protocol', 'figure']:
        data = (ROOT/audit[kind+'_file']).read_bytes()
        if hashlib.sha256(data).hexdigest() != audit[kind+'_sha256']:
            raise ValueError('Changed South Pacific source/protocol/figure: '+kind)
    return audit


def record():
    row = copy.deepcopy(load()['measurement'])
    row['original_regional_context'].update(audit_file=AUDIT, audit_sha256=PIN)
    return row


def validate_row(row, audit=None):
    expected = load()
    if audit is not None and audit != expected or row != record():
        raise ValueError('South Pacific qualifier, time, reference or current scope changed')


def validate_inventory(document):
    rows = [r for r in document['measurements']
            if str(r.get('id','')).startswith('south-pacific-stramma-1990-03-')]
    if len(rows) != 1 or rows[0]['id'] != ID:
        raise ValueError('Missing or duplicated South Pacific band constraint')
    validate_row(rows[0])


def figure():
    audit = load()
    return (ROOT/audit['figure_file']).read_text(encoding='utf8')


if __name__ == '__main__':
    row = record();validate_row(row)
    print('Verified original March1990 less-than200 km band constraint; no point, seasonal range or physical boundaries admitted')
