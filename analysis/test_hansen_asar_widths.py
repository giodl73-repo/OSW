import json
import unittest
import hansen_asar_widths as h


class AsarSourceReports(unittest.TestCase):
    def test_exact_generated_report_export_and_figure(self):
        doc, pins = h.verify_inputs()
        self.assertEqual(len(doc['width_records']), 3)
        self.assertEqual(len(doc['mixed_contexts']), 2)
        for path, value in pins.items():
            self.assertEqual(h.digest(path), value, path)

    def test_previous_measurement_rows_and_ranks_preserved(self):
        doc = h.build()
        old = json.loads((h.ROOT / h.BASE).read_bytes())
        new = h.export(doc)
        for field in ['measurements', 'length_assessments']:
            self.assertEqual(new[field], old[field])
        self.assertEqual(new['widths'][:-3], old['widths'])
        self.assertEqual(new['sources'][:-1], old['sources'])
        self.assertEqual(new['scoped_width_count'], 167)
        self.assertEqual(new['scoped_width_owners'], 84)
        self.assertEqual(sum(r['rank_eligible'] for r in new['length_assessments']), 13)

    def test_surface_mean_period_is_not_a_dated_seasonal_series(self):
        for r in h.build()['width_records']:
            self.assertEqual(r['reference_period']['start_month'], '2007-08')
            self.assertEqual(r['reference_period']['end_month'], '2010-07')
            self.assertIsNone(r['observed_period'])
            self.assertIsNone(r['calendar_months'])
            self.assertIsNone(r['fixed_layer_bounds_m'])
            self.assertIsNone(r['width_range_km'])
            for flag in ['whole_current_representative', 'rank_eligible', 'annual_extrema_eligible',
                         'seasonal_playback_eligible', 'physical_edges_admitted', 'independent_new_observation']:
                self.assertIs(r[flag], False)

    def test_svinoy_partition_is_not_a_depth_slab_or_subtraction(self):
        p1, partition, ncc = h.build()['width_records']
        self.assertEqual([p1['approximate_width_km'], partition['approximate_width_km'], ncc['approximate_width_km']], [60, 36, 30])
        self.assertTrue(partition['conditional_on_isobath_partition'])
        self.assertIn('200m isobath', partition['boundary_rule'])
        self.assertNotEqual(partition['width_metric'], p1['width_metric'])
        self.assertEqual(ncc['current_id'], 'norwegian-coastal')
        self.assertNotIn(24, [r['approximate_width_km'] for r in h.build()['width_records']])
        self.assertIn('does not explicitly restate FWHM', ncc['boundary_rule'])

    def test_mixed_profiles_are_retained_without_promotion(self):
        d = h.build()
        self.assertEqual([r['width_km'] for r in d['mixed_contexts']], [45, 60])
        self.assertTrue(all(r['separate_current_width_admitted'] is False for r in d['mixed_contexts']))
        self.assertFalse(d['velocity_rmse_is_width_error'])
        self.assertEqual(d['output_grid_km'], [5, 5])
        self.assertEqual(d['source_stated_spatial_resolution_km'], 10)

    def test_source_ownership_positions_and_pointers(self):
        d = h.build()
        for i, row in enumerate(d['width_records']):
            self.assertEqual(row['source_pointer'], '/width_records/' + str(i))
            self.assertEqual(row['source_file'], h.FILE)
            self.assertEqual(row['source_id'], d['source_record']['id'])
            self.assertFalse(row['source_position_is_current_edge'])
        self.assertEqual(d['width_records'][0]['source_reference_position_lon_lat'], [-.5, 62])
        self.assertEqual(d['width_records'][1]['source_reference_position_lon_lat'], [4.25, 62.8])
        self.assertFalse(d['source_record']['provider_asset_redistributed'])


if __name__ == '__main__':
    unittest.main()
