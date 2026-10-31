"""Evaluate fixed-window component spans without promoting them to current widths."""
from scientific_readback import canonicalize
from pathlib import Path
from datetime import datetime
import hashlib,json,math
from pyproj import Geod
from build_aleutian_p14n_vector_section import verify as verify_vectors
from build_p14n_hydrography_companion import verify as verify_hydrography

ROOT=Path(__file__).resolve().parents[1]
OUTPUT='research/aleutian-p14n-1993-component-spans.json'
PROTOCOL='plans/aleutian-p14n-component-span-protocol-v1.md'
FROZEN_INPUTS={'research/aleutian-p14n-1993-observed-vector-section.json': '76808f0d0f0959669f11ae6d1ac52cb3c58d281f965f498249fd5087c4b14d9f', 'research/aleutian-p14n-1993-hydrography-correspondence.json': '273392fe786c38eefb94528ea944d722d5a89480f4fe555822273f6675cfeb1f', 'plans/aleutian-p14n-component-span-protocol-v1.md': '2ae348b0cb5f600478b7d571cfc27bc5e643fbf1773c86c0eeea8334f2f3e3e5', 'plans/ocean-current-width-measurement-protocol-v1.md': '1d4d577d8f3b422cf3252b973280cb7073bad7e3234bc40a2808bc16bda974bb', 'plans/basin-surface-section-width-protocol-v1.md': 'deab556d97430d06bffff25b7a6e1469855785a5b3c4cf654aa2226e66b7e9b3'}
GEOD=Geod(ellps='WGS84')

