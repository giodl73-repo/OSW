"""Retain monthly profile censoring and distinguish approximate extent from exact boundaries."""
import csv, hashlib, io, json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v17 as previous
ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v18.json'
RULES='research/current-depth-rules-v18.json'
OUTPUT='research/current-depth-register-v18.json'
CSV='research/current-depth-register-v18.csv'
validate_reference=previous.validate_reference

def validate_context(row,root=ROOT):
    if row.get('same_source_width_reference_id') is not None or row.get('independent_observation_count_claimed') is not False:raise ValueError('No width join or independent repeat established')
    case=row['source_case_id']
    if case.startswith('ngcc-zhang-2020-'):
        required={'entity_id':'current:new-guinea-coastal-current','evidence_kind':'published_observational_climatology','mooring_lon_lat':[141.4,-1.7],'climatology_record_span':{'start_month':'2015-11','end_month':'2018-12'},'minimum_retained_depth_m':30,'upper_30m_unsampled':True,'data_gap_note':'Upper400m data loss reported during July2016 and March2017 due to instrument damage; uninterrupted coverage is not established.','processing':'pressure_corrected_depths_10m_interpolation_monthly_averaging','branch_section_scope':'local_mooring_profile','interannual_signal_may_contaminate_monthly_climatology':True}
        if case=='ngcc-zhang-2020-upper100':
            required.update({'metric':'reported_vertical_extent','approximate_value_m':100,'depth_basis':'source_local_seasonally_reversing_flow_description','calendar_months':None})
        else:
            tag=case.removeprefix('ngcc-zhang-2020-')
            if tag not in ['february','august']:raise ValueError('Unreviewed month')
            feb=tag=='february'
            required.update({'metric':'core_depth','approximate_value_m':30 if feb else 80,'calendar_months':[2] if feb else [8],'phase_label':tag,'core_definition':{'kind':'maximum_alongshore_speed_in_retained_monthly_profile','flow_direction':'southeastward' if feb else 'northwestward'},'reported_maximum_at_shallowest_retained_bin':feb,'depth_basis':'source_monthly_profile_velocity_maximum'})
            if not row.get('calendar_source_locator'):raise ValueError('Month requires explicit source')
    elif case=='hiri-wijeratne-2018-australian-branch':
        required={'entity_id':'current:hiri-current','metric':'reported_vertical_extent','evidence_kind':'published_model_hindcast_mean','lower_bound_m':300,'lower_bound_operator':'>','lower_bound_exclusive':True,'model_product':'ozROMS','hindcast_period':{'start_date':'2000-01-01','end_date':'2014-12-31'},'data_assimilation':False,'branch_section_scope':'northward_australian_boundary_branch','source_naming_convention':'broad_Hiri_Australian_branch_and_Gulf_of_Papua','depth_basis':'source_model_flow_reach'}
    elif case=='tasman-front-sutton-2014-norfolk':
        required={'entity_id':'current:tasman-front','metric':'reported_vertical_extent','evidence_kind':'published_observation_supported_regional_extent','approximate_value_m':800,'array_sampling_span':{'start_month':'2003-07','end_month':'2004-08'},'exact_uniform_instrument_window':False,'processing_reference_depth_m':800,'mean_flow_direction_by_nominal_depth':{'500m':'eastward','1000m':'westward_or_along_section_deep_counterflow'},'exact_zero_depth_observed':False,'branch_section_scope':'regional_Norfolk_Gap_array','depth_basis':'author_observation_supported_approximate_flow_extent'}
    else:raise ValueError('Unreviewed source case')
    if row.get('section_sampling_month') is not None:raise ValueError('No exact occupation month established')
    for k,v in required.items():
        if row.get(k)!=v:raise ValueError('Source context changed: '+k)

def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v17.py',RULES,SOURCE]:
        pins[p]=hashlib.sha256((root/p).read_bytes()).hexdigest()
    source=json.loads((root/SOURCE).read_bytes());rules=json.loads((root/RULES).read_bytes())
    if source['previous_register_sha256']!=pins[previous.OUTPUT]:raise ValueError('Prior pin mismatch')
    for p,digest in source['source_input_sha256'].items():
        if pins[p]!=digest:raise ValueError('Retained source XML changed')
    evidence=list(prior['evidence']);seen={r['id'] for r in evidence};identities={r['entity_id'] for r in prior['records']}
    for i,row in enumerate(source['references']):
        validate_reference(row,identities,rules['metric_types']);validate_context(row,root)
        if row['id'] in seen:raise ValueError('Duplicate source reference')
        seen.add(row['id']);evidence.append(dict(row,source_file=SOURCE,source_pointer=f'/references/{i}',source_sha256=pins[SOURCE]))
    records=[]
    for raw in prior['records']:
        row=dict(raw);row['depth_reference_ids']=[r['id'] for r in evidence if r['entity_id']==row['entity_id']]
        row['status']='scoped_depth_reference' if row['depth_reference_ids'] else 'not_yet_assessed';records.append(row)
    owners=sum(bool(r['depth_reference_ids']) for r in records)
    return {'schema':'osw.current-depth-register.v18','status':'LOCAL_MONTHLY_CORES_BRANCH_REACH_AND_SUPPORTED_REGIONAL_EXTENT',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v18.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v18.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Local monthly maxima retain shallow sampling censoring, record gaps and short-record caveats. Branch reach bounds and observation-supported approximate extent do not establish exact route-wide boundaries.',
            'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns += [p for p in ['climatology_record_span','minimum_retained_depth_m','upper_30m_unsampled','data_gap_note','interannual_signal_may_contaminate_monthly_climatology','reported_maximum_at_shallowest_retained_bin','hindcast_period','data_assimilation','source_naming_convention','array_sampling_span','exact_uniform_instrument_window','processing_reference_depth_m','mean_flow_direction_by_nominal_depth','exact_zero_depth_observed'] if p not in columns]
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for raw in document['evidence']:
        row=dict(raw)
        if row.get('section_sampling_window'):
            row['section_window_start']=row['section_sampling_window']['start'];row['section_window_end']=row['section_sampling_window']['end']
        for key,value in list(row.items()):
            if isinstance(value,(dict,list)):row[key]=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        writer.writerow(row)
    return out.getvalue().encode('utf8')
