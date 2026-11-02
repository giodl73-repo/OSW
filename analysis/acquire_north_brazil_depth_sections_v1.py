"""Cloud-only full fixed-latitude sections for an exploratory NBC axis proxy."""
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import netCDF4
import numpy as np
from sample_eac_hycom_route_depth_v1 import GEOD, along_velocity, clean, canonical_hash
from sample_atlantic_current_depth_v1 import wrapped_longitude
from sample_eac_hycom_route_depth_v2 import check_budget
from derive_eac_connected_layer_thickness_v1 import connected_layer

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/north-brazil-depth-sections-operator-v1.json'
OUT=Path('north-brazil-depth-sections-v1')


def selection(z,columns,op):
    if len(z)<2 or not all(math.isfinite(depth) and depth>=0 for depth in z) or any(b<=a for a,b in zip(z,z[1:])):raise ValueError('Finite ascending nonnegative native depths required')
    indices=[i for i,depth in enumerate(z) if 0<=depth<=200]
    if len(indices)<2 or z[indices[0]]!=0 or z[indices[-1]]!=200:raise ValueError('Complete native0–200m scoring axis required')
    candidates=[]
    for column in columns:
        if len(column)!=len(z):raise ValueError('Profile/depth size mismatch')
        complete=all(column[i] is not None and math.isfinite(column[i]) for i in indices)
        score=sum((column[a]+column[b])*(z[b]-z[a])/2 for a,b in zip(indices,indices[1:])) if complete else None
        eligible=complete and column[0]>op['surface_component_gate_m_s'] and max(column[i] for i in indices)>op['primary_threshold_m_s'] and score>0
        candidates.append({'complete_upper200m_support':complete,'signed_upper200m_integral_m2_s':score,'eligible':bool(eligible)})
    ready=[i for i,c in enumerate(candidates) if c['eligible']]
    selected=max(ready,key=lambda i:candidates[i]['signed_upper200m_integral_m2_s']) if ready else None
    if selected is None:status='no_qualifying_surface_connected_component_column'
    elif selected in [0,len(columns)-1]:status='section_gate_edge_maximum_axis_unresolved'
    elif not all(candidates[i]['complete_upper200m_support'] for i in [selected-1,selected+1]):status='upper_layer_support_edge_maximum_axis_unresolved'
    else:status='interior_section_integral_maximum_with_finite_neighbors_not_independently_validated_axis'
    local=[]
    for i in ready:
        score=candidates[i]['signed_upper200m_integral_m2_s']
        neighbors=[candidates[j]['signed_upper200m_integral_m2_s'] for j in [i-1,i+1] if 0<=j<len(candidates)]
        if all(v is None or score>=v for v in neighbors):local.append(i)
    return {'selected_column_index':selected,'horizontal_selection_status':status,'candidate_scores':candidates,
            'local_integral_maximum_indices':local,'multiple_peaks_are_independent_currents':False}


def longitude_indices(axis,gate):
    axis=np.asarray(axis,dtype=float)
    if axis.ndim!=1 or not len(axis) or not np.all(np.isfinite(axis)):raise ValueError('Finite one-dimensional source longitude axis required')
    values=np.asarray([wrapped_longitude(float(v)) for v in axis]);west,east=gate
    if not -180<west<east<0:raise ValueError('Declared western Atlantic increasing longitude gate required')
    indices=np.flatnonzero((values>=west)&(values<=east))
    if not 3<=len(indices)<=150 or np.any(np.diff(indices)!=1) or np.any(np.diff(values[indices])<=0):raise ValueError('Bounded contiguous native longitude section required')
    return indices


def diagnose(z,columns,op):
    result=selection(z,columns,op);selected=result['selected_column_index']
    result['selected_column_threshold_layers']=[connected_layer(z,columns[selected],threshold,op['core_search_depth_interval_m']) for threshold in op['thresholds_m_s']] if selected is not None else []
    return result


