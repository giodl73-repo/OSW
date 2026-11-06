"""Keep verified world geometry and scenario data unchanged during map repair."""
import copy
import json
import unittest
import xml.etree.ElementTree as ET

import south_java_reference_map_v2 as maps


class PresentationPreservation(unittest.TestCase):
    def test_geometry_identical_and_all_route_points_fit_both_views(self):
        raw = (maps.ROOT / maps.ARCHIVE).read_bytes()
        original = ET.fromstring(raw)
        detailed = ET.fromstring(maps.detailed(raw))
        compact = ET.fromstring(maps.compact(raw))
        self.assertEqual(maps.geometry(original), maps.geometry(detailed))
        self.assertEqual(maps.geometry(original), maps.geometry(compact))
        self.assertEqual(len(list(original.iter(maps.NS + 'polyline'))), 28)
        self.assertEqual(len(list(original.iter(maps.NS + 'circle'))), 2)
        self.assertEqual(len(list(original.iter(maps.NS + 'path'))), 1)
        for line in original.iter(maps.NS + 'polyline'):
            for pair in line.get('points').split():
                x, y = map(float, pair.split(','))
                self.assertTrue(1224 < x < 1289 and 455 < y < 520)
                self.assertTrue(1227 < x < 1277 and 481 < y < 499)

    def test_wrong_executed_svg_refused(self):
        raw = (maps.ROOT / maps.ARCHIVE).read_bytes()
        with self.assertRaises(AssertionError):
            maps.detailed(raw + b' ')
        with self.assertRaises(AssertionError):
            maps.compact(raw + b' ')

    def test_all_nonpresentation_candidate_fields_preserved(self):
        original = json.loads((maps.ROOT / maps.CANDIDATE).read_bytes())
        revised = json.loads((maps.ROOT / 'research/south-java-java-bali-reference-path-v2-candidate.json').read_bytes())
        revision = revised.pop('presentation_revision')
        self.assertTrue(revision['geometry_attributes_unchanged'])
        expected = copy.deepcopy(original)
        expected.update(figure=maps.DETAILED, map_view_box=[1224, 455, 65, 65])
        self.assertEqual(revised, expected)


if __name__ == '__main__':
    unittest.main()
