"""Frozen historical SECC width range retains unresolved temporal/depth support."""
import copy, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/pacific-secc-rotschi-1972-width-range-scope-audit.json'
PIN='ef2dc83521f6a67900ac95353dd4e1860f345bc6471250943e8c7372d44ade22'

def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

def validate_row(row,audit=None):
    reviewed=json.loads((ROOT/AUDIT).read_bytes())
    if digest(AUDIT)!=PIN or audit is not None and audit!=reviewed:raise ValueError('Changed reviewed Pacific SECC width audit')
    for kind in ['source_document','acquisition','protocol']:
        if digest(reviewed[kind+'_file'])!=reviewed[kind+'_sha256']:raise ValueError('Changed Pacific SECC original or support')
    expected=copy.deepcopy(reviewed['measurement'])
    expected['original_regional_context'].update(audit_file=AUDIT,audit_sha256=PIN)
    if row!=expected:raise ValueError('Pacific SECC width identity, range or method scope promoted')
