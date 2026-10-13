"""Bind regional descriptions without choosing a preferred or seasonal width."""
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/humboldt-fuenzalida-2008-regional-width-scope-audit.json'
AUDIT_SHA='e973b41104fbeeff7cf2505c387a260942539f85194d0ca0688d84b7fe2d983c'
def digest(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def validate_row(row,audit=None):
    reviewed=json.loads((ROOT/AUDIT).read_bytes())
    if digest(AUDIT)!=AUDIT_SHA or (audit is not None and audit!=reviewed):raise ValueError('Changed reviewed Humboldt width supports')
    for key in ['source_review','protocol']:
        if digest(reviewed[key+'_file'])!=reviewed[key+'_sha256']:raise ValueError('Changed Humboldt source review or protocol')
    for i,source in enumerate(reviewed['measurements']):
        if source['id']==row.get('id'):
            expected=copy.deepcopy(source);expected['original_regional_context'].update(audit_file=AUDIT,audit_sha256=AUDIT_SHA,audit_pointer=f'/measurements/{i}')
            if row!=expected:raise ValueError('Humboldt description scope or seasonal support promoted')
            return
    raise ValueError('Unknown Humboldt width description')
