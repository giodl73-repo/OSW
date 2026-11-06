"""Project a seasonal threshold-core vertical span without turning it into depth."""
import copy
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import build_current_depth_route_projections_v4 as previous
from build_current_depth_route_projections_v2 import digest,interpolate
from build_current_depth_route_projections_v1 import route_legs,position

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-route-projection-operator-v5.json'
OUTPUT='research/current-depth-route-projections-v5.json'
CSV='research/current-depth-route-projections-v5.csv'
CASE_SHA256='b5976d1db5570e196271cc4064c839cd9d65efe4638d2fd520fce1698192d193'


def validate_case(case,references):
    if digest(case)!=CASE_SHA256:raise ValueError('Unreviewed threshold-core span scenario')
    for anchor in case['anchors']:
        ref=references[anchor['reference_id']]
        if ref!=anchor['source_context']:raise ValueError('Normalized source context changed')
        expected={'entity_id':case['entity_id'],'metric':'core_vertical_thickness','vertical_datum':'not_applicable_thickness_distance','model_product':'BRAN2020','climatology_years':[2001,2018],'calendar_months':[3,4,5],'velocity_threshold_m_s':0.1,'velocity_threshold_operator':'>'}
        if any(ref.get(k)!=v for k,v in expected.items()):raise ValueError('Wrong quantity, product, season or threshold')
        if ref['approximate_value_m']!=anchor['approximate_core_vertical_span_m']:raise ValueError('Wrong source span')


def longitude_gate(legs,longitude):
    for start,end,a,b,_ in legs:
        if not a[0]<b[0]:raise ValueError('This gate operator requires increasing non-wrapping longitudes')
        if longitude==a[0]:return start,list(a)
        if longitude==b[0]:return end,list(b)
        if a[0]<longitude<b[0]:
            lo,hi=start,end
            for _ in range(48):
                mid=(lo+hi)/2
                if position(legs,mid)[0]<longitude:lo=mid
                else:hi=mid
            distance=(lo+hi)/2;return distance,position(legs,distance)
    raise ValueError('No longitude gate inside reference route')


def project(case,route,eligibility):
    legs=route_legs(route['coordinates_lon_lat']);total=legs[-1][1];anchors=[]
    for source_anchor in case['anchors']:
        distance,point=longitude_gate(legs,source_anchor['approximate_source_longitude_degrees_east'])
        anchors.append({'reference_id':source_anchor['reference_id'],'approximate_depth_descriptor_m':source_anchor['approximate_core_vertical_span_m'],'source_core_vertical_span_m':source_anchor['approximate_core_vertical_span_m'],'source_longitude_context_degrees_east':source_anchor['approximate_source_longitude_degrees_east'],'source_location_precision':'approximate_longitude_from_prose','distance_km':distance,'editorial_route_lon_lat':point,'coordinate_role':'exact_drawing_gate_for_approximate_source_longitude_not_observed_core_position'})
    anchors.sort(key=lambda a:a['distance_km']);distances={0.0,total,*[a['distance_km'] for a in anchors],*[leg[0] for leg in legs]}
    distances.update(i*50.0 for i in range(1,math.floor(total/50)+1));samples=[]
    low=min(a['source_core_vertical_span_m'] for a in anchors);high=max(a['source_core_vertical_span_m'] for a in anchors)
    for distance in sorted(distances):
        value,ids=interpolate(distance,anchors);matched=any(abs(distance-a['distance_km'])<1e-8 for a in anchors)
        displayed=None if value is None else value if matched else max(low,min(high,50*math.floor(value/50+0.5)))
        samples.append({'distance_along_reference_route_km':round(distance,3),'editorial_route_lon_lat':[round(v,6) for v in position(legs,distance)],'projected_depth_descriptor_m':None,'projected_core_vertical_span_m':displayed,'status':'unsupported_no_extrapolation' if value is None else 'source_threshold_core_span_anchor_mapped_to_reference_route' if matched else 'assumed_interpolation_of_threshold_core_vertical_span','source_reference_ids':ids,'depth_uncertainty_m':None,'core_span_uncertainty_m':None,'physical_thickness_m':None,'volume_eligible':False})
    exported_anchors=[]
    for anchor in anchors:
        row={k:v for k,v in anchor.items() if k!='approximate_depth_descriptor_m'}
        row['distance_km']=round(row['distance_km'],3);row['editorial_route_lon_lat']=[round(v,6) for v in row['editorial_route_lon_lat']];exported_anchors.append(row)
    return {'id':case['id'],'entity_id':case['entity_id'],'route_id':case['route_id'],'route_file':case['route_file'],'geometry_role':'osw_editorial_reference_route_with_approximate_source_longitude_gates','metric':'projected_threshold_core_vertical_span','source_metric':'core_vertical_thickness','quantity_kind':'vertical_distance_not_absolute_depth','vertical_datum':'not_applicable_thickness_distance','unit':'m','status':'regional_model_threshold_core_span_scenario','source_definition':'Maximum vertical range of zonal u>0.1m/s core at each longitude. A span need not be a fully occupied or contiguous water column.','velocity_threshold_m_s':0.1,'velocity_threshold_operator':'>','model_product':'BRAN2020','climatology_years':[2001,2018],'calendar_months':[3,4,5],'phase_label':'March–May','campaign_window':None,'annual_depth_range_m':None,'synoptic_full_route':False,'route_length_km':round(total,3),'supported_reference_distance_interval_km':[round(anchors[0]['distance_km'],3),round(anchors[-1]['distance_km'],3)],'interpolated_editorial_route_fraction':round((anchors[-1]['distance_km']-anchors[0]['distance_km'])/total,6),'fraction_interpretation':'Portion of the reference drawing between approximate74E/95E contexts, not full current coverage, uncertainty or annual occupancy.','source_reference_ids':[a['reference_id'] for a in anchors],'excluded_nonlocal_statistic_reference_ids':case['excluded_nonlocal_statistic_reference_ids'],'anchors':exported_anchors,'samples':samples,'intermediate_display_rounding_m':50,'source_anchors_preserved_without_rounding':True,'assumptions':case['assumptions'],'eligibility':copy.deepcopy(eligibility),'physical_lower_boundary_profile':None,'physical_thickness_profile':None,'cross_section_area_km2':None,'volume_km3':None}


