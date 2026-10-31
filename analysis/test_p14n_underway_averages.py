"""Checks for overlap weighting, unsupported tails and false cross-run edges."""
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
import copy
import hashlib
import json
import xml.etree.ElementTree as ET
import unittest
import build_p14n_underway_averages as averages

EPOCH = datetime(1993, 7, 14, tzinfo=timezone.utc)


def profile(index, start, end, u, latitude=45):
    return {'source_time_index': index,
            'ensemble_start_utc': averages.stamp(EPOCH + timedelta(seconds=start)),
            'ensemble_end_utc': averages.stamp(EPOCH + timedelta(seconds=end)),
            'layer_mean': {'eastward_m_s': u, 'northward_m_s': 2 * u},
            'latitude_degrees_north': latitude, 'longitude_degrees_east': -181.}


def bin_row(index, u, latitude=45, coverage=True):
    return {'bin_index': index, 'mean': {'eastward_m_s': u, 'northward_m_s': 0.,
                                        'latitude_degrees_north': latitude, 'longitude_degrees_east': -181.},
            'boundary_eligible_coverage': coverage, 'contributor_latitude_range': [latitude, latitude]}


class UnderwayAveragingTests(unittest.TestCase):
    def test_union_weighting_does_not_double_count_overlap(self):
        # [0,300]: 1; [300,600]: (1+3)/2; [600,900]: 3; [900,1000]: missing.
        rows = [profile(1, 0, 600, 1), profile(2, 300, 900, 3)]
        value = averages.average_bin(rows, EPOCH, 1000, 0)
        self.assertEqual(value['union_coverage_seconds'], 900)
        self.assertEqual(value['multiply_covered_seconds'], 300)
        self.assertEqual(value['missing_seconds'], 100)
        self.assertEqual(value['mean']['eastward_m_s'], 2)
        self.assertEqual(value['mean']['northward_m_s'], 4)
        self.assertTrue(value['boundary_eligible_coverage'])
        self.assertFalse(value['mean_position_is_instantaneous_observation'])

    def test_full_window_denominator_and_clipped_profile_weights(self):
        rows = [profile(i, i * 300, (i + 1) * 300, 1) for i in range(7)]
        bins = averages.average_run(rows, 30)
        self.assertEqual(len(bins), 2)
        self.assertEqual(bins[1]['union_coverage_seconds'], 300)
        self.assertEqual(bins[1]['coverage_fraction'], 1 / 6)
        self.assertFalse(bins[1]['boundary_eligible_coverage'])
        clipped = averages.average_bin([profile(0, -100, 100, 1), profile(1, 100, 400, 3)], EPOCH, 300, 0)
        self.assertAlmostEqual(clipped['mean']['eastward_m_s'], 7 / 3)
        self.assertEqual(clipped['union_coverage_seconds'], 300)

    def test_other_runs_cannot_supply_peak_boundaries(self):
        runs = [{'bins': [bin_row(0, 0), bin_row(1, 1)]},
                {'bins': [bin_row(0, 0)]}]
        result = averages.branch(runs, 'northern', [44, 46])
        self.assertEqual(result['selected_peak']['run_index'], 0)
        for scenario in result['boundary_choice_scenarios']:
            self.assertEqual(scenario['before_peak']['status'], 'resolved')
            self.assertEqual(scenario['after_peak']['status'], 'run_end')
            self.assertIsNone(scenario['endpoint_separation_km'])

    def test_stops_at_missing_coverage_and_window_edges(self):
        for status, outer in [('missing_bin', bin_row(4, 0)),
                              ('insufficient_coverage', bin_row(2, 0, coverage=False)),
                              ('branch_window_edge', bin_row(2, 0, latitude=43))]:
            with self.subTest(status=status):
                bins = [bin_row(0, 0), bin_row(1, 1), outer, bin_row(3, 0)]
                self.assertEqual(averages.walk(bins, 1, 1, [44, 46], .5)['status'], status)
        edge = bin_row(1, 1); edge['contributor_latitude_range'] = [43.99, 45]
        self.assertEqual(averages.eligibility(edge, [44, 46]), 'branch_window_edge')

    def test_resolved_synthetic_span_retains_actual_brackets(self):
        bins = [bin_row(0, 0, 45.2), bin_row(1, 1, 45), bin_row(2, 0, 44.8)]
        result = averages.branch([{'bins': bins}], 'northern', [44, 46])
        nominal = result['boundary_choice_scenarios'][1]
        self.assertEqual(nominal['status'], 'resolved')
        self.assertAlmostEqual(nominal['before_peak']['crossing']['latitude_degrees_north'], 45.1)
        self.assertAlmostEqual(nominal['after_peak']['crossing']['latitude_degrees_north'], 44.9)
        self.assertAlmostEqual(nominal['endpoint_separation_km'], 22.2263552543, places=6)
        tied = averages.branch([{'bins': bins}, {'bins': copy.deepcopy(bins)}], 'northern', [44, 46])
        self.assertEqual(tied['selected_peak']['run_index'], 0)

    def test_changed_source_is_rejected_before_field_access(self):
        with patch.object(averages, 'digest', return_value='0' * 64), patch.object(averages, 'verify_native') as field:
            with self.assertRaisesRegex(ValueError, 'Changed underway averaging input'):
                averages.build()
            field.assert_not_called()

    def test_actual_report_reconstructs_all_fixed_experiments_without_admission(self):
        report = averages.verify()
        experiments = report['experiments']
        self.assertEqual([(e['ship_speed_cutoff_m_s'], e['averaging_minutes']) for e in experiments],
                         [(s, m) for s in [1, 2, 3] for m in [30, 60, 150]])
        self.assertEqual([len(e['runs']) for e in experiments], [42] * 3 + [19] * 6)
        for e in experiments:
            for run in e['runs']:
                self.assertEqual([b['bin_index'] for b in run['bins']], list(range(len(run['bins']))))
                for b in run['bins']:
                    self.assertLessEqual(b['union_coverage_seconds'], b['declared_window_seconds'])
                    self.assertEqual(b['missing_seconds'] + b['union_coverage_seconds'], b['declared_window_seconds'])
                    self.assertTrue(set(c['source_time_index'] for c in b['contributors']).issubset(run['native_source_time_indices']))
            for branch in e['branches']:
                self.assertEqual(len(branch['boundary_choice_scenarios']), 3)
                self.assertEqual(len(branch['velocity_sensitivity_scenarios']), 4)
                for scenario in branch['boundary_choice_scenarios'] + branch['velocity_sensitivity_scenarios']:
                    self.assertNotEqual(scenario['status'], 'resolved')
                    self.assertIsNone(scenario['endpoint_separation_km'])
        for flag in ['current_association_verified', 'new_width_record_admitted', 'width_rank_eligible',
                     'physical_edge_geometry_admitted', 'seasonal_playback_supported', 'station_gaps_bridged']:
            self.assertFalse(report[flag])

    def test_figure_receipt_and_accessible_description_match(self):
        receipt = json.loads((averages.ROOT / 'research/aleutian-p14n-1993-underway-averages-figure.json').read_bytes())
        self.assertEqual(receipt['source_file'], averages.OUTPUT)
        self.assertEqual(receipt['source_sha256'], averages.digest(averages.OUTPUT))
        self.assertEqual(receipt['generator_sha256'], averages.digest(receipt['generator_file']))
        self.assertFalse(receipt['physical_edges_rendered'])
        self.assertFalse(receipt['horizontal_bars_are_uncertainty'])
        for value in receipt['figures'].values():
            self.assertEqual(value['sha256'], averages.digest(value['file']))
        svg = ET.fromstring((averages.ROOT / receipt['figures']['.svg']['file']).read_bytes())
        self.assertEqual(svg.attrib['role'], 'img')
        self.assertEqual(svg.attrib['aria-labelledby'], 'averaging-title averaging-desc')
        descriptions = {e.attrib.get('id'): e.text for e in svg.iter() if e.attrib.get('id')}
        self.assertIn('All 126 boundary scenarios', descriptions['averaging-desc'])


if __name__ == '__main__':
    unittest.main()
