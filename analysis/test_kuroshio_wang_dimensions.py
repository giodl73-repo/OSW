"""Geometry and source-custody gates for regional model dimensions."""
from datetime import date, timedelta
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kuroshio_wang_dimensions as k


class GeometryTests(unittest.TestCase):
    def test_shared_vertex_is_one_crossing(self):
        found, overlap = k.crossings([[124, 23], [125, 24.5], [126, 26]], 24.5)
        self.assertEqual(len(found), 1); self.assertFalse(overlap)
        self.assertEqual(found[0]['point'], [125, 24.5])

    def test_missing_vertex_is_not_bridged(self):
        found, _ = k.crossings([[124, 23], None, [126, 26]], 24.5)
        self.assertEqual(found, [])

    def test_distinct_repeated_crossings_not_deduplicated(self):
        found, _ = k.crossings([[124, 24], [124, 25], [124, 24]], 24.5)
        self.assertEqual(len(found), 2)

    def test_horizontal_gate_overlap_unresolved(self):
        curves = {p: [[124, 24.5], [125, 24.5]] for p in ['axis', 'left', 'right']}
        self.assertEqual(k.section_span(curves, 24.5)['status'], 'section_overlap')

    def test_geodesic_not_longitude_difference(self):
        curves = {p: [[lon, 24.4], [lon, 24.6]] for p, lon in [('left', 124), ('axis', 124.5), ('right', 125)]}
        row = k.section_span(curves, 24.5)
        self.assertEqual(row['status'], 'resolved')
        self.assertTrue(101 < row['span_km'] < 102)
        self.assertEqual(row['section_lon_lat'], [[124, 24.5], [124.5, 24.5], [125, 24.5]])

    def test_boundary_arrays_are_not_paired_by_index(self):
        curves = {'left': [[124, 24.4], [124, 24.6]],
                  'axis': [[124.5, 24.4], [124.5, 24.5], [124.5, 24.6]],
                  'right': [[125, 24.4], [125, 24.45], [125, 24.5], [125, 24.6]]}
        self.assertEqual(k.section_span(curves, 24.5)['status'], 'resolved')

    def test_axis_outside_boundaries_rejected(self):
        curves = {p: [[lon, 24.4], [lon, 24.6]] for p, lon in [('left', 124), ('axis', 126), ('right', 125)]}
        self.assertEqual(k.section_span(curves, 24.5)['status'], 'axis_not_between_edges')

    def test_long_segment_rejected(self):
        curves = {p: [[lon, 23], [lon, 26]] for p, lon in [('left', 124), ('axis', 124.5), ('right', 125)]}
        self.assertEqual(k.section_span(curves, 24.5)['status'], 'source_segment_exceeds_50km')

    def test_fixed_gate_axis_length(self):
        points = [[125, 17.9+i*.1] for i in range(123)]
        row = k.axis_length(points)
        self.assertEqual(row['status'], 'resolved')
        self.assertAlmostEqual(row['length_km'], k.distance([125, 18], [125, 30]), places=5)
        self.assertEqual(k.axis_length(points[::-1])['status'], 'reversed_gate_order')

    def test_axis_gap_and_multiple_gate_fail_closed(self):
        points = [[125, 17.9+i*.1] for i in range(123)]
        points[60] = None
        self.assertEqual(k.axis_length(points)['status'], 'internal_missing_vertex')
        self.assertEqual(k.axis_length([[125, 17], [125, 19], [125, 17], [125, 31]])['status'], 'gate_missing_or_multiple')

    def test_empty_and_single_sample_summary(self):
        self.assertEqual(k.summary([]), {'valid_count': 0, 'minimum_km': None, 'median_km': None, 'maximum_km': None})
        self.assertEqual(k.summary([5])['minimum_km'], k.summary([5])['maximum_km'])


class OriginalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads((k.ROOT/k.FILE).read_bytes())

    def test_byte_exact_original_and_full_scientific_rebuild(self):
        rebuilt = k.build()
        self.assertEqual(k.encoded(rebuilt), (k.ROOT/k.FILE).read_bytes())

    def test_each_leap_year_day_and_predeclared_level_retained(self):
        self.assertEqual(len(self.doc['daily']), 1098)
        expected = {(str(date(2024, 1, 1)+timedelta(days=i)), z) for i in range(366) for z in [1, 23, 30]}
        self.assertEqual({(r['date'], r['source_level']) for r in self.doc['daily']}, expected)
        self.assertTrue(all(len(r['sections']) == 5 for r in self.doc['daily']))
        self.assertEqual(sum(self.doc['axis_status_counts'].values()), 1098)
        self.assertEqual(sum(self.doc['section_status_counts'].values()), 5490)

    def test_model_sample_ranges_do_not_promote_inventory(self):
        for key in ['rank_eligible', 'scoped_width_inventory_admitted', 'physical_state_passage_admitted', 'native_wasm_ui_integrated']:
            self.assertIs(self.doc[key], False)
        self.assertIsNone(self.doc['annual_physical_width_range_km'])
        self.assertEqual(self.doc['conventions']['fallback_occurrence'], 'not encoded; search truncation possible')
        for row in self.doc['daily']:
            self.assertEqual(row['axis']['length_km'] is not None, row['axis']['status'] == 'resolved')
            for section in row['sections']:
                self.assertEqual(section['span_km'] is not None, section['status'] == 'resolved')

    def test_visual_selection_and_exact_figure(self):
        frames = self.doc['display_frames']
        self.assertEqual(len(frames), 36)
        self.assertTrue(all(f['date'].endswith('-01') for f in frames))
        self.assertEqual((k.ROOT/k.FIGURE).read_bytes(), k.figure_bytes(self.doc))
        self.assertEqual(k.verify_inputs(), self.doc)

    def test_summaries_preserve_missing_denominators(self):
        for summary in self.doc['summaries']:
            rows = [r for r in self.doc['daily'] if r['source_level'] == summary['source_level'] and (summary['month'] is None or int(r['date'][5:7]) == summary['month'])]
            self.assertEqual(summary['expected_days'], len(rows))
            self.assertEqual(summary['axis_length'], k.summary([r['axis']['length_km'] for r in rows if r['axis']['length_km'] is not None]))
            for i, s in enumerate(summary['sections']):
                self.assertEqual({p: v for p,v in s.items() if p!='latitude'}, k.summary([r['sections'][i]['span_km'] for r in rows if r['sections'][i]['span_km'] is not None]))


if __name__ == '__main__':
    unittest.main()
