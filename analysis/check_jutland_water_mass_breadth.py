"""Bind Jutland regional water-mass breadth to the unchanged original source."""
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/jutland-skov-2019-water-mass-breadth-scope-audit.json'
AUDIT_SHA='c00632558ae72c8fcb5bf7738c35ae4dbb82678dc3c9b6c4136a1a763fe701f9'
SOURCE_SHA='4d77f9ecce0fe7c3f4760d050e1a68588fb8e86b6ed40b1d397d0bee95d0d572'
def digest(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def validate_row(row,audit=None):
    reviewed=json.loads((ROOT/AUDIT).read_bytes())
    if digest(AUDIT)!=AUDIT_SHA or (audit is not None and audit!=reviewed):raise ValueError('Changed reviewed Jutland width supports')
    if digest(reviewed['source_document_file'])!=SOURCE_SHA or (ROOT/reviewed['source_document_file']).stat().st_size!=13249526:raise ValueError('Changed Jutland original source')
    for key in ['acquisition','protocol']:
        if digest(reviewed[key+'_file'])!=reviewed[key+'_sha256']:raise ValueError('Changed Jutland source provenance or protocol')
    naming=reviewed['measurements'][0]['original_regional_context']['naming_context']
    if digest(naming['naming_audit_file'])!=naming['naming_audit_sha256']:raise ValueError('Changed Jutland naming scope')
    for i,source in enumerate(reviewed['measurements']):
        if source['id']==row.get('id'):
            expected=copy.deepcopy(source);expected['original_regional_context'].update(audit_file=AUDIT,audit_sha256=AUDIT_SHA,audit_pointer=f'/measurements/{i}')
            if row!=expected:raise ValueError('Jutland regional, temporal or boundary scope promoted')
            return
    raise ValueError('Unknown Jutland width description')
