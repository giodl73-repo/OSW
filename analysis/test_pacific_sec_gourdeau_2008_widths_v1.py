import copy,json,unittest
import pacific_sec_gourdeau_2008_widths_v1 as widths

class RegionalWidthTests(unittest.TestCase):
    def test_original_values_and_distinct_components(self):
        rows=widths.prepare()['width_records']
        self.assertEqual([r['approximate_width_km'] for r in rows],[300,100])
        self.assertEqual(len({r['component'] for r in rows}),2)
        self.assertTrue(all(r['entity_id']=='current:pacific-south-equatorial' for r in rows))
    def test_missing_annual_geometry_and_uncertainty_are_not_filled(self):
        for row in widths.prepare()['width_records']:
            for key in ['annual_width_range_km','numerical_width_uncertainty_km','boundary_rule','paired_edge_coordinates','section_geometry','fixed_layer_bounds_m']:
                self.assertIsNone(row[key])
            self.assertFalse(row['seasonal_playback_eligible']);self.assertFalse(row['whole_current_representative'])
    def test_false_precision_identity_and_survey_length_are_refused(self):
        base=json.loads((widths.ROOT/widths.FACTS).read_bytes())
        for field,value in [('annual_width_range',[100,300]),('numerical_width_uncertainty',6),('entity_id','current:south-equatorial'),('whole_current_length',1640),('transport_error_is_width_error',True)]:
            changed=copy.deepcopy(base);changed[field]=value
            with self.assertRaises(ValueError):widths.prepare(changed)
    def test_frozen_preparation_and_visual_match_science(self):
        value=widths.prepare()
        self.assertEqual((widths.ROOT/widths.PREPARED).read_bytes(),widths.encoded(value))
        self.assertEqual((widths.ROOT/widths.FIGURE).read_bytes(),widths.figure(value))
        self.assertEqual(value['whole_current_lengths_added'],0)

if __name__=='__main__':unittest.main()
