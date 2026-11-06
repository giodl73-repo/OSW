"""Connect equatorial observing sites without inferring a basin-wide flow axis."""
import copy
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import build_current_depth_route_projections_v2 as previous
from build_current_depth_route_projections_v1 import GEOD,position

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-route-projection-operator-v3.json'
OUTPUT='research/current-depth-route-projections-v3.json'
CSV='research/current-depth-route-projections-v3.csv'
CASE_SHA256='66fa2ea57a61d2bb630714e1442b11d493e55af23a718efb529bf2602ce19767'


def validate_case(case,references):
    if previous.digest(case)!=CASE_SHA256:raise ValueError('Unreviewed observing-site connector contract')
    for anchor in case['anchors']:
        ref=references[anchor['reference_id']]
        if ref!=anchor['source_context']:raise ValueError('Source site, dates or selected-level definition changed')
        if ref['entity_id']!=case['entity_id'] or ref['metric']!='core_depth' or ref['section_latitude_degrees_north']!=0 or ref['section_longitude_degrees_east']!=anchor['nominal_lon_lat'][0] or ref['approximate_value_m']!=anchor['approximate_depth_descriptor_m']:raise ValueError('Incompatible equatorial core anchor')
        if not ref['source_record_period_has_gaps'] or ref['ADCP_velocities_assimilated_in_ECCOv4r4']:raise ValueError('Unreviewed observation/model relationship')


def longitude_legs(points):
    if len(points)<2:raise ValueError('Two or more nominal sites required')
    unwrapped=[points[0][0]];legs=[];distance=0.0
    for lon,lat in points:
        if not math.isfinite(lon) or not -180<=lon<=180 or lat!=0:raise ValueError('Only valid nominal equatorial sites supported')
    for a,b in zip(points,points[1:]):
        delta=(b[0]-a[0]+180)%360-180
        if not 0<delta<180:raise ValueError('Distinct eastward minor-arc site sequence required')
        unwrapped.append(unwrapped[-1]+delta)
        azimuth,_,metres=GEOD.inv(*a,*b)
        legs.append((distance,distance+metres/1000,a,b,azimuth));distance+=metres/1000
    return legs,unwrapped


def project(case,eligibility):
    points=[a['nominal_lon_lat'] for a in case['anchors']];legs,unwrapped=longitude_legs(points)
    anchors=[]
    distances=[leg[0] for leg in legs]+[legs[-1][1]]
    for anchor,distance,longitude in zip(case['anchors'],distances,unwrapped):
        anchors.append({'reference_id':anchor['reference_id'],'approximate_depth_descriptor_m':anchor['approximate_depth_descriptor_m'],'distance_km':distance,'nominal_lon_lat':anchor['nominal_lon_lat'],'unwrapped_longitude_degrees_east':longitude,'source_record_period':anchor['source_context']['source_record_period'],'source_record_period_has_gaps':True,'coordinate_role':'nominal_observing_site_not_instantaneous_current_axis'})
    total=legs[-1][1];sample_distances={0.0,total,*distances}
    sample_distances.update(i*50.0 for i in range(1,math.floor(total/50)+1));samples=[]
    for distance in sorted(sample_distances):
        value,ids=previous.interpolate(distance,anchors)
        matched=any(abs(a['distance_km']-distance)<1e-8 for a in anchors)
        samples.append({'distance_along_reference_route_km':round(distance,3),'editorial_route_lon_lat':[round(v,6) for v in position(legs,distance)],'projected_depth_descriptor_m':5*math.floor(value/5+0.5),'status':'source_anchor_at_nominal_observing_site' if matched else 'assumed_linear_interpolation_between_noncontemporaneous_record_means','source_reference_ids':ids,'source_record_periods':{a['reference_id']:a['source_record_period'] for a in anchors if a['reference_id'] in ids},'depth_uncertainty_m':None,'physical_thickness_m':None,'volume_eligible':False})
    return {'id':case['id'],'entity_id':case['entity_id'],'route_id':case['connector_id'],'route_file':OPERATOR,'geometry_role':'nominal_observing_site_connector_not_selected_whole_current_route','route_direction':'eastward_between_nominal_equatorial_sites','metric':'projected_comparison_selected_core_level_descriptor','source_metric':'core_depth','metric_interpretation':case['metric_interpretation'],'status':'regional_noncontemporaneous_core_level_scenario','vertical_datum':'local_sea_surface_positive_down','campaign_window':None,'common_record_period':None,'common_period_reanalysis_performed':False,'source_record_periods':{a['reference_id']:a['source_record_period'] for a in anchors},'phase_label':None,'calendar_months':None,'synoptic_full_route':False,'route_length_km':round(total,3),'supported_reference_distance_interval_km':[0.0,round(total,3)],'interpolated_editorial_route_fraction':1.0,'fraction_interpretation':'All of the newly declared observing-site connector lies between source sites. This is not full Pacific EUC coverage, a traced physical axis or a fraction of the published14000km extent.','full_current_length_km':None,'published_length_record_unchanged':True,'display_depth_rounding_m':5,'anchors':[{**a,'distance_km':round(a['distance_km'],3)} for a in anchors],'samples':samples,'assumptions':case['assumptions'],'eligibility':copy.deepcopy(eligibility),'physical_lower_boundary_profile':None,'physical_thickness_profile':None,'cross_section_area_km2':None,'volume_km3':None,'annual_depth_range_m':None,'source_reference_ids':[a['reference_id'] for a in anchors]}


