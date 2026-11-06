"""Append fixed-station EAC unfilled daily component isotach depths."""
import csv, hashlib, io, json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v45 as previous
ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v46.json'
RULES='research/current-depth-rules-v46.json'
OUTPUT='research/current-depth-register-v46.json'
CSV='research/current-depth-register-v46.csv'
MEMBER_OUTPUT='research/current-depth-member-index-v6.json'
MEMBERS='research/current-length-family-conventions-v1.json'
validate_reference=previous.validate_reference
EXPECTED_REFERENCE_SHA256 = {'eac-sloyan-daily-0500-2022-01-15-20cms': '1a71d699912ca58f5823d18aceea8ec1072b89a8d54605e26727344186db5f41', 'eac-sloyan-daily-2000-2022-01-15-20cms': '8e5574cccb3f67e453bfe7f8746d2fd5bcf4437f1302d9cb93cbe3fe69fcd06c', 'eac-sloyan-daily-3200-2022-01-15-5cms': 'a22bc42a8d502f3ef6ef4018a71e695dc263d45cda6c22bab0db30fcabc17eeb', 'eac-sloyan-daily-3200-2022-01-15-10cms': 'ade07b582a6153c6b051723dc1553bef34328cbad4529a03ad1289e809d51da8', 'eac-sloyan-daily-3200-2022-01-15-20cms': '66113ba87f379b0cae24760cfb496fe935e5f950626b25dc84c0b3412d48ff52', 'eac-sloyan-daily-3200-2022-07-15-5cms': '6a916aa543f8dbbf66c670df3131ed43f264ac19dd5fec51418970e7ddd50846', 'eac-sloyan-daily-3200-2022-07-15-10cms': 'fc43aa6b8926ec1d06ad3cc176acd4ed45dff88549d9d6b80d7d03e4de7c60f1', 'eac-sloyan-daily-3200-2022-07-15-20cms': '06a19985f32691ed069a09ddf2c7171bcfda291352a7069b6a3c630a220d54b4', 'eac-sloyan-daily-4200-2022-01-15-5cms': 'f0c6b837f53b7914101500f70bbb0cecd8e2da72796345bb1939461b4f28381b', 'eac-sloyan-daily-4200-2022-01-15-10cms': 'a7789b37a1d0ca9572a2a8166438827349f8756faf7075bc7b8d47953a4ddf34', 'eac-sloyan-daily-4200-2022-01-15-20cms': '36ede6d7b3d4b9d9b9a670b0283240bbb0fe57081a624abf73ce20ac55cfb38c', 'eac-sloyan-daily-4200-2022-07-15-5cms': '287e78cf61a6c4e058a0359b7d7da17b66b62de1eeafbdd8edc7b641c63bdcda', 'eac-sloyan-daily-4200-2022-07-15-10cms': 'b55a7a1615b36650e5f18c9d0204d21943c7c17f76df041978a7563e7dd81ebc', 'eac-sloyan-daily-4200-2022-07-15-20cms': '969e14cb051e1c574506c72982673441e3c7cc298bb7f7dd2635b5c5c2cb148b'}


def validate_context(row,root=ROOT):
    clean={k:v for k,v in row.items() if k not in ['source_file','source_pointer','source_sha256']}
    if hashlib.sha256(json.dumps(clean,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()!=EXPECTED_REFERENCE_SHA256.get(row['id']):raise ValueError('Unreviewed fixed station, daily filter, component frame or boundary support')


def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    extra_inputs=['research/source-data/eac-mooring-depth-benchmark-v1/candidate.json', 'research/eac-mooring-depth-benchmark-operator-v1.json', 'research/eac-mooring-depth-benchmark-source-review-v1.json', 'analysis/acquire_eac_mooring_depth_benchmark_v1.py', 'analysis/derive_eac_connected_layer_thickness_v1.py']
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v45.py',RULES,SOURCE,MEMBERS,MEMBER_OUTPUT]+extra_inputs:
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
    return {'schema':'osw.current-depth-register.v46','status':'FOURTEEN_FIXED_STATION_DATED_COMPONENT_ISOTACH_DEPTHS',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v46.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v46.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Fourteen EAC fixed-station lower component isotach depths retain six dated daily input profiles, five-day filtering, missing upper boundaries and native brackets. Offshore components are not promoted to main-jet thickness. No whole-route or volumetric claim.',
            'metadata_correction_file':prior.get('metadata_correction_file'),'metadata_correction_count':prior.get('metadata_correction_count',0),'member_depth_index_file':MEMBER_OUTPUT,'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


NEW_CSV_FIELDS = ['source_definition', 'source_url', 'source_citation', 'source_locator', 'source_case_id', 'source_profile_file', 'source_profile_sha256', 'source_profile_pointer', 'source_layer_pointer', 'source_station_id', 'mooring_lon_lat', 'source_daily_calendar_date', 'source_actual_daily_timestamp_utc', 'source_time_index', 'source_daily_filter_days', 'source_temporal_operator', 'source_velocity_quantity', 'source_velocity_field', 'source_SOM_filled_velocity_used', 'source_spatially_mapped_bottom_boundary_used', 'source_velocity_threshold_m_s', 'source_velocity_threshold_operator', 'source_computed_depth_before_display_rounding_m', 'source_native_bracketing_depths_m', 'source_core_depth_m', 'source_core_velocity_m_s', 'source_core_search_depth_interval_m', 'source_core_tie_policy', 'source_upper_boundary_status', 'source_lower_boundary_status', 'source_depth_interpolation', 'source_current_membership_role', 'source_velocity_uncertainty_field', 'source_component_uncertainty_is_depth_error', 'source_model_observation_colocation_or_identity_validated']

def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns += [p for p in NEW_CSV_FIELDS if p not in columns]
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for raw in document['evidence']:
        row=dict(raw)
        if row.get('section_sampling_window'):
            row['section_window_start']=row['section_sampling_window']['start'];row['section_window_end']=row['section_sampling_window']['end']
        for key,value in list(row.items()):
            if isinstance(value,(dict,list)):row[key]=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        writer.writerow(row)
    return out.getvalue().encode('utf8')
