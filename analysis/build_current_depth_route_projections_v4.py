"""Add an Atlantic EUC model-only mean-core connector with exact case matching."""
import copy
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import build_current_depth_route_projections_v3 as previous
from build_current_depth_route_projections_v2 import digest,interpolate
from build_current_depth_route_projections_v1 import position

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-route-projection-operator-v4.json'
OUTPUT='research/current-depth-route-projections-v4.json'
CSV='research/current-depth-route-projections-v4.csv'
CASE_SHA256='1248a8bc47578f9d7d66a43aa1844393ee77469bc7e941aa1cf3a9e5fac252c0'


def validate_case(case,references):
    if digest(case)!=CASE_SHA256:raise ValueError('Unreviewed Atlantic mean-core connector')
    expected_basis={'kind':'interannually_forced_hindcast_monthly_mean','output_years':[1990,2002]}
    for anchor in case['anchors']:
        ref=references[anchor['reference_id']]
        if ref!=anchor['source_context']:raise ValueError('Source mean definition changed')
        if ref['entity_id']!='current:atlantic-equatorial-undercurrent' or ref['metric']!='core_depth' or ref['model_product']!='FLAME_Hormann2007' or ref['model_time_basis']!=expected_basis:raise ValueError('Observed/spinup and hindcast means cannot be blended')
        if ref['section_longitude_degrees_east']!=anchor['nominal_lon_lat'][0] or ref['approximate_value_m']!=anchor['approximate_depth_descriptor_m']:raise ValueError('Wrong section/depth anchor')
        if ref['section_latitude_degrees_north'] is not None or ref['core_latitude_relation']!='slightly_south_of_equator_exact_latitude_not_reported':raise ValueError('Exact core latitude not established')


def project(case,eligibility):
    legs,_=previous.longitude_legs([a['nominal_lon_lat'] for a in case['anchors']]);total=legs[-1][1]
    anchors=[]
    for raw,distance in zip(case['anchors'],[0.0,total]):
        anchors.append({'reference_id':raw['reference_id'],'approximate_depth_descriptor_m':raw['approximate_depth_descriptor_m'],'distance_km':distance,'nominal_lon_lat':raw['nominal_lon_lat'],'source_core_latitude_relation':raw['source_context']['core_latitude_relation'],'exact_core_latitude_degrees_north':None,'coordinate_role':'nominal_equatorial_section_connector_not_exact_off_equatorial_core_axis'})
    distances={0.0,total};distances.update(i*50.0 for i in range(1,math.floor(total/50)+1));samples=[]
    for distance in sorted(distances):
        value,ids=interpolate(distance,anchors);matched=any(abs(distance-a['distance_km'])<1e-8 for a in anchors)
        samples.append({'distance_along_reference_route_km':round(distance,3),'editorial_route_lon_lat':[round(v,6) for v in position(legs,distance)],'projected_depth_descriptor_m':10*math.floor(value/10+0.5),'status':'source_model_mean_anchor_at_nominal_section' if matched else 'assumed_interpolation_between_source_model_mean_cores','source_reference_ids':ids,'model_product':'FLAME_Hormann2007','model_output_years':[1990,2002],'exact_core_latitude_degrees_north':None,'depth_uncertainty_m':None,'physical_thickness_m':None,'volume_eligible':False})
    return {'id':case['id'],'entity_id':case['entity_id'],'route_id':case['connector_id'],'route_file':OPERATOR,'geometry_role':'nominal_equatorial_section_connector_not_exact_core_axis','route_direction':'eastward_between_nominal_sections','metric':'projected_model_period_mean_core_depth_descriptor','source_metric':'core_depth','metric_interpretation':'Mean-model maximum eastward zonal velocity core depth, distinct from observed mean, spinup-model mean and physical layer thickness.','status':'regional_model_only_mean_core_interpolation_scenario','vertical_datum':'local_sea_surface_positive_down','campaign_window':None,'observed_common_record_period':None,'model_product':'FLAME_Hormann2007','model_time_basis':{'kind':'interannually_forced_hindcast_monthly_mean','output_years':[1990,2002]},'model_output_years':[1990,2002],'phase_label':None,'calendar_months':None,'annual_depth_range_m':None,'exact_core_latitude_degrees_north':None,'synoptic_full_route':False,'route_length_km':round(total,3),'supported_reference_distance_interval_km':[0.0,round(total,3)],'interpolated_editorial_route_fraction':1.0,'fraction_interpretation':'Fraction of this25degree nominal section connector only, not full Atlantic EUC coverage or physical axis verification.','display_depth_rounding_m':10,'anchors':[{**a,'distance_km':round(a['distance_km'],3)} for a in anchors],'samples':samples,'source_reference_ids':[a['reference_id'] for a in anchors],'excluded_comparison_reference_ids':case['excluded_comparison_reference_ids'],'assumptions':case['assumptions'],'eligibility':copy.deepcopy(eligibility),'physical_lower_boundary_profile':None,'physical_thickness_profile':None,'cross_section_area_km2':None,'volume_km3':None}


