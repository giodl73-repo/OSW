"""Append qualified branch reach, Pacific array means and a classification depth."""
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v12 as previous

ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v13.json'
RULES='research/current-depth-rules-v13.json'
OUTPUT='research/current-depth-register-v13.json'
CSV='research/current-depth-register-v13.csv'
validate_reference=previous.validate_reference


def validate_context(row):
    if row.get('same_source_width_reference_id') is not None or row.get('independent_observation_count_claimed') is not False:
        raise ValueError('No width join or independent repeat established')
    case=row['source_case_id'];entity=row['entity_id']
    if row['metric']!='reported_vertical_extent':raise ValueError('This batch contains reach or convention references only')
    if case=='antarctic-slope-dong-2016-deep-branch':
        if entity!='current:antarctic-slope' or row['evidence_kind']!='published_observed_branch_summary' or row.get('lower_bound_m')!=1000 or row.get('lower_bound_exclusive') is not True or row.get('lower_bound_operator')!='>':raise ValueError('Retain strict offshore-branch reach bound')
        if row.get('source_branch')!='offshore_gunnerus_bank_branch' or row.get('branch_section_scope')!='partial_named_branch' or row.get('section_longitude_degrees_east')!=30:raise ValueError('Bank-crossing branch is distinct from deeper offshore branch')
        if row.get('campaign_window')!={'start_month':'2008-02','end_month':'2008-03'} or row.get('window_role')!='whole_cruise_not_exact_branch_section' or row.get('section_sampling_month') is not None:raise ValueError('Retain whole I6S cruise month scope')
    elif case=='pacific-nec-schonau-2015-northern-mean':
        if entity!='current:pacific-north-equatorial' or row['evidence_kind']!='published_glider_geostrophic_mean' or row['approximate_value_m']!=1000:raise ValueError('Northern NEC reach is not latitude-integrated transport support')
        if row.get('section_latitude_band_degrees_north')!=[14,16] or row.get('section_longitude_degrees_east')!=134.3 or row.get('averaging_month_window')!={'start_month':'2009-06','end_month':'2014-01'}:raise ValueError('Northern NEC glider-mean support changed')
        if row.get('sampling_limit_m')!=1000 or row.get('sampling_limit_is_flow_boundary') is not False or row.get('velocity_reconstruction')!='objective_mapped_absolute_geostrophic_glider':raise ValueError('Instrument endpoint does not establish flow bottom')
    elif case in ['pacific-necc-song-2019-142e-mean','pacific-northern-sec-song-2019-142e-mean']:
        necc=case=='pacific-necc-song-2019-142e-mean'
        if entity!=('current:pacific-north-equatorial-countercurrent' if necc else 'current:pacific-south-equatorial') or row['evidence_kind']!='published_mooring_mean':raise ValueError('Retain Pacific basin and component identity')
        if row.get('section_longitude_degrees_east')!=142 or row.get('section_latitude_band_degrees_north')!=([2,7] if necc else [0,2]) or row.get('averaging_month_window')!={'start_month':'2014-08','end_month':'2015-11'}:raise ValueError('Do not inherit140E2014–2018 mooring support')
        if row.get('processing')!='ADCP60–950m vertically interpolated to10m intervals and daily averaged':raise ValueError('Keep interpolation and sampling support explicit')
        if necc:
            if row.get('upper_bound_m')!=200 or row.get('upper_bound_exclusive') is not True:raise ValueError('NECC shallower-than200m is a strict bound')
        elif row['approximate_value_m']!=150 or row.get('source_branch')!='northern_equatorial_component' or row.get('branch_section_scope')!='partial_latitude_component':raise ValueError('Do not promote northern SEC component to entire current')
    elif case=='south-java-ningsih-2021-definition':
        if entity!='current:south-java' or row['approximate_value_m']!=150 or row['evidence_kind']!='published_literature_definition' or row.get('depth_basis')!='source_current_classification_convention':raise ValueError('Classification depth is not an observed zero-flow level')
        if row.get('climatology_years') is not None or row.get('averaging_month_window') is not None or row.get('section_sampling_month') is not None or row['calendar_months'] is not None:raise ValueError('Definition does not inherit OFES or seasonal-anomaly timing')
    else:raise ValueError('Unreviewed source case')


def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v12.py',RULES,SOURCE]:
        pins[p]=hashlib.sha256((root/p).read_bytes()).hexdigest()
    source=json.loads((root/SOURCE).read_bytes());rules=json.loads((root/RULES).read_bytes())
    if source['previous_register_sha256']!=pins[previous.OUTPUT]:raise ValueError('Prior pin mismatch')
    for p,digest in source['source_input_sha256'].items():
        if pins[p]!=digest:raise ValueError('Retained source XML changed')
    evidence=list(prior['evidence']);seen={r['id'] for r in evidence};identities={r['entity_id'] for r in prior['records']}
    for i,row in enumerate(source['references']):
        validate_reference(row,identities,rules['metric_types']);validate_context(row)
        if row['id'] in seen:raise ValueError('Duplicate source reference')
        seen.add(row['id']);evidence.append(dict(row,source_file=SOURCE,source_pointer=f'/references/{i}',source_sha256=pins[SOURCE]))
    records=[]
    for raw in prior['records']:
        row=dict(raw);row['depth_reference_ids']=[r['id'] for r in evidence if r['entity_id']==row['entity_id']]
        row['status']='scoped_depth_reference' if row['depth_reference_ids'] else 'not_yet_assessed';records.append(row)
    owners=sum(bool(r['depth_reference_ids']) for r in records)
    return {'schema':'osw.current-depth-register.v13','status':'SCOPED_BRANCH_REACH_AND_CLASSIFICATION_DEPTH_REFERENCES',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v13.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v13.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Branch reach retains partial spatial scope. Instrument-limited reach and current-classification conventions are not detected physical bottoms. Mooring array means retain their own longitude and averaging months.',
            'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns+=['averaging_month_window','sampling_limit_m','depth_basis','processing']
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for raw in document['evidence']:
        row=dict(raw)
        if row.get('section_sampling_window'):
            row['section_window_start']=row['section_sampling_window']['start'];row['section_window_end']=row['section_sampling_window']['end']
        for key,value in list(row.items()):
            if isinstance(value,(dict,list)):row[key]=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        writer.writerow(row)
    return out.getvalue().encode('utf8')
