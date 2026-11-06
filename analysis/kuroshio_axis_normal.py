"""Independent normal intersections of retained model axis/boundary curves."""
from collections import Counter
from datetime import date, timedelta
import json
import math
from statistics import median

import netCDF4
import numpy as np

import kuroshio_wang_dimensions as base

ROOT=base.ROOT
FILE='research/kuroshio-wang-2024-axis-normal-spans.json'
FIGURE='figures/kuroshio-wang-2024-axis-normal-spans.svg'
PROTOCOL='plans/kuroshio-axis-normal-width-protocol-v1.md'
OPERATOR='analysis/kuroshio_axis_normal.py'
WINDOWS=(7,14,28)
EPS=1e-8


def lerp(a,b,t):
    return [a[k]+t*(b[k]-a[k]) for k in (0,1)]


def walk(points, position, direction, remaining):
    """Walk source order with geodesic leg lengths and explicit linear positions."""
    while remaining>1e-10:
        if direction>0:
            end=math.floor(position+1e-10)+1
        else:
            end=math.ceil(position-1e-10)-1
        if end<0 or end>=len(points):return None,'tangent_reaches_source_endpoint'
        segment=min(end,math.floor(position)) if direction>0 else end
        if not 0<=segment<len(points)-1:return None,'tangent_reaches_source_endpoint'
        a,b=points[segment:segment+2]
        if not base.valid(a) or not base.valid(b):return None,'tangent_missing_source_vertex'
        if base.distance(a,b)>50:return None,'tangent_source_segment_exceeds_50km'
        current=lerp(a,b,position-segment)
        length=base.distance(current,points[end])
        if length<1e-10:
            position=float(end);continue
        if remaining<=length:
            t=remaining/length
            return {'point':lerp(current,points[end],t),
                    'source_position':position+t*(end-position)},None
        remaining-=length;position=float(end)
    i=min(math.floor(position),len(points)-2)
    return {'point':lerp(*points[i:i+2],position-i),'source_position':position},None


def samples(points):
    """Per-original-segment samples; missing source vertices never connect."""
    a=[];b=[];segments=[];lo=[];hi=[];lengths=[]
    for i,(first,last) in enumerate(zip(points,points[1:])):
        if not base.valid(first) or not base.valid(last):continue
        length=base.distance(first,last)
        pieces=max(1,math.ceil(length)) if length<=50 else 1
        for j in range(pieces):
            t0,t1=j/pieces,(j+1)/pieces
            a.append(lerp(first,last,t0));b.append(lerp(first,last,t1))
            segments.append(i);lo.append(t0);hi.append(t1);lengths.append(length)
    return {'a':np.asarray(a,dtype=float).reshape((-1,2)),
            'b':np.asarray(b,dtype=float).reshape((-1,2)),
            'segment':segments,'lo':lo,'hi':hi,'source_segment_km':lengths}


def east_north(origin,points):
    if not len(points):return np.zeros((0,2))
    az,_,metres=base.GEOD.inv(np.full(len(points),origin[0]),np.full(len(points),origin[1]),points[:,0],points[:,1])
    radians=np.radians(az);km=np.asarray(metres)/1000
    return np.column_stack((km*np.sin(radians),km*np.cos(radians)))


def project(origin,point,heading):
    az,_,metres=base.GEOD.inv(*origin,*point)
    angle=math.radians(az-heading)
    return metres/1000*math.sin(angle),metres/1000*math.cos(angle)


def normal_crossings(points,prepared,origin,heading):
    d=math.radians(heading)
    ya=prepared['ea'][:,0]*math.sin(d)+prepared['ea'][:,1]*math.cos(d)
    yb=prepared['eb'][:,0]*math.sin(d)+prepared['eb'][:,1]*math.cos(d)
    overlap=bool(np.any((abs(ya)<=EPS)&(abs(yb)<=EPS)))
    candidates=np.flatnonzero((ya*yb<0)|(abs(ya)<=EPS)|(abs(yb)<=EPS))
    found=[]
    for index in candidates:
        i=prepared['segment'][index];a,b=points[i:i+2]
        t0,t1=prepared['lo'][index],prepared['hi'][index]
        y0,y1=float(ya[index]),float(yb[index])
        if abs(y0)<=EPS and abs(y1)<=EPS:continue
        if abs(y0)<=EPS:t=t0
        elif abs(y1)<=EPS:t=t1
        else:
            for _ in range(40):
                middle=(t0+t1)/2
                _,ym=project(origin,lerp(a,b,middle),heading)
                if y0*ym<=0:t1=middle
                else:t0=middle;y0=ym
            t=(t0+t1)/2
        position=i+t
        if any(abs(position-r['source_position'])<1e-9 for r in found):continue
        point=lerp(a,b,t);x,y=project(origin,point,heading)
        found.append({'point':point,'source_position':position,
                      'source_segment':i,'fraction_from_segment_start':t,
                      'source_segment_km':prepared['source_segment_km'][index],
                      'signed_normal_offset_km':x,'normal_residual_m':abs(y)*1000})
    return found,overlap


