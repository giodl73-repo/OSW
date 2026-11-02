"""Project a declared regional depth descriptor; never infer physical thickness."""
import csv
import hashlib
import io
import json
import math
from pathlib import Path
from pyproj import Geod

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-route-projection-operator-v1.json'
OUTPUT='research/current-depth-route-projections-v1.json'
CSV='research/current-depth-route-projections-v1.csv'
GEOD=Geod(ellps='WGS84')


def route_legs(points):
    if len(points)<2:raise ValueError('Two route vertices required')
    for lon,lat in points:
        if not math.isfinite(lon) or not math.isfinite(lat) or not -180<=lon<=180 or not -90<=lat<=90:raise ValueError('Invalid CRS84 vertex')
    differences=[b[1]-a[1] for a,b in zip(points,points[1:])]
    if not (all(d>0 for d in differences) or all(d<0 for d in differences)):raise ValueError('Pilot requires strictly monotonic latitude; ambiguous crossings forbidden')
    legs=[];distance=0.0
    for a,b in zip(points,points[1:]):
        azimuth,_,metres=GEOD.inv(*a,*b)
        if metres<=0:raise ValueError('Degenerate route leg')
        legs.append((distance,distance+metres/1000,a,b,azimuth));distance+=metres/1000
    return legs


def position(legs,distance):
    if not math.isfinite(distance) or distance<0 or distance>legs[-1][1]+1e-9:raise ValueError('Outside route')
    for start,end,a,b,azimuth in legs:
        if distance<=end+1e-9:
            if abs(distance-start)<1e-9:return list(a)
            if abs(distance-end)<1e-9:return list(b)
            lon,lat,_=GEOD.fwd(*a,azimuth,(distance-start)*1000)
            return [lon,lat]
    raise ValueError('Position unresolved')


def latitude_gate(legs,latitude):
    for start,end,a,b,_ in legs:
        if latitude==a[1]:return start,list(a)
        if latitude==b[1]:return end,list(b)
        if min(a[1],b[1])<latitude<max(a[1],b[1]):
            lo,hi=start,end;ascending=b[1]>a[1]
            for _ in range(48):
                mid=(lo+hi)/2;point=position(legs,mid)
                if (point[1]<latitude)==ascending:lo=mid
                else:hi=mid
            distance=(lo+hi)/2
            return distance,position(legs,distance)
    raise ValueError('Source latitude outside route: extrapolation forbidden')


def interpolate(distance,anchors):
    first,last=anchors
    if distance<first['distance_km']-1e-8 or distance>last['distance_km']+1e-8:return None
    fraction=(distance-first['distance_km'])/(last['distance_km']-first['distance_km'])
    return first['approximate_extent_depth_m']+fraction*(last['approximate_extent_depth_m']-first['approximate_extent_depth_m'])


