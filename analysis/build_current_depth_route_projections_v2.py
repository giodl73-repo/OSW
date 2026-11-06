"""Extend regional scenarios while retaining distinct depth diagnostic meanings."""
import copy
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import build_current_depth_route_projections_v1 as previous

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-route-projection-operator-v2.json'
OUTPUT='research/current-depth-route-projections-v2.json'
CSV='research/current-depth-route-projections-v2.csv'
CASE_DIGESTS = {'somali-sen-2022-winter-regional-depth-scenario-v1': '71433f7084573340a8516e3b8be60f2bbba4e598d70c9ff2eab1442de3b723d2', 'eicc-sen-2022-southward-core-depth-scenario-v1': '4bc8fd6f2f53dcd82922f1774c3bd17b3725fca6989699a5df5e22847f7ff858', 'agulhas-casal-2009-net-transport-zero-depth-scenario-v1': '1667effaa8d6ccb2683ce48dc499fe438aa2c5d9f7bc3d3e9467c442f01a1d89'}


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def validate_case(case,references):
    if case['id'] not in CASE_DIGESTS or digest(case)!=CASE_DIGESTS[case['id']]:raise ValueError('Unreviewed case contract')
    if len(case['anchors'])<2 or len(set(case['source_reference_ids']))!=len(case['anchors']):raise ValueError('Distinct anchor references required')
    for anchor in case['anchors']:
        ref=references[anchor['reference_id']]
        if ref!=anchor['source_context']:raise ValueError('Frozen source context changed')
        if ref['entity_id']!=case['entity_id'] or ref['metric']!=case['source_metric'] or ref['approximate_value_m']!=anchor['approximate_depth_descriptor_m'] or ref['section_latitude_degrees_north']!=anchor['latitude_degrees_north']:raise ValueError('Incompatible anchor')
        if ref.get('reference_route_projection_eligible') is False:raise ValueError('Explicit projection exclusion')
        if ref['source_url']!=case['source_url'] or ref['phase_label']!=case['phase_label'] or ref['calendar_months']!=case['calendar_months'] or ref.get('model_product')!=case['model_product'] or ref.get('model_time_basis')!=case['model_time_basis'] or ref.get('campaign_window')!=case['campaign_window']:raise ValueError('Mixed source phase/time basis')


def load_route(root,case,lengths):
    length=next(r for r in lengths['records'] if r['entity_id']==case['entity_id'])
    if length['selected_route_id']!=case['route_id'] or length['record_file']!=case['route_catalog_file']:raise ValueError('Selected route mismatch')
    raw=(root/case['geometry_file']).read_bytes();geometry=json.loads(raw)
    if case['geometry_file']==case['route_catalog_file']:
        route=next(r for r in geometry['records'] if r['id']==case['route_id'])
        if route['entity_id']!=case['entity_id'] or route['physical_axis_admitted']:raise ValueError('Wrong geometry identity/role')
    else:
        catalog=json.loads((root/case['route_catalog_file']).read_bytes())
        entry=next(r for r in catalog['candidates'] if r['id']==case['route_id'])
        if entry['candidate_file']!=case['geometry_file'] or entry['candidate_sha256']!=hashlib.sha256(raw).hexdigest():raise ValueError('Candidate geometry pin mismatch')
        if 'current:'+geometry['current_id']!=case['entity_id'] or geometry['geometry_role']!='osw_editorial_reference_route':raise ValueError('Wrong candidate identity/role')
        route=geometry
    return route


def interpolate(distance,anchors):
    if not math.isfinite(distance):raise ValueError('Finite route distance required')
    if len(anchors)<2 or any(a['distance_km']>=b['distance_km'] for a,b in zip(anchors,anchors[1:])):raise ValueError('Strictly ordered distinct gates required')
    if distance<anchors[0]['distance_km']-1e-8 or distance>anchors[-1]['distance_km']+1e-8:return None,[]
    for anchor in anchors:
        if abs(distance-anchor['distance_km'])<1e-8:return anchor['approximate_depth_descriptor_m'],[anchor['reference_id']]
    for a,b in zip(anchors,anchors[1:]):
        if a['distance_km']<distance<b['distance_km']:
            fraction=(distance-a['distance_km'])/(b['distance_km']-a['distance_km'])
            return a['approximate_depth_descriptor_m']+fraction*(b['approximate_depth_descriptor_m']-a['approximate_depth_descriptor_m']),[a['reference_id'],b['reference_id']]
    raise ValueError('Interpolation interval unresolved')


