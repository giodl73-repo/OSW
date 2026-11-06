"""Cloud-only fixed-longitude transverse sections for eastward surface branches."""
from datetime import datetime,timezone
import hashlib
import json
import math
from pathlib import Path
import netCDF4
import numpy as np
from sample_eac_hycom_route_depth_v1 import GEOD,along_velocity,clean,canonical_hash
from sample_eac_hycom_route_depth_v2 import check_budget
from sample_atlantic_current_depth_v1 import wrapped_longitude,nearest_longitude_index
from acquire_three_current_depth_sections_v1 import diagnose,validate_retained as validate_components

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/zonal-current-depth-sections-operator-v1.json'
OUT=Path('zonal-current-depth-sections-v1')


def latitude_indices(axis,gate):
    values=np.asarray(axis,dtype=float)
    if values.ndim!=1 or not len(values) or not np.all(np.isfinite(values)):raise ValueError('Finite one-dimensional latitude axis required')
    south,north=gate
    if not -90<=south<north<=90:raise ValueError('Increasing geographic latitude gate required')
    indices=np.flatnonzero((values>=south)&(values<=north))
    if not 3<=len(indices)<=150 or np.any(np.diff(indices)!=1) or np.any(np.diff(values[indices])<=0):raise ValueError('Bounded contiguous increasing native latitude section required')
    return indices


def maximum_longitude_distance_km(requested,native,latitudes):
    return max(GEOD.inv(requested,float(y),wrapped_longitude(native),float(y))[2]/1000 for y in latitudes)


def preflight(lats,lons,op):
    plans=[];seen=set();pairs_used=0
    for definition in op['sections']:
        key=definition['entity_id'],definition['id']
        if key in seen or definition['entity_id'] not in op['currents'] or definition['fixed_axis']!='longitude':raise ValueError('Unique declared owner/longitude section required')
        seen.add(key);requested=definition['longitude_degrees_east']
        if not math.isfinite(requested) or not -180<=requested<=180:raise ValueError('Finite geographic longitude required')
        iy=latitude_indices(lats,definition['latitude_gate_degrees_north']);ix=nearest_longitude_index(lons,requested)
        distance=maximum_longitude_distance_km(requested,float(lons[ix]),np.asarray(lats)[iy])
        if distance>op['maximum_nearest_longitude_distance_km']:raise ValueError('Nearest native longitude exceeds every-row tolerance')
        plans.append({'definition':definition,'latitude_indices':iy,'longitude_index':ix,'maximum_longitude_distance_km':distance})
    for stamp in op['snapshot_times_utc']:
        for plan in plans:
            pairs_used+=check_budget((40,len(plan['latitude_indices']),1),pairs_used,op['maximum_total_cell_pairs'])
            if pairs_used*16>op['maximum_total_decoded_velocity_bytes']:raise ValueError('Preflight decoded velocity byte cap exceeded')
    return plans,pairs_used


def columns_from_arrays(u,v,lats,native_lon,ix,iy,bearing):
    if u.shape!=v.shape or u.ndim!=2 or u.shape[1]!=len(iy):raise ValueError('Depth by native latitude arrays required')
    columns=[]
    for j,index in enumerate(iy):
        eu,nv=np.asarray(u[:,j],dtype=float),np.asarray(v[:,j],dtype=float)
        component=along_velocity(eu,nv,bearing);component=np.where(np.isfinite(eu)&np.isfinite(nv),component,np.nan)
        latitude=float(lats[index])
        columns.append({'native_source_longitude_degrees_east':float(native_lon),'native_source_latitude_degrees_north':latitude,
            'sampled_lon_lat':[wrapped_longitude(float(native_lon)),latitude],'global_longitude_index':int(ix),'global_latitude_index':int(index),
            'eastward_velocity_m_s':clean(eu),'northward_velocity_m_s':clean(nv),'signed_reference_component_m_s':clean(component)})
    return columns