def build(root=ROOT):
    read=lambda p:json.loads((root/p).read_bytes());prior=previous.build(root)
    if prior!=read(previous.OUTPUT):raise ValueError('Prior scenarios no longer reproduce')
    operator=read(OPERATOR);source=read(operator['depth_register_file']);refs={r['id']:r for r in source['evidence']}
    if any(operator['eligibility'].values()):raise ValueError('Unsupported geometry or volume admission')
    case=operator['case'];validate_case(case,refs)
    lengths=read('research/current-length-estimate-register-v1.json');length=next(r for r in lengths['records'] if r['entity_id']==case['entity_id'])
    if length['selected_route_id']!=case['route_id'] or length['record_file']!=case['route_file']:raise ValueError('Selected route changed')
    route=next(r for r in read(case['route_file'])['records'] if r['id']==case['route_id'])
    if route['physical_axis_admitted']:raise ValueError('Not an observed core axis')
    projections=copy.deepcopy(prior['projections']);projections.append(project(case,route,operator['eligibility']))
    records=copy.deepcopy(prior['records'])
    for row in records:
        row['projection_ids']=[p['id'] for p in projections if p['entity_id']==row['entity_id']];row['projection_status']='regional_assumed_interpolation_available' if row['projection_ids'] else 'not_yet_projected'
    files=set(prior['input_sha256'])|{OPERATOR,operator['depth_register_file'],case['route_file'],previous.OUTPUT,previous.CSV,'analysis/build_current_depth_route_projections_v4.py'}
    owners=sum(bool(r['projection_ids']) for r in records)
    return {'schema':'osw.current-depth-route-projections.v5','status':'FIRST_DISTANCE_TYPED_THRESHOLD_CORE_VERTICAL_SPAN_SCENARIO','generator_file':'analysis/build_current_depth_route_projections_v5.py','generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_route_projections_v5.py').read_bytes()).hexdigest(),'input_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in sorted(files)},'previous_six_projection_records_preserved':projections[:6]==prior['projections'],'counts':{'catalog_identities':len(records),'identities_with_regional_projection_scenarios':owners,'identities_not_yet_projected':len(records)-owners,'regional_projection_scenarios':len(projections),'source_anchor_references':len({ref for p in projections for ref in p['source_reference_ids']}),'new_depth_measurements':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0},'interpretation':'Six earlier depth/core/transport scenarios plus a distance-typed March–May BRAN threshold-core vertical-span scenario for Indian SEUC. Span is neither depth below sea surface nor full-flow thickness. Unknown outside74–95E support; no area/volume or annual envelope inferred.','records':records,'projections':projections,'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}


def csv_bytes(document):
    out=io.StringIO(newline='');fields=['projection_id','entity_id','route_id','geometry_role','metric','vertical_datum','model_product','model_time_basis','model_output_years','climatology_years','calendar_months','phase_label','campaign_start_month','campaign_end_month','distance_along_reference_route_km','longitude','latitude','projected_depth_descriptor_m','projected_core_vertical_span_m','status','source_reference_ids','source_record_periods','common_record_period','exact_core_latitude_degrees_north','depth_uncertainty_m','core_span_uncertainty_m','physical_thickness_m','volume_eligible']
    writer=csv.DictWriter(out,fieldnames=fields,lineterminator='\n');writer.writeheader()
    for p in document['projections']:
        for sample in p['samples']:
            row={k:v for k,v in sample.items() if k!='editorial_route_lon_lat'};window=p.get('campaign_window') or {}
            row.update(projection_id=p['id'],entity_id=p['entity_id'],route_id=p['route_id'],geometry_role=p.get('geometry_role','osw_editorial_reference_route'),metric=p['metric'],vertical_datum=p['vertical_datum'],model_product=sample.get('model_product',p.get('model_product')),model_time_basis=json.dumps(p.get('model_time_basis'),separators=(',',':')),model_output_years=json.dumps(sample.get('model_output_years',p.get('model_output_years')),separators=(',',':')),climatology_years=json.dumps(p.get('climatology_years'),separators=(',',':')),calendar_months=json.dumps(p.get('calendar_months'),separators=(',',':')),phase_label=p.get('phase_label'),campaign_start_month=window.get('start_month'),campaign_end_month=window.get('end_month'),longitude=sample['editorial_route_lon_lat'][0],latitude=sample['editorial_route_lon_lat'][1],source_reference_ids=json.dumps(sample['source_reference_ids'],separators=(',',':')),source_record_periods=json.dumps(sample.get('source_record_periods'),sort_keys=True,separators=(',',':')),common_record_period=None)
            writer.writerow(row)
    return out.getvalue().encode('utf8')
