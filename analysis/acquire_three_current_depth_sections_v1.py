"""Cloud-only fixed-latitude Mindanao, Oyashio and west-coast Leeuwin axis proxies."""
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
from acquire_north_brazil_depth_sections_v1 import selection as base_selection

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/three-current-depth-sections-operator-v1.json'
OUT=Path('three-current-depth-sections-v1')


def selection(z,columns,op,temperatures=None):
    result=base_selection(z,columns,op)
    gate=op.get('temperature_gate')
    if gate is None:return result
    if temperatures is None or len(temperatures)!=len(columns):raise ValueError('One native100m temperature per column required')
    for i,candidate in enumerate(result['candidate_scores']):
        value=temperatures[i]
        if value is not None and (not math.isfinite(value) or not -5<=value<=45):raise ValueError('Invalid decoded in-situ temperature')
        candidate['eligible_before_water_mass_gate']=candidate['eligible']
        candidate['temperature_gate_passed']=value is not None and value<=gate['maximum_temperature_degrees_celsius']
        candidate['eligible']=candidate['eligible'] and candidate['temperature_gate_passed']
    candidates=result['candidate_scores'];ready=[i for i,c in enumerate(candidates) if c['eligible']]
    selected=max(ready,key=lambda i:candidates[i]['signed_upper200m_integral_m2_s']) if ready else None
    if selected is None:status='no_qualifying_surface_connected_cold_component_column'
    elif selected in [0,len(columns)-1]:status='section_gate_edge_maximum_axis_unresolved'
    elif not all(candidates[i]['complete_upper200m_support'] for i in [selected-1,selected+1]):status='upper_layer_support_edge_maximum_axis_unresolved'
    else:status='interior_section_integral_maximum_with_finite_neighbors_not_independently_validated_axis'
    local=[]
    for i in ready:
        neighbors=[j for j in [i-1,i+1] if 0<=j<len(candidates) and candidates[j]['eligible']]
        if all(candidates[i]['signed_upper200m_integral_m2_s']>=candidates[j]['signed_upper200m_integral_m2_s'] for j in neighbors):local.append(i)
    result.update(selected_column_index=selected,horizontal_selection_status=status,local_integral_maximum_indices=local)
    return result


def longitude_indices(axis,gate):
    axis=np.asarray(axis,dtype=float)
    if axis.ndim!=1 or not len(axis) or not np.all(np.isfinite(axis)):raise ValueError('Finite one-dimensional source longitude axis required')
    values=np.asarray([wrapped_longitude(float(v)) for v in axis]);west,east=gate
    if not -180<west<east<180:raise ValueError('Increasing non-dateline longitude gate required')
    indices=np.flatnonzero((values>=west)&(values<=east))
    if not 3<=len(indices)<=150 or np.any(np.diff(indices)!=1) or np.any(np.diff(values[indices])<=0):raise ValueError('Bounded contiguous native longitude section required')
    return indices


def diagnose(z,columns,op,temperatures=None):
    result=selection(z,columns,op,temperatures);selected=result['selected_column_index']
    result['selected_column_threshold_layers']=[connected_layer(z,columns[selected],threshold,op['core_search_depth_interval_m']) for threshold in op['thresholds_m_s']] if selected is not None else []
    return result


def validate_retained(section,op):
    if section['entity_id']!=op['entity_id'] or section['source_returned_timestamp_utc']!=section['snapshot_time_utc']:raise ValueError('Source identity or exact snapshot changed')
    profiles=section['columns'];z=section['depth_levels_m']
    if canonical_hash(profiles)!=section['decoded_columns_sha256']:raise ValueError('Retained section columns hash mismatch')
    temperatures=section['native100m_temperature_degrees_celsius']
    if op.get('temperature_gate') is not None:
        receipt=section['temperature_source']
        if receipt['source_returned_timestamp_utc']!=section['snapshot_time_utc'] or receipt['native_depth_m']!=100 or receipt['variable']!='water_temp':raise ValueError('Temperature source definition changed')
        if receipt['decoded_values_sha256']!=canonical_hash(temperatures):raise ValueError('Temperature retained values hash mismatch')
    elif temperatures is not None or section.get('temperature_source') is not None:raise ValueError('Unexpected thermal gate on nonthermal current')
    result=diagnose(z,[r['signed_reference_component_m_s'] for r in profiles],op,section['native100m_temperature_degrees_celsius'])
    if result!=section['diagnosis']:raise ValueError('Retained section diagnosis mismatch')
    for profile in profiles:
        if profile['sampled_lon_lat'][0]!=wrapped_longitude(profile['native_source_longitude_degrees_east']):raise ValueError('Source/wrapped longitude mismatch')
    if section['eligibility']!=op['eligibility'] or any(section['eligibility'].values()):raise ValueError('No physical admission')
    if section['component_bearing_degrees_true']!=op['component_bearing_degrees_true']:raise ValueError('Component frame changed')
    for profile in profiles:
        u=np.asarray([np.nan if x is None else x for x in profile['eastward_velocity_m_s']])
        v=np.asarray([np.nan if x is None else x for x in profile['northward_velocity_m_s']])
        signed=along_velocity(u,v,op['component_bearing_degrees_true'])
        signed=np.where(np.isfinite(u)&np.isfinite(v),signed,np.nan)
        if clean(signed)!=profile['signed_reference_component_m_s']:raise ValueError('Retained signed component mismatch')


