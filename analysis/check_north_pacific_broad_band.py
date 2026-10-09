"""Preserve the textbook's combined-flow definition and greater-than qualifier."""
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/north-pacific-tomczak-2005-broad-band-scope-audit.json'
AUDIT_SHA='09ec3af553122962de08298c120113149d1c822857cd80fb3381fcc15c9e235a'
SOURCE_SHA='35e36f9b834c9c31c2cee64abc36d0c687d71e3d388c2cf1c40bc026e613738b'
def digest(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def validate_row(row,audit=None):
    reviewed=json.loads((ROOT/AUDIT).read_bytes())
    if digest(AUDIT)!=AUDIT_SHA or (audit is not None and audit!=reviewed):raise ValueError('Changed reviewed North Pacific broad-band supports')
    if digest(reviewed['source_document_file'])!=SOURCE_SHA or (ROOT/reviewed['source_document_file']).stat().st_size!=36625246:raise ValueError('Changed North Pacific textbook original')
    for key in ['acquisition','protocol']:
        if digest(reviewed[key+'_file'])!=reviewed[key+'_sha256']:raise ValueError('Changed North Pacific broad-band provenance or protocol')
    source=reviewed['measurement'];naming=source['original_regional_context']['naming_context']
    if digest(naming['naming_audit_file'])!=naming['naming_audit_sha256']:raise ValueError('Changed Aleutian/Alaskan Stream naming scope')
    expected=copy.deepcopy(source);expected['original_regional_context'].update(audit_file=AUDIT,audit_sha256=AUDIT_SHA)
    if row!=expected:raise ValueError('North Pacific broad band promoted or combined-flow definition changed')
