"""Explicit presentation changes and separately attested delivery controls."""
import copy
from chen_indian_sec_delivery_contract_v2 import engine_manifest as prior_manifest

PRESENTATION={'almanac/query-charts.js','almanac/object.js','almanac/query.html',
              'almanac/object.html','almanac/reference-route-atlas.js','almanac/reference-routes.html'}
ADDED={'almanac/regional-model-lengths.js','almanac/regional-model-atlas.js'}
PHASE='research/current-gap-delivery-phase.json'
KEY='indian_sec_regional_model_lengths_engine_v1'


def engine_manifest(parent,replacements,*,scope,inventory,allowed_changes,proof,**kwargs):
    if scope.get('schema')!='osw.chen-indian-sec-presentation-source-scope.v1':
        raise ValueError('Explicit presentation source scope required')
    changed=scope['presentation_source_changes'];added=scope['added_presentation_sha256']
    if set(changed)!=PRESENTATION or set(added)!=ADDED:
        raise ValueError('Exact six changed and two added presentation assets required')
    compiled=set(inventory['rust_source_sha256'])|set(inventory['compile_time_data_sha256'])
    compiled|=set(proof['production_dependencies'])
    if compiled & (PRESENTATION|ADDED|{PHASE}):
        raise ValueError('Presentation/control scope cannot override compiled inputs')
    for path,row in changed.items():
        if (row['parent_sha256']!=parent['sha256'].get(path)
                or row['candidate_sha256']!=replacements.get(path)
                or row['parent_sha256']==row['candidate_sha256']):
            raise ValueError('Incorrect presentation source binding: '+path)
    for path,pin in added.items():
        if path in parent['sha256'] or replacements.get(path)!=pin:
            raise ValueError('Incorrect added presentation binding: '+path)
    operational=scope['operational_inputs']
    if set(operational)!={PHASE}:
        raise ValueError('Only the delivery phase is a separately attested control')
    row=operational[PHASE]
    if (row['parent_sha256']!=parent['sha256'].get(PHASE)
            or row['current_sha256']!=replacements.get(PHASE)):
        raise ValueError('Incorrect delivery phase binding')
    active=dict(replacements);del active[PHASE]
    result=prior_manifest(parent,active,inventory=inventory,
        allowed_changes=set(allowed_changes)|PRESENTATION,proof=proof,**kwargs)
    if result['sha256'][PHASE]!=parent['sha256'][PHASE]:
        raise ValueError('Historical delivery control hash changed')
    result[KEY]['delivery_source_provenance_v2']={
        'presentation_source_changes':copy.deepcopy(changed),
        'added_presentation_sha256':copy.deepcopy(added),
        'operational_inputs':copy.deepcopy(operational),
        'historical_operational_hash_preserved':True,
    }
    return result
