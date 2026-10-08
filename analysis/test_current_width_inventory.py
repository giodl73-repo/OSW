import copy
import json
import unittest
from pathlib import Path
from check_current_width_inventory import validate
ROOT = Path(__file__).resolve().parents[1]

class WidthInventoryTests(unittest.TestCase):
    def test_mean_offshore_extent_preserves_surface_and_sampling_scope(self):
        i=next(i for i,r in enumerate(self.document['measurements']) if r['phase_kind']=='mean_offshore_extent_range')
        r=self.document['measurements'][i]
        self.assertEqual(r['width_range_km'],[250,300])
        self.assertIsNone(r['approximate_width_km'])
        validate(self.document,self.ledger)
        for key,value in [('approximate_width_km',275),('width_range_km',[200,300]),('phase_kind','regional_summary'),('fixed_layer_bounds_m',[0,1000]),('calendar_months',[6,7]),('section_geometry',{'type':'LineString'}),('boundary_sides','paired'),('full_width_inference_eligible',True),('seasonal_playback_eligible',True),('boundary_rule','velocity > 0.1 m/s'),('current_id','mindanao-undercurrent')]:
            bad=copy.deepcopy(self.document);bad['measurements'][i][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate(bad,self.ledger)
        for key,value in [('audit_sha256','changed'),('velocity_threshold_m_s',0.1),('campaign_context_is_mean_sampling_interval',True),('velocity_reference_depth_range_m',[0,200]),('mean_line_endpoints_lon_lat',[[126,8],[130,8]]),('source_date_discrepancy','')]:
            bad=copy.deepcopy(self.document);bad['measurements'][i]['mean_offshore_context'][key]=value
            with self.subTest(context=key),self.assertRaises(ValueError):validate(bad,self.ledger)

    def test_alaska_gulf_typical_width_does_not_acquire_winter_dates_or_edges(self):
        index=next(i for i,r in enumerate(self.document['measurements']) if r['current_id']=='alaska-coastal-gulf')
        row=self.document['measurements'][index]
        self.assertEqual(row['approximate_width_km'],35)
        self.assertIsNone(row['width_range_km'])
        validate(self.document,self.ledger)
        for key,value in [('approximate_width_km',37),('width_range_km',[20,35]),('current_id','alaska'),('observed_period',{'start':'2012-10-19','end':'2013-03-16'}),('calendar_months',[10,11,12,1,2,3]),('fixed_layer_bounds_m',[0,100]),('boundary_rule','paired speed edges'),('seasonal_playback_eligible',True),('annual_extrema_eligible',True)]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][index][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate(invalid,self.ledger)

    def test_black_sea_range_rejects_midpoint_temporal_and_source_relabeling(self):
        index=next(i for i,r in enumerate(self.document['measurements']) if r['current_id']=='black-sea-rim')
        self.assertEqual(self.document['measurements'][index]['width_range_km'],[40,80])
        validate(self.document,self.ledger)
        for key,value in [('approximate_width_km',60),('width_range_km',[40,90]),('section_geometry',{'type':'LineString'}),('fixed_layer_bounds_m',[150,300]),('calendar_months',[1,2,3]),('annual_extrema_eligible',True),('seasonal_playback_eligible',True),('full_width_inference_eligible',True),('source_url','https://example.com'),('boundary_rule','speed > 0.1 m/s')]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][index][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate(invalid,self.ledger)
        for key,value in [('audit_sha256','changed'),('boundary_coordinates_supplied',True),('pycnocline_is_measurement_layer',True)]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][index]['regional_range_context'][key]=value
            with self.subTest(context=key),self.assertRaises(ValueError):validate(invalid,self.ledger)

    def test_stream_means_preserve_threshold_averaging_and_scope(self):
        indexes=[i for i,r in enumerate(self.document['measurements']) if r['phase_kind']=='stream_mean_threshold_summary']
        self.assertEqual(len(indexes),3)
        self.assertEqual({self.document['measurements'][i]['approximate_width_km'] for i in indexes},{207,210,218})
        for index in indexes:
            for key,value in [('approximate_width_km',313),('width_range_km',[207,218]),('fixed_layer_bounds_m',[0,200]),('calendar_months',[12,1,2]),('observed_period',{'start':'1993-01-01','end':'2008-12-31'}),('seasonal_playback_eligible',True),('annual_extrema_eligible',True),('current_id','kuroshio-extension')]:
                invalid=copy.deepcopy(self.document);invalid['measurements'][index][key]=value
                with self.subTest(index=index,key=key),self.assertRaises(ValueError):validate(invalid,self.ledger)
            for key,value in [('velocity_threshold_m_s',.4),('width_of_mean_velocity_field',True),('boundary_detection_precedes_averaging',False),('study_period_years',[1991,2009]),('season','spring'),('isobath_is_measurement_layer',True),('intrusive_reach_is_mainstream_width',True),('audit_sha256','changed'),('source_pdf_sha256','changed')]:
                invalid=copy.deepcopy(self.document);invalid['measurements'][index]['stream_mean_context'][key]=value
                with self.subTest(index=index,context=key),self.assertRaises(ValueError):validate(invalid,self.ledger)

    def test_monthly_fits_preserve_month_boundary_and_averaging_conventions(self):
        indexes=[i for i,r in enumerate(self.document['measurements']) if r['phase_kind']=='monthly_climatological_fit']
        self.assertEqual(len(indexes),2)
        self.assertEqual({self.document['measurements'][i]['approximate_width_km'] for i in indexes},{89,132})
        for index in indexes:
            for key,value in [('approximate_width_km',105),('width_range_km',[89,132]),('fixed_layer_bounds_m',[0,80]),('observed_period',{'start':'1993-01-01','end':'2002-08-31'}),('calendar_months',[1]),('annual_extrema_eligible',True),('seasonal_playback_eligible',True),('measurement_type','published_regional_seasonal_summary')]:
                invalid=copy.deepcopy(self.document);invalid['measurements'][index][key]=value
                with self.subTest(index=index,key=key),self.assertRaises(ValueError):validate(invalid,self.ledger)
            for key,value in [('source_width_coefficient',1.762747),('track_angle_degrees',0),('track_id','a177'),('calendar_month',1),('mean_width_is_width_of_mean_profile',True),('complete_monthly_curve_extracted',True),('transport_layer_is_width_measurement_layer',True),('rms_is_confidence_interval',True),('source_pdf_sha256','changed')]:
                invalid=copy.deepcopy(self.document);invalid['measurements'][index]['monthly_fit_context'][key]=value
                with self.subTest(index=index,context=key),self.assertRaises(ValueError):validate(invalid,self.ledger)

    def test_east_australian_summary_cannot_become_influence_or_seasonal_range(self):
        index=next(i for i,r in enumerate(self.document['measurements']) if r['current_id']=='east-australian')
        self.assertEqual(self.document['measurements'][index]['approximate_width_km'],30)
        for key,value in [('approximate_width_km',100),('approximate_width_km',240),('approximate_width_km',200),('width_range_km',[30,100]),('fixed_layer_bounds_m',[0,200]),('calendar_months',[2]),('observed_period',{'start':'2015-01-01','end':'2025-12-31'}),('phase_kind','seasonal_summary'),('current_id','east-australian-extension')]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][index][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):validate(invalid,self.ledger)
        for key,value in [('audit_file','research/labrador-thompson-2009-regional-width-scope-audit.json'),('audit_sha256','changed'),('reported_depth_extent_is_fixed_measurement_layer',True)]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][index]['regional_scalar_context'][key]=value
            with self.subTest(context=key),self.assertRaises(ValueError):validate(invalid,self.ledger)

    def test_oblique_mean_sections_preserve_orientation_source_and_identity(self):
        indexes=[i for i,r in enumerate(self.document['measurements']) if r.get('mean_section_context',{}).get('section_axis_kind')=='oblique']
        self.assertEqual(len(indexes),3)
        validate(self.document,self.ledger)
        for index in indexes:
            for key,value in [('section_longitude_degrees_east',-50),('section_endpoints_lon_lat',[[-60,10],[-56,12]]),('rotation_angle_degrees',0),('source_flow_label','NBC4'),('source_identity_mapping','canonical_alias'),('source_latitude_limits_degrees_north',[9,12]),('audit_sha256','changed')]:
                invalid=copy.deepcopy(self.document);invalid['measurements'][index]['mean_section_context'][key]=value
                with self.subTest(index=index,key=key),self.assertRaises(ValueError):validate(invalid,self.ledger)
            invalid=copy.deepcopy(self.document);invalid['measurements'][index]['mean_section_context'].update(section_axis_kind='meridional',section_longitude_degrees_east=-42)
            with self.subTest(index=index,kind='meridional'),self.assertRaises(ValueError):validate(invalid,self.ledger)
            for key,value in [('approximate_width_km',20),('calendar_months',[3,4,5]),('annual_extrema_eligible',True),('seasonal_playback_eligible',True),('observed_period',{'start':'1993-01-01','end':'2017-12-31'}),('current_id','guiana' if self.document['measurements'][index]['current_id']=='north-brazil' else 'north-brazil')]:
                invalid=copy.deepcopy(self.document);invalid['measurements'][index][key]=value
                with self.subTest(index=index,key=key),self.assertRaises(ValueError):validate(invalid,self.ledger)

    def test_regional_scalar_rejects_invented_section_and_annual_support(self):
        index=next(i for i,r in enumerate(self.document['measurements']) if r['phase_kind']=='regional_scalar_summary')
        validate(self.document,self.ledger)
        for key,value in [('approximate_width_km',100),('width_range_km',[40,60]),('fixed_layer_bounds_m',[300,1000]),('observed_period',{'start':'2009-01-01','end':'2009-12-31'}),('calendar_months',[1]),('section_geometry',{'type':'LineString'}),('annual_extrema_eligible',True),('seasonal_playback_eligible',True),('full_width_inference_eligible',True),('width_metric','paired_velocity_edges')]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][index][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate(invalid,self.ledger)
        for key,value in [('audit_sha256','changed'),('bathymetry_is_measurement_layer',True),('boundary_coordinates_supplied',True)]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][index]['regional_scalar_context'][key]=value
            with self.subTest(context=key),self.assertRaises(ValueError):validate(invalid,self.ledger)

    def test_ensemble_angular_summary_rejects_invented_location_and_annual_range(self):
        indexes=[i for i,r in enumerate(self.document['measurements']) if r['phase_kind']=='ensemble_angular_summary']
        self.assertEqual(len(indexes),2)
        self.assertEqual({self.document['measurements'][i]['approximate_width_km'] for i in indexes},{220})
        for index in indexes:
            for key,value in [('annual_extrema_eligible',True),('seasonal_playback_eligible',True),('calendar_months',[1]),('fixed_layer_bounds_m',[150,300]),('section_geometry',{'type':'LineString'}),('observed_period',{'start':'1990-01-01','end':'1991-01-01'}),('width_range_km',[170,220]),('width_metric','pv_front_span'),('approximate_width_km',40)]:
                invalid=copy.deepcopy(self.document);invalid['measurements'][index][key]=value
                with self.subTest(index=index,key=key),self.assertRaises(ValueError):validate(invalid,self.ledger)
            for key,value in [('source_reported_latitude_span_degrees',1.5),('source_reported_center_latitude_degrees',4),('source_section_longitude_degrees_east',-155),('normalization_center_latitude_degrees',4),('normalization_limits_are_observed_edges',True),('independent_jet_measurements',True),('shared_source_claim',False),('audit_sha256','changed')]:
                invalid=copy.deepcopy(self.document);invalid['measurements'][index]['ensemble_angular_context'][key]=value
                with self.subTest(index=index,context_key=key),self.assertRaises(ValueError):validate(invalid,self.ledger)

    def test_hydrographic_core_records_reject_velocity_or_annual_reinterpretation(self):
        indexes=[i for i,r in enumerate(self.document['measurements']) if r['phase_kind']=='campaign_hydrographic_core']
        self.assertEqual(len(indexes),6)
        validate(self.document,self.ledger)
        for key,value in [('width_metric','velocity_core'),('annual_extrema_eligible',True),('calendar_months',[10,11]),('fixed_layer_bounds_m',[100,200]),('seasonal_playback_eligible',True),('observed_period',{'start':'1999-10-08','end':'1999-11-10'}),('width_range_km',[20,60])]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][indexes[1]][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate(invalid,self.ledger)
        for key,value in [('boundary_equation','S>37'),('velocity_threshold_m_s',.1),('variation_axis','month'),('audit_sha256','changed'),('section_ids',['R02'])]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][indexes[1]]['hydrographic_core_context'][key]=value
            with self.subTest(context_key=key),self.assertRaises(ValueError):validate(invalid,self.ledger)

    def test_reported_band_limits_preserve_computed_center_and_metric(self):
        index=next(i for i,r in enumerate(self.document['measurements']) if r['id']=='atlantic-secc-1994-03-described-band-span')
        validate(self.document,self.ledger)
        for key,value in [('source_reported_latitude_limits_degrees',[-8,-5]),('source_reported_latitude_limits_degrees',[-6,-8]),('source_reported_center_latitude_degrees',-7),('normalization_center_latitude_degrees',-6),('center_role','observed_velocity_core')]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][index]['angular_span_conversion'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate(invalid,self.ledger)
        invalid=copy.deepcopy(self.document);invalid['measurements'][index]['width_metric_label']='fixed-depth full width'
        with self.assertRaises(ValueError):validate(invalid,self.ledger)

    def test_seasonal_mean_range_preserves_sampling_and_mean_definition(self):
        index=next(i for i,r in enumerate(self.document['measurements']) if r['phase_kind']=='seasonal_mean_width_range')
        validate(self.document,self.ledger)
        for key,value in [('approximate_width_km',35),('range_kind','annual_width_extrema'),('phase_kind','regional_summary'),('calendar_months',None),('seasonal_playback_eligible',True),('annual_extrema_eligible',True),('section_geometry',{'type':'LineString'})]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][index][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate(invalid,self.ledger)
        for key,value in [('mean_of_instantaneous_widths',True),('width_of_mean_section',False),('paired_edges_extracted',True),('fixed_depth_bounds_m',[100,200]),('sample_years',[2016,2005]),('sample_years',[2004,2011]),('sampled_months',[5]),('sampled_months',[True]),('cruise_ids',[]),('cruise_ids',['P320','P320']),('reference_latitude_degrees',25),('averaging_rule','')]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][index]['seasonal_mean_context'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate(invalid,self.ledger)

    def test_spatial_core_range_rejects_temporal_and_full_width_relabels(self):
        index=next(i for i,row in enumerate(self.document['measurements']) if row['phase_kind']=='climatological_core_distribution')
        validate(self.document,self.ledger)
        for key,value in [('approximate_width_km',500),('width_range_km',[294,26]),('range_kind','annual_width_extrema'),('seasonal_playback_eligible',True),('annual_extrema_eligible',True),('fixed_layer_bounds_m',[300,420]),('calendar_months',[3,4,5]),('observed_period',{'start':'2001-01-01','end':'2018-12-31'})]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][index][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate(invalid,self.ledger)
        for key,value in [('summary_statistic','mean_of_daily_widths'),('range_axis','time'),('full_width_at_each_depth',True),('averaging_before_boundary_detection',False),('velocity_threshold_m_s',0),('threshold_operator','>='),('climatology_months',[0]),('averaging_period_years',[2018,2001])]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][index]['core_distribution_context'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate(invalid,self.ledger)

    def test_dated_subsurface_band_rejects_edge_and_seasonal_inferences(self):
        index=next(i for i,row in enumerate(self.document['measurements']) if row['phase_kind']=='dated_band_section')
        validate(self.document,self.ledger)
        for key,value in [('approximate_width_km',400),('seasonal_playback_eligible',True),('annual_extrema_eligible',True),('fixed_layer_bounds_m',[80,150]),('section_geometry',{'type':'Polygon'}),('calendar_months',[3]),('observed_period',{'start':'2017-03-03','end':'2017-03-01'})]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][index][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate(invalid,self.ledger)
        for key,value in [('source_reported_latitude_limits_degrees',[1.5,-1.2]),('source_reported_depth_range_m',[150,80]),('span_is_width_at_every_depth',True),('paired_velocity_edges_diagnosed',True),('velocity_boundary_m_s',.05),('unrounded_distance_km',400)]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][index]['subsurface_band_context'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate(invalid,self.ledger)

    def test_mean_profile_width_rejects_temporal_and_boundary_conflation(self):
        index=next(i for i,row in enumerate(self.document['measurements']) if row['phase_kind']=='mean_velocity_section')
        validate(self.document,self.ledger)
        for key,value in [('seasonal_playback_eligible',True),('annual_extrema_eligible',True),('width_range_km',[860,920]),('observed_period',{'start':'1993-01-01','end':'2017-12-31'})]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][index][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate(invalid,self.ledger)
        for key,value in [('velocity_boundary_m_s',.5),('averaging_before_boundary_detection',False),('is_mean_of_instantaneous_widths',True),('averaging_period_months',{'start':'2017-12','end':'1993-01'})]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][index]['mean_section_context'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate(invalid,self.ledger)

    def setUp(self):
        self.document = json.loads((ROOT / "research/ocean-current-width-inventory.json").read_text(encoding="utf-8"))
        self.ledger = json.loads((ROOT / "research/ocean-current-almanac.json").read_text(encoding="utf-8"))

    def test_rejects_missing_identity_and_unsupported_admission(self):
        invalid = copy.deepcopy(self.document)
        invalid["current_decisions"].pop()
        with self.assertRaises(ValueError):
            validate(invalid, self.ledger)
        for key in ["whole_current_representative", "width_rank_eligible"]:
            invalid = copy.deepcopy(self.document)
            invalid["measurements"][0][key] = True
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate(invalid, self.ledger)

    def test_rejects_invalid_widths_and_annual_extrema_relabel(self):
        for value in [0, -1, float("nan"), float("inf")]:
            invalid = copy.deepcopy(self.document)
            invalid["measurements"][0]["approximate_width_km"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate(invalid, self.ledger)
        invalid = copy.deepcopy(self.document)
        invalid["seasonal_summaries"][0]["range_kind"] = "observed_annual_extrema"
        with self.assertRaises(ValueError):
            validate(invalid, self.ledger)

    def test_rejects_section_relabelling_and_invalid_geometry(self):
        section_index = next(i for i,r in enumerate(self.document["measurements"]) if r["phase_kind"] == "dated_section")
        invalid = copy.deepcopy(self.document)
        invalid["measurements"][section_index]["width_metric"] = "perpendicular_velocity_core"
        with self.assertRaises(ValueError):
            validate(invalid, self.ledger)
        invalid = copy.deepcopy(self.document)
        invalid["measurements"][section_index]["section_geometry"]["coordinates"][1][0] += 1
        with self.assertRaises(ValueError):
            validate(invalid, self.ledger)
        invalid = copy.deepcopy(self.document)
        invalid["measurements"][section_index]["observed_period"]["end"] = "2008-01-01"
        with self.assertRaises(ValueError):
            validate(invalid, self.ledger)

    def test_rejects_historical_calendar_and_provenance_forgery(self):
        index = next(i for i, row in enumerate(self.document["measurements"]) if row["current_id"] == "davidson")
        for key, value in [("calendar_months", [0, 13]), ("calendar_months", [1, 1]), ("calendar_months", [True]), ("calendar_source_locator", ""), ("historical_summary", False), ("source_publication_year", 2100), ("source_document_sha256", "not-a-digest")]:
            invalid = copy.deepcopy(self.document)
            invalid["measurements"][index][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                validate(invalid, self.ledger)

    def test_rejects_review_without_metric_numeric_admission(self):
        for key, value in [('whole_current_width_km', 20), ('annual_width_range_km', [10,20]), ('evidence', [])]:
            invalid = copy.deepcopy(self.document)
            invalid['review_assessments'][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate(invalid, self.ledger)
        invalid = copy.deepcopy(self.document)
        next(row for row in invalid['current_decisions'] if row['current_id'] == 'balearic')['width_decision'] = 'width_not_assessed'
        with self.assertRaises(ValueError):
            validate(invalid, self.ledger)

    def test_rejects_range_midpoint_confidence_and_false_season(self):
        index = next(i for i,row in enumerate(self.document['measurements']) if row['current_id'] == 'gaspe')
        for key, value in [('approximate_width_km', 15), ('range_kind', 'confidence_interval'), ('is_confidence_interval', True), ('annual_extrema_eligible', True), ('phase_kind', 'seasonal_summary'), ('width_range_km', [20,10]), ('width_range_km', [0,20]), ('calendar_months', [6,7,8])]:
            invalid = copy.deepcopy(self.document)
            invalid['measurements'][index][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate(invalid, self.ledger)

    def test_profile_scale_preserves_unresolved_depth_dates_and_full_width(self):
        validate(self.document, self.ledger)
        index=next(i for i,r in enumerate(self.document['measurements']) if r['phase_kind']=='survey_profile_composite')
        for key,value in [('width_metric','paired_e_folding_span'),('approximate_width_km',16),('boundary_sides','paired'),('full_width_inference_eligible',True),('seasonal_playback_eligible',True),('annual_extrema_eligible',True),('observed_period',{'start':'2007-05-29','end':'2007-06-10'}),('cruise_context_is_composite_sampling_bounds',True),('fixed_layer_bounds_m',[20,80]),('calendar_months',[6,7,8])]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][index][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate(invalid,self.ledger)
        for key,value in [('scale_km',16),('crossing_count',True),('equation','V(x)=A*exp(-x*x/(2*a*a))'),('parameter_interpretation','standard_deviation'),('fit_uncertainty_km',2)]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][index]['profile_fit'][key]=value
            with self.subTest(fit_key=key),self.assertRaises(ValueError):validate(invalid,self.ledger)

    def test_rejects_mixed_current_seasonal_summary(self):
        invalid = copy.deepcopy(self.document)
        invalid["seasonal_summaries"][0]["current_id"] = "gaspe"
        with self.assertRaises(ValueError):
            validate(invalid, self.ledger)

    def test_month_angular_span_rejects_days_edges_and_conversion_forgery(self):
        validate(self.document,self.ledger)
        index=next(i for i,r in enumerate(self.document['measurements']) if r['phase_kind']=='month_dated_section')
        for key,value in [('observed_month','1993-13'),('observed_month','1993-02-01'),('observed_month','1993-2'),('time_precision','day'),('observed_period',{'start':'1993-02-01','end':'1993-02-28'}),('section_geometry',{'type':'LineString','coordinates':[[-35,4],[-35,6]]}),('fixed_layer_bounds_m',[65,270]),('calendar_months',[2]),('annual_extrema_eligible',True),('seasonal_playback_eligible',True),('full_width_inference_eligible',True),('is_confidence_interval',True),('approximate_width_km',440),('boundary_sides','paired_velocity_edges')]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][index][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate(invalid,self.ledger)
        for key,value in [('source_reported_latitude_span_degrees',4),('source_reported_latitude_span_degrees',True),('unrounded_distance_km',220),('normalization_limits_are_observed_edges',True),('rounding_km',1),('method','fixed_transport_box')]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][index]['angular_span_conversion'][key]=value
            with self.subTest(conversion_key=key),self.assertRaises(ValueError):validate(invalid,self.ledger)

    def test_composite_profile_band_is_span_not_position_or_season(self):
        validate(self.document,self.ledger)
        index=next(i for i,r in enumerate(self.document['measurements']) if r['phase_kind']=='ensemble_profile_band')
        for key,value in [('approximate_width_km',35),('width_range_km',[15,35]),('observed_period',{'start':'2007-06-01','end':'2008-11-30'}),('section_geometry',{'type':'LineString'}),('fixed_layer_bounds_m',[0,200]),('calendar_months',[6,7,8]),('sampling_windows_are_exact_observation_bounds',True),('annual_extrema_eligible',True),('seasonal_playback_eligible',True),('full_width_inference_eligible',True),('is_confidence_interval',True),('source_parent_current_id','west-australian'),('source_parent_current_id',None),('source_current_label',''),('sampling_context_month_windows',[{'start':'2008-11','end':'2007-06'}])]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][index][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate(invalid,self.ledger)
        for key,value in [('source_reported_band_limits_km',[15,35,45]),('source_reported_band_limits_km',[35,15]),('source_reported_band_limits_km',[True,35]),('span_calculation','farther_distance_only'),('boundary_velocity_threshold_m_s',.1),('cross_shore_bin_km',0),('cross_shore_overlap_percent',100)]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][index]['coast_distance_profile'][key]=value
            with self.subTest(profile_key=key),self.assertRaises(ValueError):validate(invalid,self.ledger)

    def test_relative_threshold_section_rejects_invented_dates_and_seasons(self):
        validate(self.document,self.ledger)
        index=next(i for i,r in enumerate(self.document['measurements']) if r['phase_kind']=='survey_threshold_section')
        for key,value in [('velocity_threshold_fraction',0),('velocity_threshold_fraction',1),('velocity_threshold_fraction',True),('velocity_threshold_fraction',float('nan')),('velocity_reference_statistic',''),('boundary_sides','paired'),('observed_period',{'start':'2004-07-01','end':'2004-08-31'}),('calendar_months',[7,8]),('fixed_layer_bounds_m',[0,75]),('section_geometry',{'type':'LineString'}),('width_range_km',[15,30]),('annual_extrema_eligible',True),('seasonal_playback_eligible',True),('full_width_inference_eligible',True),('is_confidence_interval',True),('sampling_window_is_exact_section_dates',True),('campaign_month_window',{'start_month':'2004-08','end_month':'2004-07'})]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][index][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):validate(invalid,self.ledger)

    def test_width_statistics_preserve_variation_confidence_and_year_support(self):
        index=next(i for i,r in enumerate(self.document['measurements']) if r['phase_kind']=='width_time_series_statistics')
        row=self.document['measurements'][index]
        self.assertEqual(row['width_range_km'],[41,76]);self.assertEqual(row['approximate_width_km'],59)
        for key,value in [('approximate_width_km',60),('width_range_km',[57,61]),('range_kind','annual_range'),('current_id','gulf-stream'),('calendar_months',[8,9]),('fixed_layer_bounds_m',[0,.75]),('observed_period',{'start':'2005-01-01','end':'2006-12-31'}),('section_geometry',{'type':'LineString'}),('annual_extrema_eligible',True),('seasonal_playback_eligible',True),('is_confidence_interval',True),('boundary_sides','paired_mean_zero_contours')]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][index][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate(invalid,self.ledger)
        for key,value in [('audit_sha256','changed'),('nominal_measurement_depth_m',14),('sample_period_years',[2005,2005]),('velocity_threshold_fraction',.4),('diagnostic_time_filter','unfiltered'),('boundary_coordinates_extracted',True)]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][index]['width_statistics_context'][key]=value
            with self.subTest(context=key),self.assertRaises(ValueError):validate(invalid,self.ledger)
        for key,value in [('standard_deviation_km',2),('mean_confidence_level_percent',95),('minimum_km',57)]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][index]['width_statistics_context']['reported_statistics'][key]=value
            with self.subTest(statistic=key),self.assertRaises(ValueError):validate(invalid,self.ledger)
        invalid=copy.deepcopy(self.document);invalid['measurements'][index]['width_statistics_context']['seasonal_context']['monthly_numeric_widths_km']=[59]*12
        with self.assertRaises(ValueError):validate(invalid,self.ledger)

    def test_eulerian_mean_section_keeps_boundary_period_and_layer_support(self):
        index=next(i for i,r in enumerate(self.document['measurements']) if r['phase_kind']=='eulerian_mean_section_span')
        self.assertEqual(self.document['measurements'][index]['approximate_width_km'],219)
        for key,value in [('approximate_width_km',260),('width_range_km',[219,260]),('fixed_layer_bounds_m',[0,3000]),('observed_period',{'start':'2010-04-01','end':'2013-02-28'}),('calendar_months',[12,1,2]),('annual_extrema_eligible',True),('seasonal_playback_eligible',True),('boundary_sides','paired_mean_zero_contours'),('current_id','agulhas-return')]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][index][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate(invalid,self.ledger)
        for key,value in [('audit_sha256','changed'),('section_latitude_degrees_north_approx',-32),('averaging_period_months',{'start':'2016-04','end':'2018-06'}),('reported_depth_extent_is_fixed_measurement_layer',True),('boundary_coordinates_extracted',True),('instantaneous_moving_boundary_series_extracted',True)]:
            invalid=copy.deepcopy(self.document);invalid['measurements'][index]['eulerian_section_context'][key]=value
            with self.subTest(context=key),self.assertRaises(ValueError):validate(invalid,self.ledger)

    def test_rejects_one_sided_full_width_and_false_season(self):
        index = next(i for i, row in enumerate(self.document["measurements"]) if row["phase_kind"] == "ensemble_summary")
        for key, value in [("boundary_sides", "paired"), ("full_width_inference_eligible", True), ("phase_kind", "seasonal_summary")]:
            invalid = copy.deepcopy(self.document)
            invalid["measurements"][index][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate(invalid, self.ledger)
        invalid = copy.deepcopy(self.document)
        invalid["comparability_notes"][0]["seasonal_playback_eligible"] = True
        with self.assertRaises(ValueError):
            validate(invalid, self.ledger)

if __name__ == "__main__":
    unittest.main()
