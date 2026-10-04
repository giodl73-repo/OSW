import copy,json,unittest
from pathlib import Path
from acquire_antilles_ladcp_profiles import parse_profile,sha
from build_antilles_ladcp_section_diagnostic import compute,measure

ROOT=Path(__file__).resolve().parents[1]

class AntillesProfilesTests(unittest.TestCase):
    def setUp(self):
        self.inventory=json.loads((ROOT/'research/antilles-ab0505-ladcp-profile-inventory.json').read_text(encoding='utf-8'))
        self.profile=next(r for r in self.inventory['profiles'] if r['cast_id']=='AB0505_062')
        self.raw=(ROOT/self.profile['source_file']).read_bytes()

    def test_pinned_bytes_units_and_times(self):
        manifest=json.loads((ROOT/'research/source-data/noaa-wbts-ab0505/acquisition.json').read_text(encoding='utf-8'))
        for source in manifest['files']:
            self.assertEqual(sha((ROOT/source['file']).read_bytes()),source['sha256'])
        parsed=parse_profile(self.raw)
        sample=next(r for r in parsed['samples'] if r['depth_m']==400)
        self.assertAlmostEqual(sample['northward_m_s'],.78194)
        self.assertEqual(parsed['average_cast_time_utc'],'2005-05-23T12:24:47Z')
        self.assertEqual(parsed['coordinates_lon_lat'],[-76.835319,26.519405])

    def test_unknown_units_and_sentinels_stop_for_review(self):
        for old,new in [(b'cm_per_sec',b'm_per_sec'),(b'meters',b'dbar'),(b'0078.194',b'0999.000')]:
            changed=self.raw.replace(old,new)
            # Provider numeric formatting is signed; use an actual sample token.
            if changed==self.raw and old==b'0078.194':changed=self.raw.replace(b'078.194',b'999.000')
            self.assertNotEqual(changed,self.raw)
            with self.assertRaises(ValueError):parse_profile(changed)

    def test_missing_and_caution_casts_remain_distinct(self):
        self.assertEqual(self.inventory['summary']['provider_no_ladcp_cast_numbers'],list(range(24,37)))
        self.assertEqual(self.inventory['summary']['provider_caution_count'],17)
        self.assertEqual(sum(r['section_group']=='other_cruise_section' for r in self.inventory['profiles']),7)
        result=compute(self.inventory)
        self.assertEqual([len(r['samples']) for r in result['sections']],[23,27])
        self.assertTrue(all(r['full_width_km'] is None for r in [s['half_peak_diagnostic'] for s in result['sections']]))

    def test_one_sided_span_is_not_full_width_or_annual_range(self):
        result=compute(self.inventory);first,second=result['sections']
        self.assertIsNone(first['half_peak_diagnostic']['offshore_span_km'])
        self.assertEqual(first['half_peak_diagnostic']['status'],'offshore_boundary_blocked_by_missing_or_caution_cast')
        span=second['half_peak_diagnostic']
        self.assertAlmostEqual(span['offshore_span_km'],37.352311,places=5)
        self.assertEqual(span['bracketing_cast_ids'],['AB0505_058','AB0505_057'])
        self.assertEqual(span['nearshore_boundary_status'],'not_diagnosed')
        self.assertFalse(result['width_rank_eligible']);self.assertFalse(result['seasonal_playback_eligible'])
        self.assertIsNone(result['annual_width_range_km'])

    def test_threshold_walk_never_bridges_a_quality_gap(self):
        section=compute(self.inventory)['sections'][1]
        for key,value in [('quality_class','caution'),('northward_m_s',None)]:
            rows=copy.deepcopy(section['samples'])
            next(r for r in rows if r['cast_id']=='AB0505_058')[key]=value
            self.assertIsNone(measure(rows)['offshore_span_km'])
        for fraction in [0,1,float('nan')]:
            with self.assertRaises(ValueError):measure(section['samples'],fraction)

if __name__=='__main__':unittest.main()