def project(case,route,eligibility):
    legs=previous.route_legs(route['coordinates_lon_lat']);total=legs[-1][1];anchors=[]
    for anchor in case['anchors']:
        distance,point=previous.latitude_gate(legs,anchor['latitude_degrees_north'])
        band=anchor['source_context'].get('section_longitude_band_degrees_east')
        if band and not band[0]<=point[0]<=band[1]:raise ValueError('Editorial gate outside source longitude support')
        anchors.append({'reference_id':anchor['reference_id'],'latitude_degrees_north':anchor['latitude_degrees_north'],'approximate_depth_descriptor_m':anchor['approximate_depth_descriptor_m'],'distance_km':distance,'editorial_route_lon_lat':point,'coordinate_role':'mapped_source_nominal_latitude_not_observed_profile_position','source_section_name':anchor['source_context'].get('section_name'),'source_case_id':anchor['source_context']['source_case_id']})
    anchors.sort(key=lambda a:a['distance_km'])
    distances={0.0,total,*[a['distance_km'] for a in anchors],*[leg[0] for leg in legs]}
    distances.update(i*50.0 for i in range(1,math.floor(total/50)+1));samples=[]
    for distance in sorted(distances):
        value,ids=interpolate(distance,anchors)
        matched=any(abs(distance-a['distance_km'])<1e-8 for a in anchors)
        samples.append({'distance_along_reference_route_km':round(distance,3),'editorial_route_lon_lat':[round(v,6) for v in previous.position(legs,distance)],'projected_depth_descriptor_m':None if value is None else 10*math.floor(value/10+0.5),'status':'unsupported_no_extrapolation' if value is None else 'source_anchor_mapped_to_editorial_route' if matched else 'assumed_linear_interpolation','source_reference_ids':ids,'depth_uncertainty_m':None,'physical_thickness_m':None,'volume_eligible':False})
    return {'id':case['id'],'entity_id':case['entity_id'],'route_id':case['route_id'],'route_file':case['geometry_file'],'route_direction':'stored_editorial_vertex_order_not_flow_direction','flow_direction_context':case['flow_direction_context'],'metric':case['projected_metric'],'source_metric':case['source_metric'],'metric_interpretation':case['metric_interpretation'],'route_phase_relation':case['route_phase_relation'],'vertical_datum':'local_sea_surface_positive_down','status':'regional_projected_descriptor_scenario_not_observed_profile','campaign_window':case['campaign_window'],'model_time_basis':case['model_time_basis'],'model_product':case['model_product'],'source_temporal_scope':case['source_temporal_scope'],'exact_section_dates_assigned':False,'synoptic_full_route':False,'phase_label':case['phase_label'],'calendar_months':case['calendar_months'],'calendar_months_role':'source_directional_mean_phase_not_annual_playback' if case['calendar_months'] else None,'route_length_km':round(total,3),'supported_reference_distance_interval_km':[round(anchors[0]['distance_km'],3),round(anchors[-1]['distance_km'],3)],'interpolated_editorial_route_fraction':round((anchors[-1]['distance_km']-anchors[0]['distance_km'])/total,6),'fraction_interpretation':'Share of this editorial drawing between source latitude gates; not physical current coverage or confidence.','anchors':[{**a,'distance_km':round(a['distance_km'],3),'editorial_route_lon_lat':[round(v,6) for v in a['editorial_route_lon_lat']]} for a in anchors],'samples':samples,'assumptions':['Source latitude contexts map to an editorial drawing; longitude is not a measured current axis.','Intermediate descriptor varies linearly in route distance only between adjacent gates; no extrapolation.','Source-defined regional metric and time basis remain distinct from observed full-flow thickness.'],'eligibility':copy.deepcopy(eligibility),'physical_lower_boundary_profile':None,'physical_thickness_profile':None,'cross_section_area_km2':None,'volume_km3':None,'annual_depth_range_m':None,'source_reference_ids':case['source_reference_ids']}


