"""Add source-paired EAC mean-mask depths/areas and a regional volume scenario."""
import copy
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import build_current_depth_route_projections_v5 as previous
from build_current_depth_route_projections_v2 import digest
from build_current_depth_route_projections_v1 import route_legs,latitude_gate,position

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-route-projection-operator-v6.json'
OUTPUT='research/current-depth-route-projections-v6.json'
CSV='research/current-depth-route-projections-v6.csv'
VOLUME_OUTPUT='research/current-regional-core-volume-scenarios-v1.json'
VOLUME_CSV='research/current-regional-core-volume-scenarios-v1.csv'
CASE_SHA256='d6cecba0c70af3332220e5ab4171d812f2644caeac7db78b70fc7e0ee08157b4'


def validate_case(case,references):
    if digest(case)!=CASE_SHA256:raise ValueError('Unreviewed EAC mean-mask scenario')
    expected_period={'start':'1994-01-01','end':'2016-10-01'}
    for anchor in case['anchors']:
        ref=references[anchor['reference_id']]
        if ref!=anchor['source_context']:raise ValueError('Source paired area/depth context changed')
        expected={'entity_id':'current:east-australian','metric':'core_lower_boundary_depth','model_product':'KerryRoughan2020_EAC_ROMS','model_simulation_period':expected_period,'source_signed_alongshore_isotach_m_s':-0.05,'reference_route_projection_eligible':True}
        if any(ref.get(k)!=v for k,v in expected.items()):raise ValueError('Incompatible mask, period or route scope')
        if ref['approximate_value_m']!=anchor['maximum_depth_m'] or ref['source_cross_section_area_km2']!=anchor['cross_section_area_km2']:raise ValueError('Depth and area must match the same section')
    for id in case['excluded_downstream_reference_ids']:
        if references[id]['reference_route_projection_eligible'] is not False:raise ValueError('Downstream system sections must remain excluded')


def load_route(root,case):
    read=lambda p:json.loads((root/p).read_bytes())
    length=next(r for r in read('research/current-length-estimate-register-v1.json')['records'] if r['entity_id']==case['entity_id'])
    if length['selected_route_id']!=case['route_id'] or length['record_file']!=case['catalog_file']:raise ValueError('Selected current extent changed')
    entry=next(r for r in read(case['catalog_file'])['candidates'] if r['id']==case['route_id'])
    raw=(root/case['route_file']).read_bytes();route=json.loads(raw)
    if entry['candidate_file']!=case['route_file'] or entry['candidate_sha256']!=hashlib.sha256(raw).hexdigest():raise ValueError('Candidate geometry pin mismatch')
    if route['current_id']!='east-australian' or route['geometry_role']!='osw_editorial_reference_route':raise ValueError('Wrong identity/geometry role')
    return route


def project(case,route,eligibility):
    legs=route_legs(route['coordinates_lon_lat']);total=legs[-1][1];anchors=[]
    for raw in case['anchors']:
        distance,point=latitude_gate(legs,raw['source_context']['section_latitude_degrees_north'])
        anchors.append({'reference_id':raw['reference_id'],'source_latitude_degrees_north':raw['source_context']['section_latitude_degrees_north'],'maximum_depth_m':raw['maximum_depth_m'],'cross_section_area_km2':raw['cross_section_area_km2'],'distance_km':distance,'editorial_route_lon_lat':point,'coordinate_role':'nominal_source_section_latitude_on_editorial_reference_route'})
    anchors.sort(key=lambda a:a['distance_km']);first,last=anchors
    distances={0.0,total,first['distance_km'],last['distance_km'],*[leg[0] for leg in legs]};distances.update(i*50.0 for i in range(1,math.floor(total/50)+1));samples=[]
    for distance in sorted(distances):
        supported=first['distance_km']-1e-8<=distance<=last['distance_km']+1e-8
        matched=[a for a in anchors if abs(distance-a['distance_km'])<1e-8]
        fraction=(distance-first['distance_km'])/(last['distance_km']-first['distance_km'])
        depth=first['maximum_depth_m']+fraction*(last['maximum_depth_m']-first['maximum_depth_m']) if supported else None
        area=first['cross_section_area_km2']+fraction*(last['cross_section_area_km2']-first['cross_section_area_km2']) if supported else None
        samples.append({'distance_along_reference_route_km':round(distance,3),'editorial_route_lon_lat':[round(v,6) for v in position(legs,distance)],'projected_depth_descriptor_m':None if depth is None else 10*math.floor(depth/10+0.5),'projected_core_cross_section_area_km2':None if area is None else round(area,1),'status':'unsupported_no_extrapolation' if not supported else 'source_mean_mask_section_depth_and_area_anchor' if matched else 'assumed_interpolation_of_same_source_mean_mask_sections','source_reference_ids':[] if not supported else [a['reference_id'] for a in matched] if matched else [a['reference_id'] for a in anchors],'depth_uncertainty_m':None,'physical_thickness_m':None,'volume_eligible':False})
    return {'id':case['id'],'entity_id':case['entity_id'],'route_id':case['route_id'],'route_file':case['route_file'],'geometry_role':'osw_editorial_reference_route_with_nominal_section_gates','metric':'projected_mean_isotach_core_maximum_depth','source_metric':'core_lower_boundary_depth','vertical_datum':'local_sea_surface_positive_down','status':'regional_model_mean_mask_depth_and_area_scenario','model_product':'KerryRoughan2020_EAC_ROMS','model_simulation_period':{'start':'1994-01-01','end':'2016-10-01'},'mean_mask_definition':case['mean_mask_definition'],'source_model_grid_rotation_clockwise_degrees':20,'phase_label':None,'calendar_months':None,'campaign_window':None,'annual_depth_range_m':None,'synoptic_full_route':False,'route_length_km':round(total,3),'supported_reference_distance_interval_km':[round(first['distance_km'],3),round(last['distance_km'],3)],'interpolated_editorial_route_fraction':round((last['distance_km']-first['distance_km'])/total,6),'fraction_interpretation':'Fraction of selected coastal-jet drawing between27.5S and30.3S only. No coverage of the rest of the current or downstream EAC extensions inferred.','anchors':[{**a,'distance_km':round(a['distance_km'],3),'editorial_route_lon_lat':[round(v,6) for v in a['editorial_route_lon_lat']]} for a in anchors],'samples':samples,'source_reference_ids':[a['reference_id'] for a in anchors],'excluded_downstream_reference_ids':case['excluded_downstream_reference_ids'],'assumptions':case['assumptions'],'regional_volume_scenario_file':VOLUME_OUTPUT,'regional_volume_scenario_id':'eac-kerry2020-27p5-to30p3s-reference-extrusion-v1','regional_volume_scenario_eligible':True,'eligibility':copy.deepcopy(eligibility),'physical_lower_boundary_profile':None,'physical_thickness_profile':None,'cross_section_area_km2':None,'volume_km3':None}


