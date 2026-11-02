import copy
import unittest
from build_agulhas_individual_depth_distributions_v1 import quantile,summarize,build


def rows():
    return [{'calendar_month':1,'date':str(year)+'-01-15','longitude':33,'latitude':-29,
             'derived':{'crossings':{'0.1':{'status':'resolved_adjacent_level_crossing','depth_m':float(i)}}}}
            for i,year in enumerate(range(2004,2020))]


class IndividualDistributionTests(unittest.TestCase):
    def test_declared_quantile_and_sample_range(self):
        d=summarize(rows(),1,'0.1');self.assertEqual(d['statistics']['median_m'],7.5)
        self.assertEqual(d['statistics']['q25_m'],3.75);self.assertEqual(d['statistics']['q75_m'],11.25)
        self.assertEqual([d['statistics']['minimum_m'],d['statistics']['maximum_m']],[0,15])
        self.assertFalse(d['statistics_are_confidence_bounds']);self.assertIsNone(d['physical_depth_uncertainty_m'])

    def test_missing_crossing_prevents_biased_complete_case_summary(self):
        r=rows();r[0]['derived']['crossings']['0.1']={'status':'unknown_gap_after_core','depth_m':None}
        d=summarize(r,1,'0.1');self.assertEqual(d['resolved_year_count'],15)
        self.assertIsNone(d['statistics']);self.assertEqual(len(d['year_samples']),16)

    def test_censoring_is_not_a_numeric_boundary(self):
        r=rows();r[0]['derived']['crossings']['0.1']={'status':'right_censored_at_native_domain_end','depth_m':None}
        d=summarize(r,1,'0.1');self.assertIsNone(d['statistics']);self.assertIsNone(d['year_samples'][0]['depth_m'])

    def test_unique_calendar_support_and_finite_depth_required(self):
        for mutation in ['duplicate','wrong_month','nan']:
            r=rows()
            if mutation=='duplicate':r[-1]['date']='2004-01-15'
            elif mutation=='wrong_month':r[-1]['date']='2019-02-15'
            else:r[-1]['derived']['crossings']['0.1']['depth_m']=float('nan')
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):summarize(r,1,'0.1')

    def test_real_source_keeps_all12_complete10cms_groups(self):
        d=build();selected=[r for r in d['records'] if r['poleward_velocity_threshold_m_s']==.1]
        self.assertEqual(len(selected),12);self.assertTrue(all(r['resolved_year_count']==16 for r in selected))
        self.assertTrue(all(r['statistics'] is None for r in d['records'] if r['poleward_velocity_threshold_m_s']==.05))
        self.assertEqual(d['new_independent_observations'],0)


if __name__=='__main__':unittest.main()
