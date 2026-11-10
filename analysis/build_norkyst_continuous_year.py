"""Monthly assets and a chronological year report using the frozen section operators."""
from scientific_readback import dependency_pins
from contextlib import ExitStack
from datetime import datetime, timezone
import json
from pathlib import Path
import zipfile

import numpy as np

import build_norkyst_continuous_sections as operators
import norkyst_continuous_source as source

ROOT=source.ROOT
FOLDER=ROOT/source.SOURCE


def map_accumulators(months):
    accumulators={}
    for month in months:
        start,end,halo_start,halo_end=source.month_window(month)
        count=int((end-start).total_seconds()/3600)
        raw_weights=np.zeros(count+72);raw_weights[36:36+count]=1/count
        low_weights=np.zeros(count+72);low_weights[1:-1]=np.convolve(np.ones(count)/count,operators.kernel())
        accumulators[month]={'first_epoch':int(halo_start.timestamp()),'raw_weights':raw_weights,'lowpass_weights':low_weights,
                             'raw_sum':np.zeros((48,50,3)),'lowpass_sum':np.zeros((48,50,3)),
                             'raw_count':np.zeros((48,50),dtype=np.int32),'lowpass_count':np.zeros((48,50),dtype=np.int32)}
    return accumulators


def accumulate_maps(accumulators,times,arrays):
    paired=arrays['sea_mask'][None,:,:]==1
    for name in source.VARIABLES:paired=paired & (arrays[name]!=-32767)
    decoded=np.stack([arrays[name].astype(float)*.001+(30 if name=='salinity' else 0) for name in source.VARIABLES],axis=-1)
    decoded=np.where(paired[:,:,:,None],decoded,0)
    for accumulator in accumulators.values():
        indices=(np.asarray(times,dtype=np.int64)-accumulator['first_epoch'])//3600
        selected=(indices>=0)&(indices<len(accumulator['raw_weights']))
        if not selected.any():continue
        for kind in ['raw','lowpass']:
            weights=accumulator[kind+'_weights'][indices[selected]]
            accumulator[kind+'_sum']+=np.einsum('t,tijk->ijk',weights,decoded[selected])
            accumulator[kind+'_count']+=np.sum(paired[selected] & (weights[:,None,None]>0),axis=0,dtype=np.int32)


def finish_maps(accumulators):
    results={}
    for month,accumulator in accumulators.items():
        result={}
        for kind in ['raw','lowpass']:
            expected=int(np.count_nonzero(accumulator[kind+'_weights']>0))
            complete=accumulator[kind+'_count']==expected
            result[kind]={'expected_source_hours':expected,'valid_source_hours':accumulator[kind+'_count'],
                          'mean':np.where(complete[:,:,None],accumulator[kind+'_sum'],np.nan)}
        results[month]=result
    return results


def read_original(acquisition,record,kind,archives):
    content=archives[record['archive_file']].read(record[kind+'_member'])
    if source.sha(content)!=record[kind+'_sha256']:
        raise ValueError('Changed original '+kind+' member')
    descriptor=next(a for a in acquisition['archives'] if a['file']==record['archive_file'])
    if source.sha(content)!=descriptor['members'][record[kind+'_member']]:
        raise ValueError('Rebound original member descriptor')
    return content


def verify_overlap(record,times,values,old,pilot,archives):
    if old['metadata_sha256']!=record['metadata_sha256']:raise ValueError('Changed earlier daily metadata')
    if old['key']==record['key']:
        if old['field_sha256']!=record['field_sha256']:raise ValueError('Changed earlier hourly response')
        return
    old_raw=read_original(pilot,old,'field',archives)
    old_times,old_values=source.parse_fields(old_raw,old['date'],old['first_hour'],old['last_hour'])
    indices=np.searchsorted(times,old_times)
    if np.any(indices>=len(times)) or not np.array_equal(np.asarray(times)[indices],old_times):
        raise ValueError('Missing earlier overlap timestamps')
    for name in source.VARIABLES:
        if not np.array_equal(values[name][indices],old_values[name]):raise ValueError('Changed overlapping original field')
    if not np.array_equal(values['sea_mask'],old_values['sea_mask']):raise ValueError('Changed overlapping sea mask')


