import unittest
import numpy as np
from derive_kuroshio_chandler_seasonal_depth_v1 import weights,core_index,crossing,describe,climatologies,json_safe


class SeasonalDepthTests(unittest.TestCase):
    def test_midpoint_weights_preserve_full_domain(self):
        w=weights([2.5,10,30]);self.assertEqual(w.tolist(),[6.25,13.75,10]);self.assertEqual(sum(w),30)
        with self.assertRaises(ValueError):weights([10,2.5])

    def test_horizontal_axis_uses_northward_maximum_west_of_separator(self):
        lon=np.arange(138,149,dtype=float)
        velocity=np.zeros((len(lon),2));velocity[3,:]=1;velocity[7,:]=-1
        index,value=core_index(velocity,[10,30],lon)
        self.assertEqual(index,3);self.assertGreater(value,0)
        self.assertEqual(core_index(-velocity,[10,30],lon),(None,None))

    def test_offshore_meander_cannot_win_over_source_kuroshio_branch(self):
        lon=np.arange(138,158,dtype=float)
        velocity=np.zeros((len(lon),2));velocity[3,:]=1;velocity[7,:]=-2;velocity[14,:]=10
        index,_=core_index(velocity,[10,30],lon)
        self.assertEqual(index,3)

    def test_missing_western_support_remains_unknown(self):
        self.assertEqual(core_index(np.ones((7,2)),[10,30],np.arange(151,158)),(None,None))

    def test_adjacent_threshold_crossing(self):
        r=crossing(np.array([0,100,200]),np.array([1,.2,-.2]),0,0.05)
        self.assertEqual(r['status'],'resolved_adjacent_level_crossing');self.assertAlmostEqual(r['depth_m'],137.5)

    def test_gap_is_unknown_not_bridged(self):
        r=crossing([0,100,200],[1,np.nan,-.2],0,0)
        self.assertEqual(r['status'],'unknown_gap_after_core');self.assertIsNone(r['depth_m'])

    def test_truncated_flow_and_absent_threshold_remain_distinct(self):
        self.assertEqual(crossing([0,100],[.2,.1],0,0)['status'],'right_censored_at_native_domain_end')
        self.assertEqual(crossing([0,100],[.02,0],0,.05)['status'],'threshold_not_exceeded')

    def test_sampled_edge_and_ties_do_not_establish_thickness(self):
        d=describe(np.array([2.5,10,30]),np.array([.4,.4,-.1]))
        self.assertEqual(d['core_depths_m'],[2.5,10]);self.assertTrue(d['core_at_shallowest_valid_level'])
        self.assertIsNone(d['physical_thickness_m']);self.assertIsNone(d['physical_depth_uncertainty_m'])

    def test_no_poleward_core_is_unknown(self):
        self.assertEqual(describe(np.array([0,100]),np.array([-.2,-.1]))['core_depths_m'],[])

    def test_climatology_uses_fixed16_profile_support(self):
        records=[]
        for year in range(16):
            v=[.5,0 if year else None]
            records.append({'calendar_month':1,'status':'axis_within_KUROSHIO_gate','native_velocity_profile_m_s':v,'derived':{'crossings':{}}})
        c=climatologies(records,np.array([2.5,100]))[0]
        self.assertEqual(c['finite_profile_counts_per_depth'],[16,15]);self.assertIsNone(c['native_mean_velocity_profile_m_s'][1])
        self.assertEqual(c['derived']['crossings']['0.05']['status'],'unknown_gap_after_core')
        self.assertEqual(climatologies(records[:-1],np.array([2.5,100]))[0]['status'],'unknown_incomplete16year_axis_support')

    def test_nonfinite_source_metadata_cannot_break_json(self):
        self.assertEqual(json_safe({'fill':np.float64(np.nan),'values':np.array([1,np.inf])}),{'fill':None,'values':[1,None]})


if __name__=='__main__':unittest.main()
