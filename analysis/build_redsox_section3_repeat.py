"""Matched source sections; frozen winter observations are never rewritten."""
import hashlib
import json
import math
import zipfile
import numpy as np
import gsw
import build_redsox_section3_spans as winter

ROOT = winter.ROOT
GEOD = winter.GEOD
REPORT = 'research/redsox-section3-repeat-surveys.json'
PROTOCOL = 'plans/redsox-section3-repeat-survey-protocol-v1.md'
RECEIPT = 'research/redsox-section3-repeat-source-selection.json'
STATIONS = list(range(18,30))
BRANCHES = {'southern': (list(range(19,25)), list(range(18,26))),
            'northern': (list(range(25,30)), list(range(24,30)))}
digest = winter.digest
encoded = winter.encoded


# The v1 case operator is retained locally to preserve the frozen winter
# generator/report graph. Tests compare it to v1 after explicit station renaming.
def measure(profiles, branch, fraction, offset):
    peak_stations, support = BRANCHES[branch]
    by = {p['station']: p for p in profiles}
    out = {'branch': branch, 'fraction': fraction, 'uniform_component_offset_m_s': offset,
           'span_km': None, 'left_edge': None, 'right_edge': None,
           'peak_search_stations': peak_stations, 'support_stations': support,
           'unavailable_peak_stations': [s for s in peak_stations if not by[s]['usable']]}
    if out['unavailable_peak_stations']:
        return {**out, 'status': 'incomplete_branch_peak_search'}
    peak = max(peak_stations, key=lambda s: by[s]['normal_component_m_s'] + offset)
    p = by[peak]
    value = p['normal_component_m_s'] + offset
    out.update(peak_station=peak, peak_component_m_s=value, threshold_m_s=value*fraction,
               peak_salinity_psu=(p.get('hydrography') or {}).get('layer_mean_salinity_psu'))
    if value < .2:
        return {**out, 'status': 'peak_below_component_floor'}
    out['saline_outflow_screen'] = (None if out['peak_salinity_psu'] is None else
        out['peak_salinity_psu'] >= 38 and p['layer']['speed_of_mean_vector_m_s'] >= .2)
    theta = p['section_normal_azimuth_degrees']
    azimuth = math.degrees(math.atan2(p['layer']['u_m_s'], p['layer']['v_m_s'])) % 360
    out['peak_vector_obliquity_degrees'] = abs((azimuth-theta+180) % 360-180)
    blocked = []
    for direction, key in [(-1, 'left_edge'), (1, 'right_edge')]:
        index = support.index(peak)
        while 0 <= index+direction < len(support):
            inner, outer = by[support[index]], by[support[index+direction]]
            if not outer['usable']:
                blocked.append(outer['station'])
                break
            qi = inner['normal_component_m_s'] + offset
            qo = outer['normal_component_m_s'] + offset
            if qo <= value*fraction:
                weight = (value*fraction-qi)/(qo-qi)
                distance = abs(outer['chainage_km']-inner['chainage_km'])
                bearing, _, length = GEOD.inv(*inner['position_lon_lat'], *outer['position_lon_lat'])
                lon, lat, _ = GEOD.fwd(*inner['position_lon_lat'], bearing, weight*length)
                out[key] = {'inner_station': inner['station'], 'outer_station': outer['station'],
                    'fraction_from_inner': weight, 'bracket_spacing_km': distance,
                    'chainage_km': inner['chainage_km']+weight*(outer['chainage_km']-inner['chainage_km']),
                    'position_lon_lat': [lon, lat]}
                break
            index += direction
    out['blocking_stations'] = blocked
    if out['left_edge'] is None or out['right_edge'] is None:
        return {**out, 'status': 'open_or_blocked_section_boundary'}
    span = out['right_edge']['chainage_km']-out['left_edge']['chainage_km']
    spacing = [by[b]['chainage_km']-by[a]['chainage_km'] for a, b in zip(support, support[1:])]
    ratio = span / float(np.median(spacing))
    out.update(span_km=span, native_station_spacings_km=spacing,
        span_in_median_native_spacings=ratio, fewer_than_four_native_spacings=ratio < 4,
        span_in_maximum_edge_bracket_spacings=span/max(out[k]['bracket_spacing_km'] for k in ['left_edge','right_edge']))
    status = 'paired_local_component_span' if out['saline_outflow_screen'] else 'paired_span_with_unverified_saline_association'
    return {**out, 'status': status}


