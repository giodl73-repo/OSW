"""Cloud-only averaging and descriptor sensitivity; no fitted depth boundary."""
from datetime import date
import hashlib
import json
from pathlib import Path
import netCDF4
import numpy as np
import audit_leeuwin_depth_source_v1 as source
from derive_leeuwin_seasonal_depth_v1 import lower_crossing,rotate

ROOT=Path(__file__).resolve().parents[1]
OUT=Path('leeuwin-depth-sensitivity-v1')
METHODS=['pooled_daily','equal_month_climatologies','equal_year_months','daily_11day_calendar_window']


def finite_mean(values):
    a=np.asarray(values,dtype=float);n=np.isfinite(a).sum(axis=0)
    return np.divide(np.where(np.isfinite(a),a,0).sum(axis=0),n,out=np.full(a.shape[1:],np.nan),where=n>0)


def calendar_day(t):
    if t.month==2 and t.day==29:return None
    return (date(2001,t.month,t.day)-date(2001,1,1)).days


def calendar_profiles(velocity,times):
    days=[calendar_day(t) for t in times];count=np.zeros((365,velocity.shape[1]));total=np.zeros_like(count)
    for i,k in enumerate(days):
        if k is None:continue
        valid=np.isfinite(velocity[i]);count[k]+=valid;total[k]+=np.where(valid,velocity[i],0)
    windows_count=sum(np.roll(count,shift,axis=0) for shift in range(-5,6))
    windows_total=sum(np.roll(total,shift,axis=0) for shift in range(-5,6))
    return np.divide(windows_total,windows_count,out=np.full_like(total,np.nan),where=windows_count>0)


def profiles(velocity,times,months):
    selected=np.array([t.month in months for t in times]);month_means=[];year_months=[]
    for month in months:
        rows=np.array([t.month==month for t in times]);month_means.append(finite_mean(velocity[rows]))
        years=sorted({t.year for t in times if t.month==month});means=[]
        for year in years:
            rows=np.array([t.month==month and t.year==year for t in times]);means.append(finite_mean(velocity[rows]))
        year_months.append(finite_mean(means))
    climatology=calendar_profiles(velocity,times)
    reference_months=np.array([(date(2001,1,1).fromordinal(date(2001,1,1).toordinal()+k)).month for k in range(365)])
    return {'pooled_daily':finite_mean(velocity[selected]),'equal_month_climatologies':finite_mean(month_means),'equal_year_months':finite_mean(year_months),'daily_11day_calendar_window':finite_mean(climatology[np.isin(reference_months,months)])}


def threshold_descriptor(z,v,interval,tolerance):
    if not np.isfinite(tolerance) or tolerance<0:raise ValueError('Nonnegative explicit velocity tolerance required')
    strict=lower_crossing(z,v,interval)
    # Keep the original poleward core selection: a tolerance changes the stopping
    # contour, never which current core is being traced.
    if 'core_depth_m' not in strict:return dict(strict,velocity_contour_m_s=-tolerance)
    start=int(np.flatnonzero(z==strict['core_depth_m'])[0]);result={'core_depth_m':strict['core_depth_m'],'boundary_depth_m':None,'velocity_contour_m_s':-tolerance}
    if v[start]>=-tolerance:return dict(result,status='core_not_stronger_than_tolerance')
    for i in range(start,len(z)-1):
        if not np.isfinite(v[i+1]):return dict(result,status='gap_before_contour')
        if v[i+1]>=-tolerance:
            value=z[i]+(-tolerance-v[i])*(z[i+1]-z[i])/(v[i+1]-v[i])
            return dict(result,status='adjacent_velocity_contour',boundary_depth_m=float(value),bracket_m=[float(z[i]),float(z[i+1])])
    return dict(result,status='contour_not_reached_in_sampled_profile')


def negative_local_maxima(z,v,interval):
    core=lower_crossing(z,v,interval)
    if 'core_depth_m' not in core:return []
    return [{'depth_m':float(z[i]),'velocity_m_s':float(v[i]),'is_flow_boundary':False} for i in range(1,len(z)-1) if z[i]>core['core_depth_m'] and np.all(np.isfinite(v[i-1:i+2])) and v[i]<0 and v[i]>v[i-1] and v[i]>=v[i+1]]


def main():
    op=json.loads((ROOT/'research/leeuwin-seasonal-depth-operator-v1.json').read_bytes())
    baseline=json.loads((ROOT/'research/source-data/leeuwin-seasonal-depth-v1/seasonal-candidate.json').read_bytes())
    source.main();audit=json.loads((source.OUT/'source-audit.json').read_bytes())
    if audit['source_sha256']!=op['source_sha256']:raise ValueError('Source changed')
    with netCDF4.Dataset(source.OUT/'tr50-filled-adcp.nc') as ds:
        z=np.asarray(ds['DEPTH'][:]);times=netCDF4.num2date(ds['TIME'][:],ds['TIME'].units,calendar=ds['TIME'].calendar)
        u,v,uq,vq=[np.ma.filled(ds[n][:],np.nan) for n in ['UCUR','VCUR','UCUR_quality_control','VCUR_quality_control']]
    valid=np.isfinite(u)&np.isfinite(v)&np.isin(uq,op['accepted_component_flags'])&np.isin(vq,op['accepted_component_flags'])
    velocity=np.where(valid,rotate(u,v,348),np.nan)
    rows=[]
    for phase in baseline['profiles']:
        methods=profiles(velocity,times,phase['calendar_months']);checks=[]
        strict=lower_crossing(z,methods['pooled_daily'],op['core_search_depth_interval_m'])
        old={k:v for k,v in phase['boundary'].items() if k!='display_depth_m'}
        if strict.keys()!=old.keys() or any(not np.isclose(value,old[key],rtol=0,atol=1e-10) if isinstance(value,float) else value!=old[key] for key,value in strict.items()):raise ValueError('Pooled baseline no longer reproduces')
        for method,mean in methods.items():
            checks.append({'method':method,'strict_zero_crossing':lower_crossing(z,mean,op['core_search_depth_interval_m']),'negative_local_velocity_maxima':negative_local_maxima(z,mean,op['core_search_depth_interval_m']),'assumed_velocity_contours':[threshold_descriptor(z,mean,op['core_search_depth_interval_m'],t) for t in [0.001,0.005,0.01]],'along_velocity_at350m_m_s':float(mean[np.flatnonzero(z==350)[0]])})
        rows.append({'phase_id':phase['id'],'calendar_months':phase['calendar_months'],'methods':checks})
    result={'schema':'osw.leeuwin-depth-sensitivity.v1','source_sha256':audit['source_sha256'],'methods':METHODS,'calendar_window':'365-day reference year2001, eleven-day circular window, February29 excluded from this diagnostic method only','mean_weighting':'pooled_daily weights daily samples; equal_month_climatologies weights calendar months equally; equal_year_months weights each available year-month equally within a calendar month, then months equally; calendar-window averages eleven-day pooled daily climatologies over reference calendar days','period':'Same full2011-08-01 to2023-05-01 input as frozen v1; partial first/last years retained explicitly','negative_local_maxima_are_boundaries':False,'velocity_contours_are_uncertainty_bounds':False,'exact_paper_reproduction_claimed':False,'profiles':rows,'whole_current_admission':False,'full_goal_complete':False}
    OUT.mkdir(exist_ok=True);(OUT/'sensitivity.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8')
    print(json.dumps([r for r in rows if r['phase_id'] in ['phase_2_3','phase_8_9','annual']],indent=2))


if __name__=='__main__':main()
