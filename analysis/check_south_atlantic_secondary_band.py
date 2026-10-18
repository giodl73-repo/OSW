"""Freeze the original October1983 southern component breadth."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = 'research/south-atlantic-stramma-1990-secondary-band-scope-audit.json'
PIN = 'c4e7239d16a4c92089b1c2040089026ac5c2816f5de2d60b86ab3f22e83534ed'
ID = 'south-atlantic-stramma-1983-10-southern-band-width'


def load():
    raw = (ROOT/AUDIT).read_bytes()
    if hashlib.sha256(raw).hexdigest() != PIN:
        raise ValueError('Changed reviewed South Atlantic band constraint audit')
    audit = json.loads(raw)
    for kind in ['source_document', 'acquisition', 'protocol', 'figure']:
        data = (ROOT/audit[kind+'_file']).read_bytes()
        if hashlib.sha256(data).hexdigest() != audit[kind+'_sha256']:
            raise ValueError('Changed South Atlantic source/protocol/figure: '+kind)
    return audit


def record():
    row = copy.deepcopy(load()['measurement'])
    row['original_regional_context'].update(audit_file=AUDIT, audit_sha256=PIN)
    return row


def validate_row(row, audit=None):
    expected = load()
    if audit is not None and audit != expected or row != record():
        raise ValueError('South Atlantic qualifier, time, reference or current scope changed')


def validate_inventory(document):
    rows = [r for r in document['measurements']
            if str(r.get('id','')).startswith('south-atlantic-stramma-1983-10-')]
    if len(rows) != 1 or rows[0]['id'] != ID:
        raise ValueError('Missing or duplicated South Atlantic band constraint')
    validate_row(rows[0])


def figure():
    audit = load()
    return (ROOT/audit['figure_file']).read_text(encoding='utf8')


if __name__ == '__main__':
    row = record();validate_row(row)
    print('Verified original October1983 nominal200 km southern component breadth; no whole-current width, seasonal range or physical boundaries admitted')