def comparisons(winter_layers, summer_layers, station_context):
    results=[]
    for a,b in zip(winter_layers,summer_layers):
        if a['height_layer_m'] != b['height_layer_m']:
            raise ValueError('Different comparison layers')
        for branch in BRANCHES:
            old=next(c for c in a['cases'] if c['branch']==branch and c['fraction']==.5 and c['uniform_component_offset_m_s']==0)
            new=next(c for c in b['cases'] if c['branch']==branch and c['fraction']==.5 and c['uniform_component_offset_m_s']==0)
            reasons=[]
            if not station_context:reasons.append('station_correspondence_exceeds_declared_limit')
            for name,case in [('winter',old),('summer',new)]:
                if case['span_km'] is None:reasons.append(name+'_span_unresolved')
                if case.get('saline_outflow_screen') is not True:reasons.append(name+'_saline_screen_not_passed')
            results.append({'branch':branch,'height_layer_m':a['height_layer_m'],
                'winter_status':old['status'],'summer_status':new['status'],
                'winter_span_km':old['span_km'],'summer_span_km':new['span_km'],
                'winter_saline_screen':old.get('saline_outflow_screen'),
                'summer_saline_screen':new.get('saline_outflow_screen'),
                'comparison_supported':not reasons,'unresolved_reasons':reasons,
                'summer_minus_winter_dated_component_span_km':None if reasons else new['span_km']-old['span_km']})
    return results


