"""Small retained JSON only: no engine, index or ocean-field processing."""
import calendar
import csv
from datetime import date,datetime
import hashlib
import io
import json
import math
from pathlib import Path
from eddy_map_spans_v1 import validate_map_case,span_interval
from eddy_audit_spans_v1 import validate_case as validate_audit_span_case,spans as audit_spans
from eddy_cartographic_circle_spans_v1 import validate_record as validate_cartographic_record, validate_ssh_record as validate_laura_ssh_record, spans as cartographic_spans
from eddy_author_animation_patch_v1 import validate_record as validate_author_patch_record, spans as author_patch_spans
from eddy_colour_spans_v1 import validate_case as validate_colour_span_case,spans as colour_spans
from eddy_arrow_spans_v1 import validate_case as validate_arrow_span_case
from eddy_pdf_line_spans_v1 import validate_case as validate_pdf_line_case
from eddy_height_profiles_v1 import validate_case as validate_height_case, span as height_span, peak as height_peak
from eddy_scale_bar_spans_v1 import validate_case as validate_scale_bar_case, spans as scale_bar_spans
from eddy_visible_model_front_v1 import validate_case as validate_visible_front_case, span as visible_front_span
from eddy_gridded_case_summary_v1 import summarize as gridded_case_summary
from eddy_speed_core_summary_v1 import summarize as speed_core_summary
from eddy_frontal_lobe_spans_v1 import summarize as frontal_lobe_summary
from eddy_named_frontal_chart_spans_v1 import summarize as named_frontal_chart_summary
from eddy_operational_chart_spans_v1 import validate_case as validate_operational_chart_case, spans as operational_chart_spans
from eddy_source_bold_isoline_spans_v1 import validate_case as validate_source_isoline_case, spans as source_isoline_spans

ROOT=Path(__file__).resolve().parents[1]
JSON_PATH='research/eddy-measurement-register-v1.json'
CSV_PATH='research/eddy-measurement-register-v1.csv'
RULES='plans/eddy-measurement-register-v1.md'


def pointer(document,path):
    value=document
    for token in path.strip('/').split('/'):
        token=token.replace('~1','/').replace('~0','~')
        value=value[int(token)] if isinstance(value,list) else value[token]
    return value


def registry_date_bounds(text):
    if len(text.split('/'))==3:
        value=datetime.strptime(text,'%m/%d/%Y').date()
        return value,value,'day'
    month,year=map(int,text.split('/'))
    return date(year,month,1),date(year,month,calendar.monthrange(year,month)[1]),'month'


def validate_plot_estimate(plot,interval):
    columns=plot['column_y_extents'];roi=plot['roi_xyxy_inclusive'];axis=plot['axis_calibration']
    assert len(columns)==plot['selected_columns']>20
    assert [c[0] for c in columns]==sorted({c[0] for c in columns})
    assert all(roi[0]<=x<=roi[2] and roi[1]<=lo<=hi<=roi[3] for x,lo,hi in columns)
    assert plot['first_last_x_pixel']==[columns[0][0],columns[-1][0]]
    lo=min(c[1] for c in columns);hi=max(c[2] for c in columns)
    assert plot['trace_y_extrema']==[lo,hi] and roi[1]<lo<=hi<roi[3]
    assert axis['zero_y_pixel']>axis['tick_y_pixel'] and axis['tick_value_km']>0
    scale=axis['tick_value_km']/(axis['zero_y_pixel']-axis['tick_y_pixel'])
    assert math.isclose(scale,axis['km_per_pixel'],abs_tol=1e-9)
    native=[(axis['zero_y_pixel']-hi)*scale,(axis['zero_y_pixel']-lo)*scale]
    assert all(math.isclose(a,b,abs_tol=1e-9) for a,b in zip(native,plot['unrounded_trace_range_km']))
    assert plot['reading_allowance_km']==5 and plot['round_outward_to_km']==10
    assert interval==plot['range_km']==[max(0,math.floor((native[0]-5)/10)*10),math.ceil((native[1]+5)/10)*10]
    days=[(x-axis['day_zero_x_pixel'])*100/(axis['day_100_x_pixel']-axis['day_zero_x_pixel']) for x in plot['first_last_x_pixel']]
    assert all(math.isclose(a,b,abs_tol=1e-9) for a,b in zip(days,plot['approximate_plot_day_support']))


def validate_numeric_interval(row):
    interval=row['range_value']
    assert row['value'] is None and len(interval)==2
    assert all(type(v) in (int,float) and math.isfinite(v) for v in interval)
    assert interval[0]<=interval[1]
    signed_metric='source_reported_signed_westward_translation_component_range'
    signed_kind='source_reported_signed_westward_translation_component_interval'
    if row.get('metric')==signed_metric or row.get('range_kind')==signed_kind:
        assert row['metric']==signed_metric and row['range_kind']==signed_kind
        assert row['category']=='kinematics' and row['unit']=='km/day'
        assert row['detection_context']['translation_component_positive_direction']=='westward'
    else:assert 0<=interval[0] and interval[1]>0


def validate_gridded_case(row, report=None):
    c=row['calculation'];report=report if report is not None else json.loads((ROOT/c['report_file']).read_bytes())
    assert c['report_sha256']==hashlib.sha256((ROOT/c['report_file']).read_bytes()).hexdigest()
    assert report['summarizer_sha256']==hashlib.sha256((ROOT/'analysis/eddy_gridded_case_summary_v1.py').read_bytes()).hexdigest()
    assert report['operator_sha256']==hashlib.sha256((ROOT/'analysis/eddy_altimetry_contours_v1.py').read_bytes()).hexdigest()
    summary=gridded_case_summary(report,c['component'])
    assert all(c[k]==v for k,v in summary.items())
    assert row['entity_id']==report['case']['owner_id']
    assert row['period_start']==row['period_end']==report['case']['date']
    assert row['metric']==summary['metric'] and row['unit']==summary['unit']
    assert row['range_value']==summary['range_value'] and row['value'] is None and row['category']=='size'
    assert row['range_kind']=='gridded_contour_method_sensitivity_not_measurement_uncertainty'
    assert row['evidence_role']=='qualified_osw_gridded_source_case_reference' and row['rights_screened_release_eligible'] is False


def validate_named_frontal_chart_reference(row,report):
    c=row['calculation'];summary=named_frontal_chart_summary(report,c['component'])
    assert all(c[k]==v for k,v in summary.items())
    assert row['entity_id']==report['case']['owner_id']
    assert row['metric']=='source_named_frontal_chart_'+c['component']+'_span'
    assert row['category']=='size' and row['unit']=='km' and row['value'] is None
    assert row['range_value']==summary['range_km']
    assert [row['period_start'],row['period_end']]==summary['source_week']
    assert row['period_precision']=='source_chart_data_week_not_simultaneous_observation'
    assert row['range_kind']=='manual_frontal_chart_reading_sensitivity_not_physical_uncertainty'
    assert row['evidence_role']=='map_read_named_case_reference' and row['rights_screened_release_eligible'] is False
    assert row.get('source_map_estimate') is None and row.get('depth_m') is None


def validate_frontal_lobe_reference(row,report):
    c=row['calculation'];summary=frontal_lobe_summary(report,c['component'])
    assert all(c[k]==v for k,v in summary.items())
    assert row['entity_id']==report['case']['owner_id']
    assert row['metric']=='source_chart_pre_detachment_frontal_lobe_'+c['component']+'_span'
    assert row['category']=='size' and row['unit']=='km' and row['value'] is None
    assert row['range_value']==summary['range_km']
    assert [row['period_start'],row['period_end']]==summary['source_week']
    assert row['period_precision']=='source_chart_week_not_simultaneous_observation'
    assert row['range_kind']=='manual_landmark_reading_sensitivity_not_physical_uncertainty'
    assert row['evidence_role']=='map_read_named_case_reference' and row['rights_screened_release_eligible'] is False
    assert row.get('source_map_estimate') is None and row.get('depth_m') is None


def validate_speed_core_reference(row,report):
    c=row['calculation'];summary=speed_core_summary(report,row['entity_id'],c['component'])
    assert all(c[k]==v for k,v in summary.items())
    assert row['metric']==summary['metric'] and row['unit']==summary['unit'] and row['range_value']==summary['range_value']
    assert row['value'] is None and row['period_start']==row['period_end']==summary['date']
    assert row['category']==('kinematics' if c['component']=='speed' else 'size')
    assert row['range_kind']=='level_step_comparison_and_outward_rounding_not_physical_uncertainty'
    assert row['evidence_role']=='qualified_osw_speed_core_source_case_reference' and row['rights_screened_release_eligible'] is False
    assert row.get('depth_m') is None and row.get('source_map_estimate') is None
    a=report['case_associations'][row['entity_id']]
    cases=[v for v in report['cloud_review']['result']['cases'] if v['source_name']==a['source_name'] and v['date']==a['date']]
    assert len(cases)==1 and cases[0]['source_point_role']==a['source_point_role']


def validate_model_event_contrast(row):
    c=row['model_context']
    assert c['method']=='source_reported_model_event_date_contrast'
    assert row['entity_id']=='eddy:horizon:loop-80-primary' and c['source_case_name']=='Edison'
    assert row['metric']=='source_model_counterfactual_shedding_date_difference' and row['category']=='duration' and row['unit']=='day'
    assert row['evidence_role']=='qualified_indexed_model_case_reference' and row['rights_screened_release_eligible'] is False
    expected={'No-Hurricane':('2024-10-16','Helene and Milton',6),'No-Helene':('2024-10-11','Helene only',1),'No-Milton':('2024-10-11','Milton only',1)}
    event,removed,days=expected[c['experiment']]
    assert c['control_experiment']=='Control' and c['model']=='CNAPS2-derived regional ocean model'
    assert c['control_event_date']==c['registry_initial_separation']==row['period_start']=='2024-10-10'
    assert c['counterfactual_event_date']==row['period_end']==event and c['removed_hurricanes']==removed
    assert c['calendar_day_difference']==row['value']==days==(date.fromisoformat(event)-date(2024,10,10)).days
    assert c['calculation']=='counterfactual_calendar_date_minus_control_calendar_date'
    assert c['comparison_is_between_simulated_worlds'] is True and c['preprint_not_peer_reviewed'] is True
    assert row['period_precision']=='reported_model_calendar_day'
    assert all(c[k] is False for k in ['observed_lifetime_inferred','observed_causal_effect_inferred','physical_crosswalk_verified','contrasts_are_additive','raw_model_fields_acquired','source_figure_pixels_reviewed'])


def validate_nautilus_calendar_reference(row):
    c=row['calendar_support'];a=row['independent_named_case']
    assert row['entity_id']=='eddy:horizon:loop-63-secondary' and row['category']=='duration' and row['unit']=='day'
    assert row['metric']=='source_narrative_formation_to_dissipation_calendar_span' and row['value'] is None
    assert row['period_start'] is None and row['period_end'] is None and row['period_precision']=='month_to_two_possible_months'
    assert row['range_kind']=='source_month_precision_calendar_bounds_not_measured_lifespan'
    assert row['evidence_role']=='qualified_published_named_case_reference' and row['rights_screened_release_eligible'] is False
    assert c['method']=='source_narrative_nautilus_ii_calendar_span'
    assert (c['start_month'],c['end_month_min'],c['end_month_max'])==('2015-05','2015-12','2016-01')
    assert (c['start_precision'],c['end_precision'])==('month','two_possible_months') and c['chronology_conditioned'] is False
    def bounds(month):
        year,number=map(int,month.split('-'));return date(year,number,1),date(year,number,calendar.monthrange(year,number)[1])
    start_min,start_max=bounds(c['start_month']);end_min,_=bounds(c['end_month_min']);_,end_max=bounds(c['end_month_max'])
    assert [c[k] for k in ['start_date_min','start_date_max','end_date_min','end_date_max']]==[v.isoformat() for v in [start_min,start_max,end_min,end_max]]
    assert row['range_value']==c['unconditioned_elapsed_day_range']==[(end_min-start_max).days,(end_max-start_min).days]
    assert a['method']=='source_narrative_secondary_calendar_case' and a['source_name']=='Nautilus II' and a['source_year']==2015
    assert a['source_formation_label']=='May 2015' and a['source_dissipation_label']=='between December 2015 and January 2016'
    assert a['source_narrative_reconnections_to']=='Nautilus'
    assert all(a[k] is False for k in ['association_is_verified','primary_values_inherited','exact_split_event_identified','continuous_identity_across_reconnections_verified','whole_physical_lifetime_verified','shared_figure_contour_is_child_boundary','parent_registry_dates_used'])
    assert row.get('depth_m') is None and row.get('source_map_estimate') is None


