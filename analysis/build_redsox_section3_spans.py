"""Source-declared winter transect; no canonical physical-width admission."""
from pathlib import Path
import hashlib
import json
import math
import zipfile

import numpy as np
from pyproj import Geod

from build_redsox_lower_nc_section import (
    verified_ladcp, verified_ctd, parse_gpl, parse_ctd,
    velocity_layer, hydrography_layer,
)

ROOT = Path(__file__).resolve().parents[1]
REPORT = 'research/redsox-winter-section3-component-spans.json'
PROTOCOL = 'plans/redsox-section3-width-protocol-v1.md'
RECEIPT = 'research/redsox-section3-source-selection.json'
STATIONS = [76, 75, 74, 73, 72, 71, 70, 59, 60, 61, 62, 63]
BRANCHES = {'southern': ([75, 74, 73, 72, 71, 70], STATIONS[:8]),
            'northern': ([59, 60, 61, 62, 63], STATIONS[6:])}
GEOD = Geod(ellps='WGS84')


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def geometry(positions):
    chain = [0.]
    for a, b in zip(positions, positions[1:]):
        chain.append(chain[-1] + GEOD.inv(*a, *b)[2] / 1000)
    bearings = [GEOD.inv(*positions[max(0, i-1)],
                         *positions[min(len(positions)-1, i+1)])[0] % 360
                for i in range(len(positions))]
    return chain, bearings


def component(u, v, bearing):
    theta = math.radians(bearing)
    return u * math.cos(theta) - v * math.sin(theta)


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


def readback(value, key=''):
    """Derived fields only. Source positions are restored unchanged by build."""
    if isinstance(value, dict):
        return {k: readback(v, k) for k, v in value.items()}
    if isinstance(value, list):
        return [readback(v, key) for v in value]
    if isinstance(value, float):
        digits = 8 if key in {'u_m_s','v_m_s','southward_m_s','speed_of_mean_vector_m_s',
            'normal_component_m_s','peak_component_m_s','threshold_m_s','velocity_at_knots_m_s',
            'fraction_from_inner','position_lon_lat'} else 6
        return round(value, digits) or 0.0
    return value


def build():
    selection = json.loads((ROOT/RECEIPT).read_bytes())
    if selection['source_order_stations'] != STATIONS or selection['protocol_sha256'] != digest(PROTOCOL):
        raise ValueError('Changed source selection or declared protocol')
    ladcp, ctd = verified_ladcp(), verified_ctd()
    lb = {(p['campaign'], p['station']): p for p in ladcp['profiles']}
    cb = {(p['campaign'], p['filename_station']): p for p in ctd['profiles']}
    joins = {p['ladcp_id']: p for p in ctd['filename_joins']}
    positions = [lb['RSX1', s]['position_lon_lat'] for s in STATIONS]
    chain, bearings = geometry(positions)
    layers = []
    with zipfile.ZipFile(ROOT/'research/source-data/ncei-redsox-2001/ladcp-ascii-originals.zip') as lzip, \
            zipfile.ZipFile(ROOT/'research/source-data/ncei-redsox-2001/ctd-ascii-originals.zip') as czip:
        for height in [[20,60], [10,50], [40,80]]:
            profiles = []
            for i, station in enumerate(STATIONS):
                source = lb['RSX1', station]
                raw = lzip.read(source['source_file'])
                if hashlib.sha256(raw).hexdigest() != source['source_sha256']:
                    raise ValueError('Changed source profile')
                header, rows, _ = parse_gpl(raw)
                reasons = []
                if header['reference'] == 'm':
                    reasons.append('uninterpretable_source_reference')
                if station == 63:
                    reasons.append('rejected_downcast_treatment_unverified')
                p = {'station': station, 'id': source['id'], 'source_file': source['source_file'],
                    'source_sha256': source['source_sha256'], 'time_utc': source['time_utc'],
                    'position_lon_lat': positions[i], 'chainage_km': chain[i],
                    'section_normal_azimuth_degrees': (bearings[i]+90)%360,
                    'source_reference': header['reference'], 'source_processing_tag': header['tag'],
                    'source_up_flag': header.get('up'), 'exclusion_reasons': reasons,
                    'filename_join_support': joins.get(source['id']), 'hydrography': None}
                try:
                    p['layer'] = velocity_layer(rows, height)
                    p['normal_component_m_s'] = component(p['layer']['u_m_s'], p['layer']['v_m_s'], bearings[i])
                except ValueError as error:
                    p.update(layer=None, normal_component_m_s=None)
                    reasons.append(str(error))
                companion = cb.get(('RSX1',station))
                if companion and p['layer']:
                    ch, seq, cr = parse_ctd(czip.read(companion['source_file']))
                    p.update(ctd_id=companion['id'], ctd_source_sha256=companion['source_sha256'])
                    try:
                        p['hydrography'] = hydrography_layer(ch, seq, cr, p['layer'])
                    except ValueError as error:
                        p['hydrography_failure'] = str(error)
                elif not companion:
                    p['hydrography_failure'] = 'no_distributed_same_filename_station_ctd'
                p['usable'] = not reasons
                profiles.append(p)
            cases = [measure(profiles, branch, fraction, offset) for branch in BRANCHES
                     for fraction, offset in [(.5,0),(.4,0),(.6,0),(.5,-.03),(.5,.03)]]
            layers.append({'height_layer_m': height, 'profiles': profiles, 'cases': cases})
    inputs = {PROTOCOL: digest(PROTOCOL), RECEIPT: digest(RECEIPT),
        'analysis/build_redsox_section3_spans.py': digest('analysis/build_redsox_section3_spans.py'),
        'analysis/build_redsox_lower_nc_section.py': digest('analysis/build_redsox_lower_nc_section.py'),
        'analysis/build_redsox_ladcp_source_inventory.py': digest('analysis/build_redsox_ladcp_source_inventory.py'),
        'analysis/build_redsox_ctd_companion_inventory.py': digest('analysis/build_redsox_ctd_companion_inventory.py'),
        **ladcp['input_sha256'], **ctd['input_sha256']}
    report = readback({'schema': 'osw.redsox-section3-component-spans.v1', 'input_sha256': inputs,
        'source_order_stations': STATIONS, 'layers': layers, 'new_width_record_admitted': False,
        'width_rank_eligible': False, 'whole_current_width_km': None, 'annual_width_range_km': None,
        'tides_removed': False, 'fully_blinded': False,
        'interpretation': 'Dated, non-synoptic bent-section normal-component spans; not flow-normal physical widths, annual ranges or confidence intervals.'})
    # Restore source coordinates/metadata and native height knots. Interpolated
    # velocities, depths and salinities are derived, with explicit readback above.
    for layer, raw_layer in zip(report['layers'], layers):
        for p, raw_p in zip(layer['profiles'], raw_layer['profiles']):
            p['position_lon_lat'] = raw_p['position_lon_lat']
            p['filename_join_support'] = raw_p['filename_join_support']
            p['source_up_flag'] = raw_p['source_up_flag']
            if raw_p['layer']:
                p['layer']['height_knots_m'] = raw_p['layer']['height_knots_m']
    return report


def encoded(document):
    return (json.dumps(document, indent=2, allow_nan=False)+'\n').encode('utf8')


if __name__ == '__main__':
    result = build()
    (ROOT/REPORT).write_bytes(encoded(result))
    for layer in result['layers']:
        print(json.dumps({'layer': layer['height_layer_m'], 'outcomes': [
            {k: c.get(k) for k in ['branch','fraction','uniform_component_offset_m_s','status','span_km','peak_station','peak_salinity_psu']}
            for c in layer['cases']]}))
