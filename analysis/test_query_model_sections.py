"""Source parity and missing-support behavior for model query projections."""
import copy
import json
import unittest

from build_query_model_sections import ROOT, TIMELINE, MAPS, UNITS, build, source_hashes


class ModelSectionProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.timeline = json.loads((ROOT / TIMELINE).read_bytes())
        cls.maps = json.loads((ROOT / MAPS).read_bytes())
        cls.projected = build(cls.timeline, cls.maps, source_hashes())

    def test_every_source_sample_remains_inspectable_in_order(self):
        frames = self.projected['model_frames']
        samples = self.projected['model_samples']
        self.assertEqual(len(frames), 12)
        self.assertEqual(len(samples), 2292)
        self.assertEqual(len({r['id'] for r in samples}), 2292)
        for index, original in enumerate(self.timeline['frames']):
            frame = frames[index]
            rows = [r for r in samples if r['model_frame_id'] == frame['id']]
            self.assertEqual(len(rows), 191)
            self.assertEqual(frame['sample_time_utc'], original['sample_time_utc'])
            self.assertEqual(frame['receipt_sha256'], original['receipt_sha256'])
            self.assertEqual(frame['map_figure_sha256'], self.maps['frames'][index]['figure_sha256'])
            self.assertEqual(frame['section'], self.timeline['section'])
            receipt = json.loads((ROOT / original['receipt_file']).read_bytes())
            self.assertEqual(frame['field_units'], {key: receipt['packing'][key]['units'] for key in UNITS})
            for row, point in zip(rows, original['profile']):
                self.assertEqual({key: row[key] for key in point}, point)
                self.assertEqual(row['depth_m'], receipt['depth_m'])
            self.assertEqual(frame['available_sample_count'],
                             sum(r['field_values_available'] for r in rows))

    def test_scope_is_not_promoted_to_current_dimensions_or_observations(self):
        for row in self.projected['model_frames']:
            self.assertIsNone(row['current_length_km'])
            self.assertIsNone(row['current_width_km'])
            self.assertIn('hourly model snapshots, not monthly means', row['sampling_rule'])
            self.assertEqual(row['limitations'], self.timeline['limitations'])
        for rows in self.projected.values():
            for row in rows:
                for key in ['annual_extrema_eligible', 'width_rank_eligible', 'state_footprint_join_eligible']:
                    self.assertIs(row[key], False)

    def test_missing_fields_remain_null_and_individually_queryable(self):
        timeline = copy.deepcopy(self.timeline)
        timeline['frames'][0]['profile'][1]['u_eastward'] = None
        result = build(timeline, self.maps, source_hashes())
        row = result['model_samples'][1]
        self.assertIsNone(row['u_eastward'])
        self.assertFalse(row['field_values_available'])
        self.assertEqual(row['salinity'], timeline['frames'][0]['profile'][1]['salinity'])
        self.assertEqual(result['model_frames'][0]['available_sample_count'],
                         self.projected['model_frames'][0]['available_sample_count'] - 1)

    def test_mismatched_map_support_is_rejected(self):
        maps = copy.deepcopy(self.maps)
        maps['frames'][0]['receipt_sha256'] = 'different-receipt'
        with self.assertRaisesRegex(ValueError, 'different source support'):
            build(self.timeline, maps, source_hashes())


if __name__ == '__main__':
    unittest.main()
