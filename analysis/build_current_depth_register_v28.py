"""Retain conservative Indian SECC reach from the original observed section."""
import csv, hashlib, io, json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v27 as previous
ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v28.json'
RULES='research/current-depth-rules-v28.json'
OUTPUT='research/current-depth-register-v28.json'
CSV='research/current-depth-register-v28.csv'
validate_reference=previous.validate_reference

def validate_context(row,root=ROOT):
    required={'entity_id':'current:indian-south-equatorial-countercurrent','metric':'reported_vertical_extent','evidence_kind':'original_observed_section_figure_presence','source_case_id':'indian-secc-hacker-1998-i9n-observed-100m','lower_bound_m':100,'lower_bound_operator':'>=','lower_bound_exclusive':False,'depth_basis':'inclusive_reach_from_observed_flow_presence_at_labeled_figure_depth','source_current_branch':'eastern_northeast_monsoon_SECC','source_section_id':'I9N_eastern_leg','section_nominal_longitude_degrees_east':95,'figure_reading_latitude_neighborhood_degrees_north':-6,'figure_location_precision':'approximate_neighborhood_not_digitized_position','campaign_window':{'start_date':'1995-02-06','end_date':'1995-03-21'},'phase_label':'northeast_monsoon','temporal_operator':'source_quasi_synoptic_cruise_section','source_figure_panel':'Figure2_bottom_observed_zonal_velocity','figure_reading_kind':'qualitative_flow_presence_at_labeled_depth','figure_reading_depth_m':100,'positive_zonal_velocity_direction':'eastward','figure_contour_interval_cm_s':10,'speed_digitization_performed':False,'statistical_significance_established':False,'branch_section_scope':'I9N_eastern_SECC_near_95E_6S','reference_route_id':'indian-south-equatorial-countercurrent-principal-reference-extent-v5','reference_route_projection_eligible':False,'route_scope_relationship':'regional_observation_east_of_selected_90E_route_handoff','source_access_scope':'original_author_institution_hosted_PDF_pixels_and_prose','same_source_width_reference_id':None,'independent_observation_count_claimed':False}
    for k,v in required.items():
        if row.get(k)!=v:raise ValueError('Source context changed: '+k)
    for k in ['section_sampling_month','section_sampling_window','calendar_months','climatology_years']:
        if row.get(k) is not None:raise ValueError('No exact section date or annual/seasonal envelope established')
    source=json.loads((root/SOURCE).read_bytes());audit=source['reference_route_scope_audit']
    route_file=audit['source_file']
    if hashlib.sha256((root/route_file).read_bytes()).hexdigest()!=audit['source_sha256']:raise ValueError('Route audit hash changed')
    route=next(r for r in json.loads((root/route_file).read_bytes())['records'] if r['id']==row['reference_route_id'])
    if audit['coordinates_lon_lat']!=route['coordinates_lon_lat'] or audit['projection_eligible'] is not False:raise ValueError('Route audit changed')
    east=max(p[0] for p in route['coordinates_lon_lat'])
    if east!=audit['route_easternmost_vertex_longitude_degrees_east'] or not east<row['section_nominal_longitude_degrees_east']:raise ValueError('Reassess eastern section/route relationship')

def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v27.py',RULES,SOURCE,'research/current-length-reference-extents-v5.json']:
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
    return {'schema':'osw.current-depth-register.v28','status':'INDIAN_SECC_OBSERVED_SECTION_CONSERVATIVE_REACH',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v28.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v28.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Eastern Indian SECC reach is an inclusive qualitative observed-figure presence inference at100m, outside the selected90E reference handoff. It is not flow thickness, a detected bottom, a model layer or seasonal envelope.',
            'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns += [p for p in ['source_section_id','section_nominal_longitude_degrees_east','figure_reading_latitude_neighborhood_degrees_north','figure_location_precision','campaign_window','figure_reading_kind','figure_reading_depth_m','positive_zonal_velocity_direction','figure_contour_interval_cm_s','speed_digitization_performed','statistical_significance_established'] if p not in columns]
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for raw in document['evidence']:
        row=dict(raw)
        if row.get('section_sampling_window'):
            row['section_window_start']=row['section_sampling_window']['start'];row['section_window_end']=row['section_sampling_window']['end']
        for key,value in list(row.items()):
            if isinstance(value,(dict,list)):row[key]=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        writer.writerow(row)
    return out.getvalue().encode('utf8')
