"""Original regional synthesis stays separate from the article's field campaign."""
import copy, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/algerian-cotroneo-2019-regional-width-scope-audit.json'
SOURCE_SHA='9f4bd73abd9785762fa1f498d30c120392f4847e1f573528c86d8cec13b44a18'
def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def validate_row(row,audit=None):
    if row.get("current_id") == "jutland" and row.get("id", "").startswith("jutland-nielsen-2000-"):
        from check_jutland_satellite_widths import validate_row as validate_satellite
        return validate_satellite(row,audit)
    if row.get("current_id") == "jutland":
        from check_jutland_water_mass_breadth import validate_row as validate_jutland
        return validate_jutland(row,audit)
    if row.get("current_id") == "western-adriatic":
        from check_western_adriatic_mean_widths import validate_row as validate_wac
        return validate_wac(row,audit)
    if row.get("current_id") == "baffin":
        from check_baffin_regional_widths import validate_row as validate_baffin
        return validate_baffin(row,audit)
    if row.get("current_id") == "peru-humboldt":
        from check_humboldt_width_descriptions import validate_row as validate_humboldt
        return validate_humboldt(row,audit)
    if row.get('current_id') == 'west-australian':
        from check_west_australian_breadth import validate_row as validate_wac
        return validate_wac(row,audit)
    if row.get('current_id') == 'zeehan':
        from check_zeehan_historical_width import validate_row as validate_zeehan
        return validate_zeehan(row,audit)
    if row.get('current_id') == 'new-guinea-coastal-undercurrent':
        return validate_ngcu_row(row,audit)
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

NGCU_AUDIT='research/ngcu-zenk-1999-width-constraint-scope-audit.json'
NGCU_SHA='f38a100dc030a94ce776a914b96ea798dd40c6dc1aac80fce3563806c01a6407'

def validate_ngcu_row(row,audit=None):
    audit=json.loads((ROOT/NGCU_AUDIT).read_bytes()) if audit is None else audit
    if audit['source_document_sha256']!=NGCU_SHA or audit['source_document_bytes']!=8089173 or digest(audit['source_document_file'])!=NGCU_SHA:
        raise ValueError('Changed NGCU original source')
    for kind in ['acquisition','protocol']:
        if digest(audit[kind+'_file'])!=audit[kind+'_sha256']:raise ValueError('Changed NGCU provenance or convention')
    source=audit['measurement']
    if source['current_id']!='new-guinea-coastal-undercurrent' or source['phase_kind']!='regional_summary' or any(source[k] is not None for k in ['approximate_width_km','width_range_km','observed_period','calendar_months','section_geometry','fixed_layer_bounds_m','uncertainty_km']):
        raise ValueError('Promoted NGCU size constraint to numeric width or occupation')
    if source['reported_width_constraint']!={'kind':'author_order_of_magnitude_less_than','reference_scale_km':20,'source_notation':'O(<20 km)','is_rigorous_upper_bound':False,'representative_width_km':None,'lower_bound_km':None,'numerical_uncertainty_km':None}:
        raise ValueError('Changed NGCU qualified constraint or invented hard bound')
    if any(source[k] is not False for k in ['whole_current_representative','width_rank_eligible','full_width_inference_eligible','annual_extrema_eligible','seasonal_playback_eligible','is_confidence_interval']):raise ValueError('Promoted NGCU width admission')
    context=source['original_regional_context']
    exclusions=['underlying_width_methods_reviewed','reference_scale_is_point_width','notation_is_rigorous_upper_bound','zero_to_reference_is_width_range','downstream_doubling_is_numeric_width','downstream_widening_is_seasonal_range','speed_exceedance_is_width_cutoff','core_depth_is_fixed_width_layer','adcp_depth_coverage_is_fixed_width_layer','salinity_section_is_width_boundary','cruise_dates_are_width_occupations','publication_month_is_width_observation','float_dates_are_width_occupations','boundary_coordinates_extracted']
    if any(context[k] is not False for k in exclusions) or context['cruise_context']['is_width_measurement_support'] is not False or context['downstream_context']['derived_width_km'] is not None or context['downstream_context']['is_seasonal_variation'] is not False or context['method_context']['is_width_boundary_method'] is not False:
        raise ValueError('Conflated NGCU band and surrounding supports')
    if context['cruise_context']!={'prose_cruise_number':'113','figure_3_caption_cruise_number':'133','cruise_number_conflict':True,'voyage_start':'1996-10-10','voyage_end':'1996-11-19','is_width_measurement_support':False} or context['downstream_context']['reported_core_widening_factor']!=2 or context['method_context']!={'local_speed_exceeds_cm_s':80,'core_depth_context_m':200,'adcp_coverage_context_m':[350,400],'is_width_boundary_method':False}:
        raise ValueError('Changed NGCU source context or concealed cruise conflict')
    report=context['supporting_report']
    if report['source_document_sha256']!='cc9e293b98a47581b9d162c63781af1e5842d6aa0de403a7f06941ea7e6f4cca' or digest(report['source_document_file'])!=report['source_document_sha256'] or (ROOT/report['source_document_file']).stat().st_size!=4094903 or digest(report['acquisition_file'])!=report['acquisition_sha256'] or report['is_independent_width_measurement'] is not False:
        raise ValueError('Changed supporting SONNE original or width admission')
    expected=copy.deepcopy(source);expected['original_regional_context'].update(audit_file=NGCU_AUDIT,audit_sha256=digest(NGCU_AUDIT))
    if row!=expected:raise ValueError('NGCU size constraint differs from pinned source extraction')

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
