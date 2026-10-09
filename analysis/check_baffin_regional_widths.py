"""Bind two Baffin regional summaries to the unchanged original source."""
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/baffin-fissel-1982-regional-width-scope-audit.json'
AUDIT_SHA='5e724cd74f258b8e718caac10b168e0861c3950e93e2ee077df0c8983d8c9b8a'
SOURCE_SHA='23347326454aa485a98444d98ccd141fe73bc75bbcf9c6b6943f66e2d4e8e266'
def digest(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def validate_row(row,audit=None):
    reviewed=json.loads((ROOT/AUDIT).read_bytes())
    if digest(AUDIT)!=AUDIT_SHA or (audit is not None and audit!=reviewed):raise ValueError('Changed reviewed Baffin width supports')
    if digest(reviewed['source_document_file'])!=SOURCE_SHA or (ROOT/reviewed['source_document_file']).stat().st_size!=2154964:raise ValueError('Changed Baffin original source')
    for key in ['acquisition','protocol']:
        if digest(reviewed[key+'_file'])!=reviewed[key+'_sha256']:raise ValueError('Changed Baffin source provenance or protocol')
    for i,source in enumerate(reviewed['measurements']):
        if source['id']==row.get('id'):
            expected=copy.deepcopy(source);expected['original_regional_context'].update(audit_file=AUDIT,audit_sha256=AUDIT_SHA,audit_pointer=f'/measurements/{i}')
            if row!=expected:raise ValueError('Baffin regional, temporal or boundary scope promoted')
            return
    raise ValueError('Unknown Baffin width description')