def prepare(curves,latitude):
    gates,overlap=base.crossings(curves['axis'],latitude)
    result={'axis_crossing_count':len(gates),'gate':None,'axis_gate_candidates':gates}
    if overlap:return {**result,'status':'axis_gate_overlap'}
    if len(gates)!=1:return {**result,'status':'axis_gate_missing_or_multiple'}
    gate=gates[0];result['gate']=gate
    if gate['segment_km']>50:return {**result,'status':'axis_gate_source_segment_exceeds_50km'}
    for kind in ('left','right'):
        sampled=samples(curves[kind]);sampled['ea']=east_north(gate['point'],sampled['a']);sampled['eb']=east_north(gate['point'],sampled['b'])
        result[kind]=sampled
    return {**result,'status':'ready'}


def measure(curves,latitude,window,prepared=None):
    context=prepare(curves,latitude) if prepared is None else prepared
    out={'latitude':latitude,'tangent_half_window_km':window,'span_km':None,
         'axis_crossing_count':context['axis_crossing_count'],'gate':context['gate'],
         'boundary_fallback_occurred':None,'threshold_attained':None,'physical_uncertainty_km':None}
    if context['gate'] is None:out['axis_gate_candidates']=context['axis_gate_candidates']
    if context['status']!='ready':return {**out,'status':context['status']}
    gate=context['gate'];origin=gate['point'];tangent=[]
    for direction in (-1,1):
        point,error=walk(curves['axis'],gate['position'],direction,window)
        if error:return {**out,'status':error}
        tangent.append(point)
    out['tangent_endpoints']=tangent
    if tangent[1]['point'][1]<=tangent[0]['point'][1]:return {**out,'status':'reversed_local_axis_latitude_direction'}
    heading=base.GEOD.inv(*tangent[0]['point'],*tangent[1]['point'])[0]%360
    out.update(axis_tangent_azimuth_degrees=heading,right_normal_azimuth_degrees=(heading+90)%360)
    edges={};overlaps=[];counts={};ambiguous={}
    for kind in ('left','right'):
        crossings,overlap=normal_crossings(curves[kind],context[kind],origin,heading)
        counts[kind]=len(crossings)
        if overlap:overlaps.append(kind)
        if len(crossings)==1:edges[kind]=crossings[0]
        elif crossings:ambiguous[kind]=crossings
    out.update(boundary_crossing_counts=counts,normal_overlap_curves=overlaps,edges=edges)
    if ambiguous:out['ambiguous_boundary_candidates']=ambiguous
    if overlaps:return {**out,'status':'boundary_normal_overlap'}
    if any(v!=1 for v in counts.values()):return {**out,'status':'boundary_crossing_missing_or_multiple'}
    if any(e['source_segment_km']>50 for e in edges.values()):return {**out,'status':'boundary_source_segment_exceeds_50km'}
    if not edges['left']['signed_normal_offset_km']<0<edges['right']['signed_normal_offset_km']:
        return {**out,'status':'provider_sides_do_not_bracket_axis'}
    if any(abs(e['signed_normal_offset_km'])>200 for e in edges.values()):return {**out,'status':'edge_outside_200km_search_guard'}
    if any(e['normal_residual_m']>.001 for e in edges.values()):return {**out,'status':'normal_intersection_residual_exceeds_tolerance'}
    width=base.distance(edges['left']['point'],edges['right']['point'])
    out.update(span_km=width,exceeds_source_nominal_140km_transect=width>140,
               inverse_vs_signed_offset_residual_m=abs(width-sum(abs(e['signed_normal_offset_km']) for e in edges.values()))*1000)
    return {**out,'status':'resolved'}


