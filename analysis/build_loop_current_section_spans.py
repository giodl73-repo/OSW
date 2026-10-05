"""Pinned fixed-latitude component spans; never infer whole-current dimensions."""
import hashlib
import json
import math
from pathlib import Path
from build_gulf_stream_geostrophic_path import ROOT, GEOD, load_field, sample_velocity
from build_loop_current_adt_contours import field_arrays
from build_loop_current_recorded_dates import source_rows

PROTOCOL=ROOT/'plans/loop-current-section-span-protocol-v1.md'
LATITUDE=21.875
WINDOW=(-86.875,-85.125)

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def separation(west,east): return GEOD.inv(west,LATITUDE,east,LATITUDE)[2]/1000

def measure(profile,fraction,step):
    if not math.isfinite(fraction) or not 0<fraction<1 or not math.isfinite(step) or step<=0:
        raise ValueError('Invalid threshold/grid spacing')
    if any(not math.isfinite(r['longitude']) or (r['northward_m_s'] is not None and not math.isfinite(r['northward_m_s'])) for r in profile):
        raise ValueError('Nonfinite profile')
    if any(a['longitude']>=b['longitude'] for a,b in zip(profile,profile[1:])):
        raise ValueError('Profile must be ordered west to east')
    if any(abs(b['longitude']-a['longitude']-step)>1e-8 for a,b in zip(profile,profile[1:])):
        raise ValueError('Profile must retain adjacent native samples')
    valid=[(i,r) for i,r in enumerate(profile) if r['northward_m_s'] is not None]
    result={'fraction':fraction,'status':'missing_profile','span_km':None}
    if not valid:return result
    index,peak=max(valid,key=lambda pair:pair[1]['northward_m_s'])
    result.update(peak_longitude=peak['longitude'],peak_northward_m_s=peak['northward_m_s'])
    if peak['northward_m_s']<.15:
        result['status']='weak_or_no_northward_peak';return result
    threshold=peak['northward_m_s']*fraction
    result['threshold_m_s']=threshold
    for side,direction in [('west',-1),('east',1)]:
        previous=index;current=index+direction;boundary=None;reason='corridor_edge'
        while 0<=current<len(profile):
            inner,outer=profile[previous],profile[current]
            if outer['northward_m_s'] is None:reason='missing_velocity';break
            if outer['northward_m_s']<=threshold:
                ratio=(threshold-inner['northward_m_s'])/(outer['northward_m_s']-inner['northward_m_s'])
                boundary={'longitude':inner['longitude']+ratio*(outer['longitude']-inner['longitude']),
                          'bracket_longitudes':sorted([inner['longitude'],outer['longitude']])}
                reason='threshold_crossing';break
            previous=current;current+=direction
        result[side+'_boundary']=boundary;result[side+'_stop_reason']=reason
    if result['west_boundary'] is None or result['east_boundary'] is None:
        result['status']='unbracketed_boundary';return result
    west,east=result['west_boundary'],result['east_boundary']
    span=separation(west['longitude'],east['longitude'])
    inner_west=max(west['bracket_longitudes']);inner_east=min(east['bracket_longitudes'])
    lower=separation(inner_west,inner_east) if inner_west<inner_east else 0
    upper=separation(min(west['bracket_longitudes']),max(east['bracket_longitudes']))
    cells=span/separation(peak['longitude'],peak['longitude']+step)
    result.update(status='paired_boundaries',span_km=round(span,6),grid_bracket_span_km=[round(lower,6),round(upper,6)],native_cell_spacings=round(cells,3),resolution_review_required=cells<4)
    return result

