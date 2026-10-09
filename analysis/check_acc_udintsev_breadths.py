"""Keep local major-front separation distinct from NB-SB climatological breadth."""
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/acc-park-2019-udintsev-breadths-scope-audit.json'
AUDIT_SHA='311b5a41781c9987c81dc0b6c720f7a2cc3ebe2451cfcd696a19300b3fecc8a2'
SOURCE_SHA='a9fbd7d9f0094c4ab94f6434b4428ad7000e68cb6cc74c53d550eadbe94253ef'

def digest(p): return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()

def validate_row(row,audit=None):
    reviewed=json.loads((ROOT/AUDIT).read_bytes())
    if digest(AUDIT)!=AUDIT_SHA or (audit is not None and audit!=reviewed):
        raise ValueError('Changed reviewed ACC MDT contour supports')
    if digest(reviewed['source_document_file'])!=SOURCE_SHA or (ROOT/reviewed['source_document_file']).stat().st_size!=10224104:
        raise ValueError('Changed ACC original source')
    for key in ['acquisition','protocol']:
        if digest(reviewed[key+'_file'])!=reviewed[key+'_sha256']:
            raise ValueError('Changed ACC provenance or measurement convention')
    for i,source in enumerate(reviewed['measurements']):
        if source['id']==row.get('id'):
            expected=copy.deepcopy(source)
            expected['original_regional_context'].update(audit_file=AUDIT,audit_sha256=AUDIT_SHA,audit_pointer=f'/measurements/{i}')
            if row!=expected: raise ValueError('ACC quantities pooled, support promoted or source identity changed')
            return
    raise ValueError('Unknown ACC climatological quantity')
