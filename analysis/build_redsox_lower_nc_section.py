"""Execute the prospectively declared matched-section feasibility, no admission."""
from pathlib import Path
from datetime import datetime
import json,hashlib,zipfile,math
import numpy as np
import gsw
from pyproj import Geod
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/source-data/redsox-lower-nc-2001'
RESULT=ROOT/'research/redsox-lower-nc-dated-section-diagnostic.json'
from build_redsox_ladcp_source_inventory import parse_gpl,build as verified_ladcp
from build_redsox_ctd_companion_inventory import parse_ctd,build as verified_ctd
GEOD=Geod(ellps='WGS84')
PREFLIGHT_SHA='c9aa43ff540a180e606b984400aaa29d20f525e91dfee12b17791ece53c98660'
EXTRA_PINS={'matched-section-followup-preflight.json':'cfced47f8fc78bb1fc37b1e6033f499e687afab5239388f104d330a6e0dd410a',
    'implementation-clarifications.json':'2fbf9636562ee5e22e420e1355220bded6368ab05aee82fe92f9949cc8e8a81b',
    'declaration-history-note.json':'23f5f47e82136efe661cb35422b7d2bc7447648048965d1f44a75bb6c6fb9123'}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def interpolate_complete(x,y,targets,max_gap=None):
    x=np.asarray(x,dtype=float);y=np.asarray(y,dtype=float);targets=np.asarray(targets,dtype=float)
    if x.ndim!=1 or y.shape[0]!=len(x) or len(x)<2 or not np.isfinite(x).all():raise ValueError('Invalid source axis')
    if not np.all(np.diff(x)>0):raise ValueError('Nonmonotonic source axis')
    if targets.min()<x[0] or targets.max()>x[-1]:raise ValueError('Layer endpoint outside observed support')
    left=max(0,int(np.searchsorted(x,targets.min(),side='right'))-1)
    right=min(len(x)-1,int(np.searchsorted(x,targets.max(),side='left')))
    selection=slice(left,right+1)
    if not np.isfinite(y[selection]).all():raise ValueError('Missing sample inside interpolation support')
    if max_gap is not None and np.any(np.diff(x[selection])>max_gap):raise ValueError('Source gap exceeds predeclared maximum')
    if y.ndim==1:return np.interp(targets,x,y)
    return np.column_stack([np.interp(targets,x,y[:,i]) for i in range(y.shape[1])])


def velocity_layer(rows,layer):
    data=np.array([[np.nan if v is None else v for v in row] for row in rows],dtype=float)
    height=data[:,0]
    if not np.isfinite(height).all():raise ValueError('Unknown vertical position')
    if np.all(np.diff(height)<0):data=data[::-1];height=data[:,0]
    elif not np.all(np.diff(height)>0):raise ValueError('Nonmonotonic vertical profile')
    low,high=layer;inside=(height>=low)&(height<=high)
    if int(inside.sum())<3:raise ValueError('Fewer than3 original paired layer samples')
    knots=np.unique(np.r_[low,height[inside],high])
    values=interpolate_complete(height,data[:,1:],knots,max_gap=20)
    means=np.trapezoid(values,knots,axis=0)/(high-low)
    return {'u_m_s':float(means[1]),'v_m_s':float(means[2]),'southward_m_s':float(-means[2]),
        'speed_of_mean_vector_m_s':float(np.hypot(means[1],means[2])),
        'original_samples_in_layer':int(inside.sum()),'height_knots_m':knots.tolist(),
        'source_depth_at_knots_m':values[:,0].tolist(),
        'velocity_at_knots_m_s':values[:,1:].tolist()}


def hydrography_layer(h,sequence,rows,velocity):
    data=np.array([[np.nan if v is None else v for v in row] for row in rows],dtype=float)
    if 'z' in sequence:
        depth=data[:,sequence.index('z')];operator='source_explicit_depth_m_with_documented_unit_header_typo'
    else:
        depth=-gsw.z_from_p(data[:,sequence.index('p')],float(h['lat']))
        operator='minus_gsw.z_from_p_native_pressure_dbar_source_latitude_default_zero_dynamic_height_and_surface_geopotential'
    targets=np.asarray(velocity['source_depth_at_knots_m']);salinity=data[:,sequence.index('S')]
    values=interpolate_complete(depth,salinity,targets)
    knots=np.array(velocity['height_knots_m'])
    average=float(np.trapezoid(values,knots)/(knots[-1]-knots[0]))
    return {'layer_mean_salinity_psu':average,'salinity_at_velocity_knots_psu':values.tolist(),
        'depth_operator':operator,'pressure_equals_depth':False}


