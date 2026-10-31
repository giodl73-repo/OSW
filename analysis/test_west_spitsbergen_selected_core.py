import copy,unittest
from check_west_spitsbergen_selected_core import validate,record,validate_row

class SelectedCoreTests(unittest.TestCase):
    def test_inventory_projection_keeps_sd_and_source_binding(self):
        r=record();validate_row(r);self.assertIsNone(r['width_range_km'])
        for key,value in [('width_standard_deviation_km',0),('current_id','spitsbergen-atlantic'),('width_range_km',[21,35])]:
            with self.subTest(key=key):
                bad=copy.deepcopy(r);bad[key]=value
                with self.assertRaises(ValueError):validate_row(bad)

    def test_original_and_exact_source_scope(self):
        d=validate();self.assertEqual(d['measurement']['approximate_width_km'],28)
        self.assertEqual(sum(w['sections'] for w in d['section_windows']),22)
    def test_standard_deviation_cannot_become_a_range_or_error(self):
        for key,value in [('width_range_km',[21,35]),('is_confidence_interval',True),('annual_extrema_eligible',True),('width_standard_deviation_km',14)]:
            with self.subTest(key=key):
                d=copy.deepcopy(validate());d['measurement'][key]=value
                with self.assertRaises(ValueError):validate(d)
    def test_selection_is_not_half_peak_or_fixed_region_width(self):
        for key,value in [('selection_percentile_is_peak_fraction',True),('section_selection_percentile',50),('fixed_region_span_is_core_width',True),('uses_Q_not_QAW',False),('absolute_velocity_reference','glider_dac_only'),('selected_section_count',22)]:
            with self.subTest(key=key):
                d=copy.deepcopy(validate());d['measurement']['selected_core_context'][key]=value
                with self.assertRaises(ValueError):validate(d)
    def test_deployment_dates_cannot_replace_section_windows(self):
        d=copy.deepcopy(validate());d['section_windows'][1]['start']='2021-08-03'
        with self.assertRaises(ValueError):validate(d)

if __name__=='__main__':unittest.main()
