"""Keep observed flow breadth separate from conditional salinity-origin breadth."""
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/monsoon-webber-2018-distinct-widths-scope-audit.json'
AUDIT_SHA='01add615729f0ebf28ac9632cf4f76b85d9a0d2e67af33cee9088e52018192c4'
SOURCE_SHA='6d091b84ed01d841945474db23079c0391cb06956f92fd686a57e26d73154c2d'


def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def validate_row(row,audit=None):
    reviewed=json.loads((ROOT/AUDIT).read_bytes())
    if digest(AUDIT)!=AUDIT_SHA or (audit is not None and audit!=reviewed):
        raise ValueError('Changed reviewed Monsoon feature definitions')
    if digest(reviewed['source_document_file'])!=SOURCE_SHA or (ROOT/reviewed['source_document_file']).stat().st_size!=5205619:
        raise ValueError('Changed Monsoon original paper')
    for key in ['acquisition','protocol']:
        if digest(reviewed[key+'_file'])!=reviewed[key+'_sha256']:
            raise ValueError('Changed Monsoon provenance or measurement convention')
    for i,source in enumerate(reviewed['measurements']):
        if source['id']==row.get('id'):
            expected=copy.deepcopy(source)
            expected['original_regional_context'].update(audit_file=AUDIT,audit_sha256=AUDIT_SHA,audit_pointer=f'/measurements/{i}')
            if row!=expected:raise ValueError('Monsoon quantities pooled, conditionality erased or support changed')
            return
    raise ValueError('Unknown Monsoon width description')


if __name__=='__main__':
    data=json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())
    rows=[r for r in data['measurements'] if r['current_id']=='monsoon']
    if len(rows)!=2:raise ValueError('Missing distinct Monsoon descriptions')
    for row in rows:validate_row(row)
    print('PASS: 300 km surface flow and conditional 150 km origin component retain distinct scope')
