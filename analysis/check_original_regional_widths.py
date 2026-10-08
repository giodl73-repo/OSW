"""Original regional synthesis stays separate from the article's field campaign."""
import copy, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/algerian-cotroneo-2019-regional-width-scope-audit.json'
SOURCE_SHA='9f4bd73abd9785762fa1f498d30c120392f4847e1f573528c86d8cec13b44a18'
def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def validate_row(row,audit=None):
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