def readback(value,key=''):
    if isinstance(value,dict):return {k:readback(v,k) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [readback(v,key) for v in value]
    if isinstance(value,float):
        digits=7 if key=='point' else 9 if key in {'position','source_position','fraction_from_segment_start'} else 6
        return round(value,digits) or 0.0
    return value


def sample_id(day,level,latitude,window):
    return f'dimension:kuroshio:wang-v1:{day}:z{level:02}:normal-{latitude:g}n-t{window:02}km-v1'.replace('.','p')


def build():
    previous=base.verify_inputs()
    before={(r['date'],r['source_level']):r for r in previous['daily']}
    rows=[]
    with netCDF4.Dataset('publisher-original',memory=base.source_bytes()) as dataset:
        if set(dataset.groups)!={f'day{i:03}' for i in range(1,367)}:raise ValueError('Changed source day inventory')
        for day in range(1,367):
            group=dataset.groups[f'day{day:03}']
            if set(group.groups)!={f'depth{i:02}' for i in range(1,31)}:raise ValueError('Changed source level inventory')
            when=(date(2024,1,1)+timedelta(days=day-1)).isoformat()
            for level,depth in base.LEVELS.items():
                curves=base.read_curves(group.groups[f'depth{level:02}'])
                for section,latitude in enumerate(base.SECTIONS):
                    context=prepare(curves,latitude)
                    comparison=before[when,level]['sections'][section]
                    for window in WINDOWS:
                        rows.append({'id':sample_id(when,level,latitude,window),'sample_date':when,
                            'source_day':day,'source_level':level,'nominal_depth_m':depth,
                            'comparison_latitude_span_km':comparison['span_km'],
                            'comparison_latitude_span_status':comparison['status'],
                            **measure(curves,latitude,window,context)})
            if day%30==0:print(f'Processed {day}/366 source days',flush=True)
    rows=readback(rows);summaries=[];sensitivity=[]
    for level,depth in base.LEVELS.items():
        for latitude in base.SECTIONS:
            for window in WINDOWS:
                selected=[r for r in rows if r['source_level']==level and r['latitude']==latitude and r['tangent_half_window_km']==window]
                for month in (None,*range(1,13)):
                    selected_month=[r for r in selected if month is None or int(r['sample_date'][5:7])==month]
                    finite=[r for r in selected_month if r['status']=='resolved']
                    summaries.append({'source_level':level,'nominal_depth_m':depth,'latitude':latitude,
                        'tangent_half_window_km':window,'month':month,'attempted_count':len(selected_month),
                        'status_counts':dict(Counter(r['status'] for r in selected_month)),
                        **base.summary([r['span_km'] for r in finite]),
                        'exceeds_source_nominal_transect_count':sum(r['exceeds_source_nominal_140km_transect'] for r in finite)})
            groups={}
            for r in rows:
                if r['source_level']==level and r['latitude']==latitude:groups.setdefault(r['sample_date'],[]).append(r)
            ranges=[max(r['span_km'] for r in group)-min(r['span_km'] for r in group)
                    for group in groups.values() if len(group)==3 and all(r['status']=='resolved' for r in group)]
            sensitivity.append({'source_level':level,'latitude':latitude,'expected_dates':366,
                'quantity':'within_date_max_minus_min_across_three_tangent_windows_km',**base.summary(ranges)})
    files=[PROTOCOL,OPERATOR,base.FILE,base.FIGURE]
    return {'schema':'osw.kuroshio-axis-normal-boundary-spans.v1','current_id':'kuroshio',
        'entity_id':'current:kuroshio','source':previous['source'],
        'metric':'WGS84_separation_of_independent_smoothed_boundaries_on_reconstructed_axis_normal',
        'source_year':2024,'primary_tangent_half_window_km':14,'tangent_half_windows_km':list(WINDOWS),
        'latitude_gates':list(base.SECTIONS),'nominal_levels':{str(level):depth for level,depth in base.LEVELS.items()},
        'geometry_conventions':{'axis_heading':'WGS84 inverse initial azimuth between tangent endpoints, applied at gate',
            'boundary_interpolation':'linear longitude/latitude, nominal 1km subdivision then40 root bisections',
            'tangent_interpolation':'WGS84 leg distance, linear longitude/latitude within source segment'},
        'numerical_readback':{'longitude_latitude_decimal_places':7,'azimuth_degrees_decimal_places':6,
            'source_position_fraction_decimal_places':9,'distance_km_decimal_places':6,
            'normal_residual_m_decimal_places':6,'serialized_geometry_check_tolerance_m':.03,
            'unrounded_normal_residual_acceptance_m':.001,'physical_accuracy_claim':False},
        'input_sha256':{**previous['input_sha256'],**{p:base.digest(p) for p in files}},
        'counts':{'source_days':366,'source_depth_levels':30,'extracted_depth_levels':3,'attempts':len(rows)},
        'status_counts':dict(Counter(r['status'] for r in rows)),
        'primary_status_counts':dict(Counter(r['status'] for r in rows if r['tangent_half_window_km']==14)),
        'cases':rows,'summaries':summaries,'paired_tangent_sensitivity':sensitivity,
        'boundary_fallback_occurred':None,'threshold_attained':None,'physical_uncertainty_km':None,
        'velocity_normal_verified':False,'physical_width_inventory_admitted':False,
        'ocean_connectivity_verified':False,'normal_segment_land_contact':None,
        'whole_current_width_km':None,'annual_physical_width_range_km':None,
        'physical_state_passage_admitted':False,'rank_eligible':False,
        'range_kind':'empirical_model_sample_min_median_max_not_error_interval_or_climatology',
        'figure':FIGURE}


def encoded(value):
    return base.encoded(value)


def verify_inputs():
    doc=json.loads((ROOT/FILE).read_bytes())
    if doc['schema']!='osw.kuroshio-axis-normal-boundary-spans.v1':raise ValueError('Unknown normal-span edition')
    for path,pin in doc['input_sha256'].items():
        if base.digest(path)!=pin:raise ValueError('Changed normal-span input: '+path)
    if len(doc['cases'])!=16470 or len({r['id'] for r in doc['cases']})!=16470:raise ValueError('Incomplete normal-span attempts')
    return doc


if __name__=='__main__':
    document=build();(ROOT/FILE).write_bytes(base.encoded(document))
    print(json.dumps({'counts':document['counts'],'statuses':document['status_counts'],'primary':document['primary_status_counts']}))
