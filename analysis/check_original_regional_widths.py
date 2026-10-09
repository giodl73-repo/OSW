"""Original regional synthesis stays separate from the article's field campaign."""
import copy, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/algerian-cotroneo-2019-regional-width-scope-audit.json'
SOURCE_SHA='9f4bd73abd9785762fa1f498d30c120392f4847e1f573528c86d8cec13b44a18'
def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def validate_row(row,audit=None):
    if row.get('current_id') == 'kuroshio-extension':
        return validate_kuroshio_extension_row(row,audit)
    if row.get('current_id') == 'atlantic-equatorial-undercurrent':
        return validate_atlantic_euc_row(row,audit)
    if row.get('current_id') == 'pacific-equatorial-undercurrent':
        return validate_pacific_euc_row(row,audit)
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

KUROSHIO_EXTENSION_AUDIT='research/kuroshio-extension-sasaki-2013-width-averaging-scope-audit.json'
KUROSHIO_EXTENSION_SHA='483dd114d6bbbff9b153460edf28a3391958a78e1a0b6a646db548eefcb8a674'

def validate_kuroshio_extension_row(row,audit=None):
    audit=json.loads((ROOT/KUROSHIO_EXTENSION_AUDIT).read_bytes()) if audit is None else audit
    if audit['source_document_sha256']!=KUROSHIO_EXTENSION_SHA or audit['source_document_bytes']!=3831641 or digest(audit['source_document_file'])!=KUROSHIO_EXTENSION_SHA:
        raise ValueError('Changed Kuroshio Extension original source')
    for kind in ['acquisition','protocol']:
        if digest(audit[kind+'_file'])!=audit[kind+'_sha256']:raise ValueError('Changed Kuroshio Extension provenance or convention')
    source=audit['measurement']
    if (source['current_id'],source['phase_kind'],source['approximate_width_km'],source['width_range_km'])!=('kuroshio-extension','regional_summary',100,None):
        raise ValueError('Changed Kuroshio Extension monthly-field point or pooled averaging scales')
    if any(source[k] is not None for k in ['observed_period','calendar_months','section_geometry','fixed_layer_bounds_m','uncertainty_km']):
        raise ValueError('Assigned illustration dates or invented width support')
    if any(source[k] is not False for k in ['whole_current_representative','width_rank_eligible','full_width_inference_eligible','annual_extrema_eligible','seasonal_playback_eligible','is_confidence_interval']):
        raise ValueError('Promoted Kuroshio Extension regional point')
    context=source['original_regional_context']
    exclusions=['underlying_width_methods_reviewed','monthly_mean_is_dated_width_series','illustrative_figure_date_is_width_occupation','analysis_period_is_width_occupation','climatological_scale_is_width_range_endpoint','jet_displacement_is_width_variation','axis_search_contours_are_width_edges','eof_anomaly_scale_is_width_measurement','low_pass_shading_is_monthly_width_series','meridional_width_is_flow_normal_width','boundary_coordinates_extracted']
    if any(context[k] is not False for k in exclusions) or context['analysis_period_context']['is_width_measurement_support'] is not False:
        raise ValueError('Conflated Kuroshio Extension averaging, position or axis supports')
    scale=context['climatological_scale_context']
    if context['temporal_operator']!='monthly_mean' or context['illustrative_figure_month']!='2005-01' or scale['meridional_scale_km']!=200 or scale['temporal_operator']!='climatological_mean' or scale['is_width_sample'] is not False or scale['is_range_endpoint'] is not False or scale['uncertainty_km'] is not None:
        raise ValueError('Promoted Kuroshio Extension climatological context')
    expected=copy.deepcopy(source);expected['original_regional_context'].update(audit_file=KUROSHIO_EXTENSION_AUDIT,audit_sha256=digest(KUROSHIO_EXTENSION_AUDIT))
    if row!=expected:raise ValueError('Kuroshio Extension width differs from pinned source extraction')

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