def section_span(profiles,fraction,offset=0,conditional=False,local_supported=False):
    ordered=sorted(profiles,key=lambda p:p['position_lon_lat'][0])
    values=[(p.get('layer') or {}).get('southward_m_s') if (conditional or p['primary_available']) else None for p in ordered]
    values=[value+offset if value is not None else None for value in values]
    base={'fraction':fraction,'velocity_offset_m_s':offset,'conditional_unverified_profiles_included':conditional,
        'span_km':None,'left_edge':None,'right_edge':None}
    unavailable=[ordered[i]['id'] for i,v in enumerate(values) if v is None]
    base.update(unavailable_profile_ids=unavailable,global_peak_search_complete=not unavailable,
        supported_local_core_followup=local_supported)
    if unavailable and not local_supported:return {**base,'status':'incomplete_peak_search_or_missing_profile'}
    eligible=[i for i,v in enumerate(values) if v is not None]
    if not eligible:return {**base,'status':'no_supported_peak'}
    peak=max(eligible,key=lambda i:values[i])
    if values[peak]<.2:return {**base,'status':'peak_below_predeclared_component_floor','peak_m_s':values[peak]}
    target=values[peak]*fraction;edges=[]
    for direction in [-1,1]:
        current=peak;edge=None
        while 0<=current+direction<len(values):
            neighbor=current+direction
            if values[neighbor] is None:break
            if values[neighbor]<=target:
                factor=(target-values[current])/(values[neighbor]-values[current])
                a=np.array(ordered[current]['position_lon_lat']);b=np.array(ordered[neighbor]['position_lon_lat'])
                point=a+factor*(b-a)
                edge={'position_lon_lat':point.tolist(),'interpolation_fraction_from_inner_sample':factor,
                    'inner_profile_id':ordered[current]['id'],'outer_profile_id':ordered[neighbor]['id'],
                    'source_position_bracket_lon_lat':[a.tolist(),b.tolist()]}
                break
            current=neighbor
        edges.append(edge)
    peak_profile=ordered[peak];layer=peak_profile['layer'];s=(peak_profile.get('hydrography') or {}).get('layer_mean_salinity_psu')
    base.update(peak_profile_id=peak_profile['id'],peak_m_s=values[peak],threshold_m_s=target,
        peak_salinity_psu=s,peak_saline_speed_screen=(s is not None and s>=38 and layer['speed_of_mean_vector_m_s']>=.2),
        left_edge=edges[0],right_edge=edges[1])
    if any(e is None for e in edges):return {**base,'status':'open_section_boundary'}
    a,b=[e['position_lon_lat'] for e in edges]
    span=GEOD.inv(*a,*b)[2]/1000
    spacings=[GEOD.inv(*a['position_lon_lat'],*b['position_lon_lat'])[2]/1000 for a,b in zip(ordered,ordered[1:])]
    azimuth=math.degrees(math.atan2(layer['u_m_s'],layer['v_m_s']))%360
    section_azimuth=GEOD.inv(*ordered[0]['position_lon_lat'],*ordered[-1]['position_lon_lat'])[0]%360
    normal=(section_azimuth+90)%360
    obliquity=abs((azimuth-normal+180)%360-180)
    return {**base,'status':'paired_fixed_component_section_span_requires_review','span_km':span,
        'native_station_spacings_km':spacings,'span_in_median_native_spacings':span/float(np.median(spacings)),
        'fewer_than4_spacings':span/float(np.median(spacings))<4,
        'peak_vector_azimuth_degrees':azimuth,'section_normal_azimuth_degrees':normal,
        'peak_vector_section_normal_obliquity_degrees':obliquity,'is_flow_normal_current_width':False}


