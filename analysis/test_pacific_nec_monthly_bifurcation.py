"""Keep source variability bands separate from reading allowances and dimensions."""
import copy
import json
import unittest
from unittest.mock import patch
from build_pacific_nec_monthly_bifurcation import ROOT, CONFIG, OUTPUT, build


class PacificMonthlyBifurcationTests(unittest.TestCase):
    def test_pinned_means_bands_and_unknown_statistical_conventions(self):
        result=build()
        self.assertEqual(result,json.loads((ROOT/OUTPUT).read_bytes()))
        series=result['series'][0];rows=series['months']
        self.assertEqual([r['month'] for r in rows],list(range(1,13)))
        self.assertEqual([r['approximate_latitude_degrees_north'] for r in rows],[12.3,12.0,11.7,11.6,11.6,11.5,11.6,11.7,11.9,12.2,12.2,12.3])
        self.assertEqual([r['approximate_source_standard_deviation_band_degrees_north'] for r in rows],[[10.3,14.2],[10.3,13.7],[10.2,13.3],[10.1,13.0],[10.1,13.1],[10.1,13.0],[10.1,13.0],[9.9,13.5],[10.0,13.9],[10.0,14.3],[10.1,14.4],[10.3,14.4]])
        self.assertEqual(series['source_period'],{'start':'1992-10','end':'2009-12','precision':'month'})
        self.assertEqual(result['source_variability_kind'],'caption_labelled_standard_deviation_range')
        self.assertIs(result['source_variability_envelope_extracted'],True)
        for row in rows:
            lower,upper=row['raw_plot_source_standard_deviation_band_degrees_north'];mean=row['raw_plot_latitude_degrees_north']
            self.assertLess(lower,mean);self.assertLess(mean,upper)
            self.assertLessEqual(abs((lower+upper)/2-mean),0.005)
            for center,interval in zip([row['approximate_latitude_degrees_north'],*row['approximate_source_standard_deviation_band_degrees_north']], [row['plot_reading_interval_degrees_north'],*row['band_endpoint_plot_reading_intervals_degrees_north']]):
                self.assertEqual(interval,[round(center-.1,2),round(center+.1,2)])
        for key in ['geometry','whole_current_length_km','current_width_km','annual_dimension_range_km','statistical_denominator','standard_deviation_multiplier','confidence_probability']:
            self.assertIsNone(result[key])
        for key in ['rank_eligible','annual_extrema_eligible','geographic_playback_eligible','is_confidence_interval','distinct_observed_years_inferred','individual_observations_extracted','monthly_sample_counts_extracted','monthly_averaging_weights_extracted']:
            self.assertIs(result[key],False)

    def test_changed_source_missing_paths_shifted_months_and_bad_calibration_fail(self):
        with patch('build_pacific_nec_monthly_bifurcation.digest',return_value='0'*64),self.assertRaises(ValueError):build()
        config=json.loads((ROOT/CONFIG).read_bytes());original=json.loads
        for key,value in [('selection_bounds_points',[200,305,435,385]),('expected_mean_vertices',12),
                          ('axis_latitude_degrees_north',[8,18]),('axis_x_points',[170,450]),
                          ('band_fill_color_limits',[.1,.2]),('band_symmetry_tolerance_degrees',1e-8)]:
            altered=copy.deepcopy(config);altered[key]=value
            def loads(raw):
                doc=original(raw)
                return altered if doc.get('schema')=='osw.monthly-bifurcation-line-band-config.v1' else doc
            with self.subTest(key=key),patch('build_pacific_nec_monthly_bifurcation.json.loads',side_effect=loads),self.assertRaises(ValueError):build()


if __name__=='__main__':unittest.main()
