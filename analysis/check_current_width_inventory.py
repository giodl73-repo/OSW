"""Validate scoped width evidence and seasonal-summary provenance."""
import hashlib
import json
import math
import re
from datetime import date
from pathlib import Path
from pyproj import Geod
ROOT = Path(__file__).resolve().parents[1]

def validate(document, ledger):
    if document.get('protocol_file')!='plans/ocean-current-width-measurement-protocol-v1.md' or document.get('protocol_sha256')!=hashlib.sha256((ROOT/'plans/ocean-current-width-measurement-protocol-v1.md').read_bytes()).hexdigest():
        raise ValueError('Stale width measurement protocol')
    decisions = document["current_decisions"]
    ids = {row["id"] for row in ledger["entries"]}
    if len(decisions) != len(ids) or {row["current_id"] for row in decisions} != ids:
        raise ValueError("Incomplete or duplicated width inventory")
    records = document["measurements"]
    if len({row["id"] for row in records}) != len(records):
        raise ValueError("Duplicate width measurement")
    by_id = {row["id"]: row for row in records}
    hydrographic_extraction = None
    for row in records:
        if row.get("original_regional_context") or row["current_id"] in {"algerian", "alaska", "pacific-equatorial-undercurrent", "atlantic-equatorial-undercurrent", "kuroshio-extension", "new-guinea-coastal-undercurrent", "zeehan", "west-australian"}:
            from check_original_regional_widths import validate_row
            validate_row(row)
        if row.get("model_regional_context") or row["current_id"] == "guinea":
            from check_guinea_model_width import validate_row
            validate_row(row)
        if row.get("source_scope_context") or row["current_id"] in {"california","oyashio"}:
            from check_abstract_regional_widths import validate_row
            validate_row(row)
        if row.get('id') == 'norwegian-coastal-saetre-1999-halten-regional-width' or row.get('current_id') == 'norwegian-coastal':
            audit_file = 'research/norwegian-coastal-saetre-1999-regional-width-scope-audit.json'
            path = ROOT / audit_file
            context = row.get('regional_range_context', {})
            if context.get('audit_file') != audit_file or context.get('audit_sha256') != hashlib.sha256(path.read_bytes()).hexdigest():
                raise ValueError('Stale Norwegian coastal regional width audit')
            audit = json.loads(path.read_bytes())
            if {k:v for k,v in row.items() if k != 'regional_range_context'} != audit['measurement'] or {k:v for k,v in context.items() if k not in ['audit_file','audit_sha256']} != audit['regional_range_context']:
                raise ValueError('Norwegian coastal width differs from source range or scope')
        if row["current_id"] not in ids or row["status"] != "editorial_source_extraction_not_canonical" or row["whole_current_representative"] is not False or row["width_rank_eligible"] is not False:
            raise ValueError("Width admission or identity mismatch")
        if row.get("modal_decay_context") or row["current_id"] == "tsushima":
            from check_tsushima_modal_width import validate_row
            validate_row(row)
        value = row["approximate_width_km"]
        span = row['width_range_km']
        if span is not None:
            if not isinstance(span, list) or len(span) != 2 or any(type(v) not in (float, int) or not math.isfinite(v) or v <= 0 for v in span) or span[0] >= span[1] or row.get('is_confidence_interval') is not False or row.get('annual_extrema_eligible') is not False:
                raise ValueError('Invalid width range or temporal inference')
            if row['phase_kind'] == 'climatological_core_distribution':
                if row.get('range_kind') != 'spatial_range_of_climatological_threshold_core_spans' or type(value) not in (float,int) or not math.isfinite(value) or not span[0] <= value <= span[1]:
                    raise ValueError('Invalid spatial core range or median')
            elif row['phase_kind']=='width_time_series_statistics':
                if row.get('range_kind')!='author_reported_minimum_maximum_of_filtered_width_time_series' or type(value) not in (float,int) or not span[0] <= value <= span[1]:
                    raise ValueError('Invalid time-series width statistics range')
            elif row['phase_kind']=='campaign_hydrographic_core':
                if value is not None or row.get('range_kind')!='author_reported_regional_core_width_span':
                    raise ValueError('Invented hydrographic core midpoint or temporal range')
            elif row['phase_kind'] == 'seasonal_mean_width_range':
                if value is not None or row.get('range_kind') != 'author_reported_width_span_of_seasonal_mean_section':
                    raise ValueError('Conflated seasonal mean width span or invented midpoint')
            elif row['phase_kind']=='mean_offshore_extent_range':
                if value is not None or row.get('range_kind')!='author_reported_approximate_offshore_extent_of_mean_surface_flow':
                    raise ValueError('Offshore extent promoted to midpoint or temporal width')
            elif row['phase_kind']=='seasonal_regional_width_range':
                if value is not None or row.get('range_kind')!='author_reported_seasonal_regional_width_scale_span':raise ValueError('Invented seasonal regional width midpoint or annual range')
            elif value is not None or row.get('range_kind') != 'reported_typical_regional_width_span' or row['phase_kind'] != 'regional_summary':
                raise ValueError('Unsupported regional range or invented representative width')
        elif row.get('reported_width_constraint'):
            if row['current_id'] not in {'new-guinea-coastal-undercurrent','west-australian'} or value is not None or span is not None:
                raise ValueError('Unbound size constraint or promoted numeric width')
        elif not isinstance(value, (float, int)) or isinstance(value, bool) or not math.isfinite(value) or value <= 0:
            raise ValueError("Invalid width")
        for key in ["width_metric", "measurement_type", "geographic_scope", "section_orientation", "layer", "time_convention", "boundary_rule", "source_url", "source_citation", "source_locator", "range_interpretation", "source_evidence_kind", "extraction_method"]:
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError(f"Missing width definition: {key}")
        date.fromisoformat(row["source_retrieved_date"])
        if row.get("calendar_months") is not None:
            months = row["calendar_months"]
            if row["phase_kind"] not in {"seasonal_summary", "seasonal_mean_width_range", "monthly_climatological_fit", "seasonal_regional_width_range"} or not isinstance(months, list) or not months or len(set(months)) != len(months) or any(type(month) is not int or not 1 <= month <= 12 for month in months) or not row.get("calendar_source_locator", "").strip():
                raise ValueError("Unsupported seasonal calendar")
        if row.get("source_evidence_kind") == "published_historical_regional_synthesis":
            year = row.get("source_publication_year")
            digest = row.get("source_document_sha256", "")
            if row.get("historical_summary") is not True or type(year) is not int or not 1800 <= year <= date.fromisoformat(row["source_retrieved_date"]).year or row["phase_kind"] != "seasonal_summary" or len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
                raise ValueError("Historical summary provenance mismatch")
        if row["phase_kind"] == "dated_section":
            if row["measurement_type"] != "published_dated_section_span" or row["width_metric"] != "meridional_section_span":
                raise ValueError("Dated section metric mismatch")
            period = row["observed_period"]
            if date.fromisoformat(period["start"]) > date.fromisoformat(period["end"]):
                raise ValueError("Reversed observation dates")
            geometry = row["section_geometry"]
            if geometry["type"] != "LineString" or geometry["crs"] != "OGC:CRS84" or geometry["geometry_role"] != "source_reported_section_limits_not_current_footprint":
                raise ValueError("Section geometry meaning mismatch")
            coordinates = geometry["coordinates"]
            if len(coordinates) != 2 or any(len(point) != 2 or any(not math.isfinite(value) for value in point) or not -180 <= point[0] <= 180 or not -90 <= point[1] <= 90 for point in coordinates) or coordinates[0][0] != coordinates[1][0] or coordinates[0][1] >= coordinates[1][1]:
                raise ValueError("Invalid meridional section")
        elif row['phase_kind'] == 'dated_band_section':
            if row['measurement_type'] != 'published_dated_subsurface_band_span' or row['width_metric'] != 'author_described_subsurface_meridional_band_span':
                raise ValueError('Subsurface band metric mismatch')
            period = row.get('observed_period', {})
            if row.get('time_precision') != 'day' or date.fromisoformat(period['start']) > date.fromisoformat(period['end']):
                raise ValueError('Invalid dated band observation period')
            if any(row.get(key) is not None for key in ['calendar_months', 'section_geometry', 'fixed_layer_bounds_m', 'width_range_km']) or any(row.get(key) is not False for key in ['annual_extrema_eligible', 'seasonal_playback_eligible', 'full_width_inference_eligible', 'is_confidence_interval']):
                raise ValueError('Subsurface band relabeled as full width or seasonal support')
            band = row.get('subsurface_band_context', {})
            limits = band.get('source_reported_latitude_limits_degrees')
            depths = band.get('source_reported_depth_range_m')
            lon = band.get('section_longitude_degrees_east')
            if not isinstance(limits, list) or len(limits) != 2 or any(type(v) not in (float,int) or not math.isfinite(v) for v in limits) or not -90 <= limits[0] < limits[1] <= 90 or type(lon) not in (float,int) or not math.isfinite(lon) or not -180 <= lon <= 180:
                raise ValueError('Invalid subsurface band latitude support')
            if not isinstance(depths, list) or len(depths) != 2 or any(type(v) not in (float,int) or not math.isfinite(v) for v in depths) or not 0 <= depths[0] < depths[1]:
                raise ValueError('Invalid subsurface band depth context')
            if band.get('method') != 'WGS84_meridional_distance_between_reported_latitude_limits' or band.get('rounding_km') != 10 or any(band.get(key) is not False for key in ['span_is_width_at_every_depth', 'paired_velocity_edges_diagnosed', 'depth_range_is_uniform_axis_layer']) or band.get('velocity_boundary_m_s') is not None:
                raise ValueError('Described band converted into diagnosed current edges')
            km = Geod(ellps='WGS84').inv(lon,limits[0],lon,limits[1])[2]/1000
            raw = band.get('unrounded_distance_km')
            if type(raw) not in (float,int) or not math.isfinite(raw) or abs(raw-km) > 1e-6 or value != round(km/10)*10:
                raise ValueError('Subsurface band conversion or rounding mismatch')
        elif row['phase_kind'] == 'climatological_core_distribution':
            if (row['measurement_type'], row['width_metric'], row.get('boundary_sides')) != ('published_climatological_threshold_core_distribution', 'maximum_meridional_extent_of_3d_threshold_core', 'maximum_meridional_extent_of_3d_core') or span is None:
                raise ValueError('Conflated core distribution metric')
            if any(row.get(key) is not None for key in ['observed_period','calendar_months','section_geometry','fixed_layer_bounds_m']) or any(row.get(key) is not False for key in ['annual_extrema_eligible','seasonal_playback_eligible','full_width_inference_eligible','is_confidence_interval']):
                raise ValueError('Invented core dates, layer or annual support')
            core = row.get('core_distribution_context', {})
            expected = {'velocity_component':'zonal_u', 'threshold_operator':'>', 'core_extent_statistic':'maximum_meridional_extent_across_depth_at_each_longitude', 'summary_statistic':'median_across_longitudes', 'range_axis':'longitude', 'averaging_before_boundary_detection':True, 'is_mean_of_instantaneous_widths':False, 'full_width_at_each_depth':False}
            if any(core.get(key) != val or type(core.get(key)) != type(val) for key,val in expected.items()):
                raise ValueError('Core range relabeled as temporal or fixed-depth width')
            threshold = core.get('velocity_threshold_m_s')
            years = core.get('averaging_period_years')
            months = core.get('climatology_months')
            if type(threshold) not in (float,int) or not math.isfinite(threshold) or threshold <= 0 or not isinstance(core.get('product'),str) or not core['product'].strip():
                raise ValueError('Missing threshold-core product or boundary')
            if not isinstance(years,list) or len(years)!=2 or any(type(y) is not int for y in years) or not 1800 <= years[0] <= years[1] <= date.fromisoformat(row['source_retrieved_date']).year:
                raise ValueError('Invalid core climatology years')
            if not isinstance(months,list) or not months or len(set(months)) != len(months) or any(type(m) is not int or not 1 <= m <= 12 for m in months):
                raise ValueError('Invalid core climatology month support')
        elif row['phase_kind'] == 'month_dated_section':
            if row['measurement_type'] != 'published_month_section_angular_span' or row['width_metric'] != 'author_reported_meridional_angular_span' or row.get('boundary_sides') != 'author_reported_section_span':
                raise ValueError('Month section metric mismatch')
            month = row.get('observed_month')
            if not isinstance(month,str) or not re.fullmatch(r'\d{4}-\d{2}',month):
                raise ValueError('Observation month must retain YYYY-MM precision')
            date.fromisoformat(month+'-01')  # Validate month; not an observation day.
            if row.get('time_precision') != 'month' or any(row.get(key) is not None for key in ['observed_period','calendar_months','section_geometry','fixed_layer_bounds_m']) or any(row.get(key) is not False for key in ['annual_extrema_eligible','seasonal_playback_eligible','full_width_inference_eligible','is_confidence_interval']):
                raise ValueError('Invented day, section boundaries, layer or seasonal support')
            conversion=row.get('angular_span_conversion',{})
            span_deg=conversion.get('source_reported_latitude_span_degrees')
            center=conversion.get('source_reported_center_latitude_degrees')
            lon=conversion.get('source_section_longitude_degrees_east')
            limits=conversion.get('source_reported_latitude_limits_degrees')
            if limits is not None:
                if (not isinstance(limits,list) or len(limits)!=2
                        or any(type(v) not in (int,float) or not math.isfinite(v) for v in limits)
                        or not -90<=limits[0]<limits[1]<=90
                        or center is not None
                        or conversion.get('center_role')!='computed_from_reported_limits_for_unit_conversion_only'
                        or row.get('width_metric_label')!='described meridional band span, not fixed-depth full width'
                        or span_deg!=limits[1]-limits[0]):
                    raise ValueError('Reported band limits relabeled as center or fixed-depth width')
                center=conversion.get('normalization_center_latitude_degrees')
                if type(center) not in (int,float) or center!=(limits[0]+limits[1])/2:
                    raise ValueError('Band normalization center mismatch')

            if any(type(v) not in (float,int) or not math.isfinite(v) for v in [span_deg,center,lon]) or span_deg <= 0 or not -180 <= lon <= 180 or not -90 <= center-span_deg/2 < center+span_deg/2 <= 90:
                raise ValueError('Invalid source angular span')
            if conversion.get('method') != 'WGS84_meridional_distance_centered_for_unit_conversion_only' or conversion.get('normalization_limits_are_observed_edges') is not False or conversion.get('rounding_km') != 10:
                raise ValueError('Angular conversion relabeled as observed boundaries')
            km=Geod(ellps='WGS84').inv(lon,center-span_deg/2,lon,center+span_deg/2)[2]/1000
            raw=conversion.get('unrounded_distance_km')
            if type(raw) not in (float,int) or not math.isfinite(raw) or abs(raw-km)>1e-6 or value != round(km/10)*10:
                raise ValueError('Angular span conversion or rounding mismatch')
        elif row['phase_kind'] == 'ensemble_angular_summary':
            if (row['measurement_type'],row['width_metric'],row.get('boundary_sides')) != ('published_ensemble_angular_width_summary','author_reported_ensemble_meridional_scale','author_reported_general_jet_span'):
                raise ValueError('General ensemble angular metric mismatch')
            if any(row.get(key) is not None for key in ['observed_period','calendar_months','section_geometry','fixed_layer_bounds_m','width_range_km']) or any(row.get(key) is not False for key in ['annual_extrema_eligible','seasonal_playback_eligible','full_width_inference_eligible','is_confidence_interval']):
                raise ValueError('General ensemble summary promoted into section or annual dimensions')
            context=row.get('ensemble_angular_context',{})
            expected={'source_claim_id':'rowe-2000-scc-general-two-degree-width','shared_source_claim':True,'independent_jet_measurements':False,'source_reported_latitude_span_degrees':2,'normalization_center_latitude_degrees':0,'normalization_center_role':'unit_conversion_only_not_current_location','source_reported_center_latitude_degrees':None,'source_section_longitude_degrees_east':None,'normalization_limits_are_observed_edges':False,'method':'WGS84_equatorial_meridional_unit_conversion','rounding_km':10}
            if any(context.get(key)!=val or type(context.get(key))!=type(val) for key,val in expected.items()):
                raise ValueError('General angular width scope or conversion altered')
            audit_files={'pacific-north-subsurface-countercurrent':'research/pacific-nscc-reach-layer-section-scope-audit.json','pacific-south-subsurface-countercurrent':'research/pacific-sscc-mean-reach-branch-width-scope-audit.json'}
            if row['current_id'] not in audit_files or context.get('audit_file')!=audit_files[row['current_id']]:
                raise ValueError('General Tsuchiya width assigned to another identity')
            audit_path=ROOT/context['audit_file']
            if context.get('audit_sha256')!=hashlib.sha256(audit_path.read_bytes()).hexdigest():
                raise ValueError('General angular source audit changed; extraction review required')
            audit=json.loads(audit_path.read_text(encoding='utf-8'))
            reported=audit.get('reported_ensemble_angular_width',{})
            if audit['current_id']!=row['current_id'] or reported.get('source_claim_id')!=context['source_claim_id'] or reported.get('latitude_span_degrees')!=2 or reported.get('shared_source_claim') is not True or reported.get('independent_jet_measurements') is not False or reported.get('source_url')!=row['source_url'] or any(reported.get(key) is not False for key in ['core_position_variation_is_width_range','pv_front_width_is_current_width','annual_range_supported']) or any(reported.get(key) is not None for key in ['exact_section_geometry','fixed_depth_bounds_m','observed_period']):
                raise ValueError('General angular extraction disagrees with source scope')
            km=Geod(ellps='WGS84').inv(0,-1,0,1)[2]/1000
            raw=context.get('unrounded_distance_km')
            if type(raw) not in (float,int) or not math.isfinite(raw) or abs(raw-km)>1e-6 or value!=round(km/10)*10:
                raise ValueError('General angular unit conversion mismatch')
        elif row['phase_kind'] == 'ensemble_profile_band':
            if row['measurement_type'] != 'published_composite_coast_distance_flow_band' or row['width_metric'] != 'author_reported_offshore_flow_band_span' or row.get('boundary_sides') != 'reported_coast_distance_band_limits':
                raise ValueError('Composite profile band metric mismatch')
            if any(row.get(key) is not None for key in ['observed_period','calendar_months','section_geometry','fixed_layer_bounds_m','width_range_km']) or any(row.get(key) is not False for key in ['annual_extrema_eligible','seasonal_playback_eligible','full_width_inference_eligible','is_confidence_interval','sampling_windows_are_exact_observation_bounds']):
                raise ValueError('Invented profile geometry, depth, dates or seasonal range')
            profile=row.get('coast_distance_profile',{})
            bounds=profile.get('source_reported_band_limits_km')
            if not isinstance(bounds,list) or len(bounds)!=2 or any(type(v) not in (float,int) or not math.isfinite(v) for v in bounds) or not 0 <= bounds[0] < bounds[1] or value != bounds[1]-bounds[0] or profile.get('span_calculation') != 'farther_minus_nearer_coast_distance' or profile.get('boundary_velocity_threshold_m_s') is not None:
                raise ValueError('Invalid coast distance band')
            overlap=profile.get('cross_shore_overlap_percent')
            if any(type(profile.get(key)) not in (float,int) or not math.isfinite(profile[key]) or profile[key]<=0 for key in ['cross_shore_bin_km','along_shore_bin_km']) or type(overlap) not in (float,int) or not math.isfinite(overlap) or not 0 <= overlap < 100:
                raise ValueError('Invalid profile averaging support')
            windows=row.get('sampling_context_month_windows')
            if not isinstance(windows,list) or not windows:
                raise ValueError('Missing composite sampling context')
            for window in windows:
                for key in ['start','end']:
                    month=window.get(key)
                    if not isinstance(month,str) or not re.fullmatch(r'\d{4}-\d{2}',month):
                        raise ValueError('Composite context must retain month precision')
                    date.fromisoformat(month+'-01')
                if window['start']>window['end']:
                    raise ValueError('Reversed composite context')
            parent=row.get('source_parent_current_id')
            identities={r['id']:r for r in ledger['entries']}
            if not isinstance(row.get('source_current_label'),str) or not row['source_current_label'].strip():
                raise ValueError('Missing source current identity')
            if parent is not None and (parent not in identities or identities[row['current_id']].get('part_of_current_id')!=parent or row.get('segment_assignment_role')!='OSW_editorial_parent_flow_regional_segment_assignment'):
                raise ValueError('Profile segment assignment disagrees with ledger')
            if parent is None and row.get('segment_assignment_role') is not None:
                raise ValueError('Segment assignment requires source parent identity')
        elif row['phase_kind'] == 'seasonal_regional_width_range':
            from check_somali_seasonal_width import validate_row
            validate_row(row)
        elif row['phase_kind'] == 'synoptic_stream_tube_section':
            from check_west_spitsbergen_stream_tubes import validate_row
            validate_row(row)
        elif row['phase_kind'] == 'survey_profile_composite':
            if row['measurement_type'] != 'published_survey_profile_fit_scale' or row['width_metric'] != 'gaussian_e_folding_distance_from_profile_center' or row.get('boundary_sides') != 'fitted_center_to_e_folding_distance':
                raise ValueError('Profile scale is not a paired-boundary width')
            if any(row.get(key) is not False for key in ['full_width_inference_eligible','annual_extrema_eligible','seasonal_playback_eligible','is_confidence_interval','cruise_context_is_composite_sampling_bounds']) or row['observed_period'] is not None or row.get('calendar_months') is not None or row.get('fixed_layer_bounds_m') is not None or row.get('section_geometry') is not None:
                raise ValueError('Unsupported profile composite temporal, layer or boundary inference')
            fit = row.get('profile_fit', {})
            if fit.get('model') != 'gaussian' or fit.get('equation') != 'V(x)=A*exp(-(x/a)^2)' or fit.get('scale_km') != value or fit.get('coordinate_units') != 'km' or fit.get('velocity_units') != 'cm/s' or fit.get('parameter_interpretation') != 'center_to_e_folding_distance' or fit.get('interpretation_origin') != 'OSW_algebraic_inference_from_source_equation':
                raise ValueError('Conflated Gaussian profile parameter')
            amplitude = fit.get('amplitude')
            if type(amplitude) not in (float,int) or not math.isfinite(amplitude) or amplitude <= 0 or type(fit.get('crossing_count')) is not int or fit['crossing_count'] < 2 or any(not isinstance(fit.get(key),str) or not fit[key].strip() for key in ['component','center_definition']):
                raise ValueError('Incomplete composite profile fit support')
            if fit.get('fit_uncertainty_km') is not None:
                raise ValueError('Unsupported profile fit uncertainty')
            period = row['cruise_context_period']
            if date.fromisoformat(period['start']) > date.fromisoformat(period['end']):
                raise ValueError('Reversed cruise context dates')
        elif row['phase_kind']=='survey_layer_median_threshold_width':
            context=row.get('adcp_threshold_context',{})
            audit_file='research/agulhas-return-boebel-2003-adcp-width-scope-audit.json'
            path=ROOT/audit_file
            if context.get('audit_file')!=audit_file or context.get('audit_sha256')!=hashlib.sha256(path.read_bytes()).hexdigest():
                raise ValueError('Stale ADCP threshold width audit')
            audit=json.loads(path.read_bytes())
            actual=dict(row)
            actual['adcp_threshold_context']={k:v for k,v in context.items() if k not in ['audit_file','audit_sha256']}
            expected=next((r for r in audit['measurements'] if r['id']==row['id']),None)
            if actual!=expected:
                raise ValueError('ADCP width differs from source table, error or layer-median support')
        elif row['phase_kind']=='survey_threshold_section':
            if (row['measurement_type'],row['width_metric'],row.get('boundary_sides'))!=('published_relative_velocity_section_span','relative_inner_jet_velocity_threshold_span','paired_relative_velocity_boundaries'):
                raise ValueError('Conflated threshold section metric')
            threshold=row.get('velocity_threshold_fraction')
            if type(threshold) not in (float,int) or not math.isfinite(threshold) or not 0<threshold<1 or not row.get('velocity_reference_statistic','').strip():
                raise ValueError('Invalid section velocity threshold')
            if any(row.get(key) is not None for key in ['observed_period','calendar_months','section_geometry','fixed_layer_bounds_m','width_range_km']) or any(row.get(key) is not False for key in ['annual_extrema_eligible','seasonal_playback_eligible','full_width_inference_eligible','is_confidence_interval','sampling_window_is_exact_section_dates']):
                raise ValueError('Conflated threshold section time or layer')
            window=row.get('campaign_month_window',{})
            if any(not re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])',window.get(key,'')) for key in ['start_month','end_month']) or window['start_month']>window['end_month']:
                raise ValueError('Invalid threshold section campaign window')
        elif row["phase_kind"] in {"ensemble_summary", "survey_summary"}:
            expected = {
                "ensemble_summary": ("published_ensemble_one_sided_span", "core_to_offshore_zero_crossing", "one_sided"),
                "survey_summary": ("published_synoptic_flow_band", "geostrophic_downstream_flow_band", "source_reported_band"),
            }[row["phase_kind"]]
            if (row["measurement_type"], row["width_metric"], row.get("boundary_sides")) != expected or row.get("full_width_inference_eligible") is not False or row["observed_period"] is not None:
                raise ValueError("Conflated boundary or temporal support")
        elif row['phase_kind'] == 'mean_velocity_section':
            if row['measurement_type'] != 'published_mean_section_width' or row['width_metric'] != 'mean_cross_section_zero_crossing_span' or row.get('boundary_sides') != 'paired_mean_zero_contours' or row['observed_period'] is not None or span is not None:
                raise ValueError('Conflated mean-profile width support')
            if any(row.get(key) is not None for key in ['calendar_months','section_geometry','fixed_layer_bounds_m']) or any(row.get(key) is not False for key in ['annual_extrema_eligible','seasonal_playback_eligible','full_width_inference_eligible','is_confidence_interval']):
                raise ValueError('Invented mean-profile geometry or annual range')
            context=row.get('mean_section_context',{})
            if (row['current_id'] in {'north-brazil','guiana'} or context.get('audit_file')=='research/north-brazil-guiana-oblique-mean-width-scope-audit.json') and context.get('section_axis_kind')!='oblique':
                raise ValueError('Oblique source section reclassified as meridional')
            if context.get('velocity_boundary_m_s') != 0 or context.get('averaging_before_boundary_detection') is not True or context.get('is_mean_of_instantaneous_widths') is not False:
                raise ValueError('Unsupported mean-profile boundary convention')
            if context.get('section_axis_kind')=='oblique':
                if context.get('section_longitude_degrees_east') is not None or context.get('section_endpoints_lon_lat') is not None or context.get('rotation_angle_degrees')!=45 or context.get('audit_file')!='research/north-brazil-guiana-oblique-mean-width-scope-audit.json':
                    raise ValueError('Invented oblique section location or convention')
                path=ROOT/context['audit_file']
                if hashlib.sha256(path.read_bytes()).hexdigest()!=context.get('audit_sha256'):
                    raise ValueError('Stale oblique section audit')
                audit=json.loads(path.read_text(encoding='utf-8'))
                matches=[item for item in audit['widths'] if item['section_id']==context.get('section_id')]
                if len(matches)!=1 or any(context.get(key)!=matches[0][source_key] for key,source_key in [('source_flow_label','source_flow_label'),('source_identity_mapping','identity_mapping'),('source_latitude_limits_degrees_north','source_latitude_limits_degrees_north')]) or row['current_id']!=matches[0]['current_id'] or value!=matches[0]['approximate_width_km'] or context.get('averaging_period_months')!=audit['averaging_period_months'] or row['source_url']!=audit['source_url']:
                    raise ValueError('Oblique width differs from pinned source extraction')
            elif type(context.get('section_longitude_degrees_east')) not in (int,float) or not -180 <= context['section_longitude_degrees_east'] <= 180:
                raise ValueError('Unsupported mean-profile section longitude')
            period=context.get('averaging_period_months',{})
            for key in ['start','end']:
                month=period.get(key)
                if not isinstance(month,str) or not re.fullmatch(r'\d{4}-\d{2}',month):
                    raise ValueError('Mean-profile period requires month precision')
                date.fromisoformat(month+'-01')
            if period['start']>period['end']:
                raise ValueError('Reversed mean-profile averaging period')
        elif row['phase_kind'] == 'seasonal_mean_width_range':
            context = row.get('seasonal_mean_context', {})
            months = row.get('calendar_months')
            sampled = context.get('sampled_months')
            years = context.get('sample_years')
            study = context.get('study_years')
            bounds = context.get('pooled_latitude_bounds_degrees')
            latitude = context.get('reference_latitude_degrees')
            cruises = context.get('cruise_ids')
            if (row['measurement_type'] != 'published_seasonal_mean_width_range'
                    or row['width_metric'] != 'author_reported_current_width'
                    or row['observed_period'] is not None or not months
                    or row.get('seasonal_playback_eligible') is not False
                    or context.get('width_of_mean_section') is not True
                    or context.get('mean_of_instantaneous_widths') is not False
                    or context.get('paired_edges_extracted') is not False
                    or context.get('fixed_depth_bounds_m') is not None
                    or row['section_geometry'] is not None):
                raise ValueError('Unsupported seasonal mean width interpretation')
            if (not isinstance(sampled, list) or not sampled
                    or any(type(m) is not int or m not in months for m in sampled)
                    or len(set(sampled)) != len(sampled)
                    or not isinstance(cruises,list) or not cruises
                    or any(not isinstance(c,str) or not c.strip() for c in cruises)
                    or len(set(cruises)) != len(cruises)
                    or not isinstance(years,list) or len(years)!=2
                    or not isinstance(study,list) or len(study)!=2
                    or any(type(y) is not int or not 1800<=y<=date.fromisoformat(row['source_retrieved_date']).year for y in years+study)
                    or not study[0]<=years[0]<=years[1]<=study[1]
                    or not isinstance(bounds,list) or len(bounds)!=2
                    or any(type(v) not in (int,float) or not math.isfinite(v) for v in bounds+[latitude])
                    or not -90<=bounds[0]<=latitude<=bounds[1]<=90
                    or not isinstance(context.get('averaging_rule'),str) or not context['averaging_rule'].strip()):
                raise ValueError('Missing seasonal mean sampling support')
        elif row['phase_kind']=='campaign_hydrographic_core':
            if (row['measurement_type'],row['width_metric'],row.get('boundary_sides'))!=('published_campaign_hydrographic_core_width','half_salinity_contrast_water_mass_core','source_defined_isohaline_core_span'):
                raise ValueError('Hydrographic core relabeled as velocity width')
            if any(row.get(key) is not None for key in ['observed_period','calendar_months','section_geometry','fixed_layer_bounds_m']) or any(row.get(key) is not False for key in ['annual_extrema_eligible','seasonal_playback_eligible','full_width_inference_eligible','is_confidence_interval','sampling_window_is_exact_section_dates']):
                raise ValueError('Invented hydrographic geometry, depth or annual support')
            context=row.get('hydrographic_core_context',{})
            if context.get('boundary_equation')!='S_boundary=(S_core_max+S_environment)/2' or context.get('velocity_threshold_m_s') is not None or context.get('variation_axis')!='section_location_and_occupation_not_annual_cycle' or context.get('audit_file')!='research/persian-gulf-gogp99-core-scope-audit.json':
                raise ValueError('Hydrographic core boundary or provenance mismatch')
            path=ROOT/context['audit_file']
            if hashlib.sha256(path.read_bytes()).hexdigest()!=context.get('audit_sha256'):raise ValueError('Changed hydrographic scope audit; re-extract widths')
            audit=json.loads(path.read_text(encoding='utf-8'))
            matches=[r for r in audit['reported_local_core_widths'] if r['sections']==context.get('section_ids')]
            if len(matches)!=1 or matches[0]['approximate_width_km']!=value or matches[0]['width_range_km']!=span or row['current_id']!=audit['current_id']:
                raise ValueError('Hydrographic width differs from pinned source extraction')
        elif row['phase_kind']=='stream_mean_threshold_summary':
            if row['current_id']!='kuroshio' or (row['measurement_type'],row['width_metric'])!=('published_stream_mean_threshold_width','mean_of_diagnosed_cross_stream_threshold_spans'):
                raise ValueError('Stream mean width metric mismatch')
            if any(row.get(key) is not None for key in ['observed_period','calendar_months','section_geometry','fixed_layer_bounds_m','width_range_km']) or any(row.get(key) is not False for key in ['annual_extrema_eligible','seasonal_playback_eligible','full_width_inference_eligible','is_confidence_interval']):
                raise ValueError('Stream mean promoted into geometry, annual range or occupied dates')
            context=row.get('stream_mean_context',{})
            expected={'velocity_threshold_m_s':.1,'velocity_component':'along_stream_parallel_to_diagnosed_axis','section_orientation':'normal_to_diagnosed_jet_axis','study_period_years':[1993,2008],'boundary_detection_precedes_averaging':True,'width_of_mean_velocity_field':False,'averaging_weight_detail_resolved':False,'season_month_membership_resolved':False,'paired_edges_extracted':False,'isobath_is_measurement_layer':False,'intrusive_reach_is_mainstream_width':False}
            if any(context.get(key)!=value or type(context.get(key))!=type(value) for key,value in expected.items()):
                raise ValueError('Changed stream mean threshold, averaging or support')
            audit_path=ROOT/'research/kuroshio-liu-gan-2012-stream-mean-width-scope-audit.json'
            if context.get('audit_file')!=audit_path.relative_to(ROOT).as_posix() or context.get('audit_sha256')!=hashlib.sha256(audit_path.read_bytes()).hexdigest():
                raise ValueError('Unpinned stream mean scope audit')
            audit=json.loads(audit_path.read_text(encoding='utf-8'))
            pdf=ROOT/audit['source_pdf_file']
            if context.get('source_pdf_sha256')!=audit['source_pdf_sha256'] or hashlib.sha256(pdf.read_bytes()).hexdigest()!=audit['source_pdf_sha256']:
                raise ValueError('Unpinned stream mean source PDF')
            matches=[m for m in audit['values'] if m['id']==row['id']]
            if len(matches)!=1:
                raise ValueError('Stream mean source claim missing')
            source=matches[0]
            if any(row.get(key)!=source[key] for key in ['phase_label','approximate_width_km','source_locator']) or any(context.get(key)!=source[key] for key in ['season','temporal_statistic']) or row['source_url']!=audit['source_url'] or row['boundary_rule']!=audit['boundary_definition']:
                raise ValueError('Stream mean value, time or source mismatch')
        elif row['phase_kind']=='monthly_climatological_fit':
            if row['current_id']!='leeuwin' or (row['measurement_type'],row['width_metric'])!=('published_monthly_mean_fitted_width','source_fitted_cross_flow_width') or span is not None:
                raise ValueError('Conflated monthly fitted width')
            if any(row.get(key) is not None for key in ['observed_period','section_geometry','fixed_layer_bounds_m']) or any(row.get(key) is not False for key in ['full_width_inference_eligible','annual_extrema_eligible','seasonal_playback_eligible','is_confidence_interval']):
                raise ValueError('Promoted incomplete monthly fit evidence')
            context=row.get('monthly_fit_context',{})
            if context.get('audit_file')!='research/leeuwin-deng-2008-monthly-fitted-width-scope-audit.json' or context.get('track_id')!='a101' or context.get('source_width_coefficient')!=1.89 or context.get('track_angle_degrees')!=43.45:
                raise ValueError('Changed fitted width convention')
            if any(context.get(key) is not False for key in ['mean_width_is_width_of_mean_profile','exact_combined_averaging_period_resolved','complete_monthly_curve_extracted','transport_layer_is_width_measurement_layer','rms_is_confidence_interval']):
                raise ValueError('Conflated monthly fit scope')
            path=ROOT/context['audit_file']
            if hashlib.sha256(path.read_bytes()).hexdigest()!=context.get('audit_sha256'):
                raise ValueError('Stale monthly fit audit')
            audit=json.loads(path.read_text(encoding='utf-8'))
            if hashlib.sha256((ROOT/audit['source_pdf_file']).read_bytes()).hexdigest()!=context.get('source_pdf_sha256') or context['source_pdf_sha256']!=audit['source_pdf_sha256']:
                raise ValueError('Changed monthly fit source PDF')
            matches=[item for item in audit['monthly_values'] if item['month']==context.get('calendar_month')]
            if len(matches)!=1 or value!=matches[0]['approximate_width_km'] or row['calendar_months']!=[matches[0]['month']] or row['source_url']!=audit['source_url'] or row['source_locator']!=audit['source_locator']:
                raise ValueError('Monthly fit differs from pinned extraction')
        elif row['phase_kind'] == 'width_time_series_statistics':
            if (row['measurement_type'],row['width_metric'],row.get('boundary_sides')) != ('published_filtered_width_time_series_statistics','paired_half_core_speed_jet_coordinate_span','paired_half_core_speed_edges') or span is None:
                raise ValueError('Conflated filtered time-series width metric')
            if any(row.get(key) is not None for key in ['observed_period','calendar_months','section_geometry','fixed_layer_bounds_m']) or any(row.get(key) is not False for key in ['full_width_inference_eligible','annual_extrema_eligible','seasonal_playback_eligible','is_confidence_interval']):
                raise ValueError('Invented width statistics geometry, layer or annual support')
            context=row.get('width_statistics_context',{})
            audit_file='research/florida-hf-radar-width-statistics-scope-audit.json'
            if context.get('audit_file')!=audit_file or row['current_id']!='florida':raise ValueError('Width statistics identity mismatch')
            path=ROOT/audit_file
            if context.get('audit_sha256')!=hashlib.sha256(path.read_bytes()).hexdigest():raise ValueError('Stale width statistics audit')
            audit=json.loads(path.read_bytes())
            keys=['section_latitude_degrees_north','sample_period_years','nominal_measurement_depth_m','native_grid_spacing_km','native_sampling_interval_minutes','diagnostic_time_filter','velocity_component','velocity_threshold_fraction','reported_statistics','seasonal_context','boundary_coordinates_extracted']
            if any(context.get(key)!=audit[key] or type(context.get(key))!=type(audit[key]) for key in keys):raise ValueError('Width statistics context differs from source')
            statistics=context['reported_statistics']
            if (value,span,row['source_url'],row['source_locator'],row['boundary_rule'],row['range_kind']) != (statistics['mean_km'],[statistics['minimum_km'],statistics['maximum_km']],audit['source_url'],audit['source_locator'],audit['boundary_rule'],audit['range_kind']):
                raise ValueError('Width statistics differ from pinned extraction')
        elif row['phase_kind'] == 'eulerian_mean_section_span':
            if (row['measurement_type'],row['width_metric'],row.get('boundary_sides')) != ('published_eulerian_mean_section_span','coast_to_author_reported_mean_zero_isotach','coast_to_mean_zero_isotach') or span is not None:
                raise ValueError('Conflated Eulerian mean section boundary')
            if any(row.get(key) is not None for key in ['observed_period','calendar_months','section_geometry','fixed_layer_bounds_m']) or any(row.get(key) is not False for key in ['full_width_inference_eligible','annual_extrema_eligible','seasonal_playback_eligible','is_confidence_interval']):
                raise ValueError('Invented Eulerian mean section support')
            context=row.get('eulerian_section_context',{})
            audit_file='research/agulhas-act-mean-section-width-scope-audit.json'
            if context.get('audit_file') != audit_file or row['current_id'] != 'agulhas':
                raise ValueError('Eulerian mean section provenance mismatch')
            path=ROOT/audit_file
            if hashlib.sha256(path.read_bytes()).hexdigest()!=context.get('audit_sha256'):
                raise ValueError('Stale Eulerian mean section audit')
            audit=json.loads(path.read_text(encoding='utf-8'))
            for key in ['section_id','section_latitude_degrees_north_approx','averaging_period_months','reported_depth_extent_m','reported_depth_extent_is_fixed_measurement_layer']:
                if context.get(key)!=audit[key]:raise ValueError('Eulerian section context differs from source audit')
            if any(context.get(key) is not False for key in ['boundary_coordinates_extracted','instantaneous_moving_boundary_series_extracted','reported_depth_extent_is_fixed_measurement_layer']):
                raise ValueError('Invented Eulerian boundary extraction or layer')
            if (row['current_id'],value,row['source_url'],row['source_locator'],row['boundary_rule']) != (audit['current_id'],audit['reported_width_km_approx'],audit['source_url'],audit['source_locator'],audit['boundary_rule']):
                raise ValueError('Eulerian span differs from pinned source extraction')
        elif row['phase_kind'] == 'inverse_hydrographic_section_span':
            from build_atlantic_cruise_widths import build, OUTPUT
            if hydrographic_extraction is None:
                hydrographic_extraction = build()
                if json.loads((ROOT / OUTPUT).read_bytes()) != hydrographic_extraction:
                    raise ValueError('Changed Atlantic cruise extraction; source review required')
            expected = next((r for r in hydrographic_extraction['measurements'] if r['id'] == row['id']), None)
            actual = {k:v for k,v in row.items() if k not in ['extraction_file', 'extraction_sha256']}
            if (expected is None or actual != expected or row.get('extraction_file') != OUTPUT
                    or row.get('extraction_sha256') != hashlib.sha256((ROOT / OUTPUT).read_bytes()).hexdigest()):
                raise ValueError('Cruise span differs from pinned publisher cells or scope')
        elif row['phase_kind']=='mean_offshore_extent_range':
            context=row.get('mean_offshore_context',{})
            audit_file='research/mindanao-schonau-2015-mean-offshore-extent-scope-audit.json'
            path=ROOT/audit_file
            if context.get('audit_file')!=audit_file or context.get('audit_sha256')!=hashlib.sha256(path.read_bytes()).hexdigest():
                raise ValueError('Stale mean offshore extent audit')
            audit=json.loads(path.read_bytes())
            actual={k:v for k,v in row.items() if k!='mean_offshore_context'}
            actual_context={k:v for k,v in context.items() if k not in ['audit_file','audit_sha256']}
            if actual!=audit['measurement'] or actual_context!=audit['mean_offshore_context']:
                raise ValueError('Mean offshore extent differs from source description or sampling support')
        elif row['phase_kind'] == 'regional_scalar_summary':
            if (row['measurement_type'],row['width_metric']) != ('published_regional_scalar_width_summary','author_reported_regional_current_scale') or span is not None:
                raise ValueError('Conflated regional scalar width')
            if any(row.get(key) is not None for key in ['observed_period','calendar_months','section_geometry','fixed_layer_bounds_m']):
                raise ValueError('Invented regional scalar observation support')
            if any(row.get(key) is not False for key in ['full_width_inference_eligible','annual_extrema_eligible','seasonal_playback_eligible','is_confidence_interval']):
                raise ValueError('Promoted regional scalar width')
            context=row.get('regional_scalar_context',{})
            audits={'oyashio':'research/oyashio-2005-abstract-width-scope-audit.json','alaska-coastal-gulf':'research/alaska-coastal-gulf-jarosz-2017-regional-width-scope-audit.json','labrador':'research/labrador-thompson-2009-regional-width-scope-audit.json','east-australian':'research/east-australian-imos-regional-width-scope-audit.json'}
            if context.get('boundary_coordinates_supplied') is not False or context.get('bathymetry_is_measurement_layer') is not False or context.get('audit_file')!=audits.get(row['current_id']) or row['current_id'] not in audits:
                raise ValueError('Regional scalar provenance mismatch')
            if row['current_id']=='east-australian' and context.get('reported_depth_extent_is_fixed_measurement_layer') is not False:
                raise ValueError('Regional extent promoted to fixed measurement layer')
            path=ROOT/context['audit_file']
            if hashlib.sha256(path.read_bytes()).hexdigest()!=context.get('audit_sha256'):
                raise ValueError('Stale regional scalar audit')
            audit=json.loads(path.read_text(encoding='utf-8'))
            if (row['current_id'],value,row['source_url'],row['source_locator'],row['boundary_rule'])!=(audit['current_id'],audit['reported_width_km_approx'],audit['source_url'],audit['source_locator'],audit['boundary_rule']):
                raise ValueError('Regional scalar differs from pinned source extraction')
        elif row['phase_kind'] == 'model_regional_width_summary':
            from check_guinea_model_width import validate_row
            validate_row(row)
        elif row['phase_kind'] == 'campaign_modal_decay_width':
            from check_tsushima_modal_width import validate_row
            validate_row(row)
        elif row['phase_kind'] == 'regional_summary':
            if row['measurement_type'] != 'published_regional_summary' or row['width_metric'] != 'author_reported_current_width' or row['observed_period'] is not None or row.get('calendar_months') is not None or (span is None and not row.get('original_regional_context')):
                raise ValueError('Conflated regional range support')
            if row.get('regional_range_context') and row['current_id'] not in {'black-sea-rim','norwegian-coastal'}:
                raise ValueError('Regional range source owner mismatch')
            if row['current_id'] == 'black-sea-rim':
                context = row.get('regional_range_context', {})
                audit_file = 'research/black-sea-rim-korotaev-2011-width-scope-audit.json'
                path = ROOT / audit_file
                if context.get('audit_file') != audit_file or context.get('audit_sha256') != hashlib.sha256(path.read_bytes()).hexdigest():
                    raise ValueError('Stale Black Sea regional range audit')
                audit = json.loads(path.read_bytes())
                source = ROOT / audit['source_document_file']
                if len(source.read_bytes()) != audit['source_document_bytes'] or hashlib.sha256(source.read_bytes()).hexdigest() != audit['source_document_sha256']:
                    raise ValueError('Changed Black Sea primary source')
                if (span, row['source_url'], row['source_locator'], row['boundary_rule']) != (audit['reported_width_range_km'], audit['source_url'], audit['source_locator'], audit['boundary_rule']):
                    raise ValueError('Black Sea range differs from primary-source extraction')
                if any(row.get(key) is not None for key in ['section_geometry','fixed_layer_bounds_m']) or any(row.get(key) is not False for key in ['full_width_inference_eligible','seasonal_playback_eligible']):
                    raise ValueError('Regional Black Sea range promoted to mapped or seasonal width')
                if context.get('pycnocline_is_measurement_layer') is not False or context.get('boundary_coordinates_supplied') is not False:
                    raise ValueError('Invented Black Sea range boundaries or layer')
        elif row["phase_kind"] != "seasonal_summary" or row["measurement_type"] != "published_regional_seasonal_summary" or row["observed_period"] is not None:
            raise ValueError("Unsupported or conflated temporal evidence")
    reviews = document.get('review_assessments', [])
    if len({row['current_id'] for row in reviews}) != len(reviews):
        raise ValueError('Duplicate width source-review identity')
    for review in reviews:
        if review['current_id'] not in ids or review['decision'] != 'sources_reviewed_no_comparable_numeric_current_width' or review['whole_current_width_km'] is not None or review['annual_width_range_km'] is not None or not review['reason'].strip() or not review['evidence']:
            raise ValueError('Unsupported source-review width admission')
        date.fromisoformat(review['source_retrieved_date'])
        if any(not evidence.get(key, '').strip() for evidence in review['evidence'] for key in ['url', 'citation', 'locator', 'supports']):
            raise ValueError('Missing width source-review evidence')
    states = {"section_span_diagnostic_present_width_unresolved", "scoped_width_evidence_present", "existing_width_mention_requires_source_review", "width_not_assessed", "derived_width_candidate_requires_review", "sources_reviewed_no_comparable_numeric_current_width"}
    derived = document.get('derived_width_series_candidates', [])
    if len({row['current_id'] for row in derived}) != len(derived):
        raise ValueError('Duplicate derived width identity')
    for candidate in derived:
        path = ROOT / candidate['file']
        if hashlib.sha256(path.read_bytes()).hexdigest() != candidate['sha256']:
            raise ValueError('Changed derived width candidate')
        series = json.loads(path.read_text(encoding='utf-8'))
        if series['current_id'] != candidate['current_id'] or series['status'] != 'derived_width_candidate_requires_scientific_review' or series['whole_current_representative'] is not False:
            raise ValueError('Invalid derived width admission')
    spans = document.get('section_span_diagnostics', [])
    if len({row['current_id'] for row in spans}) != len(spans):
        raise ValueError('Duplicate section-span identity')
    for diagnostic in spans:
        if diagnostic['current_id'] != 'loop' or diagnostic['status'] != 'local_component_section_diagnostic_requires_scientific_review' or diagnostic['metric'] != 'zonal_half_peak_northward_velocity_section_span':
            raise ValueError('Invalid component section-span classification')
        if diagnostic['whole_current_width_km'] is not None or diagnostic['annual_width_range_km'] is not None or diagnostic['width_rank_eligible'] is not False or diagnostic['annual_extrema_eligible'] is not False:
            raise ValueError('Component section span promoted to current width')
        expected_files = {'research/loop-current-noaa-section-spans.json', 'research/loop-current-adt-section-spans.json'}
        if len(diagnostic['sources']) != 2 or {source['file'] for source in diagnostic['sources']} != expected_files:
            raise ValueError('Incomplete component section-span sources')
        for source in diagnostic['sources']:
            path = ROOT / source['file']
            if hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
                raise ValueError('Changed component section-span source')
            series = json.loads(path.read_text(encoding='utf-8'))
            if series['current_id'] != diagnostic['current_id'] or series['status'] != diagnostic['status'] or series['metric'] != diagnostic['metric'] or series['whole_current_representative'] is not False:
                raise ValueError('Invalid component section-span source')
    for note in document.get("comparability_notes", []):
        if note["current_id"] not in ids or note["seasonal_playback_eligible"] is not False or not note["reason"].strip():
            raise ValueError("Invalid comparability restriction")
    for row in decisions:
        expected = {record["id"] for record in records if record["current_id"] == row["current_id"]}
        if set(row["measurement_ids"]) != expected or row["whole_current_width_km"] is not None or row["width_decision"] not in states or bool(expected) != (row["width_decision"] == "scoped_width_evidence_present"):
            raise ValueError("Width decision mismatch")
        if (row['width_decision'] == 'section_span_diagnostic_present_width_unresolved') != any(span['current_id'] == row['current_id'] for span in spans):
            raise ValueError('Section-span decision mismatch')
        if (row['width_decision'] == 'derived_width_candidate_requires_review') != any(candidate['current_id'] == row['current_id'] for candidate in derived):
            raise ValueError('Derived width decision mismatch')
        if (row['width_decision'] == 'sources_reviewed_no_comparable_numeric_current_width') != any(review['current_id'] == row['current_id'] for review in reviews):
            raise ValueError('Width source-review decision mismatch')
    for summary in document["seasonal_summaries"]:
        members = [by_id[identifier] for identifier in summary["measurement_ids"]]
        if len(members) < 2 or any(row["current_id"] != summary["current_id"] or row["phase_kind"] != "seasonal_summary" for row in members) or len({row["phase_label"] for row in members}) != len(members) or len({row["width_metric"] for row in members}) != 1:
            raise ValueError("Incompatible seasonal identities")
        if summary["range_kind"] != "span_of_reported_seasonal_typical_values" or summary["reported_seasonal_value_span_km"] != [min(row["approximate_width_km"] for row in members), max(row["approximate_width_km"] for row in members)]:
            raise ValueError("Seasonal span mismatch")
    counts = {"currents": len(ids), "currents_with_scoped_width_evidence": len({row["current_id"] for row in records}), "measurements": len(records), "currents_with_existing_mentions_pending_review": sum(row["width_decision"] == "existing_width_mention_requires_source_review" for row in decisions), "currents_not_assessed": sum(row["width_decision"] == "width_not_assessed" for row in decisions)}
    counts['currents_with_section_span_diagnostics_width_unresolved'] = len(spans)
    counts['currents_with_derived_width_candidates_pending_review'] = len(derived)
    counts['currents_with_sources_reviewed_no_numeric_width'] = len(reviews)
    if counts != document["counts"]:
        raise ValueError("Width coverage counts mismatch")

def main():
    path = ROOT / "research/ocean-current-width-inventory.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    ledger_path = ROOT / "research/ocean-current-almanac.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    validate(document, ledger)
    for key, target in [("current_ledger_sha256", ledger_path), ("protocol_sha256", ROOT / document["protocol_file"])]:
        if hashlib.sha256(target.read_bytes()).hexdigest() != document[key]:
            raise ValueError("Stale width provenance")
    print(f"OK: width inventory; {len(document['current_decisions'])} names, {len(document['measurements'])} scoped records")

if __name__ == "__main__":
    main()