def validate(operator,references,route):
    case=operator['case']
    if case['entity_id']!='current:west-india-coastal' or case['route_id']!='west-india-coastal-principal-reference-extent-v4':raise ValueError('Unreviewed identity or route')
    if case['reference_ids']!=['wicc-shetye-1991-northern-winter-reach','wicc-shetye-1991-southern-winter-reach']:raise ValueError('Unreviewed references')
    if case['campaign_window']!={'start_month':'1987-12','end_month':'1988-01'} or case['phase_label']!='northeast_monsoon':raise ValueError('Unreviewed period/phase')
    if case['anchors']!=[{'latitude_degrees_north':22,'approximate_extent_depth_m':400},{'latitude_degrees_north':10,'approximate_extent_depth_m':200}]:raise ValueError('Unreviewed source anchors')
    if operator['sample_spacing_km']!=50 or operator['display_depth_rounding_m']!=10 or operator['extrapolation']!='forbidden; unsupported route samples have null depth':raise ValueError('Operator changed')
    if operator['metric']!='projected_reported_vertical_extent_descriptor' or operator['vertical_datum']!='local_sea_surface_positive_down':raise ValueError('Descriptor is not physical thickness/boundary')
    if operator['uncertainty_m'] is not None or operator['annual_depth_range_m'] is not None or any(operator['eligibility'].values()):raise ValueError('Unsupported geometry/season/volume admission')
    if route['entity_id']!=case['entity_id'] or route['id']!=case['route_id'] or route['physical_axis_admitted']:raise ValueError('Wrong route identity/role')
    for reference_id,anchor in zip(case['reference_ids'],case['anchors']):
        ref=references[reference_id]
        expected={'entity_id':case['entity_id'],'metric':'reported_vertical_extent','approximate_value_m':anchor['approximate_extent_depth_m'],'section_latitude_degrees_north':anchor['latitude_degrees_north'],'campaign_window':case['campaign_window'],'phase_label':case['phase_label'],'source_url':case['source_url'],'evidence_kind':'published_observed_section_summary','vertical_datum':'local_sea_surface_positive_down','source_access_scope':'primary_publisher_abstract'}
        if any(ref.get(k)!=v for k,v in expected.items()):raise ValueError('Incompatible source case: '+reference_id)
        if any(ref.get(k) is not None for k in ['range_m','lower_bound_m','upper_bound_m','upper_boundary_m','lower_boundary_m','thickness_m','uncertainty_m']):raise ValueError('Only reviewed approximate extents supported')
        if ref.get('reference_route_projection_eligible') is False:raise ValueError('Source explicitly excludes route projection')


