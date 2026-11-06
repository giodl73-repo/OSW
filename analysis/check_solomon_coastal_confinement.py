"""Bind one-sided coastal descriptions to the reviewed Melet original."""
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/solomon-melet-2010-coastal-confinement-scope-audit.json'
AUDIT_SHA='9479bb446cb945602bc253969ca71217d073c93d8b135883005dfffb35236656'
SOURCE_SHA='9d41af95d2ccbcee1e1469ea45d703d9cb1005ce6d1701896f4a94b5e8f1da3d'

def digest(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def validate_row(row,audit=None):
    reviewed=json.loads((ROOT/AUDIT).read_bytes())
    if digest(AUDIT)!=AUDIT_SHA or (audit is not None and audit!=reviewed):raise ValueError('Changed reviewed Solomon confinement supports')
    from melet_hal_source import resolve_source
    resolve_source()
    for key in ['acquisition','protocol']:
        if digest(reviewed[key+'_file'])!=reviewed[key+'_sha256']:raise ValueError('Changed Solomon confinement provenance or protocol')
    for i,source in enumerate(reviewed['measurements']):
        if source['id']==row.get('id'):
            expected=copy.deepcopy(source);expected['original_regional_context'].update(audit_file=AUDIT,audit_sha256=AUDIT_SHA,audit_pointer=f'/measurements/{i}')
            if row!=expected:raise ValueError('Solomon coastal confinement promoted or source identity changed')
            return
    raise ValueError('Unknown Solomon coastal confinement description')
