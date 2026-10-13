"""Freeze the dated Caribbean description, including its unresolved supports."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = 'research/caribbean-duncan-1982-dated-width-scope-audit.json'
AUDIT_SHA = 'e9abd7a125b736381a2e29313fc30c2feac6711943ec5f35780d287f51fc9d2c'

def digest(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

def validate_row(row, audit=None):
    reviewed=json.loads((ROOT/AUDIT).read_bytes())
    if digest(AUDIT) != AUDIT_SHA or audit is not None and audit != reviewed:
        raise ValueError('Changed reviewed Caribbean width support')
    for kind in ['source_document','acquisition','protocol']:
        if digest(reviewed[kind+'_file']) != reviewed[kind+'_sha256']:
            raise ValueError('Changed Caribbean source or measurement convention')
    expected=copy.deepcopy(reviewed['measurement'])
    expected['original_regional_context'].update(audit_file=AUDIT,audit_sha256=AUDIT_SHA)
    if row != expected:
        raise ValueError('Caribbean dated width scope or unresolved units promoted')

if __name__ == '__main__':
    inventory=json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())
    rows=[r for r in inventory['measurements'] if r['current_id']=='caribbean']
    if len(rows)!=1:
        raise ValueError('Caribbean original description missing or duplicated')
    validate_row(rows[0])
    print('PASS: Caribbean original, month, geographic boundary and unresolved range units')