def build():
    if sha(OUT/'lower-northern-channel-section-preflight.json')!=PREFLIGHT_SHA:raise ValueError('Changed prospective preflight')
    for name,pin in EXTRA_PINS.items():
        if sha(OUT/name)!=pin:raise ValueError('Changed declared follow-up or implementation clarification')
    pre=json.loads((OUT/'lower-northern-channel-section-preflight.json').read_bytes())
    follow=json.loads((OUT/'matched-section-followup-preflight.json').read_bytes())
    assert follow['base_winter_preflight_sha256']==PREFLIGHT_SHA
    lv=verified_ladcp();cv=verified_ctd()
    lby={(r['campaign'],r['station']):r for r in lv['profiles']}
    cby={(r['campaign'],r['filename_station']):r for r in cv['profiles']}
    joins={r['ladcp_id']:r for r in cv['filename_joins']}
    layers=[pre['primary_height_above_bottom_layer_m'],*pre['predeclared_layer_sensitivities_m']]
    cases=[]
    with zipfile.ZipFile(ROOT/'research/source-data/ncei-redsox-2001/ladcp-ascii-originals.zip') as lzip,zipfile.ZipFile(ROOT/'research/source-data/ncei-redsox-2001/ctd-ascii-originals.zip') as czip:
        for campaign,stations,delta in [('RSX1',pre['primary_filename_stations'],.03),('RSX2',follow['summer_filename_stations'],.04)]:
            for layer in layers:
                profiles=[]
                for station in stations:
                    l=lby[(campaign,station)];c=cby[(campaign,station)]
                    h,rows,issues=parse_gpl(lzip.read(l['source_file']))
                    ch,sequence,crows=parse_ctd(czip.read(c['source_file']))
                    reasons=[]
                    if h['reference']=='m':reasons.append('uninterpretable_source_reference')
                    if campaign=='RSX1' and station==10:reasons.append('cast10_upcast_only_treatment_unverified')
                    r={'id':l['id'],'ctd_id':c['id'],'position_lon_lat':l['position_lon_lat'],
                        'time_utc':l['time_utc'],'reference':h['reference'],'processing_tag':h['tag'],
                        'source_up_flag':h.get('up'),'source_component_quality_notes':l['source_component_quality_notes'],
                        'filename_join_support':joins[l['id']],
                        'primary_available':not reasons,'primary_exclusion_reasons':reasons,
                        'source_profile_sha256':l['source_sha256'],'ctd_profile_sha256':c['source_sha256']}
                    heights=[row[0] for row in rows if row[0] is not None]
                    r['source_height_range_m']=[min(heights),max(heights)]
                    r['source_height_axis_monotonic']=all(a>b for a,b in zip(heights,heights[1:])) or all(a<b for a,b in zip(heights,heights[1:]))
                    try:r['layer']=velocity_layer(rows,layer)
                    except ValueError as e:r.update(layer=None,primary_available=False);r['primary_exclusion_reasons'].append(str(e))
                    if r['layer']:
                        try:r['hydrography']=hydrography_layer(ch,sequence,crows,r['layer'])
                        except ValueError as e:r.update(hydrography=None,hydrography_failure=str(e))
                    profiles.append(r)
                cases.append({'campaign':campaign,'height_layer_m':layer,'profiles':profiles,
                    'primary':section_span(profiles,.5),
                    'supported_local_core_diagnostics':[section_span(profiles,f,offset,local_supported=True)
                        for f in [.5,.4,.6] for offset in [0,-delta,delta]],
                    'conditional_diagnostics':[section_span(profiles,f,offset,conditional=True)
                        for f in [.5,.4,.6] for offset in [0,-delta,delta]]})
    result={'schema':'osw.redsox-matched-lower-NC-feasibility.v1','preflight_sha256':PREFLIGHT_SHA,
        'followup_preflight_sha256':sha(OUT/'matched-section-followup-preflight.json'),
        'implementation_clarifications_sha256':sha(OUT/'implementation-clarifications.json'),
        'declaration_history_qualification_file':'research/source-data/redsox-lower-nc-2001/declaration-history-note.json',
        'declaration_history_qualification_sha256':sha(OUT/'declaration-history-note.json'),
        'calculation_rules_declared_before_layer_and_span_computation':True,
        'fully_blinded_before_any_selected_velocity_exposure':False,
        'source_ladcp_inputs':lv['input_sha256'],'source_ctd_inputs':cv['input_sha256'],
        'generator_sha256':sha(Path(__file__)),
        'source_parser_sha256':{name:sha(ROOT/'analysis'/name) for name in ['build_redsox_ladcp_source_inventory.py','build_redsox_ctd_companion_inventory.py']},
        'interpretation':'Strict primary results preserve the initial all-profile-complete calculation. Supported-local-core results separately apply the existing OSW missing-before-crossing rule, with incomplete-global-search flags. Conditional values include unresolved source profiles and never replace either result.',
        'gsw_version':gsw.__version__,'cases':cases,'current_association_verified':False,'width_rank_eligible':False,'annual_extrema_eligible':False,'new_width_record_admitted':False,
        'whole_current_width_km':None,'annual_width_range_km':None}
    return result


def main():
    result=build();RESULT.write_bytes((json.dumps(result,indent=2,allow_nan=False)+'\n').encode())
    for case in result['cases']:
        print(json.dumps({'campaign':case['campaign'],'height_layer_m':case['height_layer_m'],
            'strict_primary':case['primary']['status'],
            'supported_local_span_km':case['supported_local_core_diagnostics'][0]['span_km'],
            'conditional_span_km':case['conditional_diagnostics'][0]['span_km']}))


if __name__=='__main__':main()