def build(root=ROOT):
    read=lambda p:json.loads((root/p).read_bytes());prior=previous.build(root)
    if prior!=read(previous.OUTPUT):raise ValueError('Prior profiles no longer reproduce')
    operator=read(OPERATOR);source=read(operator['depth_register_file']);refs={r['id']:r for r in source['evidence']}
    if any(operator['eligibility'].values()):raise ValueError('Unsupported geometry/volume/annual admission')
    validate_case(operator['case'],refs);projections=copy.deepcopy(prior['projections']);projections.append(project(operator['case'],operator['eligibility']))
    records=[]
    for raw in source['records']:
        row=copy.deepcopy(next(r for r in prior['records'] if r['entity_id']==raw['entity_id']));row['depth_reference_ids']=list(raw['depth_reference_ids'])
        row['projection_ids']=[p['id'] for p in projections if p['entity_id']==row['entity_id']];row['projection_status']='regional_assumed_interpolation_available' if row['projection_ids'] else 'not_yet_projected';records.append(row)
    files=set(prior['input_sha256'])|{OPERATOR,operator['depth_register_file'],previous.OUTPUT,previous.CSV,'analysis/build_current_depth_route_projections_v3.py'}
    owners=sum(bool(r['projection_ids']) for r in records)
    return {'schema':'osw.current-depth-route-projections.v4','status':'ATLANTIC_EUC_MODEL_PERIOD_CORE_TREND_WITH_OBSERVATIONS_SEPARATE','generator_file':'analysis/build_current_depth_route_projections_v4.py','generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_route_projections_v4.py').read_bytes()).hexdigest(),'input_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in sorted(files)},'previous_five_projection_records_preserved':projections[:5]==prior['projections'],'counts':{'catalog_identities':len(records),'identities_with_regional_projection_scenarios':owners,'identities_not_yet_projected':len(records)-owners,'regional_projection_scenarios':len(projections),'source_anchor_references':len({ref for p in projections for ref in p['source_reference_ids']}),'new_depth_measurements':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0},'interpretation':'Six regional scenarios retain distinct metric definitions and time bases. New Atlantic EUC70m35W to50m10W scenario uses only matching1990–2002 FLAME means, with observed and SPFLAME comparison values excluded from interpolation. Equatorial connector is nominal, because exact modeled off-equatorial core latitude is unavailable. No full current boundary, thickness or volume inferred.','records':records,'projections':projections,'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}


def csv_bytes(document):
    out=io.StringIO(newline='');fields=['projection_id','entity_id','route_id','geometry_role','metric','phase_label','calendar_months','campaign_start_month','campaign_end_month','model_product','model_time_basis','model_output_years','exact_core_latitude_degrees_north','distance_along_reference_route_km','longitude','latitude','projected_depth_descriptor_m','status','source_reference_ids','source_record_periods','common_record_period','depth_uncertainty_m','physical_thickness_m','volume_eligible']
    writer=csv.DictWriter(out,fieldnames=fields,lineterminator='\n');writer.writeheader()
    for p in document['projections']:
        for sample in p['samples']:
            row={k:v for k,v in sample.items() if k!='editorial_route_lon_lat'};window=p.get('campaign_window') or {}
            row.update(projection_id=p['id'],entity_id=p['entity_id'],route_id=p['route_id'],geometry_role=p.get('geometry_role','osw_editorial_reference_route'),metric=p['metric'],phase_label=p.get('phase_label'),calendar_months=json.dumps(p.get('calendar_months'),separators=(',',':')),campaign_start_month=window.get('start_month'),campaign_end_month=window.get('end_month'),model_product=sample.get('model_product',p.get('model_product')),model_time_basis=json.dumps(p.get('model_time_basis'),separators=(',',':')),model_output_years=json.dumps(sample.get('model_output_years',p.get('model_output_years')),separators=(',',':')),exact_core_latitude_degrees_north=sample.get('exact_core_latitude_degrees_north'),longitude=sample['editorial_route_lon_lat'][0],latitude=sample['editorial_route_lon_lat'][1],source_reference_ids=json.dumps(sample['source_reference_ids'],separators=(',',':')),source_record_periods=json.dumps(sample.get('source_record_periods'),sort_keys=True,separators=(',',':')),common_record_period=None)
            writer.writerow(row)
    return out.getvalue().encode('utf8')
