"""Cloud-only signed velocity layers around dated retained Kuroshio model axes."""
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import netCDF4
import numpy as np
from sample_eac_hycom_route_depth_v1 import GEOD, along_velocity, select_profile, clean, canonical_hash
from sample_eac_hycom_route_depth_v2 import check_budget
from derive_eac_connected_layer_thickness_v1 import connected_layer

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/kuroshio-hycom-depth-operator-v1.json'
OUT=Path('kuroshio-hycom-depth-v1')


def axis_cases(report,op):
    if report['entity_id']!='current:kuroshio' or report['source_year']!=2024:
        raise ValueError('Exact regional Kuroshio source edition required')
    result=[]
    for timestamp in op['snapshot_times_utc']:
        for latitude in op['latitude_gates']:
            hits=[(i,r) for i,r in enumerate(report['cases']) if r['sample_date']==timestamp[:10]
                  and r['source_level']==1 and r['latitude']==latitude
                  and r['tangent_half_window_km']==14]
            if len(hits)!=1:raise ValueError('Exactly one retained source axis case per prescribed key required')
            i,row=hits[0]
            if row['nominal_depth_m']!=.49:raise ValueError('Source level1 must retain its nominal0.49m depth')
            gate=row.get('gate');tangent=row.get('tangent_endpoints');bearing=row.get('axis_tangent_azimuth_degrees')
            eligible=(row['axis_crossing_count']==1 and gate is not None and gate['segment_km']<=50
                      and tangent is not None and len(tangent)==2 and bearing is not None and math.isfinite(bearing)
                      and tangent[1]['point'][1]>tangent[0]['point'][1])
            result.append({'snapshot_time_utc':timestamp,'latitude_gate':latitude,
                           'source_axis_case_id':row['id'],'source_axis_case_pointer':'/cases/'+str(i),
                           'source_axis_case_status':row['status'],'source_axis_nominal_depth_m':row['nominal_depth_m'],
                           'source_axis_gate':gate,'source_axis_tangent_endpoints':tangent,
                           'locked_reference_bearing_degrees_true':bearing,
                           'axis_geometry_query_eligible':bool(eligible),
                           'model_axis_is_independent_observation':False,'physical_named_current_axis_validated':False})
    return result


def diagnose_profiles(z,profiles,op):
    numerical=[dict(p,along_velocity_m_s=np.array([np.nan if x is None else x for x in p['along_velocity_m_s']])) for p in profiles]
    selected,lower=select_profile(z,numerical,op['primary_threshold_m_s'],op['core_search_depth_interval_m'])
    all_layers=[{'profile_index':i,'layers':[connected_layer(z,p['along_velocity_m_s'],threshold,op['core_search_depth_interval_m']) for threshold in op['thresholds_m_s']]} for i,p in enumerate(profiles)]
    if selected is not None:
        primary=all_layers[selected]['layers'][op['thresholds_m_s'].index(op['primary_threshold_m_s'])]
        value=lower['lower_isotach_depth_m'];other=primary['lower_depth_m']
        if (value is None)!=(other is None) or (value is not None and not math.isclose(value,other,abs_tol=1e-9)):
            raise ValueError('Frozen lower contour and paired layer implementations disagree')
    return {'selected_profile_index':selected,'horizontal_selection_status':'no_qualifying_node' if selected is None else ('edge_maximum_axis_unresolved' if selected in [0,len(profiles)-1] else 'interior_sampled_maximum_not_independently_validated_axis'),
            'primary_core_lower_descriptor':lower,'all_profile_threshold_layers':all_layers,
            'selected_profile_threshold_layers':all_layers[selected]['layers'] if selected is not None else []}


def validate_retained(result,op):
    keys=[(r['snapshot_time_utc'],r['latitude_gate']) for r in result['samples']]
    expected={(t,lat) for t in op['snapshot_times_utc'] for lat in op['latitude_gates']}
    if len(keys)!=len(expected) or set(keys)!=expected:raise ValueError('Preserve every declared source gate/date, including missing axes')
    for row in result['samples']:
        if not row['axis_geometry_query_eligible']:
            if row.get('sampled_profiles'):raise ValueError('Unresolved source axis cannot drive a field query')
            continue
        if len(row['sampled_profiles'])!=5:raise ValueError('Five fixed offsets required')
        if row['decoded_profile_sha256']!=canonical_hash(row['sampled_profiles']):raise ValueError('Retained profile hash mismatch')
        if row['source_returned_timestamp_utc']!=row['snapshot_time_utc']:raise ValueError('Different source timestamp')
        check=diagnose_profiles(row['depth_levels_m'],row['sampled_profiles'],op)
        for key,value in check.items():
            if row[key]!=value:raise ValueError('Retained profile diagnosis mismatch')
    if any(result['eligibility'].values()):raise ValueError('Regional diagnostics do not establish physical promotion')


