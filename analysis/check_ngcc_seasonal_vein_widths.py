"""Seasonal current-anomaly and thermal veins retain distinct immutable scope."""
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/ngcc-radenac-2016-seasonal-vein-width-scope-audit.json'
PIN='223405cce3aa4a5fecdf94dd25ebff225a9594f33fb04f784a469fd4e6e8ce10'

def digest(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

def validate_row(row,audit=None):
    reviewed=json.loads((ROOT/AUDIT).read_bytes())
    if digest(AUDIT)!=PIN or audit is not None and audit!=reviewed:
        raise ValueError('Changed reviewed NGCC seasonal vein audit')
    for kind in ['source_document','acquisition','protocol']:
        if digest(reviewed[kind+'_file'])!=reviewed[kind+'_sha256']:
            raise ValueError('Changed NGCC original or descriptor support')
    i=next((i for i,r in enumerate(reviewed['measurements']) if r['id']==row.get('id')),None)
    if i is None:
        raise ValueError('Unknown NGCC seasonal vein descriptor')
    expected=copy.deepcopy(reviewed['measurements'][i])
    expected['original_regional_context'].update(audit_file=AUDIT,audit_sha256=PIN,audit_pointer='/measurements/'+str(i))
    if row!=expected:
        raise ValueError('NGCC vein metric, identity or seasonal source scope promoted')

def validate_inventory(document):
    reviewed=json.loads((ROOT/AUDIT).read_bytes())
    selected=[r for r in document['measurements'] if r.get('current_id')=='new-guinea-coastal-current' or str(r.get('id','')).startswith('ngcc-radenac-2016-')]
    if len(selected)!=4 or {r['id'] for r in selected}!={r['id'] for r in reviewed['measurements']}:
        raise ValueError('Missing or duplicated NGCC seasonal vein descriptors')
    for row in selected:
        validate_row(row)
