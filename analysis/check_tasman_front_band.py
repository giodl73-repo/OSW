"""Preserve occupied meander-band breadth separately from individual jet widths."""
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/tasman-front-nilsson-1980-meander-band-scope-audit.json'
AUDIT_SHA='6205515eaa753b22b115dfebc5900b6e507bb4401644683ca14cf74c2ab838e6'
SOURCE_SHA='6bcc15747fc95fa9aa4e35767d2a713425c73ab4529434240a77c04d543a4aaa'


def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def validate_row(row,audit=None):
    reviewed=json.loads((ROOT/AUDIT).read_bytes())
    if digest(AUDIT)!=AUDIT_SHA or (audit is not None and audit!=reviewed):
        raise ValueError('Changed reviewed Tasman band definition')
    if digest(reviewed['source_document_file'])!=SOURCE_SHA or (ROOT/reviewed['source_document_file']).stat().st_size!=6188044:
        raise ValueError('Changed Tasman original report')
    for key in ['acquisition','protocol']:
        if digest(reviewed[key+'_file'])!=reviewed[key+'_sha256']:
            raise ValueError('Changed Tasman band provenance or measurement convention')
    for i,source in enumerate(reviewed['measurements']):
        if source['id']==row.get('id'):
            expected=copy.deepcopy(source)
            expected['original_regional_context'].update(audit_file=AUDIT,audit_sha256=AUDIT_SHA,audit_pointer=f'/measurements/{i}')
            if row!=expected:raise ValueError('Tasman band definition or measurement support changed')
            return
    raise ValueError('Unknown Tasman band width description')


if __name__=='__main__':
    data=json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())
    rows=[r for r in data['measurements'] if r['current_id']=='tasman-front']
    if len(rows)!=1:raise ValueError('Missing distinct Tasman band descriptions')
    for row in rows:validate_row(row)
    print('PASS: 600 km occupied band retains its distinct definition')
