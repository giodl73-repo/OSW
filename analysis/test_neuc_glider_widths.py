"""Source ownership, zero and time scope survive the working inventory join."""
import json
import unittest
import neuc_glider_widths as n


class GliderWidthRanges(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc, cls.pins = n.verify_inputs()

    def test_source_jet_ranges_and_zero_are_not_averaged(self):
        a, b = self.doc['width_records']
        self.assertEqual([a['width_range_km'], b['width_range_km']], [[100, 350], [0, 200]])
        self.assertFalse(a['source_zero_lower_bound'])
        self.assertTrue(b['source_zero_lower_bound'])
        self.assertTrue(all(r['approximate_width_km'] is None for r in [a, b]))

    def test_pacific_owner_and_core_locations_are_not_family_edges(self):
        for row, latitude in zip(self.doc['width_records'], [9.6, 13.1]):
            self.assertEqual(row['current_id'], 'pacific-north-equatorial-undercurrent')
            self.assertEqual(row['source_reference_position_lon_lat'], [134.3, latitude])
            self.assertFalse(row['source_position_is_current_edge'])
            self.assertFalse(row['core_excursion_is_width'])
            self.assertFalse(row['physical_edges_admitted'])
        self.assertIn('Two velocity maxima', self.doc['width_records'][0]['merging_context'])

    def test_density_and_multiyear_context_are_not_depth_or_seasons(self):
        for row in self.doc['width_records']:
            self.assertEqual(row['density_averaging_source_values_kg_m3'], [26.7, 27.3])
            self.assertIsNone(row['fixed_layer_bounds_m'])
            self.assertIsNone(row['observed_period'])
            self.assertIsNone(row['extrema_dates'])
            self.assertIsNone(row['calendar_months'])
            self.assertFalse(row['annual_extrema_eligible'])
            self.assertFalse(row['seasonal_playback_eligible'])
        self.assertEqual(self.doc['reference_period']['start_month'], '2009-06')
        self.assertEqual(self.doc['reference_period']['end_month'], '2014-01')

    def test_reviewed_html_is_not_claimed_as_archived_original(self):
        source = self.doc['source_record']
        self.assertFalse(source['original_file_retained'])
        self.assertIsNone(source['original_file_sha256'])
        self.assertEqual(source['factual_input_sha256'], n.digest(n.INPUT))
        self.assertFalse(self.doc['new_native_fields_acquired'])
        self.assertFalse(self.doc['new_geometry_admitted'])
        self.assertIsNone(self.doc['annual_width_range_km'])
        self.assertFalse(self.doc['sampling_context']['sampling_scale_is_width_error'])

    def test_all_preceding_measurements_survive_without_family_duplicates(self):
        old = json.loads((n.ROOT / n.BASE).read_bytes())
        new = n.export(self.doc)
        self.assertEqual(new['widths'][:-2], old['widths'])
        self.assertEqual(new['sources'][:-1], old['sources'])
        for key in ['measurements', 'length_assessments', 'ranked_length_count']:
            self.assertEqual(new[key], old[key])
        self.assertEqual((new['scoped_width_count'], new['scoped_width_owners']), (169, 84))
        self.assertEqual(sum(w['current_id'] == n.CURRENT for w in new['widths']), 4)
        self.assertFalse(any(w['current_id'] == 'north-equatorial-undercurrent' for w in new['widths']))

    def test_figure_encoding_keeps_units_and_author_readable(self):
        text = n.figure().decode('utf8')
        for expected in ['100–350km', '0–200km', '134.3°E', 'Schönau']:
            self.assertIn(expected, text)
        self.assertNotIn('Ã', text)
        self.assertNotIn('Â', text)

    def test_pin_and_diagnostic_binding(self):
        for path, sha in self.pins.items():
            self.assertEqual(n.digest(path), sha)
        diagnostic = n.diagnostic(self.doc)
        self.assertEqual(json.loads(diagnostic['source_json']), self.doc)
        self.assertEqual(diagnostic['entity_id'], 'current:' + n.CURRENT)
        self.assertEqual(diagnostic['source_file_sha256'], n.digest(n.FILE))


if __name__ == '__main__':
    unittest.main()
