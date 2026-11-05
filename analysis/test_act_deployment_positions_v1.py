import copy
import unittest
from diagnose_act_deployment_positions_v1 import build, compare, south_position


class PositionChecks(unittest.TestCase):
    def row(self):
        return {'latitude_south_degrees': 33, 'latitude_minutes': 39.3216,
                'longitude_east_degrees': 27, 'longitude_minutes': 39.474}

    def test_southern_sign_applies_to_both_parts(self):
        self.assertAlmostEqual(south_position(self.row())[1], -33.65536)

    def test_invalid_minutes_rejected(self):
        row = self.row(); row['latitude_minutes'] = 60
        with self.assertRaises(ValueError): south_position(row)

    def test_b_does_not_support_exact_signed_minutes_repair(self):
        result = compare(self.row(), [27.657899856567383, -32.34640121459961])
        self.assertTrue(result['longitude_matches_within_comparison_tolerance'])
        self.assertFalse(result['latitude_hypothesis_matches_within_comparison_tolerance'])

    def test_input_immutable_and_no_join_upgrade(self):
        row = self.row(); before = copy.deepcopy(row)
        result = compare(row, [27.6579, -32.3464])
        self.assertEqual(before, row)
        for field in ['coordinate_correction_applied', 'geographic_assignment_eligible',
                      'physical_state_join_eligible', 'route_projection_eligible', 'width_join_eligible']:
            self.assertFalse(result[field])
        self.assertIsNone(result['physical_thickness_m'])
        self.assertIsNone(result['volume_m3'])

    def test_actual_retained_packet_and_control(self):
        report = build()
        self.assertFalse(report['B']['latitude_hypothesis_matches_within_comparison_tolerance'])
        self.assertTrue(report['D_unassigned_longitude_control']['latitude_hypothesis_matches_within_comparison_tolerance'])
        self.assertFalse(report['D_instrument_row_assignment_verified'])
        self.assertFalse(report['original_pdf_byte_custody'])
        self.assertEqual(report['new_provider_operations'], 0)
        self.assertEqual(report['new_depth_references_admitted'], 0)


if __name__ == '__main__':
    unittest.main()