def main():
    op=json.loads((ROOT/OPERATOR).read_bytes())
    for file,pin in op['input_sha256'].items():
        if hashlib.sha256((ROOT/file).read_bytes()).hexdigest()!=pin:raise ValueError('Frozen source changed: '+file)
    if any(op['eligibility'].values()):raise ValueError('No physical promotion')
    OUT.mkdir(exist_ok=True);manifest=[];pairs_used=0;bytes_used=0;temperature_values_used=0;temperature_bytes_used=0
    with netCDF4.Dataset(op['opendap_dataset']) as ds, netCDF4.Dataset(op['temperature_opendap_dataset']) as ts:
        z=np.asarray(ds['depth'][:]);lats=np.asarray(ds['lat'][:]);lons=np.asarray(ds['lon'][:]);times=np.asarray(ds['time'][:])
        if len(z)!=40 or float(z[0])!=0 or float(z[-1])!=5000 or ds['depth'].units!='m' or ds['depth'].positive!='down':raise ValueError('Expected40positive-down metre levels0–5000m')
        attrs={k:str(ds.getncattr(k)) for k in ds.ncattrs()}
        if attrs.get('field_type')!='instantaneous':raise ValueError('Instantaneous source required')
        variable_attrs={}
        for name,standard in [('water_u','eastward_sea_water_velocity'),('water_v','northward_sea_water_velocity')]:
            var=ds[name]
            if var.dimensions!=('time','depth','lat','lon') or var.units!='m/s' or var.standard_name!=standard:raise ValueError('Unexpected source component dimensions/units/frame')
            variable_attrs[name]={k:str(var.getncattr(k)) for k in var.ncattrs()}
        for axis in ['depth','lat','lon']:
            if not np.array_equal(np.asarray(ts[axis][:]),np.asarray(ds[axis][:])):raise ValueError('Temperature/velocity native grid mismatch')
        temp=ts['water_temp']
        if temp.dimensions!=('time','depth','lat','lon') or temp.units!='degC' or temp.standard_name!='sea_water_temperature' or temp.comment!='in-situ temperature':raise ValueError('Unexpected native in-situ temperature definition')
        if ts.getncattr('field_type')!='instantaneous' or ts['depth'].units!='m' or ts['depth'].positive!='down':raise ValueError('Unexpected temperature product coordinates')
        t100=np.flatnonzero(z==100)
        if len(t100)!=1:raise ValueError('Exactly one native100m level required')
        iz100=int(t100[0]);temperature_times=np.asarray(ts['time'][:])
        temperature_attrs={k:str(temp.getncattr(k)) for k in temp.ncattrs()}
        temperature_global_attrs={k:str(ts.getncattr(k)) for k in ts.ncattrs()}
        for stamp in op['snapshot_times_utc']:
            target=datetime.strptime(stamp,'%Y-%m-%dT%H:%M:%SZ');numeric=netCDF4.date2num(target,ds['time'].units,calendar=getattr(ds['time'],'calendar','gregorian'))
            hits=np.flatnonzero(times==numeric)
            if len(hits)!=1:raise ValueError('Exact snapshot missing or duplicated')
            it=int(hits[0]);returned=netCDF4.num2date(times[it],ds['time'].units,calendar=getattr(ds['time'],'calendar','gregorian')).strftime('%Y-%m-%dT%H:%M:%SZ')
            for definition in op['sections']:
                config={**op,**op['currents'][definition['entity_id']]}
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
                    native_lon=float(lons[index]);eu,nv=np.asarray(u[:,j],dtype=float),np.asarray(v[:,j],dtype=float)
                    component=along_velocity(eu,nv,config['component_bearing_degrees_true']);component=np.where(np.isfinite(eu)&np.isfinite(nv),component,np.nan)
                    columns.append({'native_source_longitude_degrees_east':native_lon,'sampled_lon_lat':[wrapped_longitude(native_lon),native_lat],
                                    'global_longitude_index':int(index),'global_latitude_index':iy,
                                    'eastward_velocity_m_s':clean(eu),'northward_velocity_m_s':clean(nv),'signed_reference_component_m_s':clean(component)})
                temperatures=None;temperature_receipt=None
                if config.get('temperature_gate') is not None:
                    tn=netCDF4.date2num(target,ts['time'].units,calendar=getattr(ts['time'],'calendar','gregorian'))
                    thits=np.flatnonzero(temperature_times==tn)
                    if len(thits)!=1:raise ValueError('Exact temperature snapshot missing or duplicated')
                    tit=int(thits[0]);tstamp=netCDF4.num2date(temperature_times[tit],ts['time'].units,calendar=getattr(ts['time'],'calendar','gregorian')).strftime('%Y-%m-%dT%H:%M:%SZ')
                    if tstamp!=stamp:raise ValueError('Temperature exact time changed')
                    if temperature_values_used+len(ix)>op['maximum_total_temperature_scalars'] or temperature_bytes_used+len(ix)*8>op['maximum_total_decoded_temperature_bytes']:raise ValueError('Temperature budget exceeded before field retrieval')
                    values=np.ma.filled(temp[tit,iz100,iy:iy+1,x0:x1+1],np.nan)[0,:]
                    temperature_values_used+=len(ix);temperature_bytes_used+=values.nbytes
                    if temperature_bytes_used>op['maximum_total_decoded_temperature_bytes']:raise ValueError('Actual temperature bytes exceeded')
                    if np.any(values[np.isfinite(values)] < -5) or np.any(values[np.isfinite(values)] >45):raise ValueError('Unexpected temperature scaling')
                    temperatures=clean(values)
                    temperature_receipt={'dataset':op['temperature_opendap_dataset'],'variable':'water_temp','source_global_attributes':temperature_global_attrs,
                        'source_variable_attributes':temperature_attrs,'source_returned_timestamp_utc':tstamp,'time_index':tit,'depth_index':iz100,'native_depth_m':100,
                        'latitude_index':iy,'longitude_indices_inclusive':[x0,x1],'decoded_values_sha256':canonical_hash(temperatures),
                        'interpretation':'OSW model water-mass screen only;not JMA observed axis,vertical flow boundary or independent current identity validation'}
                result=diagnose(clean(z),[c['signed_reference_component_m_s'] for c in columns],config,temperatures)
                section={'schema':'osw.three-current-depth-section.v1','status':'EXPLORATORY_FULL_LATITUDE_SECTION_MODEL_AXIS_PROXY',
                    'entity_id':config['entity_id'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),
                    'input_sha256':op['input_sha256'],'section_definition':definition,'snapshot_time_utc':stamp,'source_returned_timestamp_utc':returned,
                    'source_time_index':it,'source_tau_hours_since_analysis':float(ds['tau'][it]) if 'tau' in ds.variables else None,
                    'actual_source_latitude_degrees_north':native_lat,'nearest_latitude_distance_km':row_distance,
                    'component_bearing_degrees_true':config['component_bearing_degrees_true'],'native100m_temperature_degrees_celsius':temperatures,'temperature_source':temperature_receipt,'depth_levels_m':clean(z),'columns':columns,
                    'decoded_columns_sha256':canonical_hash(columns),'diagnosis':result,
                    'retrieved_hyperslab':{'time_index':it,'depth_indices_inclusive':[0,39],'latitude_index':iy,'longitude_indices_inclusive':[x0,x1]},
                    'source_product':op['source_product'],'opendap_dataset':op['opendap_dataset'],'source_global_attributes':attrs,'source_variable_attributes':variable_attrs,
                    'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),'raw_HTTP_payload_bytes_instrumented':False,'source_subset_wire_byte_hash_claimed':False,
                    'geographic_gate_independently_validates_current_identity':False,'latitude_section_is_flow_normal':False,
                    'width_or_volume_join_performed':False,'uncertainty_m':None,'eligibility':op['eligibility'],'full_goal_complete':False}
                validate_retained(section,config)
                filename=stamp[:10]+'-'+config['entity_id'].split(':')[1]+'-'+definition['id']+'.json';raw=(json.dumps(section,indent=2,allow_nan=False)+'\n').encode('utf8')
                if len(raw)>=2500000:raise ValueError('Fixed per-file source publication cap exceeded')
                (OUT/filename).write_bytes(raw)
                manifest.append({'file':filename,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'section_id':definition['id'],
                    'snapshot_time_utc':stamp,'entity_id':config['entity_id'],'native_columns':len(columns),'selected_column_index':result['selected_column_index'],
                    'horizontal_selection_status':result['horizontal_selection_status'],'selected_column_threshold_layers':result['selected_column_threshold_layers']})
                print(json.dumps({'file':filename,'columns':len(columns),'status':result['horizontal_selection_status'],'selected':result['selected_column_index']}),flush=True)
    (OUT/'manifest.json').write_text(json.dumps({'schema':'osw.three-current-depth-sections-manifest.v1','operator_file':OPERATOR,
        'operator_sha256':hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),'input_sha256':op['input_sha256'],'sections':manifest,
        'decoded_velocity_cell_pairs':pairs_used,'decoded_velocity_array_bytes':bytes_used,'decoded_temperature_scalars':temperature_values_used,'decoded_temperature_array_bytes':temperature_bytes_used,'full_goal_complete':False},indent=2)+'\n',encoding='utf8')
    print(json.dumps({'completed_sections':len(manifest),'native_profiles':sum(r['native_columns'] for r in manifest),'cell_pairs':pairs_used,'decoded_bytes':bytes_used}))


if __name__=='__main__':main()
