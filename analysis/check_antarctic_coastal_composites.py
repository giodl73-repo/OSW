"""Preserve source-computed composite coastal sections and their sampling support."""
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/antarctic-coastal-schubert-2021-composite-width-scope-audit.json'
AUDIT_SHA='088b17a20ccbc2c99b406675bca7b46c519d08fa671b97d97dc61fbd59e05a5e'
SOURCE_SHA='ed082152e25690716393b11210d3a4512b08ecfa4d713ad879d10f625b46a479'


def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def validate_row(row,audit=None):
    reviewed=json.loads((ROOT/AUDIT).read_bytes())
    if digest(AUDIT)!=AUDIT_SHA or (audit is not None and audit!=reviewed):
        raise ValueError('Changed reviewed Antarctic coastal feature definitions')
    if digest(reviewed['source_document_file'])!=SOURCE_SHA or (ROOT/reviewed['source_document_file']).stat().st_size!=11522211:
        raise ValueError('Changed Antarctic coastal original paper')
    for key in ['acquisition','protocol','source_figure_receipt']:
        if digest(reviewed[key+'_file'])!=reviewed[key+'_sha256']:
            raise ValueError('Changed Antarctic coastal provenance or measurement convention')
    figure=reviewed['source_figure']
    if digest(figure['asset_file'])!=figure['asset_sha256'] or (ROOT/figure['asset_file']).stat().st_size!=figure['asset_bytes']:
        raise ValueError('Changed credited section-location figure')
    for i,source in enumerate(reviewed['measurements']):
        if source['id']==row.get('id'):
            expected=copy.deepcopy(source)
            expected['original_regional_context'].update(audit_file=AUDIT,audit_sha256=AUDIT_SHA,audit_pointer=f'/measurements/{i}')
            if row!=expected:raise ValueError('Antarctic coastal composite definitions or sampling support changed')
            return
    raise ValueError('Unknown Antarctic coastal width description')


if __name__=='__main__':
    data=json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())
    rows=[r for r in data['measurements'] if r['current_id']=='antarctic-coastal']
    if len(rows)!=7:raise ValueError('Missing distinct Antarctic coastal descriptions')
    for row in rows:validate_row(row)
    print('PASS: seven coastal composite widths retain source threshold and sampling support')