def build(root=ROOT):
    read=lambda p:json.loads((root/p).read_bytes())
    operator=read(OPERATOR);depth=read(operator['depth_register_file']);routes=read(operator['route_file']);lengths=read(operator['length_register_file'])
    case=operator['case'];references={r['id']:r for r in depth['evidence']}
    route=next(r for r in routes['records'] if r['id']==case['route_id'])
    length=next(r for r in lengths['records'] if r['entity_id']==case['entity_id'])
    if length['selected_route_id']!=case['route_id'] or length['record_file']!=operator['route_file']:raise ValueError('Selected route changed')
    validate(operator,references,route);legs=route_legs(route['coordinates_lon_lat']);total=legs[-1][1]
    anchors=[]
    for ref_id,anchor in zip(case['reference_ids'],case['anchors']):
        distance,point=latitude_gate(legs,anchor['latitude_degrees_north'])
        anchors.append(dict(anchor,reference_id=ref_id,distance_km=distance,editorial_route_lon_lat=point,coordinate_role='mapped_approximate_source_latitude_not_observed_profile_position'))
    anchors.sort(key=lambda a:a['distance_km'])
    if anchors[0]['distance_km']==anchors[1]['distance_km']:raise ValueError('Distinct anchors required')
    distances={0.0,total,*[a['distance_km'] for a in anchors],*[leg[0] for leg in legs]}
    distances.update(i*50.0 for i in range(1,math.floor(total/50)+1))
    samples=[]
    for distance in sorted(distances):
        value=interpolate(distance,anchors);matched=[a['reference_id'] for a in anchors if abs(a['distance_km']-distance)<1e-8]
        samples.append({'distance_along_reference_route_km':round(distance,3),'editorial_route_lon_lat':[round(v,6) for v in position(legs,distance)],'projected_extent_descriptor_m':None if value is None else 10*math.floor(value/10+0.5),'status':'unsupported_no_extrapolation' if value is None else 'source_anchor_mapped_to_editorial_route' if matched else 'assumed_linear_interpolation','source_reference_ids':matched if matched else list(case['reference_ids']) if value is not None else [],'depth_uncertainty_m':None,'physical_thickness_m':None,'volume_eligible':False})
    projection={'id':case['id'],'entity_id':case['entity_id'],'route_id':case['route_id'],'route_file':operator['route_file'],'route_direction':'stored_editorial_vertex_order_not_flow_direction','flow_direction_context':case['flow_direction_context'],'metric':operator['metric'],'vertical_datum':operator['vertical_datum'],'status':'regional_projected_descriptor_scenario_not_observed_profile','campaign_window':case['campaign_window'],'exact_section_dates_known':False,'synoptic_full_route':False,'phase_label':case['phase_label'],'route_length_km':round(total,3),'supported_reference_distance_interval_km':[round(a['distance_km'],3) for a in anchors],'interpolated_editorial_route_fraction':round((anchors[1]['distance_km']-anchors[0]['distance_km'])/total,6),'fraction_interpretation':'Share of this editorial drawing between source latitude gates; not physical current coverage or confidence.','anchors':[{**a,'distance_km':round(a['distance_km'],3),'editorial_route_lon_lat':[round(v,6) for v in a['editorial_route_lon_lat']]} for a in anchors],'samples':samples,'assumptions':operator['assumptions'],'eligibility':operator['eligibility'],'physical_lower_boundary_profile':None,'physical_thickness_profile':None,'cross_section_area_km2':None,'volume_km3':None,'annual_depth_range_m':None,'source_reference_ids':case['reference_ids']}
    records=[]
    for record in depth['records']:
        selected=record['entity_id']==case['entity_id']
        records.append({'entity_id':record['entity_id'],'name':record['name'],'identity_level':record['identity_level'],'depth_reference_ids':record['depth_reference_ids'],'projection_ids':[case['id']] if selected else [],'projection_status':'regional_assumed_interpolation_available' if selected else 'not_yet_projected','whole_route_physical_depth_profile':False,'volume_estimate_km3':None})
    inputs=[OPERATOR,operator['depth_register_file'],operator['route_file'],operator['length_register_file']]
    return {'schema':'osw.current-depth-route-projections.v1','status':'FIRST_REGIONAL_ALONG_ROUTE_DESCRIPTOR_SCENARIO','generator_file':'analysis/build_current_depth_route_projections_v1.py','generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_route_projections_v1.py').read_bytes()).hexdigest(),'input_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in inputs},'counts':{'catalog_identities':len(records),'identities_with_regional_projection_scenarios':1,'identities_not_yet_projected':len(records)-1,'regional_projection_scenarios':1,'source_anchor_references':2,'new_depth_measurements':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0},'interpretation':'Interpolated regional source depth descriptors on a declared reference drawing. Observations, mapped source anchors and assumed intermediate values remain distinct. Unknown outside support. No new physical boundary, thickness, annual envelope or volume.','records':records,'projections':[projection],'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}


def csv_bytes(document):
    out=io.StringIO(newline='');fields=['projection_id','entity_id','route_id','metric','campaign_start_month','campaign_end_month','distance_along_reference_route_km','longitude','latitude','projected_extent_descriptor_m','status','source_reference_ids','depth_uncertainty_m','physical_thickness_m','volume_eligible']
    writer=csv.DictWriter(out,fieldnames=fields,lineterminator='\n');writer.writeheader()
    for p in document['projections']:
        for sample in p['samples']:
            row={k:v for k,v in sample.items() if k!='editorial_route_lon_lat'}
            row.update(projection_id=p['id'],entity_id=p['entity_id'],route_id=p['route_id'],metric=p['metric'],campaign_start_month=p['campaign_window']['start_month'],campaign_end_month=p['campaign_window']['end_month'],longitude=sample['editorial_route_lon_lat'][0],latitude=sample['editorial_route_lon_lat'][1],source_reference_ids=json.dumps(sample['source_reference_ids'],separators=(',',':')))
            writer.writerow(row)
    return out.getvalue().encode('utf8')


if __name__=='__main__':
    result=build();(ROOT/OUTPUT).write_bytes((json.dumps(result,indent=2,ensure_ascii=False)+'\n').encode());(ROOT/CSV).write_bytes(csv_bytes(result));print(json.dumps(result['counts']))
