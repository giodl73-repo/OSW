"""Cloud-only bounded regional depth sampling for three surface-current branches."""
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import netCDF4
import numpy as np
from sample_eac_hycom_route_depth_v1 import GEOD, along_velocity, clean, canonical_hash
from sample_eac_hycom_route_depth_v2 import check_budget
from sample_kuroshio_hycom_depth_v1 import diagnose_profiles

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/atlantic-current-depth-operator-v1.json'
OUT=Path('atlantic-current-depth-v1')


def wrapped_longitude(value):
    if not math.isfinite(value):raise ValueError('Finite longitude required')
    return (value+180)%360-180


def nearest_longitude_index(axis,target):
    values=np.asarray(axis,dtype=float)
    if values.ndim!=1 or not len(values) or not np.all(np.isfinite(values)) or not math.isfinite(target):raise ValueError('Finite one-dimensional longitude axis required')
    return int(np.argmin(abs((values-target+180)%360-180)))


def route_context(route,case):
    if route['current_id']!=case['current_id'] or case['entity_id']!='current:'+case['current_id']:raise ValueError('Exact source route owner required')
    points=route['coordinates_lon_lat']
    if len(points)!=case['expected_route_vertices']:raise ValueError('Original route vertex count changed')
    if any(len(p)!=2 or not all(math.isfinite(x) for x in p) or not -180<=p[0]<=180 or not -90<=p[1]<=90 for p in points):raise ValueError('Finite CRS84 route positions required')
    distances=[0.]
    for a,b in zip(points,points[1:]):
        metres=GEOD.inv(*a,*b)[2]
        if not math.isfinite(metres) or metres<=0:raise ValueError('Distinct consecutive reference positions required')
        distances.append(distances[-1]+metres/1000)
    bearings=[GEOD.inv(*points[max(0,i-1)],*points[min(len(points)-1,i+1)])[0]%360 for i in range(len(points))]
    return points,distances,bearings


def diagnoses(z,profiles,case):
    result=diagnose_profiles(z,profiles,case)
    descriptor=result['primary_core_lower_descriptor']
    if 'poleward' in descriptor['status']:
        descriptor['frozen_selector_status']=descriptor['status']
        descriptor['status']=descriptor['status'].replace('poleward','downstream')
    return result


def validate_retained(result,case,op):
    if result['entity_id']!=case['entity_id'] or result['current_case']!=case:raise ValueError('Retained current ownership/operator mismatch')
    rows=result['samples'];keys=[(r['snapshot_time_utc'],r['route_vertex_index']) for r in rows]
    expected={(t,i) for t in op['snapshot_times_utc'] for i in range(case['expected_route_vertices'])}
    if len(keys)!=len(expected) or set(keys)!=expected:raise ValueError('Complete original date/vertex cases required')
    for row in rows:
        if len(row['sampled_profiles'])!=5 or row['source_returned_timestamp_utc']!=row['snapshot_time_utc']:raise ValueError('Fixed offsets/exact time changed')
        if canonical_hash(row['sampled_profiles'])!=row['decoded_profile_sha256']:raise ValueError('Retained selected-profile hash mismatch')
        check=diagnoses(row['depth_levels_m'],row['sampled_profiles'],case)
        for k,v in check.items():
            if row[k]!=v:raise ValueError('Retained layer/selection audit failed')
        for profile in row['sampled_profiles']:
            if profile['sampled_lon_lat'][0]!=wrapped_longitude(profile['native_source_longitude_degrees_east']):raise ValueError('Native/wrapped coordinate mismatch')
    if any(result['eligibility'].values()):raise ValueError('No physical admission')


