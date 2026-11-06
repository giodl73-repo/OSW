import copy,json,unittest
from pathlib import Path
from close_gaspe1991_metadata_scope_v1 import SOURCE,assess
class Tests(unittest.TestCase):
    def setUp(self):self.info=json.loads((Path(__file__).resolve().parents[1]/SOURCE).read_bytes())
    def test_numeric_and_iso_coverage_agree_but_not_requested_1991(self):
        r=assess(self.info);self.assertTrue(r['numeric_time_range_matches_iso_attributes']);self.assertFalse(r['advertised_coverage_overlaps_requested_period']);self.assertFalse(r['proves_1991_data_absent_from_entire_provider_archive'])
    def test_bad_epoch_correspondence_rejected(self):
        p=copy.deepcopy(self.info);p['global_attributes']['time_coverage_start']='1991-09-20T00:00:00Z'
        with self.assertRaises(ValueError):assess(p)
    def test_cf_names_not_absolute_velocity_processing(self):
        r=assess(self.info);self.assertTrue(r['eastward_cf_label_present']);self.assertTrue(r['northward_cf_label_present']);self.assertFalse(r['cf_labels_establish_ship_motion_corrected_absolute_velocity']);self.assertFalse(r['seafloor_velocity_fields_establish_correction_formula'])
    def test_sampling_depth_not_current_bottom(self):
        r=assess(self.info);self.assertEqual(r['native_depth_domain_from_metadata_m'],'9.6, 57.6');self.assertFalse(r['native_depth_domain_is_current_bottom']);self.assertFalse(r['native_measurement_request_qualified'])
    def test_wrong_product_rejected(self):
        p=copy.deepcopy(self.info);p['global_attributes']['DOI']='another dataset'
        with self.assertRaises(ValueError):assess(p)
if __name__=='__main__':unittest.main()
