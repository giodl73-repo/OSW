"""Explicit derived-field precision; original source values are never rounded."""
from fnmatch import fnmatchcase
import hashlib
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL='plans/scientific-calculation-readback-protocol-v1.md'
PROTOCOL_SHA='be6497b880a634084c7244150b3c517aa1dc776c29a340043dabf0daa2a16192'
RULES={
 'osw.observed-vector-section.v1':[
  ('/track_legs/*/straight_distance_between_hourly_mean_positions_km',6),
  ('/track_legs/*/bearing_between_hourly_mean_positions_degrees_true',6),
  ('/maximum_position_spacing_km',6),('/median_position_spacing_km',6)],
 'osw.native-vector-support.v1':[
  ('/run_sensitivity/*/runs/*/track_length_between_ensemble_end_positions_km',6),
  ('/run_sensitivity/*/runs/*/endpoint_distance_km',6)],
 'osw.hydrography-correspondence.v1':[('/candidate_pairs/*/position_separation_km',6)],
 'osw.observed-component-spans.v1':[
  ('*/endpoint_separation_km',6),('*/native_bracket_spacing_km',6),('*/spacing_km',6),
  ('*/bearing_degrees_true',6),('*/track_length_between_crossings_km',6),('*/largest_native_spacing_km',6),
  ('*/track_length_to_endpoint_distance_ratio',8),('*/endpoint_distance_in_largest_native_spacings',8),
  ('*/bracket_endpoint_combination_distances_km/*',6),('*/bracket_endpoint_combination_spread_km/*',6)],
 'osw.underway-component-averaging.v1':[
  ('*/ensemble_end_position_track_km',6),('*/weighted_position_bracket_km',6)],
 'osw.conditional-run-component-composite.v1':[
  ('*/ensemble_end_position_track_km',6),('*/unobserved_endpoint_distance_km',6),
  ('*/mean_position_bracket_km',6),('*/endpoint_separation_km',6)],
 'osw.necc-paired-vector-direction-evidence.v1':[
  ('/rows/*/zero_crossing_component_span/span_km',6),('/rows/*/threshold_sensitivity/*/span_km',6),
  ('/target_monthly_reproduction/*/paired_component_span_km',6),
  ('/target_monthly_reproduction/*/span_absolute_difference_km',6)],
 'osw.norkyst-continuous-section-diagnostic.v1':[('/section_distances_km/*',6)],
 'osw.loop-durante-composite-contour-paths.v1':[
  ('/cases/*/components/*/mean_vector_speed_m_s',8),('/cases/*/components/*/mean_along_path_m_s',8),
  ('/cases/*/components/*/minimum_along_path_m_s',8),
  ('/cases/*/components/*/endpoints/*/eastward_m_s',8),('/cases/*/components/*/endpoints/*/northward_m_s',8),
  ('/cases/*/components/*/endpoints/*/bilinear_weights/*',8),
  ('/cases/*/components/*/midpoint_samples/*/piece_length_m',3),
  ('/cases/*/components/*/midpoint_samples/*/longitude_latitude/*',8),
  ('/cases/*/components/*/midpoint_samples/*/tangent_azimuth_degrees',6),
  ('/cases/*/components/*/midpoint_samples/*/vector_speed_m_s',8),
  ('/cases/*/components/*/midpoint_samples/*/along_path_m_s',8),
  ('/cases/*/components/*/midpoint_samples/*/velocity/eastward_m_s',8),
  ('/cases/*/components/*/midpoint_samples/*/velocity/northward_m_s',8),
  ('/cases/*/components/*/midpoint_samples/*/velocity/bilinear_weights/*',8)]}


def dependency_pins():
    pin=hashlib.sha256((ROOT/PROTOCOL).read_bytes()).hexdigest()
    if pin!=PROTOCOL_SHA:raise ValueError('Changed scientific readback protocol')
    return {PROTOCOL:pin,'analysis/scientific_readback.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


def canonicalize(report):
    schema=report.get('schema')
    if schema not in RULES:raise ValueError('No explicit derived-field precision profile for '+str(schema))
    def visit(value,path=''):
        if isinstance(value,dict):return {k:visit(v,path+'/'+k.replace('~','~0').replace('/','~1')) for k,v in value.items()}
        if isinstance(value,list):return [visit(v,path+'/'+str(i)) for i,v in enumerate(value)]
        precision=next((digits for pattern,digits in RULES[schema] if fnmatchcase(path,pattern)),None)
        if precision is None or value is None:return value
        if not isinstance(value,(int,float)) or isinstance(value,bool) or not math.isfinite(value):
            raise ValueError('Invalid computed numeric readback at '+path)
        rounded=round(value,precision)
        return 0.0 if rounded==0 else rounded
    result=visit(report)
    result['input_sha256'].update(dependency_pins())
    result['calculation_readback_protocol']=PROTOCOL
    return result
