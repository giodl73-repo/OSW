"""Retain threshold-qualified regional NEC reach outside the selected route."""
import csv, hashlib, io, json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v26 as previous
ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v27.json'
RULES='research/current-depth-rules-v27.json'
OUTPUT='research/current-depth-register-v27.json'
CSV='research/current-depth-register-v27.csv'
validate_reference=previous.validate_reference

def validate_context(row,root=ROOT):
    required={'entity_id':'current:atlantic-north-equatorial','metric':'reported_vertical_extent','evidence_kind':'published_observation_model_comparison','source_case_id':'atlantic-nec-stramma-2005-northern-band-comparison','lower_bound_m':100,'lower_bound_operator':'>','lower_bound_exclusive':True,'depth_basis':'source_strict_threshold_qualified_reach_statement','source_current_branch':'northern_NEC_band','section_longitude_degrees_east':-27,'section_latitude_lower_exclusive_degrees_north':22,'section_latitude_degrees_north':None,'source_speed_condition':{'component':'westward_zonal_speed','operator':'>','value':0.1,'unit':'m_s-1'},'observational_section_window':{'start_month':'2003-07','end_month':'2003-08'},'model_phase_label':'July','model_elapsed_year':9,'branch_section_scope':'northern_NEC_band_north_of_22N','temporal_operator':'source_observed_section_and_model_month_comparison','reference_route_id':'atlantic-nec-basin-reference-extent-v1','reference_route_projection_eligible':False,'route_scope_relationship':'regional_northern_band_outside_selected_southern_reference_route','source_access_scope':'primary_publisher_full_HTML_prose','same_source_width_reference_id':None,'independent_observation_count_claimed':False}
    for k,v in required.items():
        if row.get(k)!=v:raise ValueError('Source context changed: '+k)
    for k in ['section_sampling_month','calendar_months','climatology_years','section_sampling_window']:
        if row.get(k) is not None:raise ValueError('No exact single-month observation or annual climatology established')
    source=json.loads((root/SOURCE).read_bytes());audit=source['reference_route_scope_audit']
    route_file=audit['source_file']
    if hashlib.sha256((root/route_file).read_bytes()).hexdigest()!=audit['source_sha256']:raise ValueError('Route audit hash changed')
    route=next(r for r in json.loads((root/route_file).read_bytes())['records'] if r['id']==row['reference_route_id'])
    if audit['coordinates_lon_lat']!=route['coordinates_lon_lat'] or audit['projection_eligible'] is not False:raise ValueError('Route audit changed')
    if not max(p[1] for p in route['coordinates_lon_lat'])<row['section_latitude_lower_exclusive_degrees_north']:raise ValueError('Reassess regional branch/route relationship')

def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v26.py',RULES,SOURCE,'research/current-length-reference-extents-v1.json']:
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
    return {'schema':'osw.current-depth-register.v27','status':'ATLANTIC_NEC_NORTHERN_BAND_THRESHOLD_REACH',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v27.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v27.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Northern Atlantic NEC threshold-qualified reach is regional context outside the selected reference route; a strict lower bound is not a physical flow bottom or an annual envelope.',
            'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns += [p for p in ['section_latitude_lower_exclusive_degrees_north','source_speed_condition','observational_section_window','model_phase_label','model_elapsed_year','reference_route_id','reference_route_projection_eligible','route_scope_relationship'] if p not in columns]
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for raw in document['evidence']:
        row=dict(raw)
        if row.get('section_sampling_window'):
            row['section_window_start']=row['section_sampling_window']['start'];row['section_window_end']=row['section_sampling_window']['end']
        for key,value in list(row.items()):
            if isinstance(value,(dict,list)):row[key]=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        writer.writerow(row)
    return out.getvalue().encode('utf8')