def build():
    selection=json.loads((ROOT/RECEIPT).read_bytes())
    if selection['summer_source_order_stations']!=STATIONS or selection['protocol_sha256']!=digest(PROTOCOL):
        raise ValueError('Changed repeat-survey selection or protocol')
    old=winter.build()
    if winter.encoded(old)!=(ROOT/winter.REPORT).read_bytes() or digest(winter.REPORT)!=selection['winter_report_sha256']:
        raise ValueError('Changed frozen winter reference')
    ladcp,ctd=winter.verified_ladcp(),winter.verified_ctd()
    lb={(p['campaign'],p['station']):p for p in ladcp['profiles']}
    cb={(p['campaign'],p['filename_station']):p for p in ctd['profiles']}
    joins={p['ladcp_id']:p for p in ctd['filename_joins']}
    positions=[lb['RSX2',s]['position_lon_lat'] for s in STATIONS]
    chain,bearings=winter.geometry(positions)
    pairs=[]
    for ws,ss in zip(winter.STATIONS,STATIONS):
        wp=lb['RSX1',ws]['position_lon_lat'];sp=lb['RSX2',ss]['position_lon_lat']
        separation=GEOD.inv(*wp,*sp)[2]/1000
        pairs.append({'winter_station':ws,'summer_station':ss,'winter_position_lon_lat':wp,
            'summer_position_lon_lat':sp,'separation_km':separation,
            'within_two_km':separation<=2})
    layers=[]
    with zipfile.ZipFile(ROOT/'research/source-data/ncei-redsox-2001/ladcp-ascii-originals.zip') as lzip, \
            zipfile.ZipFile(ROOT/'research/source-data/ncei-redsox-2001/ctd-ascii-originals.zip') as czip:
        for height in [[20,60],[10,50],[40,80]]:
            profiles=[]
            for i,station in enumerate(STATIONS):
                source=lb['RSX2',station];companion=cb.get(('RSX2',station))
                raw=lzip.read(source['source_file'])
                if hashlib.sha256(raw).hexdigest()!=source['source_sha256']:raise ValueError('Changed summer profile')
                header,rows,_=winter.parse_gpl(raw)
                reasons=[]
                if header['reference']=='m':reasons.append('uninterpretable_source_reference')
                if source['source_component_quality_notes']:reasons.append('authored_component_quality_treatment_unverified')
                p={'station':station,'id':source['id'],'source_file':source['source_file'],
                    'source_sha256':source['source_sha256'],'time_utc':source['time_utc'],
                    'position_lon_lat':positions[i],'chainage_km':chain[i],
                    'section_normal_azimuth_degrees':(bearings[i]+90)%360,
                    'source_reference':header['reference'],'source_processing_tag':header['tag'],
                    'source_component_quality_notes':source['source_component_quality_notes'],
                    'source_up_flag':header.get('up'),'exclusion_reasons':reasons,
                    'filename_join_support':joins.get(source['id']),'hydrography':None}
                try:
                    p['layer']=winter.velocity_layer(rows,height)
                    p['normal_component_m_s']=winter.component(p['layer']['u_m_s'],p['layer']['v_m_s'],bearings[i])
                except ValueError as error:
                    p.update(layer=None,normal_component_m_s=None);reasons.append(str(error))
                if companion and p['layer']:
                    ch,seq,cr=winter.parse_ctd(czip.read(companion['source_file']))
                    p.update(ctd_id=companion['id'],ctd_source_sha256=companion['source_sha256'])
                    try:p['hydrography']=winter.hydrography_layer(ch,seq,cr,p['layer'])
                    except ValueError as error:p['hydrography_failure']=str(error)
                elif not companion:p['hydrography_failure']='no_distributed_same_filename_station_ctd'
                p['usable']=not reasons;profiles.append(p)
            cases=[measure(profiles,branch,fraction,offset) for branch in BRANCHES
                for fraction,offset in [(.5,0),(.4,0),(.6,0),(.5,-.04),(.5,.04)]]
            layers.append({'height_layer_m':height,'profiles':profiles,'cases':cases})
    inputs={**old['input_sha256'],winter.REPORT:digest(winter.REPORT),
        PROTOCOL:digest(PROTOCOL),RECEIPT:digest(RECEIPT),
        'analysis/build_redsox_section3_repeat.py':digest('analysis/build_redsox_section3_repeat.py')}
    result=winter.readback({'schema':'osw.redsox-section3-repeat-surveys.v1','input_sha256':inputs,
        'winter_report_file':winter.REPORT,'winter_report_sha256':digest(winter.REPORT),
        'summer_source_order_stations':STATIONS,'station_correspondence':pairs,
        'summer_layers':layers,'comparisons':comparisons(old['layers'],layers,all(p['within_two_km'] for p in pairs)),
        'gsw_version':gsw.__version__,'fully_blinded':False,'tides_removed':False,
        'new_width_record_admitted':False,'width_rank_eligible':False,
        'whole_current_width_km':None,'annual_width_range_km':None,'seasonal_climatology':False,
        'interpretation':'Two dated, non-synoptic source sections; local component spans and quality barriers. Not annual ranges, climatology, physical widths or confidence bounds.'})
    for target,raw in zip(result['station_correspondence'],pairs):
        for key in ['winter_position_lon_lat','summer_position_lon_lat']:target[key]=raw[key]
    for target,raw_layer in zip(result['summer_layers'],layers):
        for p,raw in zip(target['profiles'],raw_layer['profiles']):
            for key in ['position_lon_lat','filename_join_support','source_up_flag']:p[key]=raw[key]
            if raw['layer']:p['layer']['height_knots_m']=raw['layer']['height_knots_m']
    return result


if __name__=='__main__':
    report=build();(ROOT/REPORT).write_bytes(encoded(report))
    for layer in report['summer_layers']:
        print(json.dumps({'layer':layer['height_layer_m'],'outcomes':[{k:c.get(k) for k in ['branch','fraction','uniform_component_offset_m_s','status','span_km','peak_station','peak_salinity_psu']} for c in layer['cases']]}))
