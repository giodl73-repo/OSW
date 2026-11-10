"""Dispatch frozen classic surface-qualified audits over frozen mixed geometry."""
import acquire_zonal_current_depth_sections_v1 as longitude_geometry
import latitude_depth_section_geometry_v1 as latitude_geometry
from mixed_interval_section_geometry_v1 import preflight,profile_count,read_arguments,columns_from_arrays,retained_geometry
from acquire_three_current_depth_sections_v1 import diagnose

def validate_retained(section,config):
    if config['selection_depth_interval_m']!=[0,200] or config['core_search_depth_interval_m']!=[0,200] or config['surface_component_gate_m_s']!=.05 or config.get('temperature_gate') is not None:raise ValueError('Declared frozen upper200m/positive5cm surface diagnostic required')
    axis=section['section_definition']['fixed_axis']
    if section['source_section_geometry']!=axis or section['surface_velocity_qualification_applied'] is not True or section['surface_component_gate_m_s']!=config['surface_component_gate_m_s']:raise ValueError('Retained surface qualification/axis declaration changed')
    if axis=='longitude':return longitude_geometry.validate_retained(section,config)
    if axis=='latitude':return latitude_geometry.validate_retained(section,config)
    raise ValueError('Unsupported retained section axis')
