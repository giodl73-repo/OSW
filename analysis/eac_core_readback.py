"""Final precision for enumerated derived EAC fields; source values stay exact."""
import copy
import hashlib
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL='plans/eac-section-core-calculation-readback-v2.md'
PROTOCOL_SHA='73b0b1701969fdc414df6d57f640c713d115496fa131b39f15bf5e12739706b7'


def dependency_pins():
    actual=hashlib.sha256((ROOT/PROTOCOL).read_bytes()).hexdigest()
    if actual!=PROTOCOL_SHA:raise ValueError('Changed EAC section-core readback protocol')
    return {PROTOCOL:actual,'analysis/eac_core_readback.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


def rounded(value,digits):
    if value is None:return None
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
        raise ValueError('Invalid EAC derived readback value')
    result=round(value,digits)
    return 0.0 if result==0 else result


def fields(record,scalars=(),arrays=()):
    for key,digits in scalars:
        if key in record:record[key]=rounded(record[key],digits)
    for key,digits in arrays:
        if record.get(key) is not None:record[key]=[rounded(value,digits) for value in record[key]]


def summaries(rows):
    for row in rows:fields(row,[(key,6) for key in ['conditional_min_km','conditional_median_km','conditional_max_km']])


def canonicalize(document):
    if document.get('schema')!='osw.eac-section-core-spans.v1':raise ValueError('Wrong EAC readback schema')
    pins=dependency_pins();result=copy.deepcopy(document)
    fields(result['geometry'],arrays=[('distance_m',3),('forward_bearing_deg',6)])
    for profile in result['profiles']:
        fields(profile,arrays=[('section_normal_velocity_m_s',8),('projected_supplied_magnitudes_m_s',8)])
        for scenario in profile['scenarios'].values():
            fields(scenario,[('peak_component_m_s',8)])
            peak=scenario.get('peak_source_components')
            if peak is not None:
                fields(peak,[('section_normal_central_m_s',8),('section_tangent_m_s',8),
                    ('bearing_deg',6),('tangent_to_normal_ratio_not_width_correction',8)])
            for case in scenario['cases']:
                fields(case,[('threshold_m_s',8),('section_span_km',6)],arrays=[('sampling_support_interval_km',6)])
                for key in ['shoreward_edge','offshore_edge']:
                    side=case.get(key)
                    if side is not None:
                        fields(side,[('distance_m',3),('fraction_inside_to_outside',7)],
                            arrays=[('distance_bracket_m',3),('component_bracket_m_s',8)])
    summaries(result['overall_outcomes'])
    for month in result['monthly_summaries']:summaries(month['outcomes'])
    result['input_sha256'].update(pins);result['calculation_readback_protocol']=PROTOCOL
    return result