def validate_retained(section,config):
    validate_components(section,config)
    definition=section['section_definition'];profiles=section['columns'];slab=section['retrieved_hyperslab']
    if definition['fixed_axis']!='longitude' or definition['entity_id']!=section['entity_id']:raise ValueError('Section owner/orientation mismatch')
    if not 3<=len(profiles)<=150 or slab['depth_indices_inclusive']!=[0,len(section['depth_levels_m'])-1]:raise ValueError('Retained slice shape changed')
    indices=[r['global_latitude_index'] for r in profiles];latitudes=[r['sampled_lon_lat'][1] for r in profiles]
    if indices!=list(range(indices[0],indices[0]+len(profiles))) or any(b<=a for a,b in zip(latitudes,latitudes[1:])):raise ValueError('Native increasing latitude profile order changed')
    if slab['latitude_indices_inclusive']!=[indices[0],indices[-1]]:raise ValueError('Latitude hyperslab changed')
    native=section['actual_source_longitude_degrees_east'];south,north=definition['latitude_gate_degrees_north']
    for profile in profiles:
        if profile['native_source_longitude_degrees_east']!=native or profile['global_longitude_index']!=slab['longitude_index']:raise ValueError('Fixed native longitude changed')
        if profile['native_source_latitude_degrees_north']!=profile['sampled_lon_lat'][1] or not south<=profile['sampled_lon_lat'][1]<=north:raise ValueError('Native latitude/gate changed')
    distance=maximum_longitude_distance_km(definition['longitude_degrees_east'],native,latitudes)
    if distance>config['maximum_nearest_longitude_distance_km'] or not math.isclose(distance,section['maximum_nearest_longitude_distance_km'],rel_tol=1e-12,abs_tol=1e-12):raise ValueError('Longitude distance receipt changed')