def validate_wilde_provisional_map(row,case):
    validate_map_case(case)
    assert row['entity_id']==case['owner_id']=='eddy:horizon:loop-72-primary' and case['source_name']=='Wilde'
    assert row['category']=='size' and row['unit']=='km' and row['value'] is None
    assert row['period_start']==row['period_end']==case['date']=='2021-11-10'
    assert row['evidence_role']=='map_read_named_case_reference' and row['rights_screened_release_eligible'] is False
    assert case['figure']==9 and case['pdf_page']==13 and case['source_raster']['xref']==89
    assert case['source_raster']['samples_sha256']=='4667397fbf0b2036303233486de00c1ff44f8eb15cf591ad92d1c11ec1129116'
    assert case['roi_xyxy_inclusive']==[208,390,267,454]
    assert case['axes']=={'longitude':[[128,-96],[184,-93],[240,-90],[295,-87],[350,-84]],'latitude':[[359,30],[416,27],[472,24],[527,21],[579,18]]}
    a=case['source_attribution']
    assert a['method']=='dated_2021_figure9_with_unresolved_duplicate_caption'
    assert (a['source_figure9_case_year'],a['source_figure10_case_year'],a['retained_snapshot_date'])==(2021,2022,'2021-11-10')
    assert all(a[k] is False for k in ['duplicate_caption_resolved','independent_2021_provider_context_used_as_size_input','wilde_ii_values_inherited','later_2022_panels_admitted','duplicate_is_independent_measurement'])
    component=row['map_span_component'];assert component in ['east_west','north_south']
    assert row['metric']=='map_read_'+component+'_bounding_span'
    assert row['range_value']==span_interval(case,component)['range_km']


def validate_profile_context(row):
    c=row['profile_context']
    if c['method']=='source_reported_laura_survey_ssh_anomaly':
        validate_laura_ssh_record(row);return
    if c['method']=='source_reported_nelson_1989_local_current_phases':
        assert row['entity_id']=='eddy:horizon:loop-11-primary' and row['category']=='kinematics' and row['unit']=='knots'
        assert row['metric']=='source_reported_local_phase_current_speed' and row.get('lower_bound') is None
        assert row['rights_screened_release_eligible'] is False and row['evidence_role']=='qualified_published_named_case_reference'
        assert c['source_year']==1989 and c['source_instrument']=='Exxon_ADCP_programme'
        assert all(c[k] is False for k in ['bathymetry_is_sampling_depth','whole_eddy_maximum_inferred','simultaneous_vertical_profile_inferred','vertical_shear_computed','is_eddy_vertical_extent','annual_extrema_inferred','raw_current_profiles_acquired','source_uncertainty_quantified','physical_crosswalk_verified','separation_conventions_reconciled'])
        expected={
          'post-severe-45m-bound':(None,None,0.4,45,None,'source_local_strict_upper_bound_at_most_sites','two_weeks_after_late_august_severe_phase'),
          'september-25-45m-maximum':(1.4,None,None,45,'1989-09-25','source_local_sampled_maximum','september_25_1989'),
          'august-surface-band':(None,[2.2,2.7],None,None,None,'source_consistent_local_surface_band','august_1989_severe_current_phase'),
          'early-september-local-maximum':(3.6,None,None,None,None,'source_local_sampled_maximum','early_september_1989'),
          'final-phase-local-maximum':(2.6,None,None,None,None,'source_local_sampled_maximum','final_measurement_phase_1989')}
        assert c['key'] in expected
        value,interval,upper,depth,day,statistic,phase=expected[c['key']]
        assert (row['value'],row.get('range_value'),row.get('upper_bound'),row.get('depth_m'))==(value,interval,upper,depth)
        assert c['sample_depth_m']==depth and (c['statistic'],c['phase'])==(statistic,phase)
        assert row['period_start']==row['period_end']==day
        assert row['period_precision']==('day' if day else 'source_phase_without_exact_sample_dates')
        if upper is not None:assert row['upper_bound_exclusive'] is True
        if interval is not None:assert row['range_kind']=='source_reported_local_current_band_not_seasonal_range'
        assert c['bathymetry_contours_m']==([500,1000] if interval else None)
        assert c['direction_as_reported']==('eastward' if interval else None)
        return
    if c['method']=='source_reported_quiet_sst_ellipse_axes':
        assert row['entity_id']=='eddy:horizon:loop-14-primary' and row['category']=='size' and row['unit']=='km'
        assert row['rights_screened_release_eligible'] is False and row['evidence_role']=='qualified_published_named_case_reference'
        assert row['period_start'] is None and row['period_end'] is None and row['period_precision']=='source_two_image_dates_no_per_image_assignment'
        assert row.get('depth_m') is None and row.get('lower_bound') is None and row.get('upper_bound') is None
        assert c['source_feature']=='Quiet Eddy' and c['image_dates']==['1990-08-12','1990-08-19']
        assert c['source_method']=='NOAA_11_AVHRR_multichannel_SST_interpretation_with_drifter_context' and c['source_front_gradient_celsius']==0.5
        assert all(c[k] is False for k in ['source_uncertainty_quantified','per_image_axis_values_known','continuous_observation_interval_inferred','strict_bound_inferred','mathematical_ellipse_fit_verified','raw_sst_images_acquired','is_eddy_vertical_extent','ellipse_area_derived','outer_boundary_operator_known','physical_crosswalk_verified','separation_conventions_reconciled','annual_extrema_inferred'])
        assert c['axis'] in ['major','minor'] and row['metric']=='source_reported_sst_ellipse_'+c['axis']+'_axis_length'
        if c['axis']=='major':
            assert row['value']==400 and row.get('range_value') is None
            assert (c['orientation_as_reported'],c['approximation_as_reported'])==('northward','nearly')
        else:
            assert row['value'] is None and row['range_value']==[250,300] and row['range_kind']=='source_reported_approximate_axis_interval_not_seasonal_range'
            assert (c['orientation_as_reported'],c['approximation_as_reported'])==('east_west','about')
        return
    if c['method']=='source_reported_k_2000_mooring_current':
        assert row['entity_id']=='eddy:horizon:loop-34-primary' and row['category']=='kinematics' and row['unit']=='cm/s'
        assert row['metric']=='source_reported_local_interaction_current_speed' and row.get('range_value') is None
        assert row['rights_screened_release_eligible'] is False and row['evidence_role']=='qualified_published_named_case_reference'
        assert row['period_start'] is None and row['period_end'] is None and row['period_precision']=='source_event_phase_not_exact_sample_dates'
        assert (c['source_event_label'],c['published_alias'],c['alias_reference_source_id'])==('WCE K','Kinetic / Eddy K','hamilton-2003-k-alias')
        assert c['source_phase']=='first_two_weeks_november_2000' and c['source_map_context_date']=='2000-11-03'
        assert c['station']=='LSU Sigsbee mooring, deployments 1–2' and c['interaction_context']=='mooring_between_WCE_K_and_cyclone'
        assert c['event_flow_direction_as_reported']=='westward'
        assert all(c[k] is False for k in ['exact_sample_dates_known','map_date_is_sample_time','cross_report_case_association_verified','physical_crosswalk_verified','simultaneous_vertical_profile_inferred','vertical_shear_computed','whole_eddy_maximum_inferred','is_eddy_vertical_extent','source_uncertainty_quantified','raw_current_time_series_acquired'])
        if c['sample_depth_m'] is None:
            assert row.get('depth_m') is None and row['value']==50 and c['statistic']=='source_reached_site_value'
        else:
            assert c['sample_depth_m']==row['depth_m']==755 and row['value']==30 and c['statistic']=='source_local_sampled_maximum'
        return
    if c['method']=='source_reported_assimilative_analysis_parent_extent':
        assert row['entity_id']=='eddy:published:thor-2020' and row['category']=='size' and row['unit']=='km'
        assert row['metric']=='source_reported_assimilative_analysis_parent_zonal_extent' and row['value']==550
        assert row['rights_screened_release_eligible'] is False and row['evidence_role']=='published_model_case_reference'
        assert row['period_start']==row['period_end']==c['source_analysis_date']=='2020-02-24'
        assert row['period_precision']=='source_analysis_date_not_observation_timestamp'
        assert row.get('depth_m') is None and row.get('range_value') is None
        assert (c['source_case_name'],c['model'],c['horizontal_resolution_km'],c['ensemble_members'])==('Thor','NCOM / NCODA / COAMPS',3,32)
        assert c['field']=='weekly_ensemble_mean_verifying_analysis' and c['extent_axis']=='zonal' and c['relation']=='approximately'
        assert c['source_boundary_threshold']=='unspecified for scalar extent' and c['phase']=='elongated_parent_before_near_split'
        assert all(c[k] is False for k in ['analysis_is_direct_observation','forecast_member_value','source_uncertainty_quantified','principal_width_inferred','diameter_inferred','child_values_inherited','registry_values_inherited','physical_crosswalk_verified','geometry_inferred','annual_extrema_inferred','raw_model_fields_acquired'])
        return
    if c['method']=='source_reported_yazoo_2022_case':
        assert row['entity_id']=='eddy:horizon:loop-74-primary'
        assert (c['source_name'],c['registry_name'],c['registry_source_number'],c['registry_initial_separation'])==('Yazoo','Yazoo',74,'2022-06-20')
        assert row['rights_screened_release_eligible'] is False and row['evidence_role']=='qualified_published_named_case_reference'
        assert row.get('depth_m') is None and c['sample_depth_m'] is None and row.get('range_value') is None
        assert all(c[k] is False for k in ['source_uncertainty_quantified','physical_crosswalk_verified','secondary_case_values_inherited','annual_extrema_inferred','whole_eddy_maximum_inferred','is_eddy_vertical_extent','geometry_inferred','mean_or_maximum_statistic_specified'])
        if c['quantity']=='radius':
            assert (row['category'],row['metric'],row['value'],row['unit'])==('size','source_reported_high_adt_patch_radius',150,'km')
            assert c['source_window']==[row['period_start'],row['period_end']]==['2022-11-07','2022-11-17']
            assert row['period_precision']=='source_field_average_window' and c['radius_relation']=='approximately'
            assert c['source_map_is_temporal_average'] is True and c['boundary_operator_transferred_to_osw'] is False
        else:
            assert c['quantity']=='current'
            assert (row['category'],row['metric'],row['value'],row['unit'])==('kinematics','source_reported_eastern_flank_cruise_current_speed',2.5,'knots')
            assert c['source_window']==[row['period_start'],row['period_end']]==['2022-10-01','2022-10-05']
            assert row['period_precision']=='source_cruise_window_not_exact_sample_times'
        return
    if c['method']=='source_reported_thermal_level_enclosed_area':
        assert row['entity_id']=='eddy:horizon:loop-03-primary' and row['category']=='size' and row['unit']=='km^2'
        assert row['metric']=='source_reported_thermal_level_enclosed_area'
        assert row['period_start'] is None and row['period_end'] is None and row['period_precision']=='source_survey_month'
        assert row.get('depth_m') is None and row.get('range_value') is None
        assert row['rights_screened_release_eligible'] is False and row['evidence_role']=='qualified_published_named_case_reference'
        assert c['thermal_reference_celsius']==8 and c['source_table']=='4.4-2'
        assert c['source_table_unit']=='10^3 km^2' and c['conversion_factor_to_km2']==1000
        assert c['measurement_method']=='source_planimeter_on_hand_contoured_hydrographic_maps'
        assert all(c[k] is False for k in ['source_uncertainty_quantified','is_eddy_vertical_extent','sample_depth_inferred','outer_boundary_inferred','annual_extrema_inferred','raw_profiles_acquired','physical_crosswalk_verified'])
        table={'1985-10':[1.3,9.0,26.0,50.0,97.0],'1985-11':[0.0,2.7,26.0,48.0,85.0],'1986-01':[2.6,7.8,17.0,50.0,None],'1986-04':[0.3,2.4,8.1,24.0,None]}
        native=table[c['survey_label']][[750,700,650,600,550].index(c['temperature_surface_depth_contour_m'])]
        assert native is not None and native>0 and c['source_table_value']==native and row['value']==round(native*1000)
        assert row['id']==f"fast-saic-1988-thermal-area-{c['survey_label']}-{c['temperature_surface_depth_contour_m']}m"
        return
    if c['method']=='source_reported_multisensor_current_comparison':
        assert row['entity_id']=='eddy:horizon:loop-66-primary' and row['component_label']=='Northern post-split Quantum I source case'
        assert row['metric']=='source_reported_local_multisensor_current_comparison_speed' and row['category']=='kinematics' and row['unit']=='m/s'
        assert row['period_start']==row['period_end'] and row['period_start'] in ['2018-03-25','2018-03-26']
        assert c['aggregation']=='source_comparison_reference_not_mean_or_maximum'
        assert row['rights_screened_release_eligible'] is False and row['evidence_role']=='qualified_published_named_case_reference'
        assert all(c[k] is False for k in ['is_eddy_vertical_extent','raw_profiles_acquired','whole_eddy_maximum_inferred','simultaneous_vertical_section_inferred','vertical_shear_computed','physical_crosswalk_verified'])
        if c['instrument']=='ADCP':
            assert c['sample_depth_m']==row['depth_m']==5 and c['shared_source_approximation'] is False
            assert row['value']=={'2018-03-25':.6,'2018-03-26':.8}[row['period_start']]
        else:
            assert c['instrument']=='ROCIS and DopplerScatt shared source approximation' and c['sample_depth_m'] is None and row.get('depth_m') is None
            assert c['shared_source_approximation'] is True and row['value']=={'2018-03-25':1.2,'2018-03-26':1.1}[row['period_start']]
        return
    if c['method']=='source_reported_operational_adcp_maximum':
        assert row['metric']=='source_reported_operational_local_maximum_current_speed' and row['category']=='kinematics' and row['unit']=='knots'
        assert (row['entity_id'],row['value'],c['phase']) in [('eddy:horizon:loop-71-primary',3.5,'early_september_2021_verne'),('eddy:horizon:loop-72-primary',4.25,'october_2021_wilde')]
        assert row['period_start'] is None and row['period_end'] is None and c['sample_depth_m'] is None
        assert row['rights_screened_release_eligible'] is False and row['evidence_role']=='qualified_published_named_case_reference'
        assert all(c[k] is False for k in ['raw_profiles_acquired','whole_eddy_maximum_inferred','is_eddy_vertical_extent','window_is_lifetime','physical_crosswalk_verified'])
        return
    if c['method']=='source_reported_mooring_current_diagnostic':
        assert c['station']=='SAIC GG' and c['quantity_support']=='fixed_current_meter'
        assert c['aggregation']=='source_described_site_current_speed' and c['statistic_mean_or_maximum_specified'] is False
        assert row['category']=='kinematics' and row['unit']=='cm/s' and row['depth_m']==c['instrument_depth_m']
        assert row['period_start'] is None and row['period_end'] is None
        assert row['evidence_role']=='qualified_published_named_case_reference' and row['rights_screened_release_eligible'] is False
        assert all(c[k] is False for k in ['raw_time_series_acquired','simultaneous_vertical_profile_inferred','is_eddy_vertical_extent','window_is_lifetime','physical_crosswalk_verified','whole_eddy_maximum_inferred'])
        if row['entity_id']=='eddy:horizon:loop-08-primary':
            assert c['phase']=='post_coalescence_spring_1988' and c['direction_as_reported']=='southward' and c['instrument_depth_m']==100
            assert c['source_small_anticyclone_coalescence_context'] is True
            assert row['metric']=='source_reported_mooring_current_speed' and row['value']==75 and row.get('range_value') is None
        else:
            assert row['entity_id']=='eddy:horizon:loop-10-primary' and c['source_small_anticyclone_coalescence_context'] is False
            assert row['metric']=='source_reported_mooring_current_speed_range' and row['value'] is None
            assert row['range_kind']=='source_reported_site_current_speed_interval'
            if c['phase']=='september_1988':
                assert c['direction_as_reported']=='northeastward' and c['instrument_depth_m'] in [100,300,725]
                assert row['range_value']=={100:[80,90],300:[30,40],725:[10,20]}[c['instrument_depth_m']]
            else:
                assert c['phase']=='late_october_1988' and c['direction_as_reported']=='eastward' and c['instrument_depth_m']==100 and row['range_value']==[70,80]
        return
    if c['method']=='source_reported_airborne_temperature_diagnostic':
        assert row['entity_id']=='eddy:horizon:loop-31-primary'
        assert c['phase']=='single_mission_temperature_transect' and c['thermal_reference_celsius']==20
        assert c['aggregation']=='maximum_sampled_isotherm_depth'
        assert row['metric']=='source_reported_sampled_maximum_20c_isotherm_depth'
        assert row['category']=='structure' and row['unit']=='m' and row['value']==200
        assert row['period_start']==row['period_end']=='1999-08-03'
        assert row['evidence_role']=='qualified_indexed_reference' and row['rights_screened_release_eligible'] is False
        assert all(c[k] is False for k in ['is_eddy_vertical_extent','window_is_lifetime','eddy_total_heat_inferred','raw_profiles_acquired','physical_crosswalk_verified'])
        return
    assert c['method']=='source_reported_glider_diagnostic'
    assert all(c[k] is False for k in ['is_eddy_vertical_extent','window_is_lifetime','eddy_total_heat_inferred','raw_profiles_acquired','physical_crosswalk_verified'])
    assert row['entity_id']=='eddy:horizon:loop-61-primary'
    assert row['evidence_role']=='qualified_indexed_reference' and row['rights_screened_release_eligible'] is False
    if c['phase']=='separation_reattachment_zone':
        assert c['sampling_window']==[row['period_start'],row['period_end']]==['2014-09-23','2014-10-01']
        assert c['thermal_reference_celsius']==26 and row['category']=='structure'
        if row['metric']=='source_reported_mean_26c_isotherm_depth':
            assert row['unit']=='m' and row['value']==30 and c['aggregation']=='source_reported_mean'
        else:
            assert row['metric']=='source_reported_transition_upper_ocean_heat_content_range'
            assert row['unit']=='kJ/cm2' and row['range_value']==[20,30] and c['quantity_support']=='local_water_column'
    else:
        assert c['phase']=='later_eastward_encounter' and c['related_circuit_window']==['2014-10-18','2014-11-07']
        assert c['window_dates_samples'] is False and row['period_start'] is None and row['period_end'] is None
        if row['metric']=='source_reported_depth_averaged_current_speed':
            assert row['category']=='kinematics' and row['unit']=='m/s' and row['value']==1
            assert c['averaging_axis']=='depth' and c['vertical_averaging_interval_m']==[0,1000]
        else:
            assert row['metric']=='source_reported_later_upper_ocean_heat_content_lower_bound'
            assert row['category']=='structure' and row['unit']=='kJ/cm2' and row['value'] is None
            assert row['lower_bound']==100 and row['lower_bound_exclusive'] is True
            assert c['thermal_reference_celsius']==26 and c['quantity_support']=='local_water_column'


