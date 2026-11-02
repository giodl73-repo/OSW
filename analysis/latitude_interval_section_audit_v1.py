"""Interval-component audit followed by unchanged frozen latitude geometry checks."""
from interval_transverse_section_audit_v1 import validate_interval_components as validate_components
from sample_eac_hycom_route_depth_v1 import GEOD


def validate_retained(section,config):
    validate_components(section,config)
    definition=section['section_definition'];profiles=section['columns'];slab=section['retrieved_hyperslab']
    if definition['fixed_axis']!='latitude' or definition['entity_id']!=section['entity_id']:raise ValueError('Section owner/orientation mismatch')
    if not 3<=len(profiles)<=150 or slab['depth_indices_inclusive']!=[0,len(section['depth_levels_m'])-1]:raise ValueError('Retained slice shape changed')
    indices=[r['global_longitude_index'] for r in profiles];longitudes=[r['sampled_lon_lat'][0] for r in profiles]
    if indices!=list(range(indices[0],indices[0]+len(profiles))) or any(b<=a for a,b in zip(longitudes,longitudes[1:])):raise ValueError('Native increasing longitude order changed')
    if slab['longitude_indices_inclusive']!=[indices[0],indices[-1]]:raise ValueError('Longitude hyperslab changed')
    native=section['actual_source_latitude_degrees_north'];west,east=definition['longitude_gate_degrees_east']
    for profile in profiles:
        if profile['native_source_latitude_degrees_north']!=native or profile['sampled_lon_lat'][1]!=native or profile['global_latitude_index']!=slab['latitude_index']:raise ValueError('Fixed native latitude changed')
        if not west<=profile['sampled_lon_lat'][0]<=east:raise ValueError('Profile outside declared gate')
    distance=GEOD.inv(0,definition['latitude_degrees_north'],0,native)[2]/1000
    if distance!=section['nearest_latitude_distance_km'] or distance>config['maximum_nearest_latitude_distance_km']:raise ValueError('Native latitude offset changed')
