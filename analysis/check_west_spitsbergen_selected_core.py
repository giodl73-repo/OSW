"""Validate the published selected-core statistic without annual-range promotion."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/west-spitsbergen-dundas-2026-selected-core-width-scope-audit.json'
SOURCE='research/source-data/dundas-fer-wsc-2026/journal-article.pdf'
AUDIT_SHA='87e5c16c7ea5787e1224cc19b05e4f7b885356268062e6c997f1e09c28dc09fa'
SOURCE_SHA='b19a8eab70d72c12f55335d70950a1722283b330b1d805f9b82af1a1ff649fbf'

def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

def validate(audit=None):
    raw=(ROOT/AUDIT).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=AUDIT_SHA:raise ValueError('Changed frozen selected-core extraction')
    expected=json.loads(raw)
    d=expected if audit is None else audit
    if d!=expected:raise ValueError('Selected-core record differs from reviewed published extraction')
    if (d['current_id'],d['source_document_file'],d['source_document_sha256'],d['source_document_bytes'])!=('west-spitsbergen',SOURCE,SOURCE_SHA,9421023):raise ValueError('Changed selected-core source identity')
    for path,pin in d['input_sha256'].items():
        if digest(path)!=pin:raise ValueError('Changed selected-core original '+path)
    if digest(SOURCE)!=SOURCE_SHA or digest(d['protocol_file'])!=d['protocol_sha256'] or digest(d['acquisition_file'])!=d['acquisition_sha256']:raise ValueError('Changed selected-core source rules')
    acq=json.loads((ROOT/d['acquisition_file']).read_bytes())
    if acq['sha256']!=SOURCE_SHA or acq['license']!='CC BY 4.0':raise ValueError('Changed selected-core rights')
    r=d['measurement'];c=r['selected_core_context']
    if (r['id'],r['current_id'],r['phase_kind'],r['width_metric'],r['approximate_width_km'],r['width_standard_deviation_km'])!=('west-spitsbergen-dundas-2026-selected-core-width-statistic','west-spitsbergen','selected_section_core_width_statistics','zonal_extent_of_selected_high_transport_core',28,7):raise ValueError('Changed published core statistic')
    for key in ['width_range_km','range_kind','section_geometry','fixed_layer_bounds_m','calendar_months','observed_period']:
        if r.get(key) is not None:raise ValueError('Promoted selected-core range, layer or geometry')
    for key in ['is_confidence_interval','whole_current_representative','width_rank_eligible','annual_extrema_eligible','seasonal_playback_eligible','full_width_inference_eligible']:
        if r.get(key) is not False:raise ValueError('Promoted selected-core admission')
    for key in ['selected_section_count','per_section_widths_km','numeric_transport_threshold','boundary_coordinates','whole_current_width_km','annual_width_range_km']:
        if c.get(key) is not None:raise ValueError('Invented selected-core reconstruction')
    expected={'study_section_count':22,'incomplete_study_sections':5,'maximum_search_minimum_distance_km':275,'section_selection_percentile':60,'fixed_wsc_transport_region_boundary_km':300,'width_standard_deviation_km':7,'source_grid_horizontal_km':2,'source_grid_vertical_dbar':2,'objective_mapping_horizontal_scale_km':40,'objective_mapping_vertical_scale_m':40,'mean_native_profile_spacing_km':3.5,'native_profile_spacing_standard_deviation_km':2.3,'absolute_velocity_reference':'satellite_surface_geostrophic_currents_for_all_sections','glider_dac_affected_sections':[7,8,9,10],'target_latitude_degrees_north':77.25,'target_longitude_bounds_degrees_east':[-2,12],'distance_origin_longitude_degrees_east':-2}
    if any(c.get(k)!=v for k,v in expected.items()):raise ValueError('Changed selected-core operator, resolution or velocity reference')
    for key in ['selection_percentile_is_peak_fraction','fixed_region_span_is_core_width','standard_deviation_is_width_measurement_error','standard_deviation_is_annual_range','width_estimator_reproduced']:
        if c.get(key) is not False:raise ValueError('Conflated selected-core method or variability')
    if c.get('uses_Q_not_QAW') is not True:raise ValueError('Changed selected-core vertical support')
    expected_windows=[(1,'2020-10-10','2021-02-07',1250,7),(2,'2021-08-14','2022-02-20',1610,7),(3,'2022-08-07','2023-01-02',1430,8)]
    if [(w['mission'],w['start'],w['end'],w['profiles'],w['sections']) for w in d['section_windows']]!=expected_windows:raise ValueError('Changed target-section windows')
    if c['protocol_file']!=d['protocol_file'] or c['protocol_sha256']!=d['protocol_sha256']:raise ValueError('Changed selected-core protocol binding')
    if any(d.get(k) is not None for k in ['whole_current_width_km','annual_width_range_km']) or any(d.get(k) is not False for k in ['native_glider_fields_acquired','width_estimator_reproduced','independent_external_review']):raise ValueError('Promoted source extraction')
    return d

def record():
    """Project the frozen source statistic with an inspectable audit address."""
    row=json.loads(json.dumps(validate()['measurement']))
    figure=json.loads((ROOT/'research/source-data/dundas-fer-wsc-2026/figure.json').read_bytes())
    if figure['audit_sha256']!=AUDIT_SHA:raise ValueError('Stale selected-core figure')
    image='figures/west-spitsbergen-selected-core-width.svg'
    if digest(image)!=figure['files'][image]:raise ValueError('Changed selected-core figure bytes')
    row['selected_core_context'].update(audit_file=AUDIT,audit_sha256=AUDIT_SHA,section_windows=validate()['section_windows'],figure_file=image,figure_sha256=figure['files'][image])
    row.update(source_file=AUDIT,source_pointer='/measurement')
    return row


def validate_row(row):
    if row!=record():raise ValueError('Selected-core inventory statistic differs from source binding or scope')

if __name__=='__main__':
    validate();print('PASS published 28 km core / 7 km standard deviation, exact mission windows, original source and nonannual scope')