def validate_year5_alias_reference(row):
    a=row['case_alias_association']
    assert a['method']=='source_reported_1988_letter_case_reference'
    assert (a['registry_source_number'],a['registry_name'],a['published_alias'],a['source_label']) in [(8,'Kathleen','Kathleen','Eddy E'),(10,'Murphy','Murphy','Eddy F')]
    assert row['entity_id']==f"eddy:horizon:loop-{a['registry_source_number']:02}-primary"
    assert a['alias_reference_source_id']=='nowlin-2001'
    assert all(a[k] is False for k in ['physical_crosswalk_verified','separation_conventions_reconciled','other_eddy_values_inherited'])
    assert row['category']=='size' and row['unit']=='km' and row['period_start'] is None and row['period_end'] is None
    assert row['rights_screened_release_eligible'] is False and row['evidence_role']=='qualified_published_named_case_reference'
    if a['registry_source_number']==8:
        assert row['metric']=='source_reported_sampled_drifter_axes_length_extrema' and row['value'] is None and row['range_value']==[50,170]
        assert row['range_kind']=='source_reported_sampled_axes_extrema_not_seasonal_range'
    else:
        values={'source_reported_sampled_drifter_ellipse_long_dimension':244,'source_reported_sampled_drifter_ellipse_short_dimension':148,'source_reported_baroclinic_radius_of_influence':180,'source_reported_eddy_diameter_definition_unspecified':300}
        assert row['metric'] in values and row['value']==values[row['metric']] and row.get('range_value') is None


def validate_fast_alias_reference(row):
    a=row['case_alias_association']
    assert row['entity_id']=='eddy:horizon:loop-03-primary'
    assert (a['source_label'],a['published_alias'],a['registry_name'],a['registry_source_number'])==('Eddy B','Fast Eddy','Fast',3)
    assert a['registry_initial_separation']=='1985-05-31' and a['report_separation_context']=='early July 1985'
    assert a['alias_reference_source_id']=='hamilton-1999'
    assert all(a[k] is False for k in ['physical_crosswalk_verified','separation_conventions_reconciled','other_eddy_values_inherited'])
    assert row['evidence_role']=='qualified_published_named_case_reference' and row['rights_screened_release_eligible'] is False
    kinds={'source_reported_thermal_level_enclosed_area':('size','km^2'),
           'source_reported_center_westward_translation_distance':('travel','km'),
           'source_reported_approximate_center_translation_speed':('kinematics','km/day'),
           'source_reported_sampled_drifter_orbit_diameter':('size','km'),
           'source_reported_sampled_drifter_orbit_radius':('size','km'),
           'source_reported_hydrographic_radius_lower_bound':('size','km'),
           'source_reported_drifter_inferred_flow_radius_lower_bound':('size','km')}
    assert row['metric'] in kinds and (row['category'],row['unit'])==kinds[row['metric']]
    if row['metric'].endswith('_lower_bound'):
        assert row['value'] is None and row['lower_bound']>0 and row['lower_bound_exclusive'] is False
    else:assert row['value']>0 and row.get('lower_bound') is None