def load_sections(acquisition_path,pilot_path):
    """Validate sources, including every overlap with the retained two-month capsule."""
    source.preflight()
    acquisition=json.loads(acquisition_path.read_bytes());pilot=json.loads(pilot_path.read_bytes())
    for packet in [acquisition,pilot]:
        if packet['status']!='complete_original_acquisition_pending_section_and_filter_analysis' or packet['failures']:
            raise ValueError('Incomplete acquisition cannot supply complete-month analysis')
        if packet['preflight_sha256']!=source.PREFLIGHT_SHA256:raise ValueError('Changed source declaration')
        actual=[(r['date'],r['first_hour'],r['last_hour']) for r in packet['responses']]
        if actual!=source.daily_requests(packet['requested_months']):raise ValueError('Missing or duplicate source request')
    legacy,latitudes,distances,rows,cols,weights=operators.grid_and_legacy()
    earlier={r['date']:r for r in pilot['responses']}
    pins={acquisition_path.relative_to(ROOT).as_posix():source.sha(acquisition_path.read_bytes()),
          pilot_path.relative_to(ROOT).as_posix():source.sha(pilot_path.read_bytes()),
          source.SOURCE+'/preflight.json':source.PREFLIGHT_SHA256}
    stamps=[];profiles=[];noon_matches={};overlap_matches=[]
    accumulators=map_accumulators(acquisition['requested_months'])
    with ExitStack() as stack:
        archives={}
        for packet in [acquisition,pilot]:
            for descriptor in packet['archives']:
                file=descriptor['file'];path=ROOT/file
                if source.sha(path.read_bytes())!=descriptor['sha256']:raise ValueError('Changed original archive')
                if file in pins and pins[file]!=descriptor['sha256']:raise ValueError('Conflicting archive identity')
                pins[file]=descriptor['sha256']
                if file not in archives:archives[file]=stack.enter_context(zipfile.ZipFile(path))
                if sorted(archives[file].namelist())!=sorted(descriptor['members']):raise ValueError('Changed archive membership')
        for record in acquisition['responses']:
            raw=read_original(acquisition,record,'field',archives)
            metadata=read_original(acquisition,record,'metadata',archives)
            source.metadata(metadata,record['date'])
            times,values=source.parse_fields(raw,record['date'],record['first_hour'],record['last_hour'])
            accumulate_maps(accumulators,times,values)
            old=earlier.get(record['date'])
            if old:
                verify_overlap(record,times,values,old,pilot,archives)
                overlap_matches.append(record['date'])
            if record['date'][8:]=='15' and record['first_hour']<=12<=record['last_hour']:
                month=int(record['date'][5:7]);index=12-record['first_hour'];old_values=legacy[month]['packed_field_arrays']
                if any(not np.array_equal(values[name][index],old_values[name]) for name in source.VARIABLES):
                    raise ValueError('Changed historical noon field at '+record['date'])
                if not np.array_equal(values['sea_mask'],old_values['sea_mask']):raise ValueError('Changed historical noon mask')
                noon_matches[str(month)]='Exact packed fields and mask at all2400 original grid cells'
            stamps.extend(times);profiles.append(operators.interpolate(values,rows,cols,weights))
    stamps=np.asarray(stamps,dtype=np.int64)
    if np.any(np.diff(stamps)<=0):raise ValueError('Source timestamps are not unique and increasing')
    return {'acquisition':acquisition,'epochs':stamps,'profiles':np.concatenate(profiles),
            'latitude':latitudes,'distance':distances,'input_sha256':pins,
            'historical_noon_matches':noon_matches,'pilot_overlap_dates':overlap_matches,
            'regional_maps':finish_maps(accumulators),'regional_coordinates':legacy[1]['packed_field_arrays']}


def monthly_sections(data):
    for month in sorted(data['acquisition']['requested_months']):
        start,end,halo_start,halo_end=source.month_window(month)
        expected=np.arange(int(halo_start.timestamp()),int(halo_end.timestamp()),3600,dtype=np.int64)
        selected=(data['epochs']>=expected[0])&(data['epochs']<=expected[-1])
        if not np.array_equal(data['epochs'][selected],expected):raise ValueError('Incomplete month or filter halo')
        raw=data['profiles'][selected];filtered=operators.lowpass(raw)
        core=(expected>=int(start.timestamp()))&(expected<int(end.timestamp()))
        yield month,expected[core],raw[core],filtered[core]


