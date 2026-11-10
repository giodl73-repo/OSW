"""Preserve a strict source qualifier without inventing support or a mean."""
import hashlib
import json
import unittest
import xml.etree.ElementTree as ET
import aleutian_onishi_width as a


class PublishedAleutianConstraint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc, cls.pins = a.verify_inputs()
        cls.row = cls.doc['width_records'][0]

    def test_strict_lower_relation_has_no_scalar_or_upper_extent(self):
        c = self.row['reported_width_constraint']
        self.assertEqual((c['operator'], c['value_km']), ('>', 400))
        self.assertIsNone(c['upper_bound_km'])
        self.assertFalse(c['is_measured_extremum'])
        self.assertIsNone(self.row['approximate_width_km'])
        self.assertIsNone(self.row['width_range_km'])

    def test_alaskan_stream_and_prior_diagnostics_are_separate(self):
        self.assertEqual(self.row['current_id'], 'aleutian')
        self.assertEqual(self.doc['excluded_neighbor']['value_km'], 120)
        self.assertEqual(self.doc['excluded_neighbor']['name'], 'Alaskan Stream')
        self.assertFalse(self.doc['previous_component_diagnostics_promoted'])
        self.assertFalse(self.doc['new_geometry_admitted'])

    def test_study_dates_and_reference_depth_are_not_width_support(self):
        c = self.doc['study_context']
        self.assertEqual((c['start_year'], c['end_year'], c['geostrophic_reference_depth_m']), (1990, 1998, 3000))
        self.assertFalse(c['is_width_support'])
        for key in ['reference_period', 'observed_period', 'calendar_months', 'fixed_layer_bounds_m']:
            self.assertIsNone(self.row[key])
        for key in ['rank_eligible', 'seasonal_playback_eligible', 'annual_extrema_eligible', 'physical_edges_admitted']:
            self.assertFalse(self.row[key])

    def test_frozen_export_and_width_owner_counts(self):
        old = json.loads((a.ROOT / a.BASE).read_bytes())
        new = a.export(self.doc)
        self.assertEqual(new['widths'][:-1], old['widths'])
        self.assertEqual(new['sources'][:-1], old['sources'])
        for key in ['measurements', 'length_assessments', 'ranked_length_count']:
            self.assertEqual(new[key], old[key])
        self.assertEqual((new['scoped_width_count'], new['scoped_width_owners']), (170, 85))
        self.assertEqual(sum(r['current_id'] == 'aleutian' for r in new['widths']), 1)

    def test_export_contract_binds_exact_bytes_without_embedded_copy(self):
        c = a.contract(self.doc)
        self.assertEqual(c['report_sha256'], a.digest(a.FILE))
        self.assertEqual(c['export_sha256'], a.digest(a.EXPORT))
        self.assertEqual(c['previous_export_sha256'], a.digest(a.BASE))
        for path, sha in self.pins.items():
            self.assertEqual(a.digest(path), sha)
        self.assertEqual(json.loads(a.diagnostic(self.doc)['source_json']), self.doc)

    def test_archived_original_receipt_and_accessible_open_bound_figure(self):
        receipt = json.loads((a.ROOT / a.ACQUISITION).read_bytes())
        self.assertEqual((receipt['pages'], receipt['bytes']), (13, 3403099))
        self.assertEqual(self.row['source_original_sha256'], receipt['sha256'])
        svg = ET.fromstring(a.figure())
        self.assertEqual(svg.attrib['role'], 'img')
        text = ''.join(svg.itertext())
        self.assertIn('width >400km', text)
        self.assertIn('Upper extent unknown', text)
        self.assertNotIn('Ã', text)
        self.assertNotIn('Â', text)


if __name__ == '__main__':
    unittest.main()
