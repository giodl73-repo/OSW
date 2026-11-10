"""Cloud derivation from published monthly cross-transect velocity sections."""
import hashlib
import json
import os
import tempfile
from collections import Counter
from pathlib import Path
from urllib.request import Request,urlopen
import netCDF4
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/kuroshio-chandler-seasonal-depth-operator-v1.json'


def weights(depth):
    depth=np.asarray(depth,dtype=float)
    if len(depth)<2 or not np.all(np.isfinite(depth)) or depth[0]<0 or np.any(np.diff(depth)<=0):raise ValueError('Invalid depth grid')
    dz=np.diff(depth)
    return np.r_[depth[0]+dz[0]/2,(dz[:-1]+dz[1:])/2,dz[-1]/2]


def core_index(vel,depth,longitude):
    # Source PX40 rule: maximum northward flow west of western-region minimum.
    integrated=np.nansum(vel*weights(depth)[None,:],axis=1)
    integrated[np.all(~np.isfinite(vel),axis=1)]=np.nan
    filtered=np.convolve(integrated,np.array([1,2,3,2,1])/9,'same')
    filtered[:2]=np.nan;filtered[-2:]=np.nan
    longitude=np.asarray(longitude)
    west=np.flatnonzero((longitude<150)&np.isfinite(filtered))
    if not len(west):return None,None
    separator=int(west[np.argmin(filtered[west])])
    candidates=np.flatnonzero((longitude<longitude[separator])&np.isfinite(filtered))
    if not len(candidates):return None,None
    index=int(candidates[np.argmax(filtered[candidates])])
    if filtered[index]<=0:return None,None
    return index,float(filtered[index])


def crossing(depth,poleward,start,threshold):
    if poleward[start]<=threshold:return {'status':'threshold_not_exceeded','depth_m':None}
    for i in range(start,len(depth)-1):
        a,b=poleward[i],poleward[i+1]
        if not np.isfinite(a) or not np.isfinite(b):return {'status':'unknown_gap_after_core','depth_m':None,'last_supported_depth_m':float(depth[i])}
        if a>threshold and b<=threshold:
            z=depth[i]+(threshold-a)/(b-a)*(depth[i+1]-depth[i])
            return {'status':'resolved_adjacent_level_crossing','depth_m':round(float(z),6),'bracketing_native_depths_m':[float(depth[i]),float(depth[i+1])]}
    return {'status':'right_censored_at_native_domain_end','depth_m':None,'last_supported_depth_m':float(depth[-1])}


def describe(depth,velocity):
    poleward=np.asarray(velocity,dtype=float)
    if not np.any(np.isfinite(poleward)) or np.nanmax(poleward)<=0:
        return {'status':'unknown_no_supported_poleward_core','core_depths_m':[],'crossings':{}}
    maximum=float(np.nanmax(poleward));indices=np.flatnonzero(poleward==maximum)
    valid=np.flatnonzero(np.isfinite(poleward))
    start=int(indices[-1])
    return {'status':'derived_native_sampled_core','core_depths_m':[float(depth[i]) for i in indices],
            'maximum_poleward_velocity_m_s':maximum,
            'core_at_shallowest_valid_level':bool(indices[0]==valid[0]),'core_at_deepest_valid_level':bool(indices[-1]==valid[-1]),
            'valid_depth_domain_m':[float(depth[valid[0]]),float(depth[valid[-1]])],
            'crossings':{str(t):crossing(depth,poleward,start,t) for t in [0.0,0.05,0.1]},
            'physical_thickness_m':None,'physical_depth_uncertainty_m':None}


def climatologies(records,depth):
    result=[]
    for month in range(1,13):
        group=[r for r in records if r['calendar_month']==month and r['status']=='axis_within_KUROSHIO_gate']
        if len(group)!=16:
            result.append({'calendar_month':month,'status':'unknown_incomplete16year_axis_support','year_samples':len(group)});continue
        profiles=np.array([[np.nan if v is None else v for v in r['native_velocity_profile_m_s']] for r in group])
        count=np.sum(np.isfinite(profiles),axis=0)
        means=np.full(len(depth),np.nan)
        full=count==16
        means[full]=np.mean(profiles[:,full],axis=0)
        result.append({'calendar_month':month,'status':'current_following_monthly_mean_profile','year_samples':16,
                       'years':[2004,2019],'finite_profile_counts_per_depth':count.tolist(),
                       'native_mean_velocity_profile_m_s':[float(v) if np.isfinite(v) else None for v in means],
                       'derived':describe(depth,means),
                       'individual_crossing_status_counts':{str(t):dict(Counter(r['derived']['crossings'].get(str(t),{}).get('status','no_core') for r in group)) for t in [0.0,0.05,0.1]}})
    return result


