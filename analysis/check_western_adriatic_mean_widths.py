"""Bind two Western Adriatic local mean profiles to the unchanged original source."""
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/western-adriatic-chavanne-2007-mean-width-scope-audit.json'
AUDIT_SHA='61d4d2dfdccb2c51c70d0487ab393a7359bb5b75b8ac5d0d89e7c8adf12ee9fa'
SOURCE_SHA='ebb25a7d586df892886aa028bc4304f93f41ec0aa1d84629d7c54d46627fe3e5'
def digest(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def validate_row(row,audit=None):
    reviewed=json.loads((ROOT/AUDIT).read_bytes())
    if digest(AUDIT)!=AUDIT_SHA or (audit is not None and audit!=reviewed):raise ValueError('Changed reviewed Western Adriatic width supports')
    if digest(reviewed['source_document_file'])!=SOURCE_SHA or (ROOT/reviewed['source_document_file']).stat().st_size!=2524809:raise ValueError('Changed Western Adriatic original source')
    for key in ['acquisition','protocol']:
        if digest(reviewed[key+'_file'])!=reviewed[key+'_sha256']:raise ValueError('Changed Western Adriatic source provenance or protocol')
    for i,source in enumerate(reviewed['measurements']):
        if source['id']==row.get('id'):
            expected=copy.deepcopy(source);expected['original_regional_context'].update(audit_file=AUDIT,audit_sha256=AUDIT_SHA,audit_pointer=f'/measurements/{i}')
            if row!=expected:raise ValueError('Western Adriatic regional, temporal or boundary scope promoted')
            return
    raise ValueError('Unknown Western Adriatic width description')