PACIFIC_EUC_AUDIT='research/pacific-euc-wang-2022-background-width-scope-audit.json'
PACIFIC_EUC_SHA='ecef3832b044af51a388e49a51fd6117c55b16eb30fc3e3e61f569a0966735b4'
def validate_pacific_euc_row(row,audit=None):
    audit=json.loads((ROOT/PACIFIC_EUC_AUDIT).read_bytes()) if audit is None else audit
    if audit['source_document_sha256']!=PACIFIC_EUC_SHA or audit['source_document_bytes']!=19499462 or digest(audit['source_document_file'])!=PACIFIC_EUC_SHA:
        raise ValueError('Changed Pacific EUC original source')
    for kind in ['acquisition','protocol']:
        if digest(audit[kind+'_file'])!=audit[kind+'_sha256']:raise ValueError('Changed Pacific EUC provenance or convention')
    source=audit['measurement']
    if (source['current_id'],source['phase_kind'],source['approximate_width_km'],source['width_range_km'])!=('pacific-equatorial-undercurrent','regional_summary',400,None):
        raise ValueError('Changed Pacific EUC background point or invented range')
    if any(source[k] is not None for k in ['observed_period','calendar_months','section_geometry','fixed_layer_bounds_m','uncertainty_km']):
        raise ValueError('Assigned model support or invented Pacific EUC boundaries')
    if any(source[k] is not False for k in ['whole_current_representative','width_rank_eligible','full_width_inference_eligible','annual_extrema_eligible','seasonal_playback_eligible','is_confidence_interval']):
        raise ValueError('Promoted Pacific EUC background width point')
    context=source['original_regional_context']
    if any(context[k] is not False for k in ['underlying_width_methods_reviewed','approximate_thickness_is_fixed_width_layer','core_depths_are_fixed_width_layer','model_transport_bounds_are_width_edges','model_transport_depths_are_width_layer','model_years_are_width_occupations','transport_velocity_climatology_is_width_climatology','transport_seasonality_is_width_seasonality','other_publication_width_is_range_endpoint','cross_basin_width_inheritance_eligible','boundary_coordinates_extracted']) or context['transport_context']['is_width_measurement_support'] is not False:
        raise ValueError('Conflated Pacific EUC background and transport/model supports')
    expected=copy.deepcopy(source);expected['original_regional_context'].update(audit_file=PACIFIC_EUC_AUDIT,audit_sha256=digest(PACIFIC_EUC_AUDIT))
    if row!=expected:raise ValueError('Pacific EUC background width differs from pinned source extraction')

ATLANTIC_EUC_AUDIT='research/atlantic-euc-gouriou-1988-background-width-scope-audit.json'
ATLANTIC_EUC_SHA='5bb0c63ee27bd9f722d1d74c656187b57c0762b854d78abb7cba4546984e3db5'

def validate_atlantic_euc_row(row,audit=None):
    audit=json.loads((ROOT/ATLANTIC_EUC_AUDIT).read_bytes()) if audit is None else audit
    if audit['source_document_sha256']!=ATLANTIC_EUC_SHA or audit['source_document_bytes']!=11747356 or digest(audit['source_document_file'])!=ATLANTIC_EUC_SHA:
        raise ValueError('Changed Atlantic EUC original source')
    for kind in ['acquisition','protocol']:
        if digest(audit[kind+'_file'])!=audit[kind+'_sha256']:raise ValueError('Changed Atlantic EUC provenance or convention')
    source=audit['measurement']
    if (source['current_id'],source['phase_kind'],source['approximate_width_km'],source['width_range_km'])!=('atlantic-equatorial-undercurrent','regional_summary',200,None):
        raise ValueError('Changed Atlantic EUC background point or invented range')
    if any(source[k] is not None for k in ['observed_period','calendar_months','section_geometry','fixed_layer_bounds_m','uncertainty_km']):
        raise ValueError('Assigned campaign support or invented Atlantic EUC boundaries')
    if any(source[k] is not False for k in ['whole_current_representative','width_rank_eligible','full_width_inference_eligible','annual_extrema_eligible','seasonal_playback_eligible','is_confidence_interval']):
        raise ValueError('Promoted Atlantic EUC background width point')
    context=source['original_regional_context']
    if any(context[k] is not False for k in ['underlying_width_methods_reviewed','thickness_is_fixed_width_layer','core_depths_are_fixed_width_layer','core_position_oscillation_is_width_range','compilation_years_are_width_occupations','figure_section_dates_are_background_width_dates','garp_transport_dates_are_width_occupations','transport_cutoff_is_background_width_boundary','translation_is_independent_width_observation','cross_basin_width_inheritance_eligible','boundary_coordinates_extracted']):
        raise ValueError('Conflated Atlantic EUC background and campaign/transport supports')
    expected=copy.deepcopy(source);expected['original_regional_context'].update(audit_file=ATLANTIC_EUC_AUDIT,audit_sha256=digest(ATLANTIC_EUC_AUDIT))
    if row!=expected:raise ValueError('Atlantic EUC background width differs from pinned source extraction')