def station_distance_interval(c):
    assert c['method']=='spherical_sampled_station_separation_v1'
    assert c['earth_radius_km']==6371 and c['coordinate_order']=='latitude_longitude'
    assert c['coordinate_allowance_degrees']==0.05 and c['coordinate_allowance_assumed'] is True
    assert c['round_outward_km']==25
    assert all(c[k] is False for k in ['simultaneity_verified','boundary_operator_specified','whole_eddy_radius_inferred','diameter_inferred','closed_footprint_inferred','source_accuracy_quantified','annual_extrema_inferred'])
    a,b=c['center_station'],c['edge_station']
    assert a['source_role']=='sampled_center' and b['source_role']=='sampled_edge'
    for p in [a,b]:
        assert all(type(p[k]) in [int,float] and math.isfinite(p[k]) for k in ['latitude','longitude'])
        assert -90<=p['latitude']<=90 and -180<=p['longitude']<=180
    p,q=map(math.radians,[a['latitude'],b['latitude']]);dl=math.radians(b['longitude']-a['longitude'])
    h=math.sin((q-p)/2)**2+math.cos(p)*math.cos(q)*math.sin(dl/2)**2
    nominal=2*6371*math.asin(math.sqrt(min(1,max(0,h))))
    # A meridional move plus a parallel move bounds each endpoint's displacement.
    # cos(latitude)<=1 gives R*(|dlat|+|dlon|); sum both endpoints.
    allowance=4*6371*math.radians(.05)
    assert c['unrounded_nominal_km']==round(nominal,6)
    assert c['triangle_inequality_allowance_km']==round(allowance,6)
    result=[max(0,math.floor((nominal-allowance)/25)*25),math.ceil((nominal+allowance)/25)*25]
    assert c['range_km']==result
    return result


def validate_station_distance(row):
    assert row['metric']=='calculated_sampled_center_to_edge_station_separation'
    assert row['entity_id']=='eddy:geography:agulhas-eddy-w-2000'
    assert row['category']=='size' and row['unit']=='km' and row['value'] is None
    assert row['period_start'] is None and row['period_end'] is None and row['period_precision']=='month'
    assert row['rights_screened_release_eligible'] is False
    c=row['calculation']
    assert c['center_station']=={'id':'06','latitude':-29.2,'longitude':8.2,'source_role':'sampled_center'}
    assert c['edge_station']=={'id':'05','latitude':-28.8,'longitude':6.3,'source_role':'sampled_edge'}
    assert row['range_kind']=='assumed_coordinate_allowance_and_outward_rounding_sensitivity'
    assert row['range_value']==station_distance_interval(c)


