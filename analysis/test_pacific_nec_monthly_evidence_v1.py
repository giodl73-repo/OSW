import copy
import unittest
import pacific_nec_monthly_evidence_v1 as evidence


class EvidenceCompaction(unittest.TestCase):
    def fixture(self):
        return {'months':[{'month':1,'length_km':None,'reason':'rejected_columns'}],
                'section_spans':[{'month':1,'longitude_east':137,'threshold_m_s':threshold,
                  'width_km':value,'profile':[{'latitude':8,'eastward_m_s':-.1,'missing_samples':0}]}
                  for threshold,value in [(0,1200.0000000000002),(.025,900.1),(.05,None)]]}

    def test_roundtrip_keeps_nulls_precision_and_distinct_operators(self):
        original=self.fixture();saved=copy.deepcopy(original)
        compact=evidence.compact(original,'a'*64)
        self.assertEqual(evidence.expand(compact),saved)
        self.assertEqual(original,saved)
        self.assertEqual(len(compact['section_profiles']),1)

    def test_different_profiles_not_silently_deduplicated(self):
        report=self.fixture();report['section_spans'][1]['profile'][0]['eastward_m_s']=-.2
        with self.assertRaises(ValueError):evidence.compact(report,'a'*64)

    def test_wrong_association_or_unused_profile_refused(self):
        for change in ('association','unused'):
            compact=evidence.compact(self.fixture(),'a'*64)
            if change=='association':compact['report']['section_spans'][0]['profile_ref_v1']='2:137'
            else:compact['section_profiles']['unused']=[]
            with self.assertRaises(ValueError):evidence.expand(compact)


if __name__=='__main__':unittest.main()