def main():
    op=json.loads((ROOT/OPERATOR).read_bytes())
    for path,pin in op['input_sha256'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=pin:raise ValueError('Pinned sampling input changed: '+path)
    if any(op['eligibility'].values()):raise ValueError('No physical admission')
    report=json.loads((ROOT/op['axis_report_file']).read_bytes())
    cases=axis_cases(report,op);rows=[];cell_pairs=0;decoded_bytes=0;OUT.mkdir(exist_ok=True)
    with netCDF4.Dataset(op['opendap_dataset']) as ds:
        z=np.asarray(ds['depth'][:]);lats=np.asarray(ds['lat'][:]);lons=np.asarray(ds['lon'][:]);times=np.asarray(ds['time'][:])
        if len(z)!=40 or float(z[0])!=0 or float(z[-1])!=5000 or ds['depth'].units!='m' or ds['depth'].positive!='down':raise ValueError('Unexpected standard source depth axis')
        attrs={k:str(ds.getncattr(k)) for k in ds.ncattrs()}
        if attrs.get('field_type')!='instantaneous':raise ValueError('Exact instantaneous product required')
        variable_attrs={}
        for name,standard in [('water_u','eastward_sea_water_velocity'),('water_v','northward_sea_water_velocity')]:
            var=ds[name]
            if var.dimensions!=('time','depth','lat','lon') or var.units!='m/s' or var.standard_name!=standard:raise ValueError('Velocity units/axes/frame changed')
            variable_attrs[name]={k:str(var.getncattr(k)) for k in var.ncattrs()}
        for case in cases:
            row=dict(case)
            if not case['axis_geometry_query_eligible']:
                row.update(status='source_axis_geometry_unresolved_no_velocity_query',sampled_profiles=[])
                rows.append(row);continue
            timestamp=case['snapshot_time_utc'];target=datetime.strptime(timestamp,'%Y-%m-%dT%H:%M:%SZ')
            value=netCDF4.date2num(target,ds['time'].units,calendar=getattr(ds['time'],'calendar','gregorian'))
            matches=np.flatnonzero(times==value)
            if len(matches)!=1:raise ValueError('Exact prescribed timestamp missing or duplicated')
            it=int(matches[0]);returned=netCDF4.num2date(times[it],ds['time'].units,calendar=getattr(ds['time'],'calendar','gregorian')).strftime('%Y-%m-%dT%H:%M:%SZ')
            point=case['source_axis_gate']['point'];bearing=case['locked_reference_bearing_degrees_true']
            targets=[GEOD.fwd(*point,bearing+90,offset*1000)[:2] for offset in op['normal_offsets_km']]
            indices=[(int(np.argmin(abs(lats-lat))),int(np.argmin(abs(lons-lon)))) for lon,lat in targets]
            y0,y1=min(p[0] for p in indices),max(p[0] for p in indices);x0,x1=min(p[1] for p in indices),max(p[1] for p in indices)
            pairs=check_budget((len(z),y1-y0+1,x1-x0+1),cell_pairs,op['maximum_total_cell_pairs'])
            if decoded_bytes+pairs*2*8>op['maximum_total_decoded_velocity_bytes']:raise ValueError('Decoded byte budget exceeded before field read')
            u=np.ma.filled(ds['water_u'][it,:,y0:y1+1,x0:x1+1],np.nan);v=np.ma.filled(ds['water_v'][it,:,y0:y1+1,x0:x1+1],np.nan)
            cell_pairs+=pairs;decoded_bytes+=u.nbytes+v.nbytes
            if decoded_bytes>op['maximum_total_decoded_velocity_bytes']:raise ValueError('Unexpected decoded array size')
            if np.any(abs(u[np.isfinite(u)])>10) or np.any(abs(v[np.isfinite(v)])>10):raise ValueError('Unexpected velocity scale')
            profiles=[]
            for offset,(lon,lat),(iy,ix) in zip(op['normal_offsets_km'],targets,indices):
                distance=GEOD.inv(lon,lat,float(lons[ix]),float(lats[iy]))[2]/1000
                if distance>op['maximum_nearest_cell_distance_km']:raise ValueError('Target outside nearest-cell tolerance')
                eu,nv=u[:,iy-y0,ix-x0],v[:,iy-y0,ix-x0]
                along=along_velocity(eu,nv,bearing);along=np.where(np.isfinite(eu)&np.isfinite(nv),along,np.nan)
                profiles.append({'normal_offset_km':offset,'target_lon_lat':[lon,lat],'sampled_lon_lat':[float(lons[ix]),float(lats[iy])],
                                 'global_latitude_index':iy,'global_longitude_index':ix,'nearest_cell_distance_km':distance,
                                 'eastward_velocity_m_s':clean(eu),'northward_velocity_m_s':clean(nv),'along_velocity_m_s':clean(along)})
            row.update(status='regional_dated_model_component_diagnostics_not_physical_current_depth',source_time_index=it,source_returned_timestamp_utc=returned,
                       source_tau_hours_since_analysis=float(ds['tau'][it]) if 'tau' in ds.variables else None,
                       depth_levels_m=clean(z),sampled_profiles=profiles,decoded_profile_sha256=canonical_hash(profiles),
                       retrieved_hyperslab={'time_index':it,'depth_indices_inclusive':[0,39],'latitude_indices_inclusive':[y0,y1],'longitude_indices_inclusive':[x0,x1]},
                       **diagnose_profiles(z,profiles,op))
            rows.append(row)
            (OUT/'checkpoint.json').write_text(json.dumps({'status':'PARTIAL_UNREVIEWED','samples':rows,'full_goal_complete':False},indent=2,allow_nan=False)+'\n',encoding='utf8')
            print(json.dumps({'date':timestamp,'latitude':case['latitude_gate'],'horizontal_status':row['horizontal_selection_status'],'primary':row['primary_core_lower_descriptor']}),flush=True)
    queried=[r for r in rows if r['axis_geometry_query_eligible']]
    counts={'prescribed_cases':len(rows),'queried_cases':len(queried),'source_axis_unresolved_cases':len(rows)-len(queried),
            'retained_velocity_profiles':sum(len(r['sampled_profiles']) for r in rows),
            'selected_primary_lower_crossings':sum(r['primary_core_lower_descriptor']['lower_isotach_depth_m'] is not None for r in queried),
            'selected_horizontal_edge_maxima':sum(r['horizontal_selection_status']=='edge_maximum_axis_unresolved' for r in queried),
            'selected_resolved_threshold_layers':{str(t):sum(r['selected_profile_threshold_layers'][i]['layer_thickness_m'] is not None for r in queried if r['selected_profile_index'] is not None) for i,t in enumerate(op['thresholds_m_s'])},
            'decoded_velocity_cell_pairs':cell_pairs,'decoded_velocity_array_bytes':decoded_bytes,
            'whole_route_physical_depth_profiles':0,'water_volume_estimates':0}
    result={'schema':'osw.kuroshio-hycom-depth.v1','status':'SOURCE_AXIS_REFERENCED_REGIONAL_MODEL_COMPONENT_LAYERS',
            'entity_id':'current:kuroshio','operator_file':OPERATOR,'operator_sha256':hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),
            'input_sha256':op['input_sha256'],'axis_report_file':op['axis_report_file'],'source_product':op['source_product'],
            'opendap_dataset':op['opendap_dataset'],'source_global_attributes':attrs,'source_variable_attributes':variable_attrs,
            'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),'counts':counts,'samples':rows,
            'raw_HTTP_payload_bytes_instrumented':False,'source_subset_wire_byte_hash_claimed':False,
            'model_products_are_statistically_independent':False,'daily_axis_and_instantaneous_velocity_are_simultaneous':False,
            'width_join_performed':False,'eligibility':op['eligibility'],'full_goal_complete':False}
    validate_retained(result,op)
    (OUT/'candidate.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print(json.dumps(counts))


if __name__=='__main__':main()
