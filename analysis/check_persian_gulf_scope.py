"""Protect hydrographic core and section-distance evidence from route admission."""
import math


def validate(document):
    if (document.get('schema')!='osw.current-source-scope-audit.v1'
        or document.get('current_id')!='persian-gulf-saline-overflow'
        or document.get('status')!='editorial_source_scope_not_scientific_approval'
        or document.get('width_metric')!='author_reported_half_salinity_contrast_water_mass_core_width'
        or document.get('boundary_rule')!='S_boundary=(S_core_max+S_environment)/2'
        or document.get('velocity_boundary_m_s') is not None
        or any(document.get(key) is not False for key in ['fixed_depth_width','paired_edges_extracted','width_rank_eligible','seasonal_route_playback_supported'])
        or any(document.get(key) is not None for key in ['whole_current_length_km','whole_current_width_km','annual_length_range_km','annual_width_range_km'])
        or document.get('width_variation_axis')!='section_location_and_occupation_not_annual_cycle'):
        raise ValueError('PGW core scope relabeled as velocity width, route or annual evidence')
    def finite(value):return type(value) in (int,float) and math.isfinite(value)
    rows=document.get('reported_local_core_widths',[])
    if not rows:raise ValueError('Missing source core widths')
    for row in rows:
        value,span=row.get('approximate_width_km'),row.get('width_range_km')
        if not row.get('sections') or not all(isinstance(s,str) for s in row['sections']):raise ValueError('Missing width section scope')
        if span is None:
            if not finite(value) or value<=0:raise ValueError('Invalid source width')
        elif value is not None or not isinstance(span,list) or len(span)!=2 or not all(finite(v) for v in span) or not 0<span[0]<span[1]:raise ValueError('Invented representative width or invalid range')
    coordinate=document.get('reported_section_distances',{})
    rows=coordinate.get('rows',[])
    if coordinate.get('origin')!='R13' or coordinate.get('units')!='km' or coordinate.get('metric')!='author_reported_section_distance_coordinate_not_OSW_geodesic_axis' or coordinate.get('is_whole_current_length') is not False or coordinate.get('axis_geometry') is not None or not rows:
        raise ValueError('Section distance converted into current axis')
    distances=[r.get('distance_km') for r in rows]
    if not all(finite(v) for v in distances) or distances[0]!=0 or any(a>=b for a,b in zip(distances,distances[1:])):raise ValueError('Invalid source distance coordinate')
    groups=[s for r in rows for s in r.get('sections',[])]
    if not groups or len(groups)!=len(set(groups)) or any(not isinstance(s,str) for s in groups):raise ValueError('Invalid source section identifiers')

