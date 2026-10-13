"""Preserve upper-core float width, nominal depth and distinct source errors."""
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/dwbc-richardson-1993-upper-core-width-scope-audit.json'
AUDIT_SHA='d3e078458894787b8a812589c48cb96263f2d6a867656840e173410f73712515'
SOURCE_SHA='86f96a7853fee735c2ba24fca3ab64cf2232871941e1fc4a46b3b00079c2ce53'
def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def validate_row(row,audit=None):
    reviewed=json.loads((ROOT/AUDIT).read_bytes())
    if digest(AUDIT)!=AUDIT_SHA or (audit is not None and audit!=reviewed):
        raise ValueError('Changed DWBC reviewed composite scope')
    if digest(reviewed['source_document_file'])!=SOURCE_SHA or (ROOT/reviewed['source_document_file']).stat().st_size!=1741213:
        raise ValueError('Changed DWBC original float paper')
    for key in ['acquisition','protocol']:
        if digest(reviewed[key+'_file'])!=reviewed[key+'_sha256']:
            raise ValueError('Changed DWBC source provenance or measurement rules')
    expected=copy.deepcopy(reviewed['measurement'])
    expected['original_regional_context'].update(audit_file=AUDIT,audit_sha256=AUDIT_SHA)
    if row!=expected:raise ValueError('DWBC float width, sampling or error support changed')
if __name__=='__main__':
    rows=[r for r in json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())['measurements'] if r['current_id']=='deep-western-boundary']
    if len(rows)!=1:raise ValueError('Missing distinct DWBC upper-core composite')
    validate_row(rows[0]);print('PASS: DWBC zero-velocity composite preserves nominal depth, sparse subsets and error roles')