def build():
    pins={}
    def read(path):
        raw=(ROOT/path).read_bytes();pins[path]=hashlib.sha256(raw).hexdigest()
        return json.loads(raw)
    inventory_path='research/ocean-eddy-name-inventory.json';inventory=read(inventory_path)
    identities={'eddy:'+r['id']:r for r in inventory['entries']}
    assert len(identities)==136 and len(inventory['entries'])==136
    geo_path='research/named-eddy-geography.json';geo=read(geo_path)
    astrid_path='research/astrid-2000-radial-scale-scope-audit.json';astrid=read(astrid_path)
    rings_path='research/agulhas-guerra-2022-ring-radius-scope-audit.json';rings=read(rings_path)
    loops_path='research/named-loop-eddy-published-observations.json';loops=read(loops_path)
    recurrence_path='research/black-sea-eddy-recurrence.json';recurrence=read(recurrence_path)
    extra_path='research/eddy-measurement-register-source-facts-v1.json';extra=read(extra_path)
    additions_path='research/eddy-measurement-register-additions-v2.json';additions=read(additions_path)
    for d in [rings,recurrence]:
        raw=(ROOT/d['protocol_file']).read_bytes();pin=hashlib.sha256(raw).hexdigest()
        assert pin==d['protocol_sha256'];pins[d['protocol_file']]=pin
    evidence=[]
    def add(identifier,owner,category,metric,value,unit,path,location,document,**kwargs):
        assert owner in identities and not any(r['id']==identifier for r in evidence)
        raw=pointer(document,location)
        row={'id':identifier,'entity_id':owner,'category':category,'metric':metric,
             'metric_label':metric.replace('_',' '),'value':value,'unit':unit,
             'lower_bound':None,'lower_bound_exclusive':False,'standard_deviation':None,
             'uncertainty':None,'sample_count':None,'period_start':None,'period_end':None,
             'period_label':None,'definition':None,'scope':None,'qualification':None,
             'source_claims':[],'value_conflict':False,'date_conflict':False,
             'source_url':raw.get('source_url') or document.get('source_url'),
             'source_locator':raw.get('source_locator'),'source_file':path,
             'source_pointer':location,'source_sha256':pins[path],'raw_record':raw,
             'rank_eligible':False,'geometry':None,'seasonal_playback_eligible':False,
             'whole_lifetime_inferred':False,'physical_state_join_eligible':False}
        row.update(kwargs)
        assert row['value'] is None or isinstance(row['value'],(int,float)) and math.isfinite(row['value']) and row['value']>0
        assert row['source_url'] and row['source_locator'],identifier
        evidence.append(row)
    for n,r in enumerate(astrid['measurements']):
        add(r['id'],r['entity_id'],'size',r['metric'],r['value_km'],'km',astrid_path,f'/measurements/{n}',astrid,
            definition=r['definition'],scope=r['layer'],period_label=r['study_period_context'],
            qualification='Two-layer diagnostic model scale; retain each radius definition separately.')
    for key,entity in rings['entities'].items():
        assert next(r for r in geo['entries'] if r['id']==key)['ring_radius_audit_sha256']==pins[rings_path]
        for n,r in enumerate(entity['measurements']):
            add(r['id'],r['entity_id'],'size',r['metric'],r['value_km'],'km',rings_path,f'/entities/{key}/measurements/{n}',rings,
                source_locator='; '.join(c['source_locator'] for c in r['source_claims']),
                definition=r['definition'],scope=r['layer'],period_label=r['period_label'],
                source_claims=r['source_claims'],value_conflict=r['radius_conflict'],date_conflict=r['date_conflict'],
                qualification='Source radius and year conflicts remain unresolved. Consistent section values are individual points, not annual extrema or an interpolated series.')
    # Structured interpretation of existing prose, with exact expected text guards.
    loop_sizes={
        'published:kraken-2013':('coherent_core_mean_radius',100,'Approximately 100 km mean radius of the coherent core, a definition distinct from the outer instantaneous SSH footprint.'),
        'published:cameron-2009-observed':('author_reported_altimetric_diameter',300,'About 300 km diameter on 2009-01-20, as assessed by the authors from the altimetric eddy field.'),
        'published:darwin-2009-observed':('author_reported_altimetric_diameter',200,'About 200 km diameter on 2009-07-25, as assessed by the authors from the altimetric eddy field.')}
    for n,r in enumerate(loops['entries']):
        if r['eddy_id'] not in loop_sizes:continue
        metric,value,expected=loop_sizes[r['eddy_id']];assert r['reported_measure']==expected
        add(r['eddy_id']+'-size-reference','eddy:'+r['eddy_id'],'size',metric,value,'km',loops_path,f'/entries/{n}',loops,
            definition=r['reported_measure'],scope=r['interpretation'],
            period_label=(r['observation_start']+' to '+r['observation_end']) if 'kraken' in r['eddy_id'] else r['observation_start'],
            qualification='Approximate author-reported value. No radius/diameter conversion or outer footprint is inferred.')
        if r['eddy_id']=='published:kraken-2013':
            elapsed=(date.fromisoformat(r['observation_end'])-date.fromisoformat(r['observation_start'])).days
            add('kraken-2013-core-analysis-interval','eddy:'+r['eddy_id'],'duration','coherent_core_analysis_interval',elapsed,'day',loops_path,f'/entries/{n}',loops,
                period_start=r['observation_start'],period_end=r['observation_end'],
                definition='Elapsed days between the retained coherent-core analysis endpoints.',scope=r['interpretation'],
                qualification='Date subtraction, not a measured full lifetime, inclusive count or continuous observation cadence.')
    for n,r in enumerate(geo['entries']):
        if r.get('reported_track_period'):
            period=r['reported_track_period'];elapsed=(date.fromisoformat(period['end'])-date.fromisoformat(period['start'])).days
            add(r['id']+'-source-track-span','eddy:geography:'+r['id'],'duration','source_track_elapsed_span',elapsed,'day',geo_path,f'/entries/{n}',geo,
                source_url=geo['sources'][r['source']],source_locator='Retained reported_track_period; Guerra et al. (2022), individual-ring track discussion in section 3.1.',
                period_start=period['start'],period_end=period['end'],definition='Elapsed days between source-reported track endpoints.',
                scope=period.get('scope') or r.get('identity_note') or 'Source track window; first/last detections do not independently prove birth or death.',
                qualification='Source identity may span a split or merger. '+r.get('identity_note',r.get('formation',{}).get('note','No full physical lifetime inferred.')))
        if r.get('reported_lifetime_years_approx') is not None:
            for category,metric,value,unit in [('duration','author_reported_approximate_lifetime',r['reported_lifetime_years_approx'],'year'),('travel','author_reported_travel_lower_bound',None,'km')]:
                add(r['id']+'-'+metric,'eddy:geography:'+r['id'],category,metric,value,unit,geo_path,f'/entries/{n}',geo,
                    source_url=geo['sources'][r['source']],source_locator=r['reported_motion_source_locator'],
                    lower_bound=r['reported_travel_km_lower_bound'] if category=='travel' else None,lower_bound_exclusive=category=='travel',
                    definition='Source-reported approximate lifetime.' if category=='duration' else 'Strict lower bound on source-reported travel distance.',
                    scope=r['identity_note'],qualification='No exact start/end dates, calendar conversion, track rejoin or speed calculation inferred.')
    for n,r in enumerate(recurrence['entries']):
        common={'scope':r['scope_note'],'definition':'Published recurrent-region statistic; averaging window and detection threshold unspecified.',
                'qualification':'Recurring-region summary, not the lifespan of an independently dated individual.'}
        add(r['id']+'-presence',r['entity_id'],'recurrence',r['occurrence_metric'],r['reported_occurrence_days_per_year_approx'],'day/year',recurrence_path,f'/entries/{n}',recurrence,**common)
        if r['reported_event_lifetime_approx'] is not None:
            add(r['id']+'-event-duration',r['entity_id'],'duration','regional_'+r['event_lifetime_statistic']+'_event_lifetime',r['reported_event_lifetime_approx'],r['event_lifetime_unit'],recurrence_path,f'/entries/{n}',recurrence,**common)
    for n,r in enumerate(extra['records']):
        add(r['id'],r['entity_id'],'size',r['metric'],r['mean_radius_km'],'km',extra_path,f'/records/{n}',extra,
            standard_deviation=r['standard_deviation_km'],sample_count=r['table_sample_count'],
            definition=extra['definition'],scope=r['longitude_label']+'; long-lived Agulhas ring population, 1993-2016.',
            period_label='1993-2016',qualification=extra['qualification']+' '+r.get('qualification',''))
    # Bind the first batch before extending it; previous source records stay exact.
    baseline_sha=hashlib.sha256(json.dumps(evidence,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
    assert len(evidence)==additions['baseline_evidence_count']==40
    assert baseline_sha==additions['baseline_evidence_sha256']
    for n,r in enumerate(additions['records']):
        source=additions['sources'][r['source_id']]
        add(r['id'],r['entity_id'],r['category'],r['metric'],r['value'],r['unit'],additions_path,f'/records/{n}',additions,
            source_url=source['url'],source_access=source['access'],source_id=r['source_id'],
            definition=r['definition'],scope=r['scope'],qualification=r['qualification'],
            period_start=r.get('period_start'),period_end=r.get('period_end'),period_label=r.get('period_label'),
            period_precision=r.get('period_precision'),component_label=r.get('component_label'),right_censored=r.get('right_censored',False))
    batches_path='research/eddy-measurement-batches-v1.json';batch_index=read(batches_path);applied=[];registry_contexts={};classifications=[]
    for entry in batch_index['batches']:
        path=entry['file'];batch=read(path);assert pins[path]==entry['sha256']
        prior=hashlib.sha256(json.dumps(evidence,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
        assert len(evidence)==batch['baseline_evidence_count'] and prior==batch['baseline_evidence_sha256']
        if batch.get('registry_rows'):
            legacy=read('research/named-loop-current-eddies.json');by_number={r['source_number']:r for r in legacy['entries']}
            assert len(batch['registry_rows'])==81
            for raw in batch['registry_rows']:
                old=by_number[raw['source_number']]
                start=raw['initial_separation_as_reported']
                normalized=registry_date_bounds(start)[0].isoformat() if len(start.split('/'))==3 else start
                assert (raw['name'],normalized,raw['dissipation_as_reported'],raw['secondary_name_as_reported'])==(old['name'],old['initial_separation'],old['dissipation_as_reported'],old['secondary_name'])
            for owner,context in batch['registry_contexts'].items():
                assert owner in identities and owner.endswith('-primary') and owner not in registry_contexts
                registry_contexts[owner]=context
        for n,r in enumerate(batch['records']):
            source=batch['sources'][r['source_id']]
            if r.get('model_context',{}).get('method')=='source_reported_model_event_date_contrast':
                validate_model_event_contrast(r)
                report=read(source['source_review_file'])
                assert pins[source['source_review_file']]==source['source_review_sha256']
                assert report['status']=='QUALIFIED_INDEXED_PREPRINT_DATES_ONLY' and report['preprint_not_peer_reviewed']
                assert report['original_pdf_retained'] is False and report['source_figure_pixels_reviewed'] is False
                assert report['counterfactual_event_dates'][r['model_context']['experiment']]==r['period_end']
            if r.get('profile_context'):validate_profile_context(r)
            if r.get('profile_context',{}).get('method')=='source_reported_nelson_1989_local_current_phases':
                report=read(source['source_review_file']);assert pins[source['source_review_file']]==source['source_review_sha256']
                assert report['status']=='NELSON_1989_LOCAL_CURRENT_PHASES_VERIFIED' and report['new_size_measurements']==0
                c=r['profile_context'];case=next(v for v in report['accepted_local_diagnostics'] if v['key']==c['key'])
                assert (r['value'],r.get('range_value'),r.get('upper_bound'),c['sample_depth_m'])==(case['value'],case.get('range_value'),case.get('upper_bound'),case['sample_depth_m'])
                legacy=next(v for v in read('research/named-loop-current-eddies.json')['entries'] if v['source_number']==11)
                assert (legacy['name'],legacy['initial_separation'])==('Nelson',report['registry_association']['registry_initial_separation'])

            if r.get('profile_context',{}).get('method')=='source_reported_quiet_sst_ellipse_axes':
                report=read(source['source_review_file']);assert pins[source['source_review_file']]==source['source_review_sha256']
                assert report['status']=='QUIET_SOURCE_REPORTED_SST_AXES_VERIFIED'
                a=report['accepted'];c=r['profile_context'];assert a['image_dates']==c['image_dates']
                assert (r['value'] if c['axis']=='major' else r['range_value'])==a['major_axis_km' if c['axis']=='major' else 'minor_axis_range_km']
                assert report['source_identity']['source_name']=='Quiet Eddy' and report['source_identity']['physical_crosswalk_verified'] is False
                legacy=next(v for v in read('research/named-loop-current-eddies.json')['entries'] if v['source_number']==14)
                assert (legacy['name'],legacy['initial_separation'])==('Quiet',report['source_identity']['registry_initial_separation'])

            if r.get('profile_context',{}).get('method')=='source_reported_k_2000_mooring_current':
                report=read(source['source_review_file']);assert pins[source['source_review_file']]==source['source_review_sha256']
                assert report['status']=='QUALIFIED_KINETIC_2000_INTERACTION_SITE_CURRENTS_VERIFIED'
                a=report['source_case_association'];assert a['registry_source_number']==34 and a['year']==2000
                assert a['physical_crosswalk_verified'] is False and a['cross_report_case_association_verified'] is False
                assert r['profile_context']['alias_reference_source_id'] in batch['sources']
                legacy=next(v for v in read('research/named-loop-current-eddies.json')['entries'] if v['source_number']==34)
                assert (legacy['name'],legacy['initial_separation'])==('Kinetic',a['registry_initial_separation'])

            if r.get('profile_context',{}).get('method')=='source_reported_assimilative_analysis_parent_extent':
                report=read(source['source_review_file']);assert pins[source['source_review_file']]==source['source_review_sha256']
                assert report['status']=='ORIGINAL_THOR_PARENT_ANALYSIS_EXTENT_VERIFIED' and report['owner_id']==r['entity_id']
                assert report['quantity']['zonal_extent_km']==r['value'] and report['quantity']['date']==r['period_start']
                prior_case=read('research/named-loop-eddy-published-observations.json')['entries'][1]
                assert prior_case['eddy_id']=='published:thor-2020' and prior_case['name']=='Thor'
                assert all(v['source_url']=='https://repository.library.noaa.gov/view/noaa/71031' for v in prior_case['independent_event_observations'])

            if r.get('profile_context',{}).get('method')=='source_reported_yazoo_2022_case':
                report=read(source['source_review_file']);assert pins[source['source_review_file']]==source['source_review_sha256']
                assert report['status']=='ORIGINAL_PRIMARY_YAZOO_RADIUS_AND_LOCAL_CURRENT_VERIFIED'
                assert report['registry_candidate']['entity_id']==r['entity_id'] and report['registry_candidate']['physical_crosswalk_verified'] is False
                assert report['accepted_references']['radius_km' if r['category']=='size' else 'eastern_flank_current_knots']==r['value']
                legacy=next(v for v in read('research/named-loop-current-eddies.json')['entries'] if v['source_number']==74)
                assert (legacy['name'],legacy['initial_separation'])==('Yazoo','2022-06-20')

            if r.get('profile_context',{}).get('method')=='source_reported_thermal_level_enclosed_area':
                report=read(source['source_review_file']);assert pins[source['source_review_file']]==source['source_review_sha256']
                lead=report['verified_numeric_source_lead'];assert lead['source_pixels_reviewed'] is True and lead['positive_numeric_cells']==17
                c=r['profile_context'];source_row=next(v for v in lead['source_rows'] if v['survey_month']==c['survey_label'])
                assert source_row['values'][lead['depth_contours_m'].index(c['temperature_surface_depth_contour_m'])]==c['source_table_value']

            if r['metric']=='source_narrative_formation_to_dissipation_calendar_span':
                validate_nautilus_calendar_reference(r)
                report=read(source['source_review_file']);assert pins[source['source_review_file']]==source['source_review_sha256']
                assert report['status']=='ORIGINAL_NAUTILUS_II_MONTH_PRECISION_NARRATIVE_VERIFIED'
                assert report['owner_id']==r['entity_id'] and report['calendar_support']==r['calendar_support'] and report['source_case']==r['independent_named_case']
                assert report['source']['original']==source['original'] and report['source_pages_actual_pixels_reviewed']==[1,54,55]
                assert source['original']['sha256']=='14cdf509d2c52f789f7593a30ea7392ba1a1819c92dd4c45ba994320564eaca9'
                assert report['new_size_reference_owners']==report['measurements_inherited_from_primary']==0
                assert report['whole_lifetime_inferred'] is False and report['physical_state_join_eligible'] is False
                primary=next(v for v in read('research/named-loop-current-eddies.json')['entries'] if v['source_number']==63)
                assert (primary['name'],primary['initial_separation'],primary['dissipation_as_reported'])==('Nautilus','2015-05-01','11/2015')
                assert report['excluded_parent_context']['used_as_numeric_inputs'] is False

            if r.get('case_alias_association'):
                if r['case_alias_association'].get('method')=='source_reported_1988_letter_case_reference':validate_year5_alias_reference(r)
                else:validate_fast_alias_reference(r)
                association=r['case_alias_association'];original=next(v for v in read('research/named-loop-current-eddies.json')['entries'] if v['source_number']==association['registry_source_number'])
                assert (association['registry_name'],association['registry_initial_separation'])==(original['name'],original['initial_separation'])
                assert association['alias_reference_source_id'] in batch['sources']
            if r['source_id']=='van-aken-2003-laura':
                report=read(source['source_review_file']);proof=read(batch['source_pixel_report'])
                assert pins[source['source_review_file']]==source['source_review_sha256']
                assert report['status']=='ORIGINAL_LAURA_CARTOGRAPHIC_EXTENT_AND_SSH_VERIFIED' and report['owner_id']==r['entity_id']
                assert report['source']['original']==source['original']
                assert proof['status']=='PASS' and proof['source_pixels_verified'] and proof['source_caption_and_ssh_text_verified']
                assert proof['batch_sha256']==pins[path] and proof['original_pdf_sha256']==source['original']['sha256']
                assert proof['verifier_sha256']==hashlib.sha256((ROOT/'analysis/eddy_cartographic_circle_spans_v1.py').read_bytes()).hexdigest()
                assert proof['span_math_sha256']==hashlib.sha256((ROOT/'analysis/eddy_map_spans_v1.py').read_bytes()).hexdigest()
                assert proof['physical_boundary_admitted'] is False and report['whole_eddy_dimensions_admitted']==0
                if r.get('profile_context'):
                    assert r['value']==report['ssh_maximum']['value'] and r['unit']==report['ssh_maximum']['unit']
            map_values={}
            if r.get('cartographic_circle_case_index') is not None:
                case=batch['cartographic_circle_cases'][r['cartographic_circle_case_index']];validate_cartographic_record(case,r)
                assert proof['stroke_cases']==case['stroke_cases']
                calculation=cartographic_spans(case,r['map_span_component'])
                assert calculation==proof['spans'][r['map_span_component']]==report['operator']['spans'][r['map_span_component']]
                map_values={'source_map_estimate':{'case':case,'component':r['map_span_component'],'calculation':calculation}}
            if r.get('isoline_case_index') is not None:
                case=batch['isoline_cases'][r['isoline_case_index']];validate_source_isoline_case(case)
                report=read(batch['source_isoline_report'])
                assert report['status']=='PASS' and report['source_pixels_verified'] and report['manual_name_date_axes_and_component_review_required']
                assert report['batch_sha256']==pins[path] and report['cases'][r['isoline_case_index']]==case
                assert all(report[k] is False for k in ['missing_ink_reconstructed','physical_footprint_admitted','whole_eddy_dimensions_inferred','original_source_assets_republished'])
                for key,module in [('verifier_sha256','eddy_source_bold_isoline_spans_v1.py'),('axis_math_sha256','eddy_map_spans_v1.py')]:
                    assert report[key]==hashlib.sha256((ROOT/'analysis'/module).read_bytes()).hexdigest()
                assert r['entity_id']==case['owner_id'] and r['period_start']==r['period_end']==case['date']
                assert r['category']=='size' and r['unit']=='km' and r['value'] is None and r['rights_screened_release_eligible'] is False
                assert r['evidence_role']=='map_read_named_case_reference' and r['period_precision']=='published_map_date_not_raw_acquisition_time'
                component=r['isoline_component'];calculation=source_isoline_spans(case,component)
                assert r['metric']=='source_chart_17cm_ssh_isoline_'+component+'_span' and r['range_value']==calculation['range_km']
                assert calculation==report['spans'][r['isoline_case_index']][component]
                legacy=next(v for v in read('research/named-loop-current-eddies.json')['entries'] if v['source_number']==75)
                assert (legacy['name'],legacy['initial_separation'])==('Zodiac','2022-12-27')
                map_values={'source_map_estimate':{'case':case,'component':component,'calculation':calculation}}
            if r.get('operational_chart_case_index') is not None:
                case=batch['operational_chart_cases'][r['operational_chart_case_index']];validate_operational_chart_case(case)
                report=read(batch['source_operational_chart_report'])
                assert report['status']=='PASS' and report['source_pixels_verified'] and report['manual_name_date_axis_and_segment_selection_required']
                assert report['missing_ink_reconstructed'] is False and report['whole_eddy_dimensions_inferred'] is False and report['physical_footprint_admitted'] is False
                assert report['batch_sha256']==pins[path] and report['original_pdf_sha256']==source['original']['sha256']
                for key,module in [('verifier_sha256','eddy_operational_chart_spans_v1.py'),('axis_math_sha256','eddy_map_spans_v1.py')]:
                    assert report[key]==hashlib.sha256((ROOT/'analysis'/module).read_bytes()).hexdigest()
                excluded=batch['excluded_gridded_comparison'];grid=read(excluded['file'])
                assert pins[excluded['file']]==excluded['sha256'] and grid['measurements_admitted']==0
                assert grid['status']=='NO_QUALIFYING_CLOSED_CONTOUR_AT_SOURCE_MAP_DATES'
                assert r['entity_id']==case['owner_id'] and r['period_start']==r['period_end']==case['date']
                assert r['category']=='size' and r['unit']=='km' and r['value'] is None and r['rights_screened_release_eligible'] is False
                assert r['evidence_role']=='map_read_named_case_reference'
                component=r['operational_chart_component'];calculation=operational_chart_spans(case,component)
                assert r['metric']=='source_operational_chart_visible_frontal_line_'+component+'_span' and r['range_value']==calculation['range_km']
                assert calculation==next(v for v in report['records'] if v['name']==case['source_name'])['spans'][component]
                map_values={'source_map_estimate':{'case':case,'component':component,'calculation':calculation}}
            if r.get('visible_model_front_case_index') is not None:
                assert all(r.get(k) is None for k in ['map_case_index','audit_span_case_index','colour_span_case_index','arrow_span_case_index','pdf_line_case_index','height_profile_case_index','scale_bar_case_index'])
                case=batch['visible_model_front_cases'][r['visible_model_front_case_index']];validate_visible_front_case(case)
                report=read(batch['source_visible_front_report'])
                assert report['status']=='PASS' and report['source_pixels_verified'] and report['east_side_clipped'] is True
                assert all(report[k] is False for k in ['missing_geometry_reconstructed','full_front_extent_inferred','physical_footprint_admitted'])
                assert report['batch_sha256']==pins[path] and report['original_pdf_sha256']==source['original']['sha256']
                for key,module in [('verifier_sha256','eddy_visible_model_front_v1.py'),('axis_math_sha256','eddy_map_spans_v1.py'),('ink_reader_sha256','eddy_scale_bar_spans_v1.py')]:
                    assert report[key]==hashlib.sha256((ROOT/'analysis'/module).read_bytes()).hexdigest()
                assert r['entity_id']==case['owner_id'] and r['period_start']==r['period_end']==case['date']
                assert r['category']=='size' and r['unit']=='km' and r['value'] is None and r['rights_screened_release_eligible'] is False
                assert r['metric']=='source_visible_model_front_meridional_span' and r['evidence_role']=='map_read_named_case_reference'
                calculation=visible_front_span(case);assert calculation==report['meridional_span'] and r['range_value']==calculation['range_km']
                map_values={'source_map_estimate':{'case':case,'component':'north_south','calculation':calculation}}
            if r.get('scale_bar_case_index') is not None:
                assert all(r.get(k) is None for k in ['map_case_index','audit_span_case_index','colour_span_case_index','arrow_span_case_index','pdf_line_case_index','height_profile_case_index'])
                case=batch['scale_bar_cases'][r['scale_bar_case_index']];validate_scale_bar_case(case)
                report=read(batch['source_scale_bar_report'])
                assert report['status']=='PASS' and report['source_pixels_verified'] and report['manual_name_date_and_curve_selection_required']
                assert report['missing_ink_reconstructed'] is False and report['physical_footprint_admitted'] is False
                assert report['batch_sha256']==pins[path] and report['original_chart_sha256']==source['chart']['sha256']
                assert report['verifier_sha256']==hashlib.sha256((ROOT/'analysis/eddy_scale_bar_spans_v1.py').read_bytes()).hexdigest()
                assert r['entity_id']==case['owner_id'] and r['period_start']==r['period_end']==case['date']
                assert r['category']=='size' and r['unit']=='km' and r['value'] is None and r['rights_screened_release_eligible'] is False
                assert r['evidence_role']=='map_read_named_case_reference'
                component=r['scale_bar_component'];calculation=scale_bar_spans(case,component)
                assert r['metric']=='source_scale_bar_equivalent_'+component+'_span'
                assert calculation==report['spans'][component] and r['range_value']==calculation['range_km']
                map_values={'source_map_estimate':{'case':case,'component':component,'calculation':calculation}}
            if r.get('height_profile_case_index') is not None:
                assert all(r.get(k) is None for k in ['map_case_index','audit_span_case_index','colour_span_case_index','arrow_span_case_index','pdf_line_case_index','source_plot_estimate'])
                case=batch['height_profile_cases'][r['height_profile_case_index']];validate_height_case(case)
                report=read(batch['source_profile_report'])
                assert report['status']=='PASS' and report['source_pixels_verified'] and report['manual_curve_selection_required']
                assert report['missing_ink_reconstructed'] is False and report['physical_boundary_admitted'] is False
                assert report['batch_sha256']==pins[path] and report['original_pdf_sha256']==source['original']['sha256']
                assert report['verifier_sha256']==hashlib.sha256((ROOT/'analysis/eddy_height_profiles_v1.py').read_bytes()).hexdigest()
                assert report['axis_math_sha256']==hashlib.sha256((ROOT/'analysis/eddy_map_spans_v1.py').read_bytes()).hexdigest()
                assert r['entity_id']==case['owner_id'] and r['period_start']==r['period_end']==case['date'] and r['value'] is None
                assert r['rights_screened_release_eligible'] is False and r['evidence_role']=='graph_digitized_named_case_reference'
                component=r['profile_component'];assert component in ['meridional_span','peak_height']
                category,unit,metric,calculation,key=('size','km','source_profile_selected_height_level_meridional_span',height_span(case),'range_km') if component=='meridional_span' else ('structure','m','source_profile_selected_main_lobe_peak_dynamic_topography',height_peak(case),'range_m')
                assert (r['category'],r['unit'],r['metric'])==(category,unit,metric)
                assert calculation==report[component] and r['range_value']==calculation[key]
                map_values={'source_plot_estimate':{'method':case['method'],'case':case,'component':component,'calculation':calculation}}
            if r.get('pdf_line_case_index') is not None:
                assert all(r.get(k) is None for k in ['map_case_index','audit_span_case_index','colour_span_case_index','arrow_span_case_index'])
                case=batch['pdf_line_cases'][r['pdf_line_case_index']];validate_pdf_line_case(case)
                report=read(batch['source_native_report'])
                assert report['status']=='PASS' and report['source_native_path_verified'] and report['source_axis_labels_verified']
                assert report['explicit_endpoint_closure_verified'] and report['chain_breaks']==0
                assert report['missing_segments_reconstructed'] is False and report['physical_footprint_admitted'] is False and report['contour_observation_date'] is None
                assert report['batch_sha256']==pins[path] and report['original_pdf_sha256']==source['original']['sha256']==case['native_path']['original_pdf_sha256']
                assert report['verifier_sha256']==hashlib.sha256((ROOT/'analysis/eddy_pdf_line_spans_v1.py').read_bytes()).hexdigest()
                assert report['span_math_sha256']==hashlib.sha256((ROOT/'analysis/eddy_map_spans_v1.py').read_bytes()).hexdigest()
                assert r['entity_id']==case['owner_id'] and r['category']=='size' and r['unit']=='km' and r['value'] is None
                assert r['period_start'] is None and r['period_end'] is None and r['rights_screened_release_eligible'] is False
                assert r['evidence_role']=='map_read_native_frontal_line_reference'
                component=r['map_span_component'];calculation=span_interval(case,component)
                assert r['metric']=='source_native_frontal_line_'+component+'_span'
                assert calculation==report['spans'][component] and r['range_value']==calculation['range_km']
                map_values={'source_map_estimate':{'case':case,'component':component,'calculation':calculation}}
            if r.get('arrow_span_case_index') is not None:
                assert all(r.get(k) is None for k in ['map_case_index','audit_span_case_index','colour_span_case_index'])
                case=batch['arrow_span_cases'][r['arrow_span_case_index']];validate_arrow_span_case(case)
                report=read(batch['source_pixel_report'])
                assert report['status']=='PASS' and report['source_pixels_verified'] and report['no_gap_repair'] and not report['physical_footprint_admitted']
                assert report['batch_sha256']==pins[path] and report['original_pdf_sha256']==source['original']['sha256']
                assert report['verifier_sha256']==hashlib.sha256((ROOT/'analysis/eddy_arrow_spans_v1.py').read_bytes()).hexdigest()
                assert report['span_math_sha256']==hashlib.sha256((ROOT/'analysis/eddy_map_spans_v1.py').read_bytes()).hexdigest()
                proof_row=next(v for v in report['records'] if v['name']==case['source_name'])
                assert proof_row['source_extrema_pixels_verified'] and proof_row['closed_outline_gate_rejected'] and proof_row['bbox_xyxy']==case['outline']['bbox_xyxy']
                assert case['owner_id']==r['entity_id'] and r['category']=='size' and r['unit']=='km'
                assert case['source_name']==identities[r['entity_id']]['name'] and r['entity_id'].endswith('-primary')
                registry=next(v for v in read('research/named-loop-current-eddies.json')['entries'] if v['source_number']==int(r['entity_id'].split('-')[1]))
                assert (case['registry_primary_name'],case['registry_primary_initial_separation'])==(registry['name'],registry['initial_separation'])
                assert r['metric']=='plotted_circulation_arrow_'+r['map_span_component']+'_extremum_arc_span'
                assert r['period_start']==r['period_end']==case['date']
                assert r['evidence_role']=='map_read_circulation_arrow_reference' and r['rights_screened_release_eligible'] is False
                calculation=span_interval(case,r['map_span_component']);assert calculation==proof_row['spans'][r['map_span_component']]
                assert r['range_value']==calculation['range_km']
                map_values={'source_map_estimate':{'case':case,'component':r['map_span_component'],'calculation':calculation}}
            if r.get('author_animation_patch_case_index') is not None:
                case=batch['author_animation_patch_cases'][r['author_animation_patch_case_index']]
                validate_author_patch_record(case,r)
                report=read(batch['source_pixel_report']);review=read(source['source_review_file'])
                assert report['status']=='PASS' and report['source_pixels_verified'] and report['source_palette_verified']
                assert report['batch_sha256']==pins[path] and report['original_gif_sha256']==source['original']['sha256']
                assert report['verifier_sha256']==hashlib.sha256((ROOT/'analysis/eddy_author_animation_patch_v1.py').read_bytes()).hexdigest()
                assert report['patches']==case['patch_cases'] and report['physical_footprint_admitted'] is False
                assert pins[source['source_review_file']]==source['source_review_sha256']
                assert review['status']=='QUALIFIED_ATWATER_AUTHOR_IMAGE_PATCH_VERIFIED' and review['owner_id']==r['entity_id']
                assert review['source']['original_gif']==source['original'] and not review['source']['peer_reviewed']
                assert review['source']['repository_commit']=='6af0827c0e20c8d4a548a9d9ad750df0d4ca4ee5'
                assert not review['source_case_association']['physical_crosswalk_verified'] and not review['field_qualification']['exact_product_verified']
                legacy=next(v for v in read('research/named-loop-current-eddies.json')['entries'] if v['source_number']==76)
                assert (legacy['name'],legacy['initial_separation'])==('Atwater','2023-05-18')
                calculation=author_patch_spans(case,r['map_span_component'])
                assert calculation==report['spans'][r['map_span_component']]==review['operator']['derived_spans'][r['map_span_component']]
                map_values={'source_map_estimate':{'case':case,'component':r['map_span_component'],'calculation':calculation}}
            if r.get('colour_span_case_index') is not None:
                assert r.get('map_case_index') is None and r.get('audit_span_case_index') is None
                case=batch['colour_span_cases'][r['colour_span_case_index']];validate_colour_span_case(case)
                report=read(batch['source_pixel_report'])
                assert report['status']=='PASS' and report['source_pixels_verified'] and report['source_palette_verified']
                assert report['batch_sha256']==pins[path] and report['original_pdf_sha256']==source['original']['sha256']
                assert report['verifier_sha256']==hashlib.sha256((ROOT/'analysis/eddy_colour_spans_v1.py').read_bytes()).hexdigest()
                assert report['span_math_sha256']==hashlib.sha256((ROOT/'analysis/eddy_map_spans_v1.py').read_bytes()).hexdigest()
                assert report['patches']==case['patch_cases'] and report['source_level_unit'] is None and not report['full_ring_boundary_admitted']
                assert case['owner_id']==r['entity_id'] and r['category']=='size' and r['unit']=='km'
                assert r['metric']=='source_colour_level_patch_'+r['map_span_component']+'_bounding_arc_span'
                assert r['period_start']==r['period_end']==case['date']
                assert r['evidence_role']=='map_read_source_colour_patch_reference' and r['rights_screened_release_eligible'] is False
                calculation=colour_spans(case,r['map_span_component']);assert calculation==report['spans'][r['map_span_component']]
                assert r['range_value']==calculation['range_km']
                map_values={'source_map_estimate':{'case':case,'component':r['map_span_component'],'calculation':calculation}}
            if r.get('audit_span_case_index') is not None:
                assert r.get('map_case_index') is None
                case=batch['audit_span_cases'][r['audit_span_case_index']]
                audit=read(case['audit_file']);assert pins[case['audit_file']]==case['audit_sha256']
                validate_audit_span_case(case,audit,pins[case['audit_file']])
                report=read(batch['source_pixel_report'])
                assert report['status']=='PASS' and report['source_pixels_verified'] and report['prior_rejected_paths_remain_excluded']
                assert report['verifier_sha256']==hashlib.sha256((ROOT/'analysis/eddy_audit_spans_v1.py').read_bytes()).hexdigest()
                for proof_path,pin in report['input_sha256'].items():
                    actual=hashlib.sha256((ROOT/proof_path).read_bytes()).hexdigest();assert actual==pin; pins[proof_path]=actual
                assert case['owner_id']==r['entity_id'] and r['category']=='size' and r['unit']=='km'
                assert r['metric']=='figure_contour_candidate_'+r['map_span_component']+'_bounding_arc_span'
                assert r['period_start']==r['period_end']==case['date']
                assert r['evidence_role']=='map_read_editorial_candidate_reference' and r['rights_screened_release_eligible'] is False
                calculation=audit_spans(case,r['map_span_component']);assert r['range_value']==calculation['range_km']==report['spans'][r['map_span_component']]['range_km']
                map_values={'source_map_estimate':{'case':case,'component':r['map_span_component'],'calculation':calculation}}
            if r.get('map_case_index') is not None:
                case=batch['map_cases'][r['map_case_index']];validate_map_case(case)
                assert case['owner_id']==r['entity_id'] and case['source_name']==identities[r['entity_id']]['name']
                assert r['entity_id'].endswith('-primary') and r['category']=='size' and r['unit']=='km'
                assert r['period_start']==r['period_end']==case['date']
                assert r['evidence_role']=='map_read_named_case_reference' and r['rights_screened_release_eligible'] is False
                registry=next(v for v in read('research/named-loop-current-eddies.json')['entries'] if v['source_number']==int(r['entity_id'].split('-')[1]))
                assert (case['registry_primary_name'],case['registry_primary_initial_separation'])==(registry['name'],registry['initial_separation'])
                if case.get('source_attribution',{}).get('method')=='dated_2021_figure9_with_unresolved_duplicate_caption':
                    validate_wilde_provisional_map(r,case)
                    review=read(source['source_review_file']);proof=read(batch['source_pixel_report'])
                    assert pins[source['source_review_file']]==source['source_review_sha256']
                    assert review['status']=='PROVISIONAL_2021_FIGURE9_ONLY_DUPLICATE_UNRESOLVED'
                    assert review['source_case']==case and review['duplicate_caption_resolved'] is False
                    assert review['wilde_ii_measurements_admitted']==0 and review['later_2022_panels_admitted'] is False
                    assert review['physical_identity_established'] is False and review['physical_boundary_established'] is False
                    assert review['prior_exclusion_preserved']['sha256']==pins[review['prior_exclusion_preserved']['file']]
                    assert proof['status']=='PASS' and proof['batch_sha256']==pins[path]
                    assert proof['verifier_sha256']==hashlib.sha256((ROOT/'analysis/eddy_map_spans_v1.py').read_bytes()).hexdigest()
                    assert proof['original_pdf_sha256']==source['original']['sha256']=='9b4bcb00763d730773f8cf71a1ab1e22e1b932f5aeafd81282f331045375149a'
                    assert proof['source_pixels_verified'] is True and proof['duplicate_figure_images_verified'] is True
                    assert len(proof['records'])==1 and proof['records'][0]['name']=='Wilde' and proof['records'][0]['date']==case['date']
                    assert proof['records'][0]['spans']=={c:span_interval(case,c)['range_km'] for c in ['east_west','north_south']}
                calculation=span_interval(case,r['map_span_component']);assert r['range_value']==calculation['range_km']
                map_values={'source_map_estimate':{'case':case,'component':r['map_span_component'],'calculation':calculation}}
            if r.get('model_table_row_index') is not None:
                raw=batch['model_table_rows'][r['model_table_row_index']]
                assert raw['mapped_entity_id']==r['entity_id']
                assert r['evidence_role']=='published_model_case_reference' and r['model_context']['model']=='POLCOMS'
                if r['category']=='structure':
                    assert raw['depth_relation']=='approximately' and r['value']==raw['penetration_depth_m'] and r['unit']=='m'
                    assert r['period_start']==r['period_end']=='2000-06-10'
                else:
                    assert r['category']=='kinematics' and r['value'] is None and r['unit']=='m/s'
                    assert r['range_value']==raw['velocity_range_m_s']
            if r['entity_id'].endswith('-secondary'):
                a=r['independent_named_case']
                assert a['source_name']==identities[r['entity_id']]['name']
                assert a['association_is_verified'] is False and a['primary_values_inherited'] is False
                assert r['evidence_role'] in ['qualified_published_named_case_reference','graph_digitized_named_case_reference'] and r['rights_screened_release_eligible'] is False
            if r.get('source_plot_estimate'):
                validate_plot_estimate(r['source_plot_estimate'],r['range_value'])
                assert r['value'] is None and r['unit']=='km' and r['category']=='size'
                assert r['evidence_role']=='graph_digitized_named_case_reference'
            if r.get('named_case_association'):
                a=r['named_case_association'];legacy=read('research/named-loop-current-eddies.json')
                original=next(v for v in legacy['entries'] if v['source_number']==a['registry_source_number'])
                assert r['entity_id']==f"eddy:horizon:loop-{a['registry_source_number']:02}-primary"
                assert (a['registry_name'],a['registry_initial_separation'])==(original['name'],original['initial_separation'])
                assert a['source_name']==original['name'] or (a['source_name'],original['name'])==('Millenium','Millennium')
                assert a['dates_equal']==(a['study_separation_date']==original['initial_separation'])
                assert a['physical_crosswalk_verified'] is False and r['rights_screened_release_eligible'] is False
                assert r['period_start']==r['period_end']==a['study_separation_date']
                assert r['metric']=='published_named_case_separation_contour_area' and r['category']=='size' and r['unit']=='km2'
            assert r['category'] in ['size','duration','recurrence','travel','structure','kinematics']
            assert any(r.get(k) is not None for k in ['value','range_value','upper_bound','lower_bound'])
            interval=r.get('range_value')
            if interval is not None:validate_numeric_interval(r)
            if r['metric']=='source_main_track_calendar_supported_elapsed_span':
                c=r['calendar_support'];assert r['category']=='duration' and r['unit']=='day'
                start0,start1,end0,end1=[date.fromisoformat(c[k]) for k in ['start_date_min','start_date_max','end_date_min','end_date_max']]
                assert c['start_precision']==c['end_precision']=='month' and not c['chronology_conditioned']
                assert start0.day==end0.day==1
                assert start1==date(start0.year,start0.month,calendar.monthrange(start0.year,start0.month)[1])
                assert end1==date(end0.year,end0.month,calendar.monthrange(end0.year,end0.month)[1])
                assert interval==c['unconditioned_elapsed_day_range']==[(end0-start1).days,(end1-start0).days]
            if r.get('upper_bound') is not None:assert r['upper_bound']>0 and r['value'] is None
            if r.get('lower_bound') is not None:
                assert isinstance(r['lower_bound'],(int,float)) and math.isfinite(r['lower_bound']) and r['lower_bound']>0 and r['value'] is None
                assert isinstance(r.get('lower_bound_exclusive',False),bool)
            if r.get('calculation'):
                c=r['calculation']
                if c.get('method')=='spherical_sampled_station_separation_v1':validate_station_distance(r)
                elif c.get('method')=='gridded_adt_named_source_case_v1':validate_gridded_case(r,read(c['report_file']))
                elif c.get('method')=='source_named_nelson_frontal_chart_spans_v1':
                    report=read(c['report_file']);assert pins[c['report_file']]==c['report_sha256']==source['source_review_sha256']
                    validate_named_frontal_chart_reference(r,report)
                    assert report['original']==source['original']
                    for key in ['method','axis_math']:
                        assert hashlib.sha256((ROOT/report[key+'_file']).read_bytes()).hexdigest()==report[key+'_sha256']
                elif c.get('method')=='source_hot_core_pre_detachment_frontal_lobe_spans_v1':
                    report=read(c['report_file']);assert pins[c['report_file']]==c['report_sha256']==source['source_review_sha256']
                    validate_frontal_lobe_reference(r,report)
                    assert report['original']==source['original']
                    for key in ['method','axis_math']:
                        assert hashlib.sha256((ROOT/report[key+'_file']).read_bytes()).hexdigest()==report[key+'_sha256']
                elif c.get('method')=='osw_speed_contour_named_source_case_v1':
                    report=read(c['report_file']);assert pins[c['report_file']]==c['report_sha256']==source['source_review_sha256']
                    validate_speed_core_reference(r,report)
                    assert report['source_tests_passed']=={'geometry':7,'speed_core':12}
                    for filename,pin in report['cloud_input_sha256'].items():
                        assert hashlib.sha256((ROOT/filename).read_bytes()).hexdigest()==pin
                    a=report['case_associations'][r['entity_id']]
                    assert a['source_name']==identities[r['entity_id']]['name']
                    locations=read(a['position_reference_file']);assert pins[a['position_reference_file']]==a['position_reference_sha256']
                    position=next(v for v in locations['records'] if v['id']==a['position_reference_id'])
                    assert position['entity_id']==r['entity_id'] and position['source_name']==a['source_name']
                    assert position['observation_date']==a['date'] and a['source_point']==[position['navigation_candidate']['longitude_deg'],position['navigation_candidate']['latitude_deg']]
                    assert position['physical_crosswalk_verified'] is False and position['size_inferred'] is False
                    read(report['primary_location_source_review_file'])
                    assert pins[report['primary_location_source_review_file']]==report['primary_location_source_review_sha256']
                else:assert c['multiplier']*c['deformation_radius_km']==c['unrounded_km'] and round(c['unrounded_km'])==r['value']
            if r.get('basis_source_file'):
                basis=read(r['basis_source_file']);events=pointer(basis,r['basis_source_pointer'])
                assert hashlib.sha256(json.dumps(events,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()==r['basis_sha256']
                assert [v['observation_date'] for v in events]==[r['period_start'],r['period_end']]
                assert r['value']==(date.fromisoformat(r['period_end'])-date.fromisoformat(r['period_start'])).days
            if r.get('registry_row_index') is not None:
                raw=batch['registry_rows'][r['registry_row_index']]
                assert r['entity_id']==f"eddy:horizon:loop-{raw['source_number']:02}-primary"
                assert r['rights_screened_release_eligible'] is False
                if r['metric']=='registry_reported_maximum_surface_current':
                    assert r['unit']=='knots' and r['value']==float(raw['max_surface_current_knots_as_reported'])
                elif r['metric']=='registry_separation_to_dissipation_calendar_span':
                    start0,start1,precision=registry_date_bounds(raw['initial_separation_as_reported'])
                    end0,end1,_=registry_date_bounds(raw['dissipation_as_reported'])
                    unconstrained=[(end0-start1).days,(end1-start0).days]
                    assert r['range_value']==[max(0,unconstrained[0]),unconstrained[1]]
                    assert r['calendar_support']=={'start_date_min':start0.isoformat(),'start_date_max':start1.isoformat(),'end_date_min':end0.isoformat(),'end_date_max':end1.isoformat(),'start_precision':precision,'end_precision':'month','unconditioned_elapsed_day_range':unconstrained,'chronology_conditioned':unconstrained[0]<0}
                else:raise ValueError('Unknown registry interpretation')
            add(r['id'],r['entity_id'],r['category'],r['metric'],r['value'],r['unit'],path,f'/records/{n}',batch,
                source_url=source['url'],source_access=source['access'],source_id=r['source_id'],
                definition=r['definition'],scope=r['scope'],qualification=r['qualification'],
                **{k:r[k] for k in ['period_start','period_end','period_label','period_precision','case_label','component_label','right_censored','range_value','range_kind','lower_bound','lower_bound_exclusive','upper_bound','upper_bound_exclusive','calculation','basis_source_file','basis_source_pointer','basis_sha256','depth_m','evidence_role','registry_row_index','registry_column','calendar_support','rights_screened_release_eligible','named_case_association','independent_named_case','source_plot_estimate','model_context','model_table_row_index','detection_context','profile_context','case_alias_association'] if k in r},**map_values)
        class_legacy={v['source_number']:v for v in read('research/named-loop-current-eddies.json')['entries']} if batch.get('size_classifications') else {}
        for n,c in enumerate(batch.get('size_classifications',[])):
            owner=c['entity_id'];assert owner in identities and not any(v['id']==c['id'] for v in classifications)
            assert c['label'] in ['Small','Medium','Huge'] and isinstance(c['source_year'],int)
            assert 1900<=c['source_year']<=2100
            assert identities[owner]['name']==c['registry_name']
            original=class_legacy[int(owner.split('-')[1])]
            assert c['registry_primary_initial_separation']==original['initial_separation'] and c['registry_primary_name']==original['name']
            assert c['registry_name']==original['secondary_name' if owner.endswith('-secondary') else 'name']
            assert c['source_name']==c['registry_name'] or (c['source_name'],c['registry_name']) in [('Titantic','Titanic'),('Millenium','Millennium')]
            assert c['source_name_match']==('exact' if c['source_name']==c['registry_name'] else 'candidate_spelling_variant')
            assert all(c[k] is None for k in ['numeric_thresholds','value','unit'])
            assert all(c[k] is False for k in ['association_is_verified','source_year_is_separation_year','rank_eligible','seasonal_playback_eligible','physical_state_join_eligible','rights_screened_release_eligible'])
            source=batch['sources'][c['source_id']]
            classifications.append({**c,'source_url':source['url'],'source_access':source['access'],
                'source_file':path,'source_pointer':f'/size_classifications/{n}','source_sha256':pins[path],'raw_record':c})
        applied.append({'file':path,'baseline_count':batch['baseline_evidence_count'],'preserved_baseline_sha256':prior,'added':len(batch['records'])})
    records=[]
    for identifier,current in identities.items():
        owned=[r for r in evidence if r['entity_id']==identifier]
        geographic=next((r for r in geo['entries'] if 'eddy:geography:'+r['id']==identifier),None)
        published=next((r for r in loops['entries'] if 'eddy:'+r['eddy_id']==identifier),None)
        linked_primary=None
        if current['source_collection']=='horizon_loop_current' and current['source_record_id'].endswith('-secondary'):
            parent='eddy:horizon:'+current['source_record_id'].removesuffix('-secondary')+'-primary'
            assert parent in identities
            linked_primary={'entity_id':parent,'name':identities[parent]['name'],'url':'eddies.html?id='+parent,
                'evidence_ids':[r['id'] for r in evidence if r['entity_id']==parent],
                'relation':('Associated primary registry row; this entry has independent named source-case references. No primary measurements assigned.' if owned else 'Associated primary registry row only; no independent secondary measurement assigned.')}
        records.append({'entity_id':identifier,'name':current['name'],'basin':current['basin'],
            'identity_level':current['identity_level'],'source_collection':current['source_collection'],
            'source_url':current['source_url'],'source_pointer':'/entries/'+str(inventory['entries'].index(current)),
            'evidence_ids':[r['id'] for r in owned],'categories':sorted({r['category'] for r in owned}),
            'size_classification_ids':[c['id'] for c in classifications if c['entity_id']==identifier],
            'size_gap':not any(r['category']=='size' for r in owned),
            'duration_gap':not any(r['category']=='duration' for r in owned),
            'status':'has_measurements' if owned else 'linked_primary_context' if linked_primary else 'needs_measurements',
            'linked_primary_context':linked_primary,'registry_context':registry_contexts.get(identifier),
            'event_date':current.get('source_event_date') if current['identity_evidence']=='numbered_primary_separation' else None,
            'date_context':current.get('date_evidence'),
            'paper_window_context':({'start':published['observation_start'],'end':published['observation_end'],'interpretation':published['interpretation']} if published else None),
            'identity_note':geographic.get('identity_note') if geographic else None,
            'possible_same_ring_as':published.get('possible_same_ring_as_horizon_id') if published else None,
            'candidate_crosswalk_is_verified':False,'whole_lifetime_days':None,
            'annual_size_range_km':None,'closed_footprint':None,
            'current_card_url':'object.html?id='+identifier,'atlas_url':'index.html'+current['atlas_anchor'],
            'next_action':'Recover definition-qualified dated size and duration evidence; verify identity before joining satellite detections.'})
    owners=lambda category:{r['entity_id'] for r in evidence if r['category']==category}
    return {'schema':'osw.eddy-measurement-register.v1','status':'MEASUREMENT_GAP_FILLING_IN_PROGRESS',
        'rules_file':RULES,'rules_sha256':hashlib.sha256((ROOT/RULES).read_bytes()).hexdigest(),
        'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'input_sha256':pins,
        'method_implementation_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['analysis/eddy_cartographic_circle_spans_v1.py','analysis/eddy_author_animation_patch_v1.py','analysis/eddy_map_spans_v1.py','analysis/eddy_audit_spans_v1.py','analysis/eddy_colour_spans_v1.py','analysis/eddy_arrow_spans_v1.py','analysis/eddy_pdf_line_spans_v1.py','analysis/eddy_height_profiles_v1.py','analysis/eddy_scale_bar_spans_v1.py','analysis/eddy_visible_model_front_v1.py','analysis/eddy_gridded_case_summary_v1.py','analysis/eddy_altimetry_contours_v1.py','analysis/eddy_operational_chart_spans_v1.py','analysis/eddy_source_bold_isoline_spans_v1.py']},
        'first_batch_evidence_sha256':baseline_sha,'first_batch_evidence_preserved':40,
        'additional_batches':applied,
        'scope':inventory['scope'],'identity_rule':'Source records remain separate; possible Horizon/published matches are not verified identity joins.',
        'release_scope':'Full research candidate: 136 source identities. The separate rights-screened release excludes 96 Horizon registry labels.',
        'counts':{'identities':len(records),'individual_source_records':sum(r['identity_level']=='individual_eddy' for r in records),
            'recurrent_regions':sum(r['identity_level']=='recurrent_eddy_region' for r in records),'families':sum(r['identity_level']=='eddy_family' for r in records),
            'evidence_records':len(evidence),'size_records':sum(r['category']=='size' for r in evidence),
            'size_owners':len(owners('size')),'duration_owners':len(owners('duration')),'recurrence_owners':len(owners('recurrence')),
            'structure_owners':len(owners('structure')),'kinematics_owners':len(owners('kinematics')),
            'non_registry_entries':sum(r['source_collection']!='horizon_loop_current' for r in records),
            'non_registry_entries_with_references':sum(r['source_collection']!='horizon_loop_current' and bool(r['evidence_ids']) for r in records),
            'registry_entries_with_own_references':sum(r['source_collection']=='horizon_loop_current' and bool(r['evidence_ids']) for r in records),
            'linked_primary_context_entries':sum(r['linked_primary_context'] is not None and not r['evidence_ids'] for r in records),
            'secondary_entries_with_own_references':sum(r['entity_id'].endswith('-secondary') and bool(r['evidence_ids']) for r in records),
            'entries_without_numeric_or_primary_context':sum(not r['evidence_ids'] and r['linked_primary_context'] is None for r in records),
            'identities_with_measurements':sum(bool(r['evidence_ids']) for r in records),
            'identities_without_measurements':sum(not r['evidence_ids'] for r in records),
            'conflicted_size_records':sum(r['value_conflict'] for r in evidence),
            'source_track_spans':sum(r['metric']=='source_track_elapsed_span' for r in evidence)},
        'size_classification_counts':{'records':len(classifications),'owners':len({c['entity_id'] for c in classifications}),
            'owners_with_numeric_size_gap':sum(bool(r['size_classification_ids']) and r['size_gap'] for r in records),
            'labels':{label:sum(c['label']==label for c in classifications) for label in sorted({c['label'] for c in classifications})}},
        'size_classifications':classifications,
        'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def main():
    document=build();(ROOT/JSON_PATH).write_bytes((json.dumps(document,indent=1,ensure_ascii=False)+'\n').encode())
    fields=['entity_id','id','category','metric','value','unit','range_value_json','range_kind','lower_bound','lower_bound_exclusive','upper_bound','upper_bound_exclusive','standard_deviation','sample_count','period_start','period_end','period_label','period_precision','component_label','case_label','right_censored','value_conflict','date_conflict','source_claims_json','calculation_json','calendar_support_json','rights_screened_release_eligible','evidence_role','definition','scope','qualification','source_access','source_url','source_locator','source_file','source_pointer','source_sha256']
    fields.extend(['named_case_association_json','independent_named_case_json','source_plot_estimate_json','model_context_json','detection_context_json','source_map_estimate_json','profile_context_json'])
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=fields,extrasaction='ignore');writer.writeheader()
    for r in document['evidence']:writer.writerow({**r,'source_claims_json':json.dumps(r['source_claims'],ensure_ascii=False),'range_value_json':json.dumps(r.get('range_value')),'calculation_json':json.dumps(r.get('calculation')),'calendar_support_json':json.dumps(r.get('calendar_support')),'named_case_association_json':json.dumps(r.get('named_case_association')),'independent_named_case_json':json.dumps(r.get('independent_named_case')),'source_plot_estimate_json':json.dumps(r.get('source_plot_estimate')),'model_context_json':json.dumps(r.get('model_context')),'detection_context_json':json.dumps(r.get('detection_context')),'source_map_estimate_json':json.dumps(r.get('source_map_estimate')),'profile_context_json':json.dumps(r.get('profile_context'))})
    (ROOT/CSV_PATH).write_bytes(out.getvalue().encode());print(json.dumps(document['counts']))
    fields=['id','entity_id','source_name','source_year','label','registry_name','registry_primary_name','registry_primary_initial_separation','source_name_match','numeric_thresholds','value','unit','association_is_verified','source_year_is_separation_year','rank_eligible','seasonal_playback_eligible','physical_state_join_eligible','rights_screened_release_eligible','definition','qualification','source_access','source_url','source_locator','source_file','source_pointer','source_sha256']
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=fields,extrasaction='ignore');writer.writeheader()
    writer.writerows(document['size_classifications'])
    (ROOT/'research/eddy-size-classifications-v1.csv').write_bytes(out.getvalue().encode())


if __name__=='__main__':main()