def build(root=ROOT):
    read=lambda p:json.loads((root/p).read_bytes())
    prior=previous.build(root)
    if prior!=read(previous.OUTPUT):raise ValueError('Prior projection no longer reproduces')
    operator=read(OPERATOR);depth=read(operator['depth_register_file']);lengths=read(operator['length_register_file'])
    if operator['sample_spacing_km']!=50 or operator['display_depth_rounding_m']!=10 or any(operator['eligibility'].values()):raise ValueError('Unsupported operator/eligibility')
    cases=operator['cases']
    if {c['id'] for c in cases}!=set(CASE_DIGESTS) or len(cases)!=3:raise ValueError('Reviewed three-case set required')
    refs={r['id']:r for r in depth['evidence']};projections=copy.deepcopy(prior['projections'])
    for p in projections:
        for sample in p['samples']:sample['projected_depth_descriptor_m']=sample.pop('projected_extent_descriptor_m')
    files={OPERATOR,previous.OUTPUT,previous.CSV,previous.OPERATOR,'analysis/build_current_depth_route_projections_v1.py',operator['depth_register_file'],operator['length_register_file']}
    for case in cases:
        validate_case(case,refs);route=load_route(root,case,lengths)
        projections.append(project(case,route,operator['eligibility']));files.update([case['geometry_file'],case['route_catalog_file']])
    records=copy.deepcopy(prior['records'])
    for record in records:
        record['projection_ids']=[p['id'] for p in projections if p['entity_id']==record['entity_id']]
        record['projection_status']='regional_assumed_interpolation_available' if record['projection_ids'] else 'not_yet_projected'
    owners=sum(bool(r['projection_ids']) for r in records)
    return {'schema':'osw.current-depth-route-projections.v2','status':'EXTENT_CORE_AND_NET_TRANSPORT_DIAGNOSTICS_SEPARATE','generator_file':'analysis/build_current_depth_route_projections_v2.py','generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_route_projections_v2.py').read_bytes()).hexdigest(),'input_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in sorted(files)},'previous_projection_numerical_semantics_preserved':True,'sample_value_schema_change':'v1 projected_extent_descriptor_m renamed projected_depth_descriptor_m in v2 samples; per-projection metric retains exact meaning. Frozen v1 files unchanged.','counts':{'catalog_identities':len(records),'identities_with_regional_projection_scenarios':owners,'identities_not_yet_projected':len(records)-owners,'regional_projection_scenarios':len(projections),'source_anchor_references':len({ref for p in projections for ref in p['source_reference_ids']}),'new_depth_measurements':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0},'interpretation':'Extent, core-depth and net-section-transport-zero descriptors are different metrics, with separate source definitions and temporal support. Piecewise interpolation on an editorial drawing adds assumed intermediate values, not new observations, physical thickness or volume.','records':records,'projections':projections,'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}


def csv_bytes(document):
    out=io.StringIO(newline='');fields=['projection_id','entity_id','route_id','metric','phase_label','calendar_months','campaign_start_month','campaign_end_month','model_product','model_time_basis','distance_along_reference_route_km','longitude','latitude','projected_depth_descriptor_m','status','source_reference_ids','depth_uncertainty_m','physical_thickness_m','volume_eligible']
    writer=csv.DictWriter(out,fieldnames=fields,lineterminator='\n');writer.writeheader()
    for p in document['projections']:
        for sample in p['samples']:
            row={k:v for k,v in sample.items() if k!='editorial_route_lon_lat'};window=p.get('campaign_window') or {}
            row.update(projection_id=p['id'],entity_id=p['entity_id'],route_id=p['route_id'],metric=p['metric'],phase_label=p.get('phase_label'),calendar_months=json.dumps(p.get('calendar_months'),separators=(',',':')),campaign_start_month=window.get('start_month'),campaign_end_month=window.get('end_month'),model_product=p.get('model_product'),model_time_basis=json.dumps(p.get('model_time_basis'),separators=(',',':')),longitude=sample['editorial_route_lon_lat'][0],latitude=sample['editorial_route_lon_lat'][1],source_reference_ids=json.dumps(sample['source_reference_ids'],separators=(',',':')))
            writer.writerow(row)
    return out.getvalue().encode('utf8')