def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def encoded(data):return (json.dumps(data,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def distance(a,b):return GEOD.inv(a['longitude_degrees_east'],a['latitude_degrees_north'],b['longitude_degrees_east'],b['latitude_degrees_north'])[2]/1000
def minutes(a,b):return (datetime.fromisoformat(b['observed_at'])-datetime.fromisoformat(a['observed_at'])).total_seconds()/60
def position(row):return {k:row[k] for k in ['latitude_degrees_north','longitude_degrees_east']}
def sample(row):return {k:row[k] for k in ['source_time_index','observed_at','latitude_degrees_north','longitude_degrees_east','layer_mean']}
def round10(value):return 10*math.floor(value/10+0.5)

def crossing(rows,peak_index,step,low,high,threshold):
    inside=peak_index
    while True:
        outside=inside+step
        if outside<0 or outside>=len(rows):return {'status':'source_edge','crossing':None}
        a,b=rows[inside],rows[outside]
        if not low<=b['latitude_degrees_north']<=high:return {'status':'window_edge','crossing':None}
        if abs(minutes(a,b))>90:return {'status':'time_gap','crossing':None,'stopped_before_source_time_index':b['source_time_index']}
        u=b['layer_mean']['eastward_m_s']
        if u is None:return {'status':'missing_mean','crossing':None,'stopped_before_source_time_index':b['source_time_index']}
        if u<=threshold:
            fraction=(a['layer_mean']['eastward_m_s']-threshold)/(a['layer_mean']['eastward_m_s']-u)
            point={k:a[k]+fraction*(b[k]-a[k]) for k in position(a)}
            return {'status':'resolved','crossing':point,'inside':sample(a),'outside':sample(b),'fraction_from_inside_to_outside':fraction,'native_bracket_spacing_km':distance(a,b),'inside_row_index':inside,'outside_row_index':outside}
        inside=outside

def scenario(rows,peak_index,window,fraction,offset=0):
    peak=rows[peak_index]['layer_mean']['eastward_m_s']
    threshold=peak*fraction+offset
    result={'fraction_of_selected_peak':fraction,'threshold_displacement_m_s':offset,'comparison_threshold_m_s':threshold,'endpoint_separation_km':None,'display_endpoint_separation_km':None}
    if not 0<threshold<peak:return dict(result,status='ineligible_threshold',before_peak=None,after_peak=None)
    before=crossing(rows,peak_index,-1,*window,threshold)
    after=crossing(rows,peak_index,1,*window,threshold)
    result.update(before_peak=before,after_peak=after)
    if before['status']!='resolved' or after['status']!='resolved':return dict(result,status='unresolved')
    first,last=before['inside_row_index'],after['inside_row_index']
    retained=rows[first:last+1]
    positions=[before['crossing'],*map(position,retained),after['crossing']]
    track_length=sum(distance(a,b) for a,b in zip(positions,positions[1:]))
    separation=distance(before['crossing'],after['crossing'])
    native=rows[before['outside_row_index']:after['outside_row_index']+1]
    spacings=[distance(a,b) for a,b in zip(native,native[1:])]
    legs=[]
    for a,b in zip(native,native[1:]):
        bearing,_,metres=GEOD.inv(a['longitude_degrees_east'],a['latitude_degrees_north'],b['longitude_degrees_east'],b['latitude_degrees_north'])
        legs.append({'from_source_time_index':a['source_time_index'],'to_source_time_index':b['source_time_index'],'time_gap_minutes':minutes(a,b),'spacing_km':metres/1000,'bearing_degrees_true':bearing%360 if metres else None})
    max_spacing=max(spacings)
    combinations=[distance(a,b) for a in [before['inside'],before['outside']] for b in [after['inside'],after['outside']]]
    result.update(status='resolved',endpoint_separation_km=separation,display_endpoint_separation_km=round10(separation),
                  lobe_source_time_indices=[r['source_time_index'] for r in retained],native_legs=legs,
                  bracketing_observation_elapsed_hours=minutes(native[0],native[-1])/60,
                  track_length_between_crossings_km=track_length,track_length_to_endpoint_distance_ratio=track_length/separation if separation else None,
                  northward_steps_including_brackets=sum(b['latitude_degrees_north']>a['latitude_degrees_north'] for a,b in zip(native,native[1:])),
                  largest_native_spacing_km=max_spacing,endpoint_distance_in_largest_native_spacings=separation/max_spacing if max_spacing else None,
                  fewer_than_four_native_spacings=separation<4*max_spacing,
                  bracket_endpoint_combination_distances_km=combinations,
                  bracket_endpoint_combination_spread_km=[min(combinations),max(combinations)],
                  bracket_spread_is_error_or_confidence_bounds=False)
    return result

def branch(rows,name,window):
    eligible=[i for i,r in enumerate(rows) if window[0]<=r['latitude_degrees_north']<=window[1] and r['layer_mean']['eastward_m_s'] is not None]
    result={'branch':name,'latitude_search_window_degrees_north':window,'selected_peak':None,'boundary_choice_scenarios':[],'velocity_sensitivity_scenarios':[],'complete_boundary_choice_envelope_km':None}
    if not eligible:return dict(result,status='no_valid_means')
    index=max(eligible,key=lambda i:(rows[i]['layer_mean']['eastward_m_s'],-rows[i]['source_time_index']))
    peak=rows[index];result['selected_peak']=sample(peak)
    result['peak_at_window_sample_edge']=index in [min(eligible),max(eligible)]
    if peak['layer_mean']['eastward_m_s']<0.02:return dict(result,status='below_peak_floor')
    choices=[scenario(rows,index,window,f) for f in [.4,.5,.6]]
    sensitivity=[scenario(rows,index,window,.5,offset) for offset in [-.06,-.02,.02,.06]]
    result.update(status='evaluated',boundary_choice_scenarios=choices,velocity_sensitivity_scenarios=sensitivity)
    if all(s['status']=='resolved' for s in choices):
        values=[s['endpoint_separation_km'] for s in choices]
        result['complete_boundary_choice_envelope_km']=[10*math.floor(min(values)/10),10*math.ceil(max(values)/10)]
    return result

def build():
    if len(FROZEN_INPUTS)!=5:raise ValueError('Missing component-span source/protocol pins')
    for path,pin in FROZEN_INPUTS.items():
        if digest(path)!=pin:raise ValueError('Changed component-span input: '+path)
    vectors=verify_vectors();hydro=verify_hydrography()
    if hydro['velocity_section']!=vectors:raise ValueError('Changed original observed section')
    rows=vectors['profiles']
    return canonicalize({'schema':'osw.observed-component-spans.v1','current_id':'aleutian','status':'exploratory_component_spans_pending_review',
            'label':'P14N Subarctic branch component spans: July 1993',
            'metric':'hourly-track eastward-component relative-peak endpoint separation',
            'input_sha256':dict(FROZEN_INPUTS),'generator_file':Path(__file__).relative_to(ROOT).as_posix(),'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'protocol_file':PROTOCOL,'layer_bounds_m':[100,300],'retained_samples':[sample(r) for r in rows],
            'hydrography_context':hydro,
            'branches':[branch(rows,'northern',[44,46]),branch(rows,'southern',[41,43])],
            'current_association_verified':False,'new_width_record_admitted':False,'whole_current_width_km':None,'annual_width_range_km':None,
            'width_rank_eligible':False,'physical_edge_geometry_admitted':False,'seasonal_playback_supported':False,
            'sensitivity_is_confidence_interval':False,'observed_track_reordered_by_latitude':False,
            'interpretation':['Source paper places branches near 45 N and 42 N and an eddy near 41.5 N. Its same-cruise interpretation does not validate these OSW component boundaries.',
            'Acquisition order includes CTD occupations and northward steps. These means are not exclusively underway cross-track velocities.',
            'Threshold-choice and velocity-perturbation scenarios are separate finite sensitivities, not annual ranges or total measurement uncertainty.',
            'CTD companion retains quality codes, nominal-bottom pairing ambiguity and unresolved historical temperature-correction notice. No new water-mass classification is made.']})

def verify():
    expected=build()
    if (ROOT/OUTPUT).read_bytes()!=encoded(expected):raise ValueError('Stale component-span report')
    return expected

if __name__=='__main__':
    report=build();(ROOT/OUTPUT).write_bytes(encoded(report))
    print(json.dumps([{'branch':r['branch'],'peak':r['selected_peak'],'envelope_km':r['complete_boundary_choice_envelope_km'],'scenarios':[{'fraction':s['fraction_of_selected_peak'],'offset':s['threshold_displacement_m_s'],'status':s['status'],'km':s['endpoint_separation_km'],'before':s.get('before_peak',{}).get('status'),'after':s.get('after_peak',{}).get('status')} for s in r['boundary_choice_scenarios']+r['velocity_sensitivity_scenarios']]} for r in report['branches']]))
