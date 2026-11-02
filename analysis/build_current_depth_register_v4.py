"""Append source summaries and local climatological zero-flow boundary depths."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v3 as previous
from build_current_depth_register_v2 import validate_reference

ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v4.json'
RULES=previous.RULES
OUTPUT='research/current-depth-register-v4.json'
CSV='research/current-depth-register-v4.csv'


def validate_boundary_context(row):
    if row['entity_id']=='current:leeuwin':
        if row['metric']!='lower_flow_boundary_depth' or row.get('depth_operator')!='zero_alongshore_velocity_in_mooring_climatology':
            raise ValueError('Leeuwin depth must retain its local zero-flow operator')
        if row.get('mooring_id')!='TR50' or row.get('climatology_period')!={'start_month':'2010-01','end_month':'2023-05'}:
            raise ValueError('Mooring/climatology support changed')
        if row.get('processing')!='QC-selected observations, gap filling and climatological averaging; not instantaneous profiles':
            raise ValueError('Observation processing must remain explicit')
    elif row['metric']!='reported_vertical_extent':raise ValueError('Summary is not a diagnosed boundary')


def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Previous register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v3.py',SOURCE]:pins[p]=hashlib.sha256((root/p).read_bytes()).hexdigest()
    source=json.loads((root/SOURCE).read_bytes());rules=json.loads((root/RULES).read_bytes())
    if source['previous_register_sha256']!=pins[previous.OUTPUT]:raise ValueError('Prior pin mismatch')
    evidence=list(prior['evidence']);seen={r['id'] for r in evidence};identities={r['entity_id'] for r in prior['records']}
    for i,row in enumerate(source['references']):
        validate_reference(row,identities,rules['metric_types']);validate_boundary_context(row)
        if row['id'] in seen:raise ValueError('Duplicate reference')
        seen.add(row['id']);evidence.append(dict(row,source_file=SOURCE,source_pointer=f'/references/{i}',source_sha256=pins[SOURCE]))
    records=[]
    for raw in prior['records']:
        row=dict(raw);row['depth_reference_ids']=[r['id'] for r in evidence if r['entity_id']==row['entity_id']]
        row['status']='scoped_depth_reference' if row['depth_reference_ids'] else 'not_yet_assessed';records.append(row)
    owners=sum(bool(r['depth_reference_ids']) for r in records)
    return {'schema':'osw.current-depth-register.v4','status':'SCOPED_DEPTH_REFERENCES_WITH_LOCAL_CLIMATOLOGICAL_BOUNDARIES','rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v4.py','generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v4.py').read_bytes()).hexdigest(),'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),'coverage_interpretation':prior['coverage_interpretation']+' Local zero-flow boundaries from a processed climatology do not establish instantaneous or whole-route thickness.','records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


csv_bytes=previous.csv_bytes


if __name__=='__main__':
    d=build();(ROOT/OUTPUT).write_bytes((json.dumps(d,indent=2,ensure_ascii=False)+'\n').encode('utf8'));(ROOT/CSV).write_bytes(csv_bytes(d));print(json.dumps(d['counts']))
