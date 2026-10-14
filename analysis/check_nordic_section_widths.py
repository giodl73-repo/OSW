"""Keep proposed slope widths separate; reuse the six existing WSC records."""
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NOR='norwegian-atlantic-slope'
WSC='west-spitsbergen'
SOURCES={
    NOR:('research/norwegian-fer-2020-gimsoy-width-scope-audit.json','084f2ab755c06589ab5985e362621e44eb1f08ec684d74e1086b65ede3c8c8bb'),
    WSC:('research/west-spitsbergen-kolas-2018-stream-tube-width-scope-audit.json','cb35ac68f45f3d1697583f129c4eb16156803c333d319eb724f60a8ca0083075')}
OLD='research/norwegian-atlantic-branch-width-scope-audit.json'
OLD_PIN='1d0df8d68b02025a055ab072ab52b522dcb6b989d6be388c8d5e7725421667ae'

def pinned(path,pin):
    raw=(ROOT/path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=pin:raise ValueError('Changed Nordic source definition audit')
    return json.loads(raw)

def load(owner):return pinned(*SOURCES[owner])

def records(owner):
    path,pin=SOURCES[owner]
    rows=copy.deepcopy(load(owner)['measurements'])
    for i,row in enumerate(rows):
        context=row['stream_tube_context' if owner==WSC else 'original_regional_context']
        context.update(audit_file=path,audit_sha256=pin)
        if owner==NOR:
            context['audit_pointer']=f'/measurements/{i}'
            row.update(source_file=path,source_pointer=f'/measurements/{i}')
    return rows

def proposed_records():
    rows=copy.deepcopy(pinned(OLD,OLD_PIN)['measurements'])
    for i,row in enumerate(rows):row.update(source_file=OLD,source_pointer=f'/measurements/{i}')
    return rows+records(NOR)

def validate_row(row,audit=None):
    owner=next((o for o in SOURCES if any(r['id']==row.get('id') for r in records(o))),None)
    if owner is None or row not in records(owner):raise ValueError('Nordic section width differs from source identity or support')
    expected=load(owner)
    if audit is not None and audit!=expected:raise ValueError('Changed Nordic source definition audit')
    for kind in ['source_document','acquisition','protocol']:
        if hashlib.sha256((ROOT/expected[kind+'_file']).read_bytes()).hexdigest()!=expected[kind+'_sha256']:
            raise ValueError('Changed Nordic original source or provenance')

def validate_proposal(proposals):
    expected=records(NOR)
    row=next(r for r in proposals['entries'] if r['proposed_id']==NOR)
    if row.get('section_width_evidence')!=expected or row.get('section_width_scope_audit')!={'file':SOURCES[NOR][0],'sha256':SOURCES[NOR][1]}:
        raise ValueError('Proposed Gimsøy section width binding changed')
    for r in expected:validate_row(r)

def validate_inventory(document):
    if any(r.get('current_id') in {'norwegian','spitsbergen-atlantic'} or r.get('id')==records(NOR)[0]['id'] for r in document['measurements']):
        raise ValueError('Unresolved names or proposed widths transferred to canonical inventory')
    expected=records(WSC)
    actual=[r for r in document['measurements'] if r['current_id']==WSC]
    if actual!=expected:raise ValueError('Existing WSC records duplicated or changed')

def visual(row):
    """Presentation values retain the underlying record and operator cases."""
    if 'stream_tube_context' not in row:return row
    result=copy.deepcopy(row);c=row['stream_tube_context']
    result['original_regional_context']={'section':c['section_id'],'tube':c['stream_tube']}
    if c['stream_tube']==1:
        values=[row['approximate_width_km']]+[r['width_km'] for r in c['threshold_sensitivity_cases']]
        result['width_range_km']=[min(values),max(values)]
    return result
