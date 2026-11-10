"""Cloud-only bounded snapshot sampling around an editorial current route."""
from datetime import datetime,timezone
import hashlib
import json
import math
from pathlib import Path
import urllib.parse
import urllib.request
import netCDF4
import numpy as np
from pyproj import Geod

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/eac-hycom-route-depth-operator-v1.json'
OUT=Path('eac-hycom-route-depth-v1')
GEOD=Geod(ellps='WGS84')


def along_velocity(u,v,bearing):
    theta=math.radians(bearing)
    return u*math.sin(theta)+v*math.cos(theta)


def core_lower_contour(z,v,threshold,core_interval):
    z=np.asarray(z,dtype=float);v=np.asarray(v,dtype=float)
    if len(z)!=len(v) or len(z)<2 or not np.all(np.isfinite(z)) or not np.all(np.diff(z)>0) or not math.isfinite(threshold) or threshold<=0:raise ValueError('Finite ascending depths and positive velocity threshold required')
    candidates=np.flatnonzero((z>=core_interval[0])&(z<=core_interval[1])&np.isfinite(v)&(v>threshold))
    if not len(candidates):return {'status':'no_qualifying_poleward_core','lower_isotach_depth_m':None}
    seed=int(candidates[np.argmax(v[candidates])]);result={'lower_isotach_depth_m':None,'core_depth_m':float(z[seed]),'core_along_velocity_m_s':float(v[seed]),'threshold_m_s':threshold}
    for i in range(seed,len(z)-1):
        if not np.isfinite(v[i+1]):return dict(result,status='censored_before_missing_or_dry_level',last_contiguous_above_threshold_depth_m=float(z[i]))
        if v[i+1]<=threshold:
            value=z[i]+(threshold-v[i])*(z[i+1]-z[i])/(v[i+1]-v[i])
            return dict(result,status='adjacent_lower_isotach_crossing',lower_isotach_depth_m=float(value),depth_bracket_m=[float(z[i]),float(z[i+1])])
    return dict(result,status='censored_at_last_model_depth',last_contiguous_above_threshold_depth_m=float(z[-1]))


def select_profile(z,profiles,threshold,core_interval):
    # Preserve declared offset order as a deterministic tie break. Never broaden
    # the search window or switch nodes independently for alternate contours.
    candidates=[]
    for i,p in enumerate(profiles):
        result=core_lower_contour(z,p['along_velocity_m_s'],threshold,core_interval)
        if 'core_along_velocity_m_s' in result:candidates.append((result['core_along_velocity_m_s'],-i,i,result))
    if not candidates:return None,{'status':'no_qualifying_poleward_core_in_declared_window','lower_isotach_depth_m':None}
    _,_,i,result=max(candidates)
    return i,result


def clean(a):return [float(v) if np.isfinite(v) else None for v in a]


def canonical_hash(data):
    return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def fetch_patch(url,limit):
    with urllib.request.urlopen(url,timeout=60) as response:
        raw=response.read(limit+1)
    if len(raw)>limit:raise ValueError('Remote spatial subset exceeds declared byte cap')
    if not raw.startswith((b'CDF',b'\x89HDF')):raise ValueError('Subset response is not NetCDF')
    return raw


