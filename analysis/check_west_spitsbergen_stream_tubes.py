"""Preserve source table columns and threshold/transport semantics."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/west-spitsbergen-kolas-2018-stream-tube-width-scope-audit.json'
SOURCE='research/source-data/kolas-fer-wsc-2018/journal-article.pdf'
SOURCE_HASH='023bfcf7361b854dd4e6c751cce949edc613a92f0f554d93712338009f00928f'
PROTOCOL='plans/west-spitsbergen-stream-tube-width-protocol-v1.md'

def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

def validate_row(row, audit=None):
    audit=json.loads((ROOT/AUDIT).read_bytes()) if audit is None else audit
    if (audit['source_document_file'],audit['source_document_sha256'],audit['source_document_bytes'])!=(SOURCE,SOURCE_HASH,3810789) or digest(SOURCE)!=SOURCE_HASH:
        raise ValueError('Changed West Spitsbergen original source')
    acq=json.loads((ROOT/audit['acquisition_file']).read_bytes())
    if digest(audit['acquisition_file'])!=audit['acquisition_sha256'] or acq['sha256']!=SOURCE_HASH or acq['license']!='CC BY 4.0':raise ValueError('Changed WSC acquisition or rights')
    if audit['protocol_file']!=PROTOCOL or audit['protocol_sha256']!=digest(PROTOCOL):raise ValueError('Stale WSC stream-tube rules')
    expected=[('a',1,24,[29,17]),('a',2,24,[]),('b',1,21,[24,11]),('b',2,61,[]),('c',1,35,[37,32]),('c',2,10,[])]
    if len(audit['measurements'])!=6 or len({r['id'] for r in audit['measurements']})!=6:raise ValueError('Incomplete WSC table')
    for r,(section,tube,width,cases) in zip(audit['measurements'],expected):
        c=r['stream_tube_context']
        if (r['id'],r['current_id'],r['approximate_width_km'],r['phase_kind'],r['measurement_type'],r['width_metric'])!=(f'west-spitsbergen-kolas-2018-{section}-tube-{tube}','west-spitsbergen',width,'synoptic_stream_tube_section','published_synoptic_AW_stream_tube_section_width','along_section_span_of_property_bounded_transport_stream_tube'):raise ValueError('WSC table cell identity or metric changed')
        if any(r.get(k) is not None for k in ['width_range_km','range_kind','observed_period','calendar_months','section_geometry','fixed_layer_bounds_m']):raise ValueError('Invented WSC interval, dates or edges')
        if any(r.get(k) is not False for k in ['whole_current_representative','width_rank_eligible','annual_extrema_eligible','seasonal_playback_eligible','full_width_inference_eligible','is_confidence_interval']):raise ValueError('Promoted WSC stream-tube support')
        if c['threshold_sensitivity_cases']!=[{'velocity_m_s':v,'width_km':w} for v,w in zip([0.02,0.08],cases)] or c['threshold_velocity_m_s']!=(0.04 if tube==1 else None):raise ValueError('WSC threshold cases changed')
        if (c['section_id'],c['stream_tube'],c['constraint_transport_sv'],c['constraint_transport_tolerance_fraction'])!=(section.upper(),tube,1.3 if tube==2 else None,0.1 if tube==2 else None):raise ValueError('WSC section or transport constraint changed')
        if (c['offshore_core_relative_edge_km'],c['section_c_offshore_edge_from_SADCP'],c['section_b_tube2_shelf_limited'],c['shared_observation_group'])!=(-11 if section=='c' and tube==1 else None,section=='c' and tube==1,section=='b' and tube==2,'kolas-2018-section-a-identical-tube' if section=='a' else None):raise ValueError('WSC section exception or shared observation changed')
        if any(c.get(k) is not False for k in ['transport_tolerance_is_width_error','cruise_period_is_section_sampling_period','AW_depth_context_is_fixed_width_layer','reference_pressure_is_width_depth','comparison_depth_is_width_layer','study_coordinate_is_whole_current_length','boundary_coordinates_extracted']):raise ValueError('Conflated WSC sampling context')
        if c['cruise_context_period']!={'start':'2015-08-12','end':'2015-08-21'} or c['AW_observed_depth_context_m']!=[45,475] or c['comparison_velocity_depth_context_m']!=[50,500] or c['geostrophic_reference_pressure_dbar']!=100 or c['study_along_isobath_coordinate_km']!={'c':0,'b':86,'a':171}[section] or [c[k] for k in ['grid_horizontal_km','grid_vertical_m','smoothing_horizontal_km','smoothing_vertical_m']]!=[1,2,10,10]:raise ValueError('Changed WSC source context')
        if c['protocol_file']!=PROTOCOL or c['protocol_sha256']!=digest(PROTOCOL):raise ValueError('Changed WSC row protocol')
    if audit['whole_current_width_km'] is not None or audit['annual_width_range_km'] is not None:raise ValueError('Invented WSC system dimensions')
    source=next((r for r in audit['measurements'] if r['id']==row['id']),None)
    if source is None:raise ValueError('Unknown WSC stream-tube record')
    expected=json.loads(json.dumps(source));expected['stream_tube_context'].update(audit_file=AUDIT,audit_sha256=digest(AUDIT))
    if row!=expected:raise ValueError('WSC inventory record differs from original-source extraction')

if __name__=='__main__':
    rows=json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())['measurements']
    selected=[r for r in rows if r['current_id']=='west-spitsbergen']
    for row in selected:validate_row(row)
    assert len(selected)==6
    print('PASS: six WSC source table cells, thresholds and transport semantics')
