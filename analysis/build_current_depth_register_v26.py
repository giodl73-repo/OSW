"""Retain spatially scoped main southern Tsuchiya-jet core depths."""
import csv, hashlib, io, json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v25 as previous
ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v26.json'
RULES='research/current-depth-rules-v26.json'
OUTPUT='research/current-depth-register-v26.json'
CSV='research/current-depth-register-v26.csv'
validate_reference=previous.validate_reference

def validate_context(row,root=ROOT):
    common={'entity_id':'current:pacific-south-subsurface-countercurrent','metric':'core_depth','depth_basis':'source_reported_approximate_velocity_core_depth','source_current_branch':'main_SSCC','source_figure_pixels_used_for_value':False,'same_source_width_reference_id':None,'independent_observation_count_claimed':False}
    case=row['source_case_id']
    if case in ['pacific-sscc-rowe-2000-western-core-summary','pacific-sscc-rowe-2000-eastern-core-summary']:
        western='western' in case
        required={'approximate_value_m':300 if western else 150,'evidence_kind':'published_observational_core_position_summary','branch_section_scope':('western' if western else 'eastern')+'_main_southern_Tsuchiya_jet','section_longitude_degrees_east':None if western else -95,'section_latitude_degrees_north':-3 if western else None,'temporal_operator':'uneven_archive_core_position_summary','sampling_time_space_aliasing_possible':True,'source_access_scope':'primary_publisher_and_institutional_indexed_full_text'}
        if any(row.get(k) is not None for k in ['archive_observation_window','climatology_years']):raise ValueError('Exact regional archive years not established')
    elif case=='pacific-sscc-johnson-2002-140w-main-fitted-mean':
        required={'approximate_value_m':200,'evidence_kind':'published_isopycnal_fit_mean_core','branch_section_scope':'nominal_140W_main_southern_Tsuchiya_jet','section_longitude_degrees_east':-140,'section_latitude_degrees_north':-4.5,'temporal_operator':'isopycnal_mixed_layer_longitude_annual_SOI_fit_mean','archive_observation_window':{'start_month':'1985-06','end_month':'2000-12'},'fit_longitude_neighborhood_degrees':20,'fit_minimum_local_sections_exclusive':16,'annual_harmonic_included':True,'SOI_term_included':True,'source_access_scope':'original_institution_hosted_PDF_prose'}
        if row.get('climatology_years') is not None:raise ValueError('Archive window is not uniformly sampled climatology')
    else:raise ValueError('Unreviewed source case')
    for k in ['section_sampling_month','calendar_months','section_sampling_window']:
        if row.get(k) is not None:raise ValueError('No one dated section or seasonal envelope established')
    for k,v in dict(common,**required).items():
        if row.get(k)!=v:raise ValueError('Source context changed: '+k)

def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v25.py',RULES,SOURCE]:
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
    return {'schema':'osw.current-depth-register.v26','status':'PACIFIC_MAIN_SSCC_REGIONAL_CORE_DEPTHS',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v26.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v26.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Main southern Tsuchiya-jet core depths retain regional source cases and mean operators. They are not flow boundaries, a synoptic continuous profile or a seasonal envelope; source archives may overlap.',
            'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns += [p for p in ['source_current_branch','sampling_time_space_aliasing_possible','source_figure_pixels_used_for_value','archive_observation_window','fit_longitude_neighborhood_degrees','fit_minimum_local_sections_exclusive','annual_harmonic_included','SOI_term_included'] if p not in columns]
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for raw in document['evidence']:
        row=dict(raw)
        if row.get('section_sampling_window'):
            row['section_window_start']=row['section_sampling_window']['start'];row['section_window_end']=row['section_sampling_window']['end']
        for key,value in list(row.items()):
            if isinstance(value,(dict,list)):row[key]=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        writer.writerow(row)
    return out.getvalue().encode('utf8')