def build():
    acquisition_path=FOLDER/'acquisition-year.json';pilot_path=FOLDER/'acquisition-pilot.json'
    acquisition=json.loads(acquisition_path.read_bytes())
    if sorted(acquisition['requested_months'])!=list(range(1,13)):raise ValueError('Year analysis requires all twelve declared months')
    data=load_sections(acquisition_path,pilot_path)
    expected=np.arange(int(datetime(2023,12,30,12,tzinfo=timezone.utc).timestamp()),
                       int(datetime(2025,1,2,12,tzinfo=timezone.utc).timestamp()),3600,dtype=np.int64)
    if not np.array_equal(data['epochs'],expected):raise ValueError('Incomplete year, leap day or global halo')
    if len(data['historical_noon_matches'])!=12 or len(data['pilot_overlap_dates'])!=70:
        raise ValueError('Incomplete comparisons with retained source evidence')
    records=[];assets=[]
    for month,times,raw,filtered in monthly_sections(data):
        start,end,_,_=source.month_window(month)
        arrays={'epoch_seconds':times,'latitude_degrees_north':data['latitude'],'distance_km':data['distance']}
        summary={}
        for index,name in enumerate(source.VARIABLES):
            arrays['raw_'+name]=raw[:,:,index];arrays['lowpass_'+name]=filtered[:,:,index]
            summary[name]={'raw':operators.summarize(raw[:,:,index]),'lowpass':operators.summarize(filtered[:,:,index])}
        path=FOLDER/f'section-hourly-year-2024-{month:02d}.npz';operators.write_npz(path,arrays)
        asset={'month':month,'file':path.relative_to(ROOT).as_posix(),'sha256':source.sha(path.read_bytes()),
               'bytes':path.stat().st_size,'calendar_hours':len(times),'section_positions':len(data['latitude'])}
        assets.append(asset)
        records.append({'month':month,'start_utc':start.isoformat(),'end_exclusive_utc':end.isoformat(),
                        'expected_month_hours':len(times),'summary':summary,'current_width_km':None,'hourly_asset':asset['file']})
    complete=all(all(count==month['expected_month_hours'] for count in month['summary'][name][kind]['valid_hours'])
                 for month in records for name in source.VARIABLES for kind in ['raw','lowpass'])
    pins=data['input_sha256']
    pins.update(dependency_pins())
    for file in ['analysis/build_norkyst_continuous_sections.py','analysis/norkyst_continuous_source.py',
                 'plans/norkyst-ingoy-within-month-support-2026-10-17.md','plans/norkyst-ingoy-monthly-regional-map-rules-2026-10-17.md']:
        pins[file]=source.sha((ROOT/file).read_bytes())
    def nullable(array):
        array=np.asarray(array)
        return np.where(np.isfinite(array),array,None).tolist()
    regional=[]
    longitude=np.asarray(data['regional_coordinates']['lon']);latitude=np.asarray(data['regional_coordinates']['lat'])
    arrow_rows,arrow_cols=np.meshgrid(np.arange(0,48,5),np.arange(0,50,5),indexing='ij')
    ar,ac=arrow_rows.ravel(),arrow_cols.ravel()
    for month in range(1,13):
        entry={'month':month}
        for kind in ['raw','lowpass']:
            native=data['regional_maps'][month][kind]
            entry[kind]={'expected_source_hours':native['expected_source_hours'],
                         'valid_source_hours':native['valid_source_hours'].tolist(),
                         'mean':{name:nullable(native['mean'][:,:,index]) for index,name in enumerate(source.VARIABLES)}}
            east=native['mean'][ar,ac,1];north=native['mean'][ar,ac,2];speed=np.hypot(east,north)
            lon,lat=longitude[ar,ac],latitude[ar,ac]
            lon2,lat2,_=operators.GEOD.fwd(lon,lat,np.degrees(np.arctan2(east,north)),np.full_like(speed,1000.))
            x,y=operators.TRANSFORM.transform(lon,lat);x2,y2=operators.TRANSFORM.transform(lon2,lat2)
            norm=np.hypot(x2-x,y2-y);vx=(x2-x)/norm*speed;vy=(y2-y)/norm*speed
            entry[kind]['arrows']=[{'row':int(r),'column':int(c),'x_km':float(c*3.2),'y_km':float(r*3.2),
                                    'velocity_x_m_s':float(u) if np.isfinite(u) else None,
                                    'velocity_y_m_s':float(v) if np.isfinite(v) else None}
                                   for r,c,u,v in zip(ar,ac,vx,vy)]
        regional.append(entry)
    sx,sy=operators.TRANSFORM.transform(np.full(191,24.),data['latitude'])
    map_file=FOLDER/'regional-monthly-means-year.json'
    map_document={'schema':'osw.norkyst-regional-monthly-means.v1','year':2024,'depth_m':10,
                  'variable_units':{'salinity':'1','u_eastward':'m/s','v_northward':'m/s'},
                  'status':'model_region_means_not_current_footprint','source_grid':source.preflight()['source_grid'],
                  'longitude':data['regional_coordinates']['lon'],'latitude':data['regional_coordinates']['lat'],
                  'section_plane_xy_km':np.column_stack([(sx-source.X[0]*800)/1000,(sy-source.Y[0]*800)/1000]).tolist(),
                  'plotting':{'projection':'Original source polar stereographic grid, equal relative projected kilometre axes',
                              'x_limits_km':[0,156.8],'y_limits_km':[0,150.4],'salinity_color_limits':[33,35.2],
                              'arrow_grid_stride':5,'arrow_scale_m_s_per_projected_km':.07,'arrow_reference_m_s':.5,
                              'arrow_rotation':'True east/north mean velocity projected with a1km geodesic direction probe; normalized direction and original mean speed'},
                  'months':regional,'source_project':'Norkyst_v3','source_license':'CC-BY-4.0','credit':acquisition['credit'],
                  'input_sha256':pins,'generator_sha256':source.sha(Path(__file__).read_bytes()),
                  'lowpass_mean_method':'Exact linear convolution of the monthly averaging window and the71-point kernel; complete positive-weight source support required',
                  'scope':'Fixed offshore model patch; no coastline, physical current boundary, width, annual width extrema or state containment admitted.',
                  'physical_geometry_admitted':False,'new_width_record_admitted':False}
    map_file.write_bytes((json.dumps(map_document,indent=2,allow_nan=False)+'\n').encode())
    report={'schema':'osw.norkyst-continuous-year-diagnostic.v1','status':'research_model_temporal_support_not_current_width_admission',
            'current_context_id':'norwegian-coastal','year':2024,'completed_months':list(range(1,13)),
            'acquired_hourly_fields':len(data['epochs']),'complete_annual_timestamp_coverage':True,
            'complete_annual_section_support':complete,'calendar_hours':sum(m['expected_month_hours'] for m in records),
            'section':source.preflight()['section'],'source_grid':source.preflight()['source_grid'],
            'variable_units':{'salinity':'1','u_eastward':'m/s','v_northward':'m/s'},
            'section_latitudes_degrees_north':data['latitude'].tolist(),'section_distances_km':data['distance'].tolist(),
            'filter':source.preflight()['filter'],'standard_deviation_ddof':0,'sample_quantiles_are_confidence_intervals':False,
            'sample_quantile_levels':[.05,.5,.95],'sample_quantile_method':'linear',
            'monthly_assets':assets,'monthly_asset_format':'NPZ with NPY float64 raw/lowpass sections and int64 UTC epoch seconds; NaN preserves missing support',
            'months':records,'historical_noon_field_comparison':data['historical_noon_matches'],
            'pilot_overlap_dates_verified':data['pilot_overlap_dates'],'source_project':'Norkyst_v3',
            'source_license':'CC-BY-4.0','credit':acquisition['credit'],'input_sha256':pins,
            'generator_sha256':source.sha(Path(__file__).read_bytes()),
            'regional_maps':{'file':map_file.relative_to(ROOT).as_posix(),'sha256':source.sha(map_file.read_bytes())},
            'interpretation':'Complete calendar sampling of model fields at one offshore fixed section and10m layer. Low-pass filtering attenuates tides and other high-frequency variation, not a complete harmonic tidal solution. The section does not establish coastal coverage, physical current identity or boundaries. Monthly distributions are not confidence intervals or annual physical width extrema.',
            'new_width_record_admitted':False,'whole_current_width_km':None,'annual_width_range_km':None,
            'annual_extrema_eligible':False,'rank_eligible':False,'physical_geometry_admitted':False}
    return report


def main():
    report=build();path=FOLDER/'section-diagnostic-year.json'
    path.write_bytes((json.dumps(report,indent=2,allow_nan=False)+'\n').encode())
    print('Built twelve monthly assets;',report['calendar_hours'],'calendar hours; no physical-width admission')


if __name__=='__main__':main()
