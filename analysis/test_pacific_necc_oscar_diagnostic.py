import copy
import unittest
from acquire_pacific_necc_oscar_section import CACHE,build as inventory,parse
from build_pacific_necc_oscar_section_diagnostic import build,measure,monthly_profiles,diagnostic_matches


class NeccSectionTests(unittest.TestCase):
    def test_roundoff_tolerance_does_not_allow_source_or_scope_changes(self):
        original=build();changed=copy.deepcopy(original)
        changed['months'][0]['zero_crossing']['span_km']+=1e-11
        self.assertTrue(diagnostic_matches(original,changed))
        changed['months'][0]['zero_crossing']['span_km']+=1e-6
        self.assertFalse(diagnostic_matches(original,changed))
        for key,value in [('protocol_sha256','changed'),('whole_current_representative',True),('peak_eligibility_m_s',.10000000001)]:
            changed=copy.deepcopy(original);changed[key]=value
            self.assertFalse(diagnostic_matches(original,changed))
        changed=copy.deepcopy(original);changed['months'][0]['profile'][0]['latitude']+=1e-11
        self.assertFalse(diagnostic_matches(original,changed))

    def test_pinned_archive_and_monthly_support(self):
        source=inventory();self.assertEqual(source['counts'],{'times':72,'latitudes_per_time':37,'values':2664,'missing_values':0})
        result=build();self.assertEqual(len(result['months']),12)
        self.assertEqual(result['summary']['resolved_months'],12)
        self.assertFalse(result['is_climatology'])
        self.assertFalse(result['monthly_width_is_mean_of_instantaneous_widths'])
        self.assertIsNone(result['annual_width_range_km'])
        for month in result['months']:
            self.assertGreaterEqual(month['sample_count'],5)
            self.assertEqual(len(month['profile']),37)
            self.assertEqual({t[5:7] for t in month['sample_times']},{f"{month['month']:02d}"})
            zero=month['zero_crossing']
            self.assertLess(zero['boundaries']['south']['latitude'],zero['peak_latitude'])
            self.assertGreater(zero['boundaries']['north']['latitude'],zero['peak_latitude'])
            for alternative in month['threshold_sensitivity']:
                if alternative['span_km'] is not None:self.assertLess(alternative['span_km'],zero['span_km'])

    def test_parser_rejects_unit_and_year_drift(self):
        metadata=(CACHE/'metadata.json').read_bytes();raw=(CACHE/'section.csv').read_bytes()
        with self.assertRaises(ValueError):parse(metadata,raw.replace(b'm s-1',b'cm s-1',1))
        with self.assertRaises(ValueError):parse(metadata,raw.replace(b'2013-01-01',b'2014-01-01',1))

    def test_missing_sample_is_not_averaged_away(self):
        frames=copy.deepcopy(inventory()['frames']);frames[0]['samples'][15]['eastward_m_s']=None
        january=monthly_profiles(frames)[0]
        self.assertIsNone(january['profile'][15]['eastward_m_s'])
        self.assertEqual(january['profile'][15]['missing_count'],1)

    def test_first_crossing_excludes_second_positive_component(self):
        profile=[{'latitude':i,'eastward_m_s':v} for i,v in enumerate([-.1,-.1,.2,.5,.2,-.1,.3,.2,-.1])]
        result=measure(profile)
        self.assertEqual(result['peak_latitude'],3)
        self.assertLess(result['boundaries']['north']['latitude'],5)
        profile[4]['eastward_m_s']=None
        result=measure(profile)
        self.assertIsNone(result['span_km'])
        self.assertEqual(result['boundaries']['north']['status'],'missing_before_crossing')

    def test_open_domain_and_weak_flow_are_unresolved_not_zero_width(self):
        profile=[{'latitude':i,'eastward_m_s':.2} for i in range(13)]
        self.assertIsNone(measure(profile)['span_km'])
        for row in profile:row['eastward_m_s']=.09
        self.assertEqual(measure(profile)['status'],'weak_or_no_eligible_peak')
        with self.assertRaises(ValueError):measure(profile,-.1)
        with self.assertRaises(ValueError):measure(list(reversed(profile)))


if __name__=='__main__':unittest.main()