def main():
    op=json.loads((ROOT/OPERATOR).read_bytes());route_raw=(ROOT/op['route_file']).read_bytes()
    if hashlib.sha256(route_raw).hexdigest()!=op['route_sha256']:raise ValueError('Editorial route changed')
    if any(op['eligibility'].values()):raise ValueError('No physical or whole-current admission')
    points=json.loads(route_raw)['coordinates_lon_lat'];distances=[0.]
    for a,b in zip(points,points[1:]):distances.append(distances[-1]+GEOD.inv(*a,*b)[2]/1000)
    rows=[];payload_bytes=0;cell_pairs=0;OUT.mkdir(exist_ok=True)
    for timestamp in op['snapshot_times_utc']:
        for index,point in enumerate(points):
            a,b=points[max(index-1,0)],points[min(index+1,len(points)-1)]
            bearing=GEOD.inv(*a,*b)[0]%360
            targets=[]
            for offset in op['normal_offsets_km']:
                lon,lat,_=GEOD.fwd(*point,bearing+90,offset*1000);targets.append((lon,lat))
            bounds={'north':max(p[1] for p in targets)+.05,'south':min(p[1] for p in targets)-.05,'east':max(p[0] for p in targets)+.09,'west':min(p[0] for p in targets)-.09}
            params=[('var','water_u'),('var','water_v'),('time',timestamp),('accept','netcdf'),('horizStride','1'),('vertStride','1')]+list(bounds.items())
            url=op['subset_service']+'?'+urllib.parse.urlencode(params)
            raw=fetch_patch(url,op['maximum_patch_bytes']);payload_bytes+=len(raw)
            if payload_bytes>op['maximum_total_payload_bytes']:raise ValueError('Total payload cap exceeded')
            with netCDF4.Dataset('patch.nc',memory=raw) as ds:
                for variable,standard in [('water_u','eastward_sea_water_velocity'),('water_v','northward_sea_water_velocity')]:
                    if ds[variable].getncattr('standard_name')!=standard or ds[variable].getncattr('units')!='m/s':raise ValueError('Unreviewed component definition or units')
                if ds['depth'].getncattr('units')!='m' or ds['depth'].getncattr('positive')!='down':raise ValueError('Depth datum/units changed')
                z=np.asarray(ds['depth'][:]);lats=np.asarray(ds['lat'][:]);lons=np.asarray(ds['lon'][:])
                if len(z)!=40 or float(z[0])!=0 or float(z[-1])!=5000:raise ValueError('Expected complete40-level source axis')
                if ds['water_u'].dimensions!=('time','depth','lat','lon') or ds['water_v'].dimensions!=('time','depth','lat','lon'):raise ValueError('Velocity array axes changed')
                time=netCDF4.num2date(ds['time'][0],ds['time'].units,calendar=getattr(ds['time'],'calendar','gregorian')).strftime('%Y-%m-%dT%H:%M:%SZ')
                if time!=timestamp:raise ValueError('Server selected another timestamp')
                u=np.ma.filled(ds['water_u'][0],np.nan);v=np.ma.filled(ds['water_v'][0],np.nan)
                cell_pairs+=u.size
                if cell_pairs>op['maximum_total_cell_pairs']:raise ValueError('Cell budget exceeded')
                if np.any(np.abs(u[np.isfinite(u)])>10) or np.any(np.abs(v[np.isfinite(v)])>10):raise ValueError('Unreviewed scaling or extreme velocities')
                profiles=[]
                for offset,(lon,lat) in zip(op['normal_offsets_km'],targets):
                    iy=int(np.argmin(abs(lats-lat)));ix=int(np.argmin(abs(lons-lon)))
                    distance=GEOD.inv(lon,lat,float(lons[ix]),float(lats[iy]))[2]/1000
                    if distance>op['maximum_nearest_cell_distance_km']:raise ValueError('Nearest source node too far from declared target')
                    eu,nv=u[:,iy,ix],v[:,iy,ix];along=along_velocity(eu,nv,bearing);along=np.where(np.isfinite(eu)&np.isfinite(nv),along,np.nan)
                    profiles.append({'normal_offset_km':offset,'target_lon_lat':[lon,lat],'sampled_lon_lat':[float(lons[ix]),float(lats[iy])],'nearest_cell_distance_km':distance,'eastward_velocity_m_s':clean(eu),'northward_velocity_m_s':clean(nv),'along_velocity_m_s':clean(along)})
                tau=float(ds['tau'][0]) if 'tau' in ds.variables else None
                global_attrs={k:str(ds.getncattr(k)) for k in ds.ncattrs()}
            numerical=[dict(p,along_velocity_m_s=np.array([np.nan if v is None else v for v in p['along_velocity_m_s']])) for p in profiles]
            selected,result=select_profile(z,numerical,op['primary_lower_isotach_m_s'],op['core_search_depth_interval_m'])
            alternate=[]
            if selected is not None:
                for threshold in op['alternate_lower_isotachs_m_s']:alternate.append(core_lower_contour(z,numerical[selected]['along_velocity_m_s'],threshold,op['core_search_depth_interval_m']))
            sample={'snapshot_time_utc':time,'route_vertex_index':index,'reference_distance_km':distances[index],'editorial_lon_lat':point,'downstream_reference_bearing_degrees_true':bearing,'depth_levels_m':clean(z),'sampled_profiles':profiles,'selected_profile_index':selected,'primary_core_lower_descriptor':result,'alternate_contours_at_same_horizontal_node':alternate,'subset_url':url,'subset_bytes':len(raw),'subset_sha256':hashlib.sha256(raw).hexdigest(),'decoded_profile_sha256':canonical_hash(profiles),'source_tau_hours_since_analysis':tau,'source_global_attributes':global_attrs,'geographic_window_establishes_current_identity':False}
            rows.append(sample)
            (OUT/'checkpoint.json').write_text(json.dumps({'status':'PARTIAL_UNREVIEWED_SNAPSHOT_SAMPLES','samples':rows,'full_goal_complete':False},indent=2,allow_nan=False)+'\n',encoding='utf8')
            print(json.dumps({'snapshot':time,'vertex':index,'offset_km':profiles[selected]['normal_offset_km'] if selected is not None else None,'descriptor':result}),flush=True)
    result={'schema':'osw.eac-hycom-route-depth-candidate.v1','status':'BOUNDED_MODEL_ROUTE_SNAPSHOT_DIAGNOSTICS_PENDING_REVIEW','entity_id':op['entity_id'],'source_product':op['source_product'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),'route_file':op['route_file'],'route_sha256':op['route_sha256'],'reference_route_length_km':distances[-1],'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),'counts':{'snapshots':len(op['snapshot_times_utc']),'route_vertices':len(points),'sampled_cases':len(rows),'cases_with_adjacent_lower_isotach_crossing':sum(r['primary_core_lower_descriptor']['status']=='adjacent_lower_isotach_crossing' for r in rows),'subset_payload_bytes':payload_bytes,'sampled_velocity_cell_pairs':cell_pairs},'samples':rows,'eligibility':op['eligibility'],'full_goal_complete':False}
    OUT.mkdir(exist_ok=True);(OUT/'candidate.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8')
    print(json.dumps(result['counts']))


if __name__=='__main__':main()