def integrate_area(anchors):
    if len(anchors)<2:raise ValueError('At least two area sections required')
    for a in anchors:
        if any(not isinstance(a[k],(int,float)) or isinstance(a[k],bool) or not math.isfinite(a[k]) or a[k]<0 for k in ['distance_km','cross_section_area_km2']):raise ValueError('Finite nonnegative kilometre distances and square-kilometre areas required')
    terms=[]
    for a,b in zip(anchors,anchors[1:]):
        distance=b['distance_km']-a['distance_km']
        if distance<=0:raise ValueError('Strictly ordered distinct area sections required')
        terms.append({'source_reference_ids':[a['reference_id'],b['reference_id']],'interval_start_km':a['distance_km'],'interval_end_km':b['distance_km'],'interval_length_km':distance,'left_area_km2':a['cross_section_area_km2'],'right_area_km2':b['cross_section_area_km2'],'volume_km3':0.5*(a['cross_section_area_km2']+b['cross_section_area_km2'])*distance})
    return sum(t['volume_km3'] for t in terms),terms


def build(root=ROOT):
    read=lambda p:json.loads((root/p).read_bytes());prior=previous.build(root)
    if prior!=read(previous.OUTPUT):raise ValueError('Prior scenarios no longer reproduce')
    operator=read(OPERATOR);source=read(operator['depth_register_file']);refs={r['id']:r for r in source['evidence']}
    if any(operator['eligibility'].values()):raise ValueError('No whole-current geometry/volume admission')
    case=operator['case'];validate_case(case,refs);route=load_route(root,case)
    projections=copy.deepcopy(prior['projections']);projections.append(project(case,route,operator['eligibility']))
    records=[]
    for raw in source['records']:
        row=copy.deepcopy(next(r for r in prior['records'] if r['entity_id']==raw['entity_id']));row['depth_reference_ids']=list(raw['depth_reference_ids']);row['projection_ids']=[p['id'] for p in projections if p['entity_id']==row['entity_id']];row['projection_status']='regional_assumed_interpolation_available' if row['projection_ids'] else 'not_yet_projected';records.append(row)
    files=set(prior['input_sha256'])|{OPERATOR,operator['depth_register_file'],case['route_file'],case['catalog_file'],previous.OUTPUT,previous.CSV,'analysis/build_current_depth_route_projections_v5.py'}
    owners=sum(bool(r['projection_ids']) for r in records)
    return {'schema':'osw.current-depth-route-projections.v6','status':'EAC_SAME_MASK_DEPTH_AREA_AND_REGIONAL_REFERENCE_VOLUME_SCENARIO','generator_file':'analysis/build_current_depth_route_projections_v6.py','generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_route_projections_v6.py').read_bytes()).hexdigest(),'input_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in sorted(files)},'previous_seven_projection_records_preserved':projections[:7]==prior['projections'],'counts':{'catalog_identities':len(records),'identities_with_regional_projection_scenarios':owners,'identities_not_yet_projected':len(records)-owners,'regional_projection_scenarios':len(projections),'source_anchor_references':len({ref for p in projections for ref in p['source_reference_ids']}),'new_depth_measurements':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0,'regional_reference_geometry_volume_scenarios':1},'interpretation':'Eight regional profiles. New EAC27.5–30.3S depth/area pairs come from one fixed model-mean velocity mask. Separate provisional volume scenario integrates source areas over editorial distance under explicit perpendicular-section/extrusion assumptions; it is not an observed, instantaneous or whole-current water volume.','regional_volume_scenario_file':VOLUME_OUTPUT,'records':records,'projections':projections,'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}


