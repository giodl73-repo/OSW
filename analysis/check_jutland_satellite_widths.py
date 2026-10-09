"""Bind three cited Jutland satellite widths to the unchanged original source."""
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/jutland-nielsen-2000-cited-satellite-width-scope-audit.json'
AUDIT_SHA='7e5b8d9899ca5eea3664c83ffc3f7f6457dc65934505285032ad04a64f9d7121'
SOURCE_SHA='29e027afd56877b6acec02382a8a6a2e5b2ecce24572171c2e15c1f1ae071525'
def digest(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def validate_row(row,audit=None):
    reviewed=json.loads((ROOT/AUDIT).read_bytes())
    if digest(AUDIT)!=AUDIT_SHA or (audit is not None and audit!=reviewed):raise ValueError('Changed reviewed Jutland satellite width supports')
    if digest(reviewed['source_document_file'])!=SOURCE_SHA or (ROOT/reviewed['source_document_file']).stat().st_size!=4292648:raise ValueError('Changed Jutland satellite original source')
    for key in ['acquisition','protocol']:
        if digest(reviewed[key+'_file'])!=reviewed[key+'_sha256']:raise ValueError('Changed Jutland satellite source provenance or protocol')
    comparison=reviewed['source_comparison']
    if digest(comparison['later_report_audit_file'])!=comparison['later_report_audit_sha256']:raise ValueError('Changed Jutland source comparison')
    naming=reviewed['measurements'][0]['original_regional_context']['naming_context']
    if digest(naming['naming_audit_file'])!=naming['naming_audit_sha256']:raise ValueError('Changed Jutland naming scope')
    for i,source in enumerate(reviewed['measurements']):
        if source['id']==row.get('id'):
            expected=copy.deepcopy(source);expected['original_regional_context'].update(audit_file=AUDIT,audit_sha256=AUDIT_SHA,audit_pointer=f'/measurements/{i}')
            if row!=expected:raise ValueError('Jutland satellite regional, temporal or boundary scope promoted')
            return
    raise ValueError('Unknown Jutland satellite width description')