def inspect_file(path,operator):
    with netCDF4.Dataset(path) as ds:
        depth=np.asarray(ds['depth'][:],dtype=float);lon=np.asarray(ds['longitude'][:],dtype=float);lat=np.asarray(ds['latitude'][:],dtype=float)
        if ds['depth'].getncattr('units')!='m' or ds['depth'].getncattr('positive')!='down':raise ValueError('Unreviewed source vertical units/datum')
        var=ds['vel']
        if var.getncattr('units')!='m/s' or var.getncattr('positive')!='northward':raise ValueError('Unreviewed native velocity sign/units')
        dims=list(var.dimensions)
        if set(dims)!={'time','longitude','depth'}:raise ValueError('Unexpected velocity dimensions')
        velocity=np.transpose(np.ma.filled(var[:],np.nan),[dims.index(k) for k in ['time','longitude','depth']])
        time=ds['time'];dates=netCDF4.num2date(time[:],time.units,calendar=getattr(time,'calendar','standard'))
        if len(dates)!=192 or [(d.year,d.month) for d in dates]!=[(y,m) for y in range(2004,2020) for m in range(1,13)]:raise ValueError('Expected192 distinct source months')
        if len(depth)!=76 or abs(depth[-1]-1975)>1e-6 or np.any(np.diff(lon)<=0):raise ValueError('Unexpected source grid')
        records=[]
        for t,date in enumerate(dates):
            index,speed=core_index(velocity[t],depth,lon)
            row={'date':date.strftime('%Y-%m-%d'),'calendar_month':date.month,'core_longitude_index':index}
            if index is None or not operator['KUROSHIO_axis_longitude_gate_degrees_east'][0]<=lon[index]<=operator['KUROSHIO_axis_longitude_gate_degrees_east'][1]:
                row.update(status='unknown_axis_outside_KUROSHIO_gate',unconstrained_axis_longitude=None if index is None else float(lon[index]))
            else:
                profile=velocity[t,index,:]
                row.update(status='axis_within_KUROSHIO_gate',longitude=float(lon[index]),latitude=float(lat[index]),
                           axis_smoothed_depth_integrated_northward_velocity_m2_s=speed,
                           native_velocity_profile_m_s=[float(v) if np.isfinite(v) else None for v in profile],derived=describe(depth,profile))
            records.append(row)
        metadata={'dimensions':{k:len(v) for k,v in ds.dimensions.items()},'variable_attributes':{k:{a:ds[k].getncattr(a) for a in ds[k].ncattrs()} for k in ['time','depth','longitude','latitude','vel','vel_err']},
                  'global_attributes':{k:ds.getncattr(k) for k in ds.ncattrs()}}
    return {'schema':'osw.kuroshio-chandler-seasonal-depth.v1','status':'REGIONAL_RECONSTRUCTED_MONTHLY_AXIS_DEPTH_DESCRIPTORS',
            'entity_id':'current:kuroshio','source_doi':'10.5281/zenodo.5851312','source_file':'px40_velocity.nc',
            'source_metadata':metadata,'native_depths_m':depth.tolist(),'records':records,'monthly_climatologies':climatologies(records,depth),
            'monthly_profile_count':len(records),'axis_gate_status_counts':dict(Counter(r['status'] for r in records)),
            'new_independent_observations':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0,'full_goal_complete':False}


def json_safe(value):
    if isinstance(value,dict):return {k:json_safe(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [json_safe(v) for v in value]
    if isinstance(value,np.generic):return json_safe(value.item())
    if isinstance(value,np.ndarray):return json_safe(value.tolist())
    if isinstance(value,float) and not np.isfinite(value):return None
    return value


def main():
    if os.environ.get('GITHUB_ACTIONS')!='true':raise RuntimeError('Ocean-field processing is cloud-only')
    operator=json.loads((ROOT/OPERATOR).read_bytes())
    with tempfile.TemporaryDirectory() as folder:
        path=Path(folder)/'px40_velocity.nc';md5=hashlib.md5();sha=hashlib.sha256();total=0
        with urlopen(Request(operator['source_download_url'],headers={'User-Agent':'OSW-depth-research/1.0'}),timeout=50) as response,path.open('wb') as output:
            while chunk:=response.read(1048576):
                total+=len(chunk)
                if total>operator['maximum_source_bytes']:raise ValueError('Source byte bound exceeded')
                md5.update(chunk);sha.update(chunk);output.write(chunk)
        if total!=operator['expected_source_bytes'] or md5.hexdigest()!=operator['expected_source_md5']:raise ValueError('Source checksum/size mismatch')
        result=inspect_file(path,operator)
    result['source_raw_sha256']=sha.hexdigest();result['source_raw_md5']=md5.hexdigest();result['source_raw_bytes']=total
    result['input_sha256']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [OPERATOR,'analysis/derive_kuroshio_chandler_seasonal_depth_v1.py']}
    directory=ROOT/'kuroshio-chandler-seasonal-depth-v1';directory.mkdir(exist_ok=True)
    result['nonfinite_source_metadata_serialized_as_null']=True
    (directory/'candidate.json').write_bytes((json.dumps(json_safe(result),indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode('utf8'))
    print(json.dumps({'months':result['monthly_profile_count'],'axis_status':result['axis_gate_status_counts'],
                      'climatologies':[{'month':r['calendar_month'],'status':r['status'],'core':r.get('derived',{}).get('core_depths_m'),'crossings':r.get('derived',{}).get('crossings')} for r in result['monthly_climatologies']]}))


if __name__=='__main__':main()
