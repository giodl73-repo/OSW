import json
import unittest
from pathlib import Path
import collect_tao_pacific_euc_direct_source_v2 as source
import test_tao_pacific_euc_daily_depth_v1 as fixtures

ROOT=Path(__file__).resolve().parents[1]


class DirectRemainingFields(unittest.TestCase):
    def test_prior_custody_and_unattempted_scope_are_proven(self):
        old,metadata=source.imported()
        self.assertEqual(len(old['requests']),2)
        self.assertEqual(old['field_scalars_decoded'],0)
        self.assertEqual(metadata['units'],'cm/s')
        self.assertFalse({r['url'] for r in old['requests']} & {r['url'] for r in source.plan()})
        self.assertEqual(len(old['requests'])+len(source.plan()),old['maximum_requests'])

    def test_all_original_locations_and_dates_kept_without_station_guess(self):
        original=source.frozen.targets([{'array':'not_used','station':'not_guessed','longitude':lon,'latitude':0} for lon in [165,190,220,250]])
        self.assertEqual([t['times_utc'] for t in source.plan()],[t['times_utc'] for t in original])
        self.assertEqual(sum(t['reserved_numeric_scalars'] for t in source.plan()),11520)
        for t in source.plan():
            self.assertTrue(t['url'].startswith(source.DIRECT))
            self.assertNotIn('&station=',t['url']);self.assertNotIn('&array=',t['url'])

    def test_actual_returned_identifier_does_not_change_depth_diagnosis(self):
        a,n=source.diagnose(fixtures.field_bytes(),source.plan()[0])
        b,m=source.frozen.profiles(fixtures.field_bytes(),fixtures.target())
        self.assertEqual(n,m)
        self.assertEqual(a[0]['threshold_contexts'],b[0]['threshold_contexts'])
        self.assertEqual(a[0]['nominal_station']['station'],'site165')

    def test_ambiguous_identifiers_or_wrong_geography_rejected(self):
        def ambiguous(rows):rows[0][1]='other';return rows
        def displaced(rows):rows[0][2]=166;return rows
        for f in [ambiguous,displaced]:
            with self.assertRaises(ValueError):source.diagnose(fixtures.field_bytes(f),source.plan()[0])

    def test_aggregate_caps_are_not_reset_by_resume(self):
        op=json.loads((ROOT/source.OP).read_bytes())
        self.assertEqual(op['prior_request_attempts']+op['maximum_new_field_requests'],18)
        self.assertEqual(op['prior_request_time_reserve_seconds']+op['remaining_programme_seconds'],210)
        self.assertEqual(op['global_scalar_reserve'],12520)
        self.assertEqual(op['maximum_attempts_per_target'],1)


if __name__=='__main__':unittest.main()
