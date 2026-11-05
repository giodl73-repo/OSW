import unittest
from datetime import datetime
from unittest.mock import patch
import plan_norkyst_jutland_calendar_months_v1 as m


class CalendarPreflight(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('urllib.request.urlopen',side_effect=AssertionError('No provider retrieval')):
            cls.plan=m.build()

    def test_four_complete_calendar_months_and_daily_custody(self):
        self.assertEqual(self.plan['planned_month_hours'],{'3':744,'6':720,'9':720,'12':744})
        self.assertEqual(self.plan['metadata_archive_members_validated'],122)

    def test_global_reserve_includes_prior_and_all_new_months(self):
        b=self.plan['budget']
        self.assertEqual(b['combined_reserved_decoded_scalars'],b['prior_reserved_decoded_scalars']+b['new_velocity_scalars']+b['new_coordinate_scalars'])
        self.assertLessEqual(b['combined_reserved_decoded_scalars'],250000)
        self.assertLessEqual(b['combined_reserved_decoded_bytes'],7000000)
        self.assertEqual(b['prior_reserved_decoded_scalars'],39348)

    def test_prior_noon_hours_never_requested_again(self):
        self.assertEqual(len(self.plan['reused_prior_noon_profiles']),12)
        for t in self.plan['request_plan']:
            if t['date'].endswith('-15'):self.assertFalse(t['first_hour']<=12<=t['last_hour'])

    def test_fixed_source_positions_and_actual_z_levels(self):
        self.assertEqual(len(self.plan['fixed_points']),3)
        self.assertEqual(self.plan['source_depth_levels_m'],[0,1,2,3,5,7,10,15,25,50,65])
        self.assertTrue(all(p['selection_role']=='original_editorial_center_node_not_a_selected_velocity_maximum' for p in self.plan['fixed_points']))

    def test_distinct_bounded_requests_and_no_network_during_plan(self):
        targets=self.plan['request_plan']
        self.assertEqual(len(targets),378)
        self.assertEqual(len({t['http_url'] for t in targets}),378)
        self.assertTrue(all(3<=t['hourly_profiles']<=150 for t in targets))
        self.assertEqual(self.plan['new_provider_requests_performed'],0)
        self.assertEqual(self.plan['new_ocean_values_decoded'],0)

    def test_only_original_metadata_members_verified(self):
        for record in self.plan['daily_metadata_records']:
            self.assertTrue(record['metadata_member'].endswith('.das'))
            self.assertIn('originals-year-2024-',record['archive_file'])
            self.assertEqual(len(record['metadata_sha256']),64)


if __name__=='__main__':unittest.main()
