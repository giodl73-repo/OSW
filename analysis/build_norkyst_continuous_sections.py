"""Complete-month raw/low-pass model profiles, preserving gaps and all original pins."""
from scientific_readback import canonicalize
import argparse
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import zipfile

import numpy as np

from build_norkyst_ingoy_timeline import TRANSFORM, GEOD
import norkyst_continuous_source as source

ROOT = source.ROOT
FOLDER = ROOT / source.SOURCE


def kernel():
    weights = np.convolve(np.convolve(np.ones(24,dtype=np.int64),np.ones(24,dtype=np.int64)),np.ones(25,dtype=np.int64))
    assert len(weights)==71 and int(weights.sum())==14400
    return weights.astype(np.float64)/14400


def lowpass(values):
    """Centered 71-hour support, with no padding, bridging or channel mixing."""
    values = np.asarray(values,dtype=np.float64)
    if values.ndim!=3 or values.shape[2]!=3 or values.shape[0]<71:
        raise ValueError('Expected at least71 hourly profiles with three paired fields')
    paired = np.isfinite(values).all(axis=2)
    working = np.where(paired[:,:,None],values,0)
    output = np.full(values.shape,np.nan,dtype=np.float64)
    weights=kernel()
    for point in range(values.shape[1]):
        support=np.convolve(paired[:,point].astype(np.int32),np.ones(71,dtype=np.int32),mode='valid')==71
        for field in range(3):
            filtered=np.convolve(working[:,point,field],weights,mode='valid')
            output[35:-35,point,field]=np.where(support,filtered,np.nan)
    return output


def summarize(values):
    values=np.asarray(values,dtype=np.float64)
    count=np.isfinite(values).sum(axis=0)
    complete=count==len(values)
    result={'valid_hours':count.astype(int).tolist(),'expected_hours':len(values)}
    for label,fn in [('mean',lambda x:np.mean(x,axis=0)),
                     ('standard_deviation',lambda x:np.std(x,axis=0,ddof=0)),
                     ('p05',lambda x:np.quantile(x,.05,axis=0)),
                     ('median',lambda x:np.quantile(x,.5,axis=0)),
                     ('p95',lambda x:np.quantile(x,.95,axis=0))]:
        calculated=fn(values[:,complete]) if complete.any() else []
        row=[None]*values.shape[1]
        for index,value in zip(np.flatnonzero(complete),calculated):row[int(index)]=round(float(value),8)
        result[label]=row
    return result


def grid_and_legacy():
    acquisition=json.loads((ROOT/'research/norkyst-ingoy-2024-monthly-sample-receipts.json').read_bytes())
    receipts={}
    for record in acquisition['observations']:
        raw=(ROOT/record['file']).read_bytes()
        if source.sha(raw)!=record['receipt_sha256']:raise ValueError('Changed older hourly receipt')
        receipt=json.loads(raw)
        if source.sha((ROOT/receipt['source_response_file']).read_bytes())!=receipt['source_response_sha256']:
            raise ValueError('Changed older hourly source response')
        receipts[int(record['date'][5:7])]=receipt
    grid=receipts[1]['packed_field_arrays']
    longitude,latitude=np.asarray(grid['lon']),np.asarray(grid['lat'])
    x,y=TRANSFORM.transform(longitude,latitude)
    expected_x=np.asarray(source.X)[None,:]*800;expected_y=np.asarray(source.Y)[:,None]*800
    if np.max(np.hypot(x-expected_x,y-expected_y))>1:raise ValueError('Legacy source grid/projection mismatch')
    latitudes=np.asarray([round(71.1+i*.01,2) for i in range(191)])
    x,y=TRANSFORM.transform(np.full(191,24),latitudes)
    fx,fy=(x/800-source.X[0])/4,(y/800-source.Y[0])/4
    ix,iy=np.floor(fx).astype(int),np.floor(fy).astype(int)
    if np.any(ix<0) or np.any(ix>=len(source.X)-1) or np.any(iy<0) or np.any(iy>=len(source.Y)-1):
        raise ValueError('Fixed section outside source patch')
    dx,dy=fx-ix,fy-iy
    rows=np.stack([iy,iy,iy+1,iy+1],axis=1)
    cols=np.stack([ix,ix+1,ix,ix+1],axis=1)
    weights=np.stack([(1-dx)*(1-dy),dx*(1-dy),(1-dx)*dy,dx*dy],axis=1)
    distances=np.asarray([GEOD.inv(24,71.1,24,float(lat))[2]/1000 for lat in latitudes])
    distances=np.round(distances,6)
    return receipts,latitudes,distances,rows,cols,weights


