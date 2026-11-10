"""Retain an unlocated historical eastward Aleutian/Subarctic reach diagnostic."""
import csv, hashlib, io, json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v28 as previous
ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v29.json'
RULES='research/current-depth-rules-v29.json'
OUTPUT='research/current-depth-register-v29.json'
CSV='research/current-depth-register-v29.csv'
validate_reference=previous.validate_reference

def validate_context(row,root=ROOT):
    required={'entity_id':'current:aleutian','metric':'reported_vertical_extent','evidence_kind':'published_historical_geostrophic_profile_figure','source_case_id':'aleutian-tabata-1975-unlocated-subarctic-profile','lower_bound_m':500,'lower_bound_operator':'>=','lower_bound_exclusive':False,'depth_basis':'inclusive_reach_from_named_geostrophic_curve_at_labeled_depth','source_current_name':'Subarctic_Current','source_name_mapping':'historical_northernmost_eastward_Subarctic_or_Aleutian','source_nomenclature_scope':'Subarctic_combines_West_Wind_Drift_but_excludes_North_Pacific_Current','source_figure_panel':'Figure7b_left_group_Subarctic_curve','figure_reading_kind':'qualitative_nonzero_named_curve_at_labeled_depth','figure_reading_depth_m':500,'profile_location_recovered':False,'profile_observation_dates_recovered':False,'profile_geostrophic_reference_level_recovered':False,'temporal_operator':'undated_historical_illustrative_geostrophic_profile','speed_digitization_performed':False,'branch_section_scope':'unlocated_historical_eastward_Subarctic_Aleutian_profile','reference_route_id':'aleutian-principal-reference-extent-v5','reference_route_projection_eligible':False,'route_scope_relationship':'historical_name_matches_but_profile_unlocated','source_access_scope':'original_journal_issue_PDF_pixels_and_prose','same_source_width_reference_id':None,'independent_observation_count_claimed':False}
    for k,v in required.items():
        if row.get(k)!=v:raise ValueError('Source context changed: '+k)
    for k in ['section_sampling_month','section_sampling_window','calendar_months','climatology_years','section_latitude_degrees_north','section_longitude_degrees_east','geostrophic_reference_depth_m','geostrophic_reference_pressure_dbar','source_speed_fraction_of_surface']:
        if row.get(k) is not None:raise ValueError('Unrecovered profile context or adjacent curve substitution: '+k)

def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v28.py',RULES,SOURCE,'research/current-length-reference-extents-v5.json']:
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
    return {'schema':'osw.current-depth-register.v29','status':'HISTORICAL_EASTWARD_ALEUTIAN_SUBARCTIC_PROFILE_REACH',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v29.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v29.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Historical eastward Aleutian/Subarctic geostrophic-curve presence at500m is unlocated and undated, with source naming retained. It is not an absolute-velocity profile, physical boundary or projectable route depth.',
            'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns += [p for p in ['source_name_mapping','source_nomenclature_scope','profile_location_recovered','profile_observation_dates_recovered','profile_geostrophic_reference_level_recovered'] if p not in columns]
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for raw in document['evidence']:
        row=dict(raw)
        if row.get('section_sampling_window'):
            row['section_window_start']=row['section_sampling_window']['start'];row['section_window_end']=row['section_sampling_window']['end']
        for key,value in list(row.items()):
            if isinstance(value,(dict,list)):row[key]=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        writer.writerow(row)
    return out.getvalue().encode('utf8')