def validate_retained(section,op):
    if section['entity_id']!='current:north-brazil' or section['source_returned_timestamp_utc']!=section['snapshot_time_utc']:raise ValueError('Source identity or exact snapshot changed')
    profiles=section['columns'];z=section['depth_levels_m']
    if canonical_hash(profiles)!=section['decoded_columns_sha256']:raise ValueError('Retained section columns hash mismatch')
    result=diagnose(z,[r['signed_northwest_component_m_s'] for r in profiles],op)
    if result!=section['diagnosis']:raise ValueError('Retained section diagnosis mismatch')
    for profile in profiles:
        if profile['sampled_lon_lat'][0]!=wrapped_longitude(profile['native_source_longitude_degrees_east']):raise ValueError('Source/wrapped longitude mismatch')
    if any(section['eligibility'].values()):raise ValueError('No physical admission')


def main():
    op=json.loads((ROOT/OPERATOR).read_bytes())
    for file,pin in op['input_sha256'].items():
        if hashlib.sha256((ROOT/file).read_bytes()).hexdigest()!=pin:raise ValueError('Frozen source changed: '+file)
    if any(op['eligibility'].values()):raise ValueError('No physical promotion')
    OUT.mkdir(exist_ok=True);manifest=[];pairs_used=0;bytes_used=0
    with netCDF4.Dataset(op['opendap_dataset']) as ds:
        z=np.asarray(ds['depth'][:]);lats=np.asarray(ds['lat'][:]);lons=np.asarray(ds['lon'][:]);times=np.asarray(ds['time'][:])
        if len(z)!=40 or float(z[0])!=0 or float(z[-1])!=5000 or ds['depth'].units!='m' or ds['depth'].positive!='down':raise ValueError('Expected40positive-down metre levels0–5000m')
        attrs={k:str(ds.getncattr(k)) for k in ds.ncattrs()}
        if attrs.get('field_type')!='instantaneous':raise ValueError('Instantaneous source required')
        variable_attrs={}
        for name,standard in [('water_u','eastward_sea_water_velocity'),('water_v','northward_sea_water_velocity')]:
            var=ds[name]
            if var.dimensions!=('time','depth','lat','lon') or var.units!='m/s' or var.standard_name!=standard:raise ValueError('Unexpected source component dimensions/units/frame')
            variable_attrs[name]={k:str(var.getncattr(k)) for k in var.ncattrs()}
        for stamp in op['snapshot_times_utc']:
            target=datetime.strptime(stamp,'%Y-%m-%dT%H:%M:%SZ');numeric=netCDF4.date2num(target,ds['time'].units,calendar=getattr(ds['time'],'calendar','gregorian'))
            hits=np.flatnonzero(times==numeric)
            if len(hits)!=1:raise ValueError('Exact snapshot missing or duplicated')
            it=int(hits[0]);returned=netCDF4.num2date(times[it],ds['time'].units,calendar=getattr(ds['time'],'calendar','gregorian')).strftime('%Y-%m-%dT%H:%M:%SZ')
            for definition in op['sections']:
                latitude=definition['latitude_degrees_north'];iy=int(np.argmin(abs(lats-latitude)))
                native_lat=float(lats[iy]);row_distance=GEOD.inv(-45,latitude,-45,native_lat)[2]/1000
                if row_distance>op['maximum_nearest_latitude_distance_km']:raise ValueError('Native latitude outside declared tolerance')
                ix=longitude_indices(lons,definition['longitude_gate_degrees_east']);x0,x1=int(ix[0]),int(ix[-1])
                pairs=check_budget((len(z),1,len(ix)),pairs_used,op['maximum_total_cell_pairs'])
                if bytes_used+pairs*16>op['maximum_total_decoded_velocity_bytes']:raise ValueError('Decoded byte cap exceeded before field retrieval')
                u=np.ma.filled(ds['water_u'][it,:,iy:iy+1,x0:x1+1],np.nan)[:,0,:]
                v=np.ma.filled(ds['water_v'][it,:,iy:iy+1,x0:x1+1],np.nan)[:,0,:]
                pairs_used+=pairs;bytes_used+=u.nbytes+v.nbytes
                if bytes_used>op['maximum_total_decoded_velocity_bytes']:raise ValueError('Unexpected decoded array size')
                if np.any(abs(u[np.isfinite(u)])>10) or np.any(abs(v[np.isfinite(v)])>10):raise ValueError('Unexpected source scaling')
                columns=[]
                for j,index in enumerate(ix):
                    native_lon=float(lons[index]);eu,nv=u[:,j],v[:,j]
                    component=along_velocity(eu,nv,op['component_bearing_degrees_true']);component=np.where(np.isfinite(eu)&np.isfinite(nv),component,np.nan)
                    columns.append({'native_source_longitude_degrees_east':native_lon,'sampled_lon_lat':[wrapped_longitude(native_lon),native_lat],
                                    'global_longitude_index':int(index),'global_latitude_index':iy,
                                    'eastward_velocity_m_s':clean(eu),'northward_velocity_m_s':clean(nv),'signed_northwest_component_m_s':clean(component)})
                result=diagnose(clean(z),[c['signed_northwest_component_m_s'] for c in columns],op)
                section={'schema':'osw.north-brazil-depth-section.v1','status':'EXPLORATORY_FULL_LATITUDE_SECTION_MODEL_AXIS_PROXY',
                    'entity_id':'current:north-brazil','operator_file':OPERATOR,'operator_sha256':hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),
                    'input_sha256':op['input_sha256'],'section_definition':definition,'snapshot_time_utc':stamp,'source_returned_timestamp_utc':returned,
                    'source_time_index':it,'source_tau_hours_since_analysis':float(ds['tau'][it]) if 'tau' in ds.variables else None,
                    'actual_source_latitude_degrees_north':native_lat,'nearest_latitude_distance_km':row_distance,
                    'component_bearing_degrees_true':op['component_bearing_degrees_true'],'depth_levels_m':clean(z),'columns':columns,
                    'decoded_columns_sha256':canonical_hash(columns),'diagnosis':result,
                    'retrieved_hyperslab':{'time_index':it,'depth_indices_inclusive':[0,39],'latitude_index':iy,'longitude_indices_inclusive':[x0,x1]},
                    'source_product':op['source_product'],'opendap_dataset':op['opendap_dataset'],'source_global_attributes':attrs,'source_variable_attributes':variable_attrs,
                    'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),'raw_HTTP_payload_bytes_instrumented':False,'source_subset_wire_byte_hash_claimed':False,
                    'geographic_gate_independently_validates_current_identity':False,'latitude_section_is_flow_normal':False,
                    'width_or_volume_join_performed':False,'uncertainty_m':None,'eligibility':op['eligibility'],'full_goal_complete':False}
                validate_retained(section,op)
                filename=stamp[:10]+'-'+definition['id']+'.json';raw=(json.dumps(section,indent=2,allow_nan=False)+'\n').encode('utf8')
                if len(raw)>=2500000:raise ValueError('Fixed per-file source publication cap exceeded')
                (OUT/filename).write_bytes(raw)
                manifest.append({'file':filename,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'section_id':definition['id'],
                    'snapshot_time_utc':stamp,'native_columns':len(columns),'selected_column_index':result['selected_column_index'],
                    'horizontal_selection_status':result['horizontal_selection_status'],'selected_column_threshold_layers':result['selected_column_threshold_layers']})
                print(json.dumps({'file':filename,'columns':len(columns),'status':result['horizontal_selection_status'],'selected':result['selected_column_index']}),flush=True)
    (OUT/'manifest.json').write_text(json.dumps({'schema':'osw.north-brazil-depth-sections-manifest.v1','operator_file':OPERATOR,
        'operator_sha256':hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),'input_sha256':op['input_sha256'],'sections':manifest,
        'decoded_velocity_cell_pairs':pairs_used,'decoded_velocity_array_bytes':bytes_used,'full_goal_complete':False},indent=2)+'\n',encoding='utf8')
    print(json.dumps({'completed_sections':len(manifest),'native_profiles':sum(r['native_columns'] for r in manifest),'cell_pairs':pairs_used,'decoded_bytes':bytes_used}))


if __name__=='__main__':main()
