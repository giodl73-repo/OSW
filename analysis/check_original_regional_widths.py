"""Original regional synthesis stays separate from the article's field campaign."""
import copy, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/algerian-cotroneo-2019-regional-width-scope-audit.json'
SOURCE_SHA='9f4bd73abd9785762fa1f498d30c120392f4847e1f573528c86d8cec13b44a18'
def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def validate_row(row,audit=None):
    if row.get('current_id') == 'alaska':
        return validate_alaska_row(row,audit)
    audit=json.loads((ROOT/AUDIT).read_bytes()) if audit is None else audit
    if audit['source_document_sha256']!=SOURCE_SHA or audit['source_document_bytes']!=3583991 or digest(audit['source_document_file'])!=SOURCE_SHA:raise ValueError('Changed Algerian original source')
    for kind in ['acquisition','protocol']:
        if digest(audit[kind+'_file'])!=audit[kind+'_sha256']:raise ValueError('Changed Algerian provenance or convention')
    source=audit['measurement']
    if (source['current_id'],source['phase_kind'],source['width_range_km'],source['approximate_width_km'])!=('algerian','regional_summary',[30,50],None):raise ValueError('Changed Algerian regional span or invented midpoint')
    if any(source[k] is not None for k in ['observed_period','calendar_months','section_geometry','fixed_layer_bounds_m','uncertainty_km']):raise ValueError('Assigned survey dates/depth or invented boundaries to Algerian width')
    if any(source[k] is not False for k in ['whole_current_representative','width_rank_eligible','full_width_inference_eligible','annual_extrema_eligible','seasonal_playback_eligible','is_confidence_interval']):raise ValueError('Promoted Algerian background width span')
    context=source['original_regional_context']
    if any(context[k] is not False for k in ['underlying_width_methods_reviewed','survey_years_are_width_occupations','survey_depth_is_width_layer','LIW_depth_is_width_layer','eddy_diameter_is_current_width','span_is_annual_range','boundary_coordinates_extracted']):raise ValueError('Conflated Algerian synthesis and survey supports')
    expected=copy.deepcopy(source);expected['original_regional_context'].update(audit_file=AUDIT,audit_sha256=digest(AUDIT))
    if row!=expected:raise ValueError('Algerian regional width differs from pinned source extraction')

ALASKA_AUDIT='research/alaska-weingartner-2002-regional-width-scope-audit.json'
ALASKA_SHA='9d8b6464a0d2d3817a088de7425935d0fdef3697534e1c33b7c552b370764b76'
def validate_alaska_row(row,audit=None):
    audit=json.loads((ROOT/ALASKA_AUDIT).read_bytes()) if audit is None else audit
    if audit['source_document_sha256']!=ALASKA_SHA or audit['source_document_bytes']!=5693842 or digest(audit['source_document_file'])!=ALASKA_SHA:
        raise ValueError('Changed Alaska original source')
    for kind in ['acquisition','protocol']:
        if digest(audit[kind+'_file'])!=audit[kind+'_sha256']:raise ValueError('Changed Alaska provenance or convention')
    source=audit['measurement']
    if (source['current_id'],source['phase_kind'],source['approximate_width_km'],source['width_range_km'])!=('alaska','regional_summary',300,None):
        raise ValueError('Changed Alaska approximate point or invented range')
    if any(source[k] is not None for k in ['observed_period','calendar_months','section_geometry','fixed_layer_bounds_m','uncertainty_km']):
        raise ValueError('Assigned survey support or invented Alaska boundaries')
    if any(source[k] is not False for k in ['whole_current_representative','width_rank_eligible','full_width_inference_eligible','annual_extrema_eligible','seasonal_playback_eligible','is_confidence_interval']):
        raise ValueError('Promoted Alaska background width point')
    context=source['original_regional_context']
    if any(context[k] is not False for k in ['underlying_width_methods_reviewed','survey_years_are_width_occupations','drifter_depth_is_width_layer','forcing_climatologies_are_width_climatology','year_round_persistence_is_monthly_width_series','alaskan_stream_width_is_range_endpoint','coastal_confinement_is_alaska_width','shelf_breadth_is_current_width','boundary_coordinates_extracted']):
        raise ValueError('Conflated Alaska synthesis and neighboring supports')
    expected=copy.deepcopy(source);expected['original_regional_context'].update(audit_file=ALASKA_AUDIT,audit_sha256=digest(ALASKA_AUDIT))
    if row!=expected:raise ValueError('Alaska regional width differs from pinned source extraction')
