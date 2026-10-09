"""Keep the issuer's geographic breadth distinct from measured core width."""
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/west-australian-glenn-2008-breadth-scope-audit.json'
AUDIT_SHA='cae64ac5000db69c62c1c8d7bb2b1785c28a7dcd3ddec7cd9277caac27b6851e'
SOURCE_SHA='243020ced1fbec8b6ded01f1aa3bd1837228e28fffa4bfea152e8b95d4532d23'
def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def validate_row(row,audit=None):
    reviewed=json.loads((ROOT/AUDIT).read_bytes())
    if digest(AUDIT)!=AUDIT_SHA or (audit is not None and audit!=reviewed):
        raise ValueError('Changed reviewed West Australian breadth extraction')
    if reviewed['source_document_sha256']!=SOURCE_SHA or digest(reviewed['source_document_file'])!=SOURCE_SHA or (ROOT/reviewed['source_document_file']).stat().st_size!=50913973:
        raise ValueError('Changed West Australian original report')
    for kind in ['acquisition','protocol']:
        if digest(reviewed[kind+'_file'])!=reviewed[kind+'_sha256']:
            raise ValueError('Changed West Australian provenance or breadth convention')
    expected=copy.deepcopy(reviewed['measurement'])
    expected['original_regional_context'].update(audit_file=AUDIT,audit_sha256=AUDIT_SHA)
    if row!=expected:raise ValueError('West Australian geographic constraint or support promoted')
