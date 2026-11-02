"""Fixed-latitude section geometry; frozen selection and connected layers reused."""
import math
import numpy as np
from acquire_three_current_depth_sections_v1 import longitude_indices,diagnose,validate_retained as validate_components
from sample_eac_hycom_route_depth_v1 import GEOD,along_velocity,clean,canonical_hash
from sample_eac_hycom_route_depth_v2 import check_budget
from sample_atlantic_current_depth_v1 import wrapped_longitude


def preflight(lats,lons,op):
    axis=np.asarray(lats,dtype=float)
    if axis.ndim!=1 or not len(axis) or not np.all(np.isfinite(axis)) or np.any(np.diff(axis)<=0):raise ValueError('Finite increasing native latitude axis required')
    plans=[];seen=set();pairs_used=0
    for definition in op['sections']:
        key=definition['entity_id'],definition['id']
        if key in seen or definition['entity_id'] not in op['currents'] or definition['fixed_axis']!='latitude':raise ValueError('Unique declared owner/latitude section required')
        seen.add(key);requested=definition['latitude_degrees_north']
        if not math.isfinite(requested) or not -90<=requested<=90:raise ValueError('Finite geographic latitude required')
        iy=int(np.argmin(abs(axis-requested)));native=float(axis[iy])
        distance=GEOD.inv(0,requested,0,native)[2]/1000
        if distance>op['maximum_nearest_latitude_distance_km']:raise ValueError('Nearest native latitude exceeds tolerance')
        ix=longitude_indices(lons,definition['longitude_gate_degrees_east'])
        plans.append({'definition':definition,'longitude_indices':ix,'latitude_index':iy,'nearest_latitude_distance_km':distance})
    for stamp in op['snapshot_times_utc']:
        for plan in plans:
            pairs_used+=check_budget((40,1,len(plan['longitude_indices'])),pairs_used,op['maximum_total_cell_pairs'])
            if pairs_used*16>op['maximum_total_decoded_velocity_bytes']:raise ValueError('Preflight decoded velocity byte cap exceeded')
    return plans,pairs_used


def columns_from_arrays(u,v,lons,native_lat,iy,ix,bearing):
    if u.shape!=v.shape or u.ndim!=2 or u.shape[1]!=len(ix):raise ValueError('Depth by native longitude arrays required')
    columns=[]
    for j,index in enumerate(ix):
        eu,nv=np.asarray(u[:,j],dtype=float),np.asarray(v[:,j],dtype=float)
        component=along_velocity(eu,nv,bearing);component=np.where(np.isfinite(eu)&np.isfinite(nv),component,np.nan)
        longitude=float(lons[index])
        columns.append({'native_source_longitude_degrees_east':longitude,'native_source_latitude_degrees_north':float(native_lat),
            'sampled_lon_lat':[wrapped_longitude(longitude),float(native_lat)],'global_longitude_index':int(index),'global_latitude_index':int(iy),
            'eastward_velocity_m_s':clean(eu),'northward_velocity_m_s':clean(nv),'signed_reference_component_m_s':clean(component)})
    return columns


def validate_retained(section,config):
    validate_components(section,config)
    definition=section['section_definition'];profiles=section['columns'];slab=section['retrieved_hyperslab']
    if definition['fixed_axis']!='latitude' or definition['entity_id']!=section['entity_id']:raise ValueError('Section owner/orientation mismatch')
    if not 3<=len(profiles)<=150 or slab['depth_indices_inclusive']!=[0,len(section['depth_levels_m'])-1]:raise ValueError('Retained slice shape changed')
    indices=[r['global_longitude_index'] for r in profiles];longitudes=[r['sampled_lon_lat'][0] for r in profiles]
    if indices!=list(range(indices[0],indices[0]+len(profiles))) or any(b<=a for a,b in zip(longitudes,longitudes[1:])):raise ValueError('Native increasing longitude order changed')
    if slab['longitude_indices_inclusive']!=[indices[0],indices[-1]]:raise ValueError('Longitude hyperslab changed')
    native=section['actual_source_latitude_degrees_north'];west,east=definition['longitude_gate_degrees_east']
    for profile in profiles:
        if profile['native_source_latitude_degrees_north']!=native or profile['sampled_lon_lat'][1]!=native or profile['global_latitude_index']!=slab['latitude_index']:raise ValueError('Fixed native latitude changed')
        if not west<=profile['sampled_lon_lat'][0]<=east:raise ValueError('Profile outside declared gate')
    distance=GEOD.inv(0,definition['latitude_degrees_north'],0,native)[2]/1000
    if distance!=section['nearest_latitude_distance_km'] or distance>config['maximum_nearest_latitude_distance_km']:raise ValueError('Native latitude offset changed')
