"""Bind the finite-campaign modal estimate to its reviewed original and operators."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = 'research/tsushima-matsuyama-1990-modal-width-scope-audit.json'
AUDIT_SHA = '587cccbd45b3673137523241a2bbab07f3ee681e8f5549a7b44f0ae6ced90fb6'
SOURCE_SHA = '513c7b63658ab04c8e5157d414743d249ba919176d4682dbe8df4b72ab9ced55'


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def validate_row(row, audit=None):
    reviewed = json.loads((ROOT / AUDIT).read_bytes())
    if digest(AUDIT) != AUDIT_SHA or (audit is not None and audit != reviewed):
        raise ValueError('Changed reviewed Tsushima modal extraction')
    audit = reviewed
    if audit['source_document_sha256'] != SOURCE_SHA or digest(audit['source_document_file']) != SOURCE_SHA or (ROOT / audit['source_document_file']).stat().st_size != 1772559:
        raise ValueError('Changed Tsushima original source')
    for kind in ['protocol', 'acquisition']:
        if digest(audit[kind + '_file']) != audit[kind + '_sha256']:
            raise ValueError('Changed Tsushima provenance or modal convention')
    expected = copy.deepcopy(audit['measurement'])
    expected['modal_decay_context'].update(audit_file=AUDIT, audit_sha256=AUDIT_SHA)
    if row != expected:
        raise ValueError('Tsushima modal width or operator support differs from reviewed original')
    return row


if __name__ == '__main__':
    document = json.loads((ROOT / 'research/ocean-current-width-inventory.json').read_bytes())
    rows = [r for r in document['measurements'] if r['current_id'] == 'tsushima']
    if len(rows) != 1:
        raise ValueError('Expected one Tsushima modal estimate, not independent summary records')
    validate_row(rows[0])
    print('PASS: reported modal width, arithmetic discrepancy and separate campaign operators')
