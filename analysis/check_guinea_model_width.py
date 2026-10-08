"""A climatologically forced model mean cannot become dated or seasonal widths."""
import copy
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
AUDIT = 'research/guinea-djakoure-2017-model-width-source-review.json'
SOURCE_SHA = 'bbdd703b7e69602c2022c85075e8675b5b427ffb779884c8d2d9a4c8a004e7b8'

def digest(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

def validate_row(row, audit=None):
    audit = json.loads((ROOT/AUDIT).read_bytes()) if audit is None else audit
    if audit['source_document_sha256'] != SOURCE_SHA or audit['source_document_bytes'] != 7701446 or digest(audit['source_document_file']) != SOURCE_SHA:
        raise ValueError('Changed Guinea original source')
    for kind in ['acquisition', 'protocol', 'general_protocol']:
        if digest(audit[kind+'_file']) != audit[kind+'_sha256']:
            raise ValueError('Changed Guinea provenance or measurement convention')
    source = audit['measurement']
    if (source['current_id'], source['phase_kind'], source['approximate_width_km'], source['width_range_km']) != ('guinea', 'model_regional_width_summary', 200, None):
        raise ValueError('Guinea model mean confused with theoretical scale or range')
    if any(source[k] is not None for k in ['observed_period', 'calendar_months', 'section_geometry', 'fixed_layer_bounds_m', 'uncertainty_km']):
        raise ValueError('Invented Guinea dates, edges, layer or uncertainty')
    if any(source[k] is not False for k in ['whole_current_representative', 'width_rank_eligible', 'annual_extrema_eligible', 'seasonal_playback_eligible', 'full_width_inference_eligible', 'is_confidence_interval']):
        raise ValueError('Promoted Guinea regional mean to whole-current or annual evidence')
    context = source['model_regional_context']
    model = context['model']
    if model['analysis_model_years'] != [5,6,7,8,9,10] or model['calendar_dates'] is not None or model['ten_year_climatological_integration'] is not True or model['child_resolution_degrees'] != 1/15:
        raise ValueError('Guinea model integration relabeled as observation period')
    if any(context[k] is not False for k in ['theoretical_inertial_scale_is_width_bound', 'model_years_are_calendar_years', 'annual_mean_is_annual_extrema', 'introduction_thickness_is_fixed_width_layer', 'velocity_maximum_is_boundary_cutoff', 'boundary_coordinates_extracted', 'figure_caption_conflict_resolved']):
        raise ValueError('Conflated Guinea source supports')
    expected = copy.deepcopy(source)
    expected['model_regional_context'].update(audit_file=AUDIT, audit_sha256=digest(AUDIT))
    if row != expected:
        raise ValueError('Guinea width differs from pinned source extraction')