def build_volume_scenarios(document,root=ROOT):
    p=document['projections'][-1];value,terms=integrate_area(p['anchors'])
    row={'id':p['regional_volume_scenario_id'],'entity_id':p['entity_id'],'projection_id':p['id'],'status':'PROVISIONAL_REGIONAL_REFERENCE_GEOMETRY_VOLUME_SCENARIO','volume_kind':'extrusion_of_source_model_mean_isotach_section_areas','scope':'EAC coastal-jet reference interval between nominal27.5S and30.3S sections only. No extrapolation to full current or downstream extensions.','model_product':p['model_product'],'model_simulation_period':p['model_simulation_period'],'mean_mask_definition':p['mean_mask_definition'],'source_reference_ids':p['source_reference_ids'],'reference_route_id':p['route_id'],'reference_distance_interval_km':p['supported_reference_distance_interval_km'],'reference_interval_length_km':round(p['anchors'][-1]['distance_km']-p['anchors'][0]['distance_km'],3),'area_interpolation':'linear_between_source_sections_in_editorial_reference_distance','integration_formula':'V_km3 = sum((A_left_km2 + A_right_km2)/2 * delta_s_km)','computed_integral_km3':round(value,3),'scenario_volume_km3':1000*math.floor(value/1000+0.5),'display_rounding_km3':1000,'computational_terms':terms,'uncertainty_km3':None,'confidence_interval_km3':None,'orientation_assumption':'Reported source cross-shore areas are treated as normal sections of the editorial reference route for this extrusion scenario. Source grid is rotated20degrees clockwise; exact source section/route orientation correction is not recovered or applied.','shape_assumption':'Use source-reported areas directly; no rectangle, ellipse or offshore-distance-times-maximum-depth area inferred. Adjacent areas are connected by linear area interpolation.','temporal_interpretation':'Volume of an extruded long-term mean-field mask scenario, not mean of instantaneous threshold-core volumes, a dated observed water volume or an annual seasonal envelope.','whole_current_volume_estimate':False,'observed_water_volume':False,'mean_of_instantaneous_core_volumes':False,'physical_state_join_eligible':False,'global_total_eligible':False,'regional_scenario_admitted':True}
    files=[OUTPUT,OPERATOR,'research/current-depth-register-v36.json','analysis/build_current_depth_route_projections_v6.py']
    return {'schema':'osw.current-regional-core-volume-scenarios.v1','status':'FIRST_EXPLICIT_REGIONAL_MODEL_CORE_REFERENCE_VOLUME_SCENARIO','input_sha256':{f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in files},'counts':{'regional_reference_geometry_scenarios':1,'whole_current_volume_estimates':0,'observed_water_volume_estimates':0},'records':[row],'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}


def volume_csv_bytes(document):
    out=io.StringIO(newline='');fields=list(document['records'][0]);writer=csv.DictWriter(out,fieldnames=fields,lineterminator='\n');writer.writeheader()
    for raw in document['records']:
        row={k:json.dumps(v,sort_keys=True,separators=(',',':')) if isinstance(v,(dict,list)) else v for k,v in raw.items()};writer.writerow(row)
    return out.getvalue().encode('utf8')


def csv_bytes(document):
    # Preserve v5's export of prior quantities and append same-mask area/context.
    compatible=copy.deepcopy(document)
    for p in compatible['projections']:
        for sample in p['samples']:sample.pop('projected_core_cross_section_area_km2',None)
    prior_raw=previous.csv_bytes(compatible);reader=csv.DictReader(io.StringIO(prior_raw.decode('utf8')));columns=list(reader.fieldnames)
    rows=list(reader);columns += ['projected_core_cross_section_area_km2','model_simulation_period']
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader();i=0
    for p in document['projections']:
        for sample in p['samples']:
            row=rows[i];i+=1;row['projected_core_cross_section_area_km2']=sample.get('projected_core_cross_section_area_km2');row['model_simulation_period']=json.dumps(p.get('model_simulation_period'),separators=(',',':'));writer.writerow(row)
    return out.getvalue().encode('utf8')