def interpolate(arrays,rows,cols,weights):
    valid=arrays['sea_mask'][rows,cols][None,:,:]==1
    for name in source.VARIABLES:valid=valid & (arrays[name][:,rows,cols]!=-32767)
    paired=valid.all(axis=2)
    result=[]
    for name in source.VARIABLES:
        corners=arrays[name][:,rows,cols].astype(np.float64)*.001+(30 if name=='salinity' else 0)
        values=np.sum(corners*weights[None,:,:],axis=2)
        result.append(np.where(paired,values,np.nan))
    return np.stack(result,axis=2)


def write_npz(path,arrays):
    """Standard NPY members in a deterministic ZIP container."""
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as output:
        for name,array in sorted(arrays.items()):
            buffer=io.BytesIO();np.save(buffer,np.asarray(array),allow_pickle=False)
            info=zipfile.ZipInfo(name+'.npy',date_time=(1980,1,1,0,0,0))
            info.external_attr=0o100644<<16
            output.writestr(info,buffer.getvalue(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)


def build(phase='pilot',write_asset=True,return_arrays=False):
    declaration=source.preflight()
    acquisition_path=FOLDER/('acquisition-'+phase+'.json')
    acquisition=json.loads(acquisition_path.read_bytes())
    if acquisition['status']!='complete_original_acquisition_pending_section_and_filter_analysis' or acquisition['failures']:
        raise ValueError('Source acquisition is not complete')
    if acquisition['preflight_sha256']!=source.PREFLIGHT_SHA256:raise ValueError('Rebound acquisition preflight')
    expected_requests=source.daily_requests(acquisition['requested_months'])
    actual=[(r['date'],r['first_hour'],r['last_hour']) for r in acquisition['responses']]
    if actual!=expected_requests:raise ValueError('Missing, duplicated or reordered daily source coverage')
    legacy,latitudes,distances,rows,cols,weights=grid_and_legacy()
    timestamps=[];profiles=[];pins={acquisition_path.relative_to(ROOT).as_posix():source.sha(acquisition_path.read_bytes())}
    comparisons={};archives={}
    for archive in acquisition['archives']:
        path=ROOT/archive['file']
        if source.sha(path.read_bytes())!=archive['sha256']:raise ValueError('Changed original archive')
        pins[archive['file']]=archive['sha256'];archives[archive['file']]=archive
    for record in acquisition['responses']:
        archive=archives[record['archive_file']]
        with zipfile.ZipFile(ROOT/record['archive_file']) as original:
            raw=original.read(record['field_member']);meta=original.read(record['metadata_member'])
        for kind,content in [('field',raw),('metadata',meta)]:
            if source.sha(content)!=record[kind+'_sha256'] or source.sha(content)!=archive['members'][record[kind+'_member']]:
                raise ValueError('Changed original archive member')
        source.metadata(meta,record['date'])
        times,arrays=source.parse_fields(raw,record['date'],record['first_hour'],record['last_hour'])
        if record['date'][8:]=='15' and record['first_hour']<=12<=record['last_hour']:
            month=int(record['date'][5:7]);old=legacy[month]['packed_field_arrays'];index=12-record['first_hour']
            for name in source.VARIABLES:
                if not np.array_equal(arrays[name][index],np.asarray(old[name])):
                    raise ValueError('New archive field differs from retained noon snapshot: '+record['date']+' '+name)
            if not np.array_equal(arrays['sea_mask'],np.asarray(old['sea_mask'])):raise ValueError('Changed retained source mask')
            comparisons[str(month)]='Exact original packed arrays and sea mask match all2400 cells at retained noon'
        timestamps.extend(times);profiles.append(interpolate(arrays,rows,cols,weights))
    timestamps=np.asarray(timestamps,dtype=np.int64);profiles=np.concatenate(profiles,axis=0)
    if len(np.unique(timestamps))!=len(timestamps):raise ValueError('Duplicate source timestamps')
    bulk={'latitude_degrees_north':latitudes,'distance_km':distances}
    months=[]
    for month in acquisition['requested_months']:
        start,end,halo_start,halo_end=source.month_window(month)
        expected=np.arange(int(halo_start.timestamp()),int(halo_end.timestamp()),3600,dtype=np.int64)
        selected=(timestamps>=expected[0])&(timestamps<=expected[-1])
        if not np.array_equal(timestamps[selected],expected):raise ValueError('Missing hourly/halo support')
        raw=profiles[selected];filtered=lowpass(raw)
        core=(expected>=int(start.timestamp()))&(expected<int(end.timestamp()))
        times=expected[core];raw=raw[core];filtered=filtered[core]
        stem=f'month_{month:02d}_'
        bulk[stem+'epoch_seconds']=times
        summary={}
        for index,name in enumerate(source.VARIABLES):
            bulk[stem+'raw_'+name]=raw[:,:,index];bulk[stem+'lowpass_'+name]=filtered[:,:,index]
            summary[name]={'raw':summarize(raw[:,:,index]),'lowpass':summarize(filtered[:,:,index])}
        months.append({'month':month,'start_utc':start.isoformat(),'end_exclusive_utc':end.isoformat(),
                       'expected_month_hours':len(times),'acquired_halo_hours':len(expected),
                       'summary':summary,'current_width_km':None})
    asset=FOLDER/('section-hourly-'+phase+'.npz')
    if write_asset:write_npz(asset,bulk)
    report={'schema':'osw.norkyst-continuous-section-diagnostic.v1','status':'research_temporal_support_not_current_width_admission',
            'current_context_id':'norwegian-coastal','source_project':'Norkyst_v3','source_license':'CC-BY-4.0',
            'credit':acquisition['credit'],'preflight_file':source.SOURCE+'/preflight.json','preflight_sha256':source.PREFLIGHT_SHA256,
            'target_year':2024,'target_months':declaration['target_months'],'completed_months':acquisition['requested_months'],
            'complete_annual_temporal_support':len(months)==12,'acquired_hourly_fields':len(timestamps),
            'completed_calendar_hours':sum(m['expected_month_hours'] for m in months),
            'section':declaration['section'],'source_grid':declaration['source_grid'],
            'section_distances_km':distances.tolist(),'section_latitudes_degrees_north':latitudes.tolist(),
            'filter':{'name':'24/24/25-hour boxcar convolution','weights':kernel().tolist(),'support_hours_each_side':35,
                      'halo_hours_each_side':36,'missing_policy':'All71 paired hourly profiles required; no bridging or padding'},
            'sample_quantiles_are_confidence_intervals':False,'standard_deviation_ddof':0,
            'interpretation':'Model temporal variation at a fixed offshore meridional section and 10m layer. Low-pass filtering attenuates tides and other high-frequency variability; it is not a complete harmonic tidal solution. Missing support is not zero flow. No physical current edges, whole-current width, seasonal width range or annual extrema established.',
            'previous_noon_field_comparison':comparisons,'months':months,
            'bulk_asset':{'file':asset.relative_to(ROOT).as_posix(),'sha256':source.sha(asset.read_bytes()),'bytes':asset.stat().st_size,
                          'format':'NPZ: little-endian NPY arrays, float64 sections and int64 UTC epoch seconds; NaN preserves missing support'},
            'visualization':{'svg_file':'figures/norkyst-ingoy-continuous-months.svg','png_file':'figures/norkyst-ingoy-continuous-months.png',
                             'generator_file':'analysis/build_norkyst_continuous_figure.py',
                             'generator_sha256':source.sha((ROOT/'analysis/build_norkyst_continuous_figure.py').read_bytes())},
            'input_sha256':pins,'generator_sha256':source.sha(Path(__file__).read_bytes()),
            'source_validator_sha256':source.sha((ROOT/'analysis/norkyst_continuous_source.py').read_bytes()),
            'new_width_record_admitted':False,'whole_current_width_km':None,'annual_width_range_km':None,'rank_eligible':False}
    report=canonicalize(report)
    return (report,bulk) if return_arrays else report


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--all-months',action='store_true');args=parser.parse_args()
    phase='year' if args.all_months else 'pilot';report=build(phase)
    path=FOLDER/('section-diagnostic-'+phase+'.json');path.write_bytes((json.dumps(report,indent=2,allow_nan=False)+'\n').encode())
    print('Built',len(report['months']),'complete monthly sections;',report['completed_calendar_hours'],'monthly hours; physical widths unresolved')


if __name__=='__main__':main()
