"""Bounded direct OPeNDAP transport for the unchanged snapshot experiment."""
from datetime import datetime,timezone
import hashlib,json,math
from pathlib import Path
import netCDF4
import numpy as np
from sample_eac_hycom_route_depth_v1 import GEOD,along_velocity,select_profile,core_lower_contour,clean,canonical_hash

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/eac-hycom-route-depth-operator-v2.json'
OUT=Path('eac-hycom-route-depth-v2')


def check_budget(shape,used,maximum):
    if len(shape)!=3 or any(type(n) is not int or n<=0 for n in shape):raise ValueError('Positive depth/latitude/longitude shape required')
    pairs=math.prod(shape)
    if pairs>20000 or used+pairs>maximum:raise ValueError('Bounded model-cell budget exceeded before velocity retrieval')
    return pairs


def main():
    op=json.loads((ROOT/OPERATOR).read_bytes());raw=(ROOT/op['route_file']).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=op['route_sha256'] or any(op['eligibility'].values()):raise ValueError('Route pin or admission policy changed')
    points=json.loads(raw)['coordinates_lon_lat'];distances=[0.]
    for a,b in zip(points,points[1:]):distances.append(distances[-1]+GEOD.inv(*a,*b)[2]/1000)
    OUT.mkdir(exist_ok=True);rows=[];cell_pairs=0;decoded_bytes=0
    with netCDF4.Dataset(op['opendap_dataset']) as ds:
        z=np.asarray(ds['depth'][:]);lats=np.asarray(ds['lat'][:]);lons=np.asarray(ds['lon'][:]);numeric_times=np.asarray(ds['time'][:])
        if len(z)!=40 or float(z[0])!=0 or float(z[-1])!=5000 or ds['depth'].units!='m' or ds['depth'].positive!='down':raise ValueError('Unexpected source depth axis')
        variable_attrs={}
        for name,standard in [('water_u','eastward_sea_water_velocity'),('water_v','northward_sea_water_velocity')]:
            var=ds[name]
            if var.dimensions!=('time','depth','lat','lon') or var.units!='m/s' or var.standard_name!=standard:raise ValueError('Unexpected velocity axes, units or direction')
            variable_attrs[name]={k:str(var.getncattr(k)) for k in var.ncattrs()}
        attrs={k:str(ds.getncattr(k)) for k in ds.ncattrs()}
        if attrs.get('field_type')!='instantaneous':raise ValueError('Source no longer declares instantaneous fields')
        for timestamp in op['snapshot_times_utc']:
            target=datetime.strptime(timestamp,'%Y-%m-%dT%H:%M:%SZ');value=netCDF4.date2num(target,ds['time'].units,calendar=getattr(ds['time'],'calendar','gregorian'))
            matches=np.flatnonzero(numeric_times==value)
            if len(matches)!=1:raise ValueError('Exact snapshot time missing or duplicated')
            it=int(matches[0]);tau=float(ds['tau'][it]) if 'tau' in ds.variables else None
            for index,point in enumerate(points):
                a,b=points[max(0,index-1)],points[min(len(points)-1,index+1)];bearing=GEOD.inv(*a,*b)[0]%360
                targets=[GEOD.fwd(*point,bearing+90,offset*1000)[:2] for offset in op['normal_offsets_km']]
                indices=[(int(np.argmin(abs(lats-lat))),int(np.argmin(abs(lons-lon)))) for lon,lat in targets]
                y0,y1=min(p[0] for p in indices),max(p[0] for p in indices);x0,x1=min(p[1] for p in indices),max(p[1] for p in indices)
                pairs=check_budget((len(z),y1-y0+1,x1-x0+1),cell_pairs,op['maximum_total_cell_pairs'])
                u=np.ma.filled(ds['water_u'][it,:,y0:y1+1,x0:x1+1],np.nan);v=np.ma.filled(ds['water_v'][it,:,y0:y1+1,x0:x1+1],np.nan)
                cell_pairs+=pairs;decoded_bytes+=u.nbytes+v.nbytes
                if decoded_bytes>op['maximum_total_decoded_velocity_bytes']:raise ValueError('Decoded array byte cap exceeded')
                if np.any(abs(u[np.isfinite(u)])>10) or np.any(abs(v[np.isfinite(v)])>10):raise ValueError('Unexpected velocity scaling or magnitude')
                profiles=[]
                for offset,(lon,lat),(iy,ix) in zip(op['normal_offsets_km'],targets,indices):
                    distance=GEOD.inv(lon,lat,float(lons[ix]),float(lats[iy]))[2]/1000
                    if distance>op['maximum_nearest_cell_distance_km']:raise ValueError('Source node outside target tolerance')
                    eu,nv=u[:,iy-y0,ix-x0],v[:,iy-y0,ix-x0];along=along_velocity(eu,nv,bearing);along=np.where(np.isfinite(eu)&np.isfinite(nv),along,np.nan)
                    profiles.append({'normal_offset_km':offset,'target_lon_lat':[lon,lat],'sampled_lon_lat':[float(lons[ix]),float(lats[iy])],'global_latitude_index':iy,'global_longitude_index':ix,'nearest_cell_distance_km':distance,'eastward_velocity_m_s':clean(eu),'northward_velocity_m_s':clean(nv),'along_velocity_m_s':clean(along)})
                numerical=[dict(p,along_velocity_m_s=np.array([np.nan if v is None else v for v in p['along_velocity_m_s']])) for p in profiles]
                selected,result=select_profile(z,numerical,op['primary_lower_isotach_m_s'],op['core_search_depth_interval_m'])
                alternate=[]
                if selected is not None:
                    for threshold in op['alternate_lower_isotachs_m_s']:alternate.append(core_lower_contour(z,numerical[selected]['along_velocity_m_s'],threshold,op['core_search_depth_interval_m']))
                row={'snapshot_time_utc':timestamp,'source_time_index':it,'source_tau_hours_since_analysis':tau,'route_vertex_index':index,'reference_distance_km':distances[index],'editorial_lon_lat':point,'downstream_reference_bearing_degrees_true':bearing,'depth_levels_m':clean(z),'sampled_profiles':profiles,'selected_profile_index':selected,'horizontal_selection_status':'no_qualifying_node' if selected is None else ('edge_maximum_axis_unresolved' if selected in [0,len(profiles)-1] else 'interior_sampled_maximum_not_validated_axis'),'primary_core_lower_descriptor':result,'alternate_contours_at_same_horizontal_node':alternate,'opendap_dataset':op['opendap_dataset'],'retrieved_hyperslab':{'time_index':it,'depth_indices_inclusive':[0,39],'latitude_indices_inclusive':[y0,y1],'longitude_indices_inclusive':[x0,x1]},'decoded_profile_sha256':canonical_hash(profiles),'geographic_window_establishes_current_identity':False}
                rows.append(row);(OUT/'checkpoint.json').write_text(json.dumps({'status':'PARTIAL_UNREVIEWED_SNAPSHOT_SAMPLES','samples':rows,'full_goal_complete':False},indent=2,allow_nan=False)+'\n',encoding='utf8')
                print(json.dumps({'snapshot':timestamp,'vertex':index,'horizontal_status':row['horizontal_selection_status'],'offset':profiles[selected]['normal_offset_km'] if selected is not None else None,'descriptor':result}),flush=True)
    output={'schema':'osw.eac-hycom-route-depth-candidate.v2','status':'BOUNDED_MODEL_ROUTE_SNAPSHOT_DIAGNOSTICS_PENDING_REVIEW','entity_id':op['entity_id'],'source_product':op['source_product'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),'route_file':op['route_file'],'route_sha256':op['route_sha256'],'reference_route_length_km':distances[-1],'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),'source_global_attributes':attrs,'source_variable_attributes':variable_attrs,'counts':{'snapshots':2,'route_vertices':len(points),'sampled_cases':len(rows),'cases_with_adjacent_lower_isotach_crossing':sum(r['primary_core_lower_descriptor']['status']=='adjacent_lower_isotach_crossing' for r in rows),'selected_horizontal_edge_maxima':sum(r['horizontal_selection_status']=='edge_maximum_axis_unresolved' for r in rows),'sampled_velocity_cell_pairs':cell_pairs,'decoded_velocity_array_bytes':decoded_bytes},'raw_HTTP_payload_bytes_instrumented':False,'source_subset_wire_byte_hash_claimed':False,'samples':rows,'eligibility':op['eligibility'],'full_goal_complete':False}
    (OUT/'candidate.json').write_text(json.dumps(output,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8');print(json.dumps(output['counts']))


if __name__=='__main__':main()
