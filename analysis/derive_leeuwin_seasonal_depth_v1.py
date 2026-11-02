"""Cloud-only local mean-profile boundaries; never extrapolate a whole current."""
import hashlib
import json
import math
from pathlib import Path
import netCDF4
import numpy as np
import audit_leeuwin_depth_source_v1 as source

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/leeuwin-seasonal-depth-operator-v1.json'
OUT=Path('leeuwin-seasonal-depth-v1')


def rotate(u,v,bearing):
    theta=math.radians(bearing)
    return u*math.sin(theta)+v*math.cos(theta)


def lower_crossing(depth,velocity,core_interval):
    z=np.asarray(depth,dtype=float);v=np.asarray(velocity,dtype=float)
    if len(z)!=len(v) or len(z)<2 or not np.all(np.isfinite(z)) or not np.all(np.diff(z)>0):raise ValueError('Distinct ascending finite depths required')
    eligible=np.flatnonzero((z>=core_interval[0])&(z<=core_interval[1])&np.isfinite(v)&(v<0))
    if len(eligible)==0:return {'status':'no_poleward_core','boundary_depth_m':None}
    seed=int(eligible[np.argmin(v[eligible])]);result={'core_depth_m':float(z[seed]),'core_velocity_m_s':float(v[seed]),'boundary_depth_m':None}
    for i in range(seed,len(z)-1):
        if not np.isfinite(v[i+1]):return dict(result,status='gap_before_boundary',last_contiguous_poleward_depth_m=float(z[i]))
        if v[i+1]>=0:
            value=z[i]-v[i]*(z[i+1]-z[i])/(v[i+1]-v[i])
            return dict(result,status='adjacent_zero_crossing',boundary_depth_m=float(value),crossing_bracket_m=[float(z[i]),float(z[i+1])])
    return dict(result,status='censored_at_deepest_level',minimum_reach_m=float(z[-1]))


def mean_profile(u,v,uq,vq,selected,flags,bearing):
    a=u[selected];b=v[selected];qa=uq[selected];qb=vq[selected]
    accepted=np.isfinite(a)&np.isfinite(b)&np.isin(qa,flags)&np.isin(qb,flags)
    counts=accepted.sum(axis=0);vel=rotate(a,b,bearing)
    means=np.divide(np.where(accepted,vel,0).sum(axis=0),counts,out=np.full(a.shape[1],np.nan),where=counts>0)
    observed=accepted&(qa==1)&(qb==1)
    return means,counts,observed.sum(axis=0)


def clean(values):
    return [float(x) if np.isfinite(x) else None for x in values]


def main():
    operator=json.loads((ROOT/OPERATOR).read_bytes())
    if any(operator['eligibility'].values()):raise ValueError('No whole-current admission')
    source.main();audit=json.loads((source.OUT/'source-audit.json').read_bytes())
    if audit['source_sha256']!=operator['source_sha256']:raise ValueError('Pinned source hash changed')
    with netCDF4.Dataset(source.OUT/'tr50-filled-adcp.nc') as ds:
        if ds.getncattr('Site_code')!=operator['site_id']:raise ValueError('Wrong mooring')
        for name in ['UCUR','VCUR']:
            if ds[name].getncattr('units')!='m s-1' or ds[name].dimensions!=('TIME','DEPTH'):raise ValueError('Velocity units or axes changed')
        z=np.ma.filled(ds['DEPTH'][:],np.nan)
        if ds['DEPTH'].getncattr('units') not in ['m','meters','metres']:raise ValueError('Depth units changed')
        times=netCDF4.num2date(ds['TIME'][:],ds['TIME'].units,calendar=ds['TIME'].calendar)
        months=np.array([t.month for t in times]);dates=[t.strftime('%Y-%m-%d') for t in times]
        if len(set(dates))!=len(dates) or dates!=sorted(dates):raise ValueError('Daily ordering/uniqueness changed')
        arrays=[np.ma.filled(ds[n][:],np.nan) for n in ['UCUR','VCUR','UCUR_quality_control','VCUR_quality_control']]
        lat=float(ds['LATTITUDE'][0]);lon=float(ds['LONGITUDE'][0])
    cases=[('month_'+str(m),[m],'calendar_month') for m in range(1,13)]+[('phase_'+'_'.join(map(str,p)),p,'two_month_phase') for p in operator['two_month_phases']]+[('annual',list(range(1,13)),'annual_mean_context')]
    profiles=[]
    for id,phase,kind in cases:
        selected=np.isin(months,phase)
        v,n,observed=mean_profile(*arrays,selected,operator['accepted_component_flags'],operator['local_along_mean_bearing_degrees_true'])
        sensitivity,sn,so=mean_profile(*arrays,selected,operator['sensitivity_component_flags'],operator['local_along_mean_bearing_degrees_true'])
        boundary=lower_crossing(z,v,operator['core_search_depth_interval_m'])
        if boundary['boundary_depth_m'] is not None:boundary['display_depth_m']=10*math.floor(boundary['boundary_depth_m']/10+0.5)
        profiles.append({'id':id,'phase_kind':kind,'calendar_months':phase,'selected_daily_records':int(selected.sum()),'contributing_years':sorted({t.year for t,ok in zip(times,selected) if ok}),'boundary':boundary,'depth_levels_m':clean(z),'mean_along_velocity_m_s':clean(v),'paired_valid_daily_counts':n.tolist(),'paired_observed_daily_counts':observed.tolist(),'observed_only_sensitivity':{'boundary':lower_crossing(z,sensitivity,operator['core_search_depth_interval_m']),'paired_valid_daily_counts':sn.tolist()},'monthly_values_not_independent_daily_boundaries':True})
    result={'schema':'osw.leeuwin-seasonal-depth-candidate.v1','status':'CLOUD_DERIVED_LOCAL_BOUNDARIES_PENDING_SCIENTIFIC_ADMISSION','entity_id':operator['entity_id'],'site_id':operator['site_id'],'latitude_degrees_north':lat,'longitude_degrees_east':lon,'source_sha256':audit['source_sha256'],'source_period':{'start':dates[0],'end':dates[-1],'daily_records':len(dates)},'operator_file':OPERATOR,'operator_sha256':hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),'source_acknowledgement':operator['source_acknowledgement'],'source_licence':'CC-BY-4.0','eligibility':operator['eligibility'],'profiles':profiles,'raw_source_values_admitted_to_depth_register':False,'full_goal_complete':False}
    OUT.mkdir(exist_ok=True);(OUT/'candidate.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8')
    print(json.dumps({'period':result['source_period'],'profiles':[{'id':r['id'],'days':r['selected_daily_records'],'boundary':r['boundary'],'observed_only':r['observed_only_sensitivity']['boundary']} for r in profiles]},indent=2))


if __name__=='__main__':main()