def compute(source,method):
    if method not in ['noaa','adt']:raise ValueError('Unknown source method')
    fields=load_field(source) if method=='noaa' else field_arrays(source)
    origin=source['grid_origin_lon_lat'][0];step=source['grid_step_degrees'][0]
    count=source['subset_shape'][1] if method=='noaa' else source['grid_shape'][1]
    profile=[]
    for i in range(count):
        longitude=origin+i*step
        if not WINDOW[0]<=longitude<=WINDOW[1]:continue
        velocity=sample_velocity(source,fields,longitude,LATITUDE)
        profile.append({'longitude':longitude,'northward_m_s':velocity[1] if velocity else None})
    scenarios=[measure(profile,f,step) for f in [.4,.5,.6]];nominal=scenarios[1]
    values=[s['span_km'] for s in scenarios if s['span_km'] is not None]
    return {'profile':profile,'nominal':nominal,'threshold_scenarios':scenarios,
        'approximate_section_span_km':int(math.floor(nominal['span_km']/10+.5)*10) if nominal['span_km'] is not None else None,
        'threshold_sensitivity_span_km':[math.floor(min(values)/10)*10,math.ceil(max(values)/10)*10] if len(values)==3 else None,
        'failed_threshold_count':3-len(values),'native_grid_step_degrees':step}

def output(method):return ROOT/f'research/loop-current-{method}-section-spans.json'

def build(method):
    if method not in ['noaa','adt']:raise ValueError('Unknown source method')
    selections=[(r['date'],r[method]) for r in source_rows()]
    if method=='noaa':
        from build_loop_current_dated_streamline import SOURCE,SOURCE_SUBSET_SHA256
        src={'file':SOURCE.relative_to(ROOT).as_posix(),'sha256':SOURCE_SUBSET_SHA256}
    else:
        from build_loop_current_adt_contours import SOURCE,SOURCE_SHA256
        src={'file':SOURCE.relative_to(ROOT).as_posix(),'sha256':SOURCE_SHA256}
    selections.append(('2026-09-25',src));frames=[]
    for day,receipt in selections:
        path=ROOT/receipt['file']
        if digest(path)!=receipt['sha256']:raise ValueError('Changed section source receipt')
        source=json.loads(path.read_bytes())
        if (source.get('observation_date') or source['source_time_start'][:10])!=day:raise ValueError('Mismatched source day')
        frames.append({'date':day,'product_key':method,'source_subset':receipt['file'],'source_subset_sha256':digest(path),
            'source_response_sha256':source['source_response_sha256'],'source_url':source['source_url'],
            'source_algorithm':source.get('source_algorithm',source.get('source_metadata',{}).get('subset_datasetId')),
            **compute(source,method)})
    spans=[]
    for year in sorted({r['date'][:4] for r in frames}):
        values=[r['approximate_section_span_km'] for r in frames if r['date'].startswith(year) and r['approximate_section_span_km'] is not None]
        spans.append({'year':int(year),'sample_count':len(values),'source_algorithms':sorted({r['source_algorithm'] for r in frames if r['date'].startswith(year)}),'sampled_value_span_km':[min(values),max(values)] if values else None,'range_kind':'sparse_sampled_nominal_value_span_not_annual_extrema'})
    return {'schema':'osw.loop-section-spans.v1','current_id':'loop','product_key':method,
        'status':'local_component_section_diagnostic_requires_scientific_review',
        'metric':'zonal_half_peak_northward_velocity_section_span','section_latitude':LATITUDE,'section_longitude':None,
        'longitude_window':list(WINDOW),'layer':'altimetry-derived absolute surface geostrophic velocity',
        'scope_note':'Fixed Yucatan-gate component span. Not flow-normal width, a streamline width, passage width, whole-current envelope or footprint. Products may share observations.',
        'whole_current_representative':False,'width_rank_eligible':False,'annual_extrema_eligible':False,
        'whole_current_width_km':None,'annual_width_range_km':None,'is_confidence_interval':False,
        'protocol_file':PROTOCOL.relative_to(ROOT).as_posix(),'protocol_sha256':digest(PROTOCOL),
        'general_protocol_sha256':digest(ROOT/'plans/ocean-current-width-measurement-protocol-v1.md'),
        'generator_sha256':digest(Path(__file__)),'velocity_sampler_sha256':digest(ROOT/'analysis/build_gulf_stream_geostrophic_path.py'),
        'sample_value_spans':spans,'frames':frames}

if __name__=='__main__':
    for method in ['noaa','adt']:
        document=build(method);output(method).write_text(json.dumps(document,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(method,[(r['date'],r['approximate_section_span_km'],r['failed_threshold_count']) for r in document['frames']])
