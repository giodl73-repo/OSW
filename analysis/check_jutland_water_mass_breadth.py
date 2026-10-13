"""Bind Jutland regional water-mass breadth to the unchanged original source."""
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/jutland-skov-2019-water-mass-breadth-scope-audit.json'
AUDIT_SHA='c3fdcff1113465b8a14a0cc78bcee043beed088979a6de8b3e7d6767a76956ad'
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
    supporting=reviewed['measurements'][0]['original_regional_context']['supporting_original_review']
    if digest(supporting['source_document_file'])!=supporting['source_document_sha256'] or (ROOT/supporting['source_document_file']).stat().st_size!=supporting['source_document_bytes'] or digest(supporting['acquisition_file'])!=supporting['acquisition_sha256']:raise ValueError('Changed Jutland supporting original')
    for i,source in enumerate(reviewed['measurements']):
        if source['id']==row.get('id'):
            expected=copy.deepcopy(source);expected['original_regional_context'].update(audit_file=AUDIT,audit_sha256=AUDIT_SHA,audit_pointer=f'/measurements/{i}')
            if row!=expected:raise ValueError('Jutland regional, temporal or boundary scope promoted')
            return
    raise ValueError('Unknown Jutland width description')