def main():
    op=json.loads((ROOT/OPERATOR).read_bytes())
    for p,pin in op['input_sha256'].items():
        if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=pin:raise ValueError('Frozen input changed: '+p)
    if any(op['eligibility'].values()) or any(c.get('temperature_gate') is not None for c in op['currents'].values()):raise ValueError('No physical promotion or thermal field gate')
    OUT.mkdir(exist_ok=True);manifest=[];pairs_used=0;bytes_used=0
    with netCDF4.Dataset(op['opendap_dataset']) as ds:
        z=np.asarray(ds['depth'][:]);lats=np.asarray(ds['lat'][:]);lons=np.asarray(ds['lon'][:]);times=np.asarray(ds['time'][:])
        if len(z)!=40 or float(z[0])!=0 or float(z[-1])!=5000 or ds['depth'].units!='m' or ds['depth'].positive!='down':raise ValueError('Expected40positive-down metre levels0–5000m')
        if not np.all(np.isfinite(z)) or np.any(np.diff(z)<=0) or not np.any(z==200):raise ValueError('Finite increasing native depth axis with200m scoring boundary required')
        if ds['lat'].units!='degrees_north' or ds['lon'].units!='degrees_east':raise ValueError('Native geographic coordinates required')
        attrs={k:str(ds.getncattr(k)) for k in ds.ncattrs()}
        if attrs.get('field_type')!='instantaneous':raise ValueError('Instantaneous source required')
        variable_attrs={}
        for name,standard in [('water_u','eastward_sea_water_velocity'),('water_v','northward_sea_water_velocity')]:
            var=ds[name]
            if var.dimensions!=('time','depth','lat','lon') or var.units!='m/s' or var.standard_name!=standard:raise ValueError('Unexpected source component dimensions/units/frame')
            variable_attrs[name]={k:str(var.getncattr(k)) for k in var.ncattrs()}
        plans,planned_pairs=preflight(lats,lons,op)
        time_plan=[]
        for stamp in op['snapshot_times_utc']:
            target=datetime.strptime(stamp,'%Y-%m-%dT%H:%M:%SZ');numeric=netCDF4.date2num(target,ds['time'].units,calendar=getattr(ds['time'],'calendar','gregorian'))
            hits=np.flatnonzero(times==numeric)
            if len(hits)!=1:raise ValueError('Exact requested snapshot absent or duplicated')
            it=int(hits[0]);returned=netCDF4.num2date(times[it],ds['time'].units,calendar=getattr(ds['time'],'calendar','gregorian')).strftime('%Y-%m-%dT%H:%M:%SZ')
            if returned!=stamp:raise ValueError('Returned snapshot changed')
            time_plan.append((stamp,it,returned))
        for stamp,it,returned in time_plan:
            for plan in plans:
                definition=plan['definition'];config={**op,**op['currents'][definition['entity_id']]}
                iy=plan['latitude_indices'];y0,y1=int(iy[0]),int(iy[-1]);ix=plan['longitude_index'];native=float(lons[ix])
                pairs=check_budget((40,len(iy),1),pairs_used,op['maximum_total_cell_pairs'])
                if bytes_used+pairs*16>op['maximum_total_decoded_velocity_bytes']:raise ValueError('Actual running decoded byte cap exceeded before field retrieval')
                u=np.ma.filled(ds['water_u'][it,:,y0:y1+1,ix:ix+1],np.nan)[:,:,0]
                v=np.ma.filled(ds['water_v'][it,:,y0:y1+1,ix:ix+1],np.nan)[:,:,0]
                if u.shape!=(40,len(iy)) or v.shape!=u.shape:raise ValueError('Unexpected source depth/latitude hyperslab shape')
                pairs_used+=pairs;bytes_used+=u.nbytes+v.nbytes
                if bytes_used>op['maximum_total_decoded_velocity_bytes'] or np.any(abs(u[np.isfinite(u)])>10) or np.any(abs(v[np.isfinite(v)])>10):raise ValueError('Source decoded byte cap/scaling changed')
                columns=columns_from_arrays(u,v,lats,native,ix,iy,config['component_bearing_degrees_true'])
                result=diagnose(clean(z),[r['signed_reference_component_m_s'] for r in columns],config)
                section={'schema':'osw.zonal-current-depth-section.v1','status':'EXPLORATORY_FULL_LONGITUDE_SECTION_MODEL_AXIS_PROXY',
                    'entity_id':definition['entity_id'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),
                    'input_sha256':op['input_sha256'],'section_definition':definition,'snapshot_time_utc':stamp,'source_returned_timestamp_utc':returned,
                    'source_time_index':it,'source_tau_hours_since_analysis':float(ds['tau'][it]) if 'tau' in ds.variables else None,
                    'actual_source_longitude_degrees_east':native,'actual_source_latitude_degrees_north':None,
                    'maximum_nearest_longitude_distance_km':plan['maximum_longitude_distance_km'],
                    'component_bearing_degrees_true':config['component_bearing_degrees_true'],'depth_levels_m':clean(z),'columns':columns,
                    'decoded_columns_sha256':canonical_hash(columns),'diagnosis':result,
                    'native100m_temperature_degrees_celsius':None,'temperature_source':None,
                    'retrieved_hyperslab':{'time_index':it,'depth_indices_inclusive':[0,39],'latitude_indices_inclusive':[y0,y1],'longitude_index':ix},
                    'profile_order':'native_increasing_latitude_first_southern_index_breaks_ties',
                    'source_product':op['source_product'],'opendap_dataset':op['opendap_dataset'],'source_global_attributes':attrs,'source_variable_attributes':variable_attrs,
                    'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),'raw_HTTP_payload_bytes_instrumented':False,'source_subset_wire_byte_hash_claimed':False,
                    'geographic_gate_independently_validates_current_identity':False,'longitude_section_is_flow_normal':False,
                    'width_or_volume_join_performed':False,'uncertainty_m':None,'eligibility':op['eligibility'],'full_goal_complete':False}
                validate_retained(section,config)
                filename=stamp[:10]+'-'+definition['entity_id'].split(':')[1]+'-'+definition['id']+'.json'
                raw=(json.dumps(section,indent=2,allow_nan=False)+'\n').encode('utf8')
                if len(raw)>=2500000:raise ValueError('Fixed per-file publication cap exceeded')
                (OUT/filename).write_bytes(raw)
                manifest.append({'file':filename,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'section_id':definition['id'],'snapshot_time_utc':stamp,
                    'entity_id':definition['entity_id'],'native_columns':len(columns),'selected_column_index':result['selected_column_index'],
                    'horizontal_selection_status':result['horizontal_selection_status'],'selected_column_threshold_layers':result['selected_column_threshold_layers']})
                print(json.dumps({'file':filename,'profiles':len(columns),'selected':result['selected_column_index'],'status':result['horizontal_selection_status']}),flush=True)
    if pairs_used!=planned_pairs:raise ValueError('Actual source field count differs from preflight')
    (OUT/'manifest.json').write_text(json.dumps({'schema':'osw.zonal-current-depth-sections-manifest.v1','operator_file':OPERATOR,
        'operator_sha256':hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),'input_sha256':op['input_sha256'],'sections':manifest,
        'preflight_velocity_cell_pairs':planned_pairs,'decoded_velocity_cell_pairs':pairs_used,'decoded_velocity_array_bytes':bytes_used,
        'decoded_temperature_scalars':0,'decoded_temperature_array_bytes':0,'full_goal_complete':False},indent=2)+'\n',encoding='utf8')
    print(json.dumps({'completed_sections':len(manifest),'native_profiles':sum(r['native_columns'] for r in manifest),'cell_pairs':pairs_used,'decoded_bytes':bytes_used}))


if __name__=='__main__':main()