def main():
    op=json.loads((ROOT/OPERATOR).read_bytes())
    for path,pin in op['input_sha256'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=pin:raise ValueError('Frozen sampling input changed: '+path)
    if any(op['eligibility'].values()):raise ValueError('No physical promotion')
    OUT.mkdir(exist_ok=True);cell_pairs=0;decoded_bytes=0;manifest=[]
    with netCDF4.Dataset(op['opendap_dataset']) as ds:
        z=np.asarray(ds['depth'][:]);lats=np.asarray(ds['lat'][:]);lons=np.asarray(ds['lon'][:]);times=np.asarray(ds['time'][:])
        if len(z)!=40 or float(z[0])!=0 or float(z[-1])!=5000 or ds['depth'].units!='m' or ds['depth'].positive!='down':raise ValueError('Unexpected standard positive-down metre depth axis')
        attrs={k:str(ds.getncattr(k)) for k in ds.ncattrs()};variable_attrs={}
        if attrs.get('field_type')!='instantaneous':raise ValueError('Exact instantaneous model output required')
        for name,standard in [('water_u','eastward_sea_water_velocity'),('water_v','northward_sea_water_velocity')]:
            var=ds[name]
            if var.dimensions!=('time','depth','lat','lon') or var.units!='m/s' or var.standard_name!=standard:raise ValueError('Unexpected component units/frame/axes')
            variable_attrs[name]={k:str(var.getncattr(k)) for k in var.ncattrs()}
        for case in op['currents']:
            route=json.loads((ROOT/case['route_file']).read_bytes());points,distances,bearings=route_context(route,case)
            rows=[];start_pairs=cell_pairs;start_bytes=decoded_bytes
            for stamp in op['snapshot_times_utc']:
                target=datetime.strptime(stamp,'%Y-%m-%dT%H:%M:%SZ')
                value=netCDF4.date2num(target,ds['time'].units,calendar=getattr(ds['time'],'calendar','gregorian'))
                matches=np.flatnonzero(times==value)
                if len(matches)!=1:raise ValueError('Exact prescribed time missing or duplicated')
                it=int(matches[0]);returned=netCDF4.num2date(times[it],ds['time'].units,calendar=getattr(ds['time'],'calendar','gregorian')).strftime('%Y-%m-%dT%H:%M:%SZ')
                for vertex,(point,bearing) in enumerate(zip(points,bearings)):
                    targets=[GEOD.fwd(*point,bearing+90,offset*1000)[:2] for offset in op['normal_offsets_km']]
                    indices=[(int(np.argmin(abs(lats-lat))),nearest_longitude_index(lons,lon)) for lon,lat in targets]
                    y0,y1=min(p[0] for p in indices),max(p[0] for p in indices);x0,x1=min(p[1] for p in indices),max(p[1] for p in indices)
                    pairs=check_budget((len(z),y1-y0+1,x1-x0+1),cell_pairs,op['maximum_total_cell_pairs'])
                    if decoded_bytes+pairs*16>op['maximum_total_decoded_velocity_bytes']:raise ValueError('Decoded byte cap exceeded before field retrieval')
                    u=np.ma.filled(ds['water_u'][it,:,y0:y1+1,x0:x1+1],np.nan);v=np.ma.filled(ds['water_v'][it,:,y0:y1+1,x0:x1+1],np.nan)
                    cell_pairs+=pairs;decoded_bytes+=u.nbytes+v.nbytes
                    if decoded_bytes>op['maximum_total_decoded_velocity_bytes']:raise ValueError('Unexpected decoded array size')
                    if np.any(abs(u[np.isfinite(u)])>10) or np.any(abs(v[np.isfinite(v)])>10):raise ValueError('Unexpected velocity scaling')
                    profiles=[]
                    for offset,(lon,lat),(iy,ix) in zip(op['normal_offsets_km'],targets,indices):
                        native_lon=float(lons[ix]);sampled=[wrapped_longitude(native_lon),float(lats[iy])]
                        distance=GEOD.inv(lon,lat,*sampled)[2]/1000
                        if distance>op['maximum_nearest_cell_distance_km']:raise ValueError('Target outside nearest-cell tolerance')
                        eu,nv=u[:,iy-y0,ix-x0],v[:,iy-y0,ix-x0]
                        along=along_velocity(eu,nv,bearing);along=np.where(np.isfinite(eu)&np.isfinite(nv),along,np.nan)
                        profiles.append({'normal_offset_km':offset,'target_lon_lat':[lon,lat],'sampled_lon_lat':sampled,
                                         'native_source_longitude_degrees_east':native_lon,'global_latitude_index':iy,'global_longitude_index':ix,
                                         'nearest_cell_distance_km':distance,'eastward_velocity_m_s':clean(eu),
                                         'northward_velocity_m_s':clean(nv),'along_velocity_m_s':clean(along)})
                    row={'snapshot_time_utc':stamp,'source_returned_timestamp_utc':returned,'source_time_index':it,
                         'source_tau_hours_since_analysis':float(ds['tau'][it]) if 'tau' in ds.variables else None,
                         'route_vertex_index':vertex,'editorial_lon_lat':point,'reference_distance_km':distances[vertex],
                         'locked_reference_bearing_degrees_true':bearing,'depth_levels_m':clean(z),'sampled_profiles':profiles,
                         'decoded_profile_sha256':canonical_hash(profiles),
                         'retrieved_hyperslab':{'time_index':it,'depth_indices_inclusive':[0,39],'latitude_indices_inclusive':[y0,y1],'longitude_indices_inclusive':[x0,x1]},
                         'geographic_window_establishes_current_identity':False,**diagnoses(z,profiles,case)}
                    rows.append(row)
                    (OUT/'checkpoint.json').write_text(json.dumps({'entity_id':case['entity_id'],'status':'PARTIAL_UNREVIEWED','samples':rows,'full_goal_complete':False},indent=2,allow_nan=False)+'\n',encoding='utf8')
                    print(json.dumps({'current':case['current_id'],'date':stamp,'vertex':vertex,'horizontal_status':row['horizontal_selection_status'],'primary':row['primary_core_lower_descriptor']}),flush=True)
            counts={'snapshots':len(op['snapshot_times_utc']),'route_vertices':len(points),'sampled_cases':len(rows),
                    'retained_velocity_profiles':sum(len(r['sampled_profiles']) for r in rows),
                    'selected_primary_lower_crossings':sum(r['primary_core_lower_descriptor']['lower_isotach_depth_m'] is not None for r in rows),
                    'selected_horizontal_edge_maxima':sum(r['horizontal_selection_status']=='edge_maximum_axis_unresolved' for r in rows),
                    'no_qualifying_core_cases':sum(r['selected_profile_index'] is None for r in rows),
                    'selected_resolved_threshold_layers':{str(t):sum(r['selected_profile_threshold_layers'][i]['layer_thickness_m'] is not None for r in rows if r['selected_profile_index'] is not None) for i,t in enumerate(case['thresholds_m_s'])},
                    'decoded_velocity_cell_pairs':cell_pairs-start_pairs,'decoded_velocity_array_bytes':decoded_bytes-start_bytes,
                    'whole_route_physical_depth_profiles':0,'water_volume_estimates':0}
            result={'schema':'osw.atlantic-current-depth-candidate.v1','status':'REGIONAL_EDITORIAL_CORRIDOR_MODEL_COMPONENT_LAYERS',
                    'entity_id':case['entity_id'],'current_case':case,'operator_file':OPERATOR,
                    'operator_sha256':hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),'input_sha256':op['input_sha256'],
                    'route_file':case['route_file'],'route_sha256':op['input_sha256'][case['route_file']],
                    'reference_route_length_km':distances[-1],'source_product':op['source_product'],'opendap_dataset':op['opendap_dataset'],
                    'source_global_attributes':attrs,'source_variable_attributes':variable_attrs,
                    'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),'counts':counts,'samples':rows,
                    'raw_HTTP_payload_bytes_instrumented':False,'source_subset_wire_byte_hash_claimed':False,
                    'named_current_axis_independently_validated':False,'width_join_performed':False,
                    'eligibility':op['eligibility'],'full_goal_complete':False}
            validate_retained(result,case,op)
            filename=case['current_id']+'.json';raw=(json.dumps(result,indent=2,allow_nan=False)+'\n').encode('utf8')
            (OUT/filename).write_bytes(raw)
            manifest.append({'entity_id':case['entity_id'],'file':filename,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'counts':counts})
            print(json.dumps({'completed_current':case['current_id'],'counts':counts}),flush=True)
    (OUT/'manifest.json').write_text(json.dumps({'schema':'osw.atlantic-current-depth-manifest.v1','operator_file':OPERATOR,
        'operator_sha256':hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),'input_sha256':op['input_sha256'],
        'currents':manifest,'total_decoded_velocity_cell_pairs':cell_pairs,'total_decoded_velocity_array_bytes':decoded_bytes,
        'full_goal_complete':False},indent=2)+'\n',encoding='utf8')
    print(json.dumps({'completed_currents':len(manifest),'cell_pairs':cell_pairs,'decoded_bytes':decoded_bytes}))


if __name__=='__main__':main()
