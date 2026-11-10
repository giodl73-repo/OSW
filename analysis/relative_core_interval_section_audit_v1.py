"""Audits for relative-core interval-selected meridional sections; frozen geometry checks reused."""
import math
import numpy as np
from relative_core_interval_diagnostic_v1 import diagnose
from sample_eac_hycom_route_depth_v1 import along_velocity,clean,canonical_hash
from sample_atlantic_current_depth_v1 import wrapped_longitude
from acquire_zonal_current_depth_sections_v1 import maximum_longitude_distance_km


def validate_interval_components(section,op):
    if section['entity_id']!=op['entity_id'] or section['source_returned_timestamp_utc']!=section['snapshot_time_utc']:raise ValueError('Source identity or exact snapshot changed')
    profiles=section['columns'];z=section['depth_levels_m']
    if canonical_hash(profiles)!=section['decoded_columns_sha256']:raise ValueError('Retained section columns hash mismatch')
    if op['surface_component_gate_m_s'] is not None or op.get('temperature_gate') is not None:raise ValueError('Relative-core source forbids surface and thermal gates')
    temperatures=section['native100m_temperature_degrees_celsius']
    if temperatures is not None or section.get('temperature_source') is not None:raise ValueError('Unexpected thermal values on interval-only source')
    result=diagnose(z,[r['signed_reference_component_m_s'] for r in profiles],op)
    if result!=section['diagnosis']:raise ValueError('Retained section diagnosis mismatch')
    for profile in profiles:
        if profile['sampled_lon_lat'][0]!=wrapped_longitude(profile['native_source_longitude_degrees_east']):raise ValueError('Source/wrapped longitude mismatch')
    if section['eligibility']!=op['eligibility'] or any(section['eligibility'].values()):raise ValueError('No physical admission')
    if section['component_bearing_degrees_true']!=op['component_bearing_degrees_true']:raise ValueError('Component frame changed')
    for profile in profiles:
        u=np.asarray([np.nan if x is None else x for x in profile['eastward_velocity_m_s']])
        v=np.asarray([np.nan if x is None else x for x in profile['northward_velocity_m_s']])
        signed=along_velocity(u,v,op['component_bearing_degrees_true'])
        signed=np.where(np.isfinite(u)&np.isfinite(v),signed,np.nan)
        if clean(signed)!=profile['signed_reference_component_m_s']:raise ValueError('Retained signed component mismatch')



def validate_retained(section,config):
    validate_interval_components(section,config)
    definition=section['section_definition'];profiles=section['columns'];slab=section['retrieved_hyperslab']
    if definition['fixed_axis']!='longitude' or definition['entity_id']!=section['entity_id']:raise ValueError('Section owner/orientation mismatch')
    if not 3<=len(profiles)<=150 or slab['depth_indices_inclusive']!=[0,len(section['depth_levels_m'])-1]:raise ValueError('Retained slice shape changed')
    indices=[r['global_latitude_index'] for r in profiles];latitudes=[r['sampled_lon_lat'][1] for r in profiles]
    if indices!=list(range(indices[0],indices[0]+len(profiles))) or any(b<=a for a,b in zip(latitudes,latitudes[1:])):raise ValueError('Native increasing latitude profile order changed')
    if slab['latitude_indices_inclusive']!=[indices[0],indices[-1]]:raise ValueError('Latitude hyperslab changed')
    native=section['actual_source_longitude_degrees_east'];south,north=definition['latitude_gate_degrees_north']
    for profile in profiles:
        if profile['native_source_longitude_degrees_east']!=native or profile['global_longitude_index']!=slab['longitude_index']:raise ValueError('Fixed native longitude changed')
        if profile['native_source_latitude_degrees_north']!=profile['sampled_lon_lat'][1] or not south<=profile['sampled_lon_lat'][1]<=north:raise ValueError('Native latitude/gate changed')
    distance=maximum_longitude_distance_km(definition['longitude_degrees_east'],native,latitudes)
    if distance>config['maximum_nearest_longitude_distance_km'] or not math.isclose(distance,section['maximum_nearest_longitude_distance_km'],rel_tol=1e-12,abs_tol=1e-12):raise ValueError('Longitude distance receipt changed')