def build(root=ROOT):
    read=lambda p:json.loads((root/p).read_bytes())
    prior=previous.build(root)
    if prior!=read(previous.OUTPUT):raise ValueError('Previous scenarios no longer reproduce')
    operator=read(OPERATOR);source=read(operator['depth_register_file']);refs={r['id']:r for r in source['evidence']}
    if any(operator['eligibility'].values()):raise ValueError('Unsupported geometry/volume/annual admission')
    validate_case(operator['case'],refs);projections=copy.deepcopy(prior['projections'])
    projections.append(project(operator['case'],operator['eligibility']))
    records=[]
    for source_row in source['records']:
        row=copy.deepcopy(next(r for r in prior['records'] if r['entity_id']==source_row['entity_id']))
        row['depth_reference_ids']=list(source_row['depth_reference_ids'])
        row['projection_ids']=[p['id'] for p in projections if p['entity_id']==row['entity_id']]
        row['projection_status']='regional_assumed_interpolation_available' if row['projection_ids'] else 'not_yet_projected';records.append(row)
    files=set(prior['input_sha256'])|{OPERATOR,operator['depth_register_file'],previous.OUTPUT,previous.CSV,'analysis/build_current_depth_route_projections_v2.py'}
    return {'schema':'osw.current-depth-route-projections.v3','status':'PACIFIC_EUC_OBSERVING_SITE_CORE_CONNECTOR_WITH_DISTINCT_PERIODS','generator_file':'analysis/build_current_depth_route_projections_v3.py','generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_route_projections_v3.py').read_bytes()).hexdigest(),'input_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in sorted(files)},'previous_four_projection_records_preserved':projections[:4]==prior['projections'],'counts':{'catalog_identities':len(records),'identities_with_regional_projection_scenarios':5,'identities_not_yet_projected':106,'regional_projection_scenarios':5,'source_anchor_references':14,'new_depth_measurements':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0},'interpretation':'Four earlier metric-specific scenarios plus a Pacific EUC nominal observing-site connector across the date line. Comparison-selected core levels retain per-site gapped record windows. Interpolation is assumed, not a common-period diagnosed physical profile. No full-current length, boundary, thickness, annual envelope or volume admission.','records':records,'projections':projections,'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}


def csv_bytes(document):
    out=io.StringIO(newline='');fields=['projection_id','entity_id','route_id','geometry_role','metric','phase_label','calendar_months','campaign_start_month','campaign_end_month','model_product','model_time_basis','distance_along_reference_route_km','longitude','latitude','projected_depth_descriptor_m','status','source_reference_ids','source_record_periods','common_record_period','depth_uncertainty_m','physical_thickness_m','volume_eligible']
    writer=csv.DictWriter(out,fieldnames=fields,lineterminator='\n');writer.writeheader()
    for p in document['projections']:
        for sample in p['samples']:
            row={k:v for k,v in sample.items() if k!='editorial_route_lon_lat'};window=p.get('campaign_window') or {}
            row.update(projection_id=p['id'],entity_id=p['entity_id'],route_id=p['route_id'],geometry_role=p.get('geometry_role','osw_editorial_reference_route'),metric=p['metric'],phase_label=p.get('phase_label'),calendar_months=json.dumps(p.get('calendar_months'),separators=(',',':')),campaign_start_month=window.get('start_month'),campaign_end_month=window.get('end_month'),model_product=p.get('model_product'),model_time_basis=json.dumps(p.get('model_time_basis'),separators=(',',':')),longitude=sample['editorial_route_lon_lat'][0],latitude=sample['editorial_route_lon_lat'][1],source_reference_ids=json.dumps(sample['source_reference_ids'],separators=(',',':')),source_record_periods=json.dumps(sample.get('source_record_periods'),sort_keys=True,separators=(',',':')),common_record_period=None)
            writer.writerow(row)
    return out.getvalue().encode('utf8')
