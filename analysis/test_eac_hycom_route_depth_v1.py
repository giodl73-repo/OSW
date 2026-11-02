import unittest
import numpy as np
from sample_eac_hycom_route_depth_v1 import along_velocity,core_lower_contour,select_profile


class ModelCoreDepthTests(unittest.TestCase):
    def test_downstream_bearing_rotation(self):
        self.assertAlmostEqual(along_velocity(0,-1,180),1)
        self.assertAlmostEqual(along_velocity(1,0,90),1)

    def test_first_lower_isotach_not_deeper_return(self):
        r=core_lower_contour([0,100,200,300,400],[.2,.4,.1,0,.2],.05,[0,200])
        self.assertEqual(r['lower_isotach_depth_m'],250)
        self.assertEqual(r['depth_bracket_m'],[200,300])

    def test_missing_or_dry_level_is_censored_not_seabed_bottom(self):
        r=core_lower_contour([0,100,200],[.2,.3,np.nan],.05,[0,100])
        self.assertIsNone(r['lower_isotach_depth_m']);self.assertEqual(r['last_contiguous_above_threshold_depth_m'],100)

    def test_last_model_level_is_censored(self):
        r=core_lower_contour([0,100,200],[.2,.3,.1],.05,[0,100])
        self.assertEqual(r['status'],'censored_at_last_model_depth');self.assertIsNone(r['lower_isotach_depth_m'])

    def test_opposing_flow_is_not_current_core(self):
        i,r=select_profile([0,100],[{'along_velocity_m_s':[-.5,-.3]}],.05,[0,200])
        self.assertIsNone(i);self.assertIsNone(r['lower_isotach_depth_m'])

    def test_fixed_window_strongest_core_and_tie_order(self):
        p=[{'along_velocity_m_s':[.2,.3,.1]},{'along_velocity_m_s':[.4,.5,.1]},{'along_velocity_m_s':[.4,.5,.1]}]
        i,r=select_profile([0,100,200],p,.05,[0,100]);self.assertEqual(i,1)
        self.assertEqual(r['core_along_velocity_m_s'],.5)

    def test_invalid_axes_or_threshold_rejected(self):
        for z,t in [([0,0],.05),([100,0],.05),([0,100],0),([0,100],float('nan'))]:
            with self.assertRaises(ValueError):core_lower_contour(z,[.2,.1],t,[0,100])


if __name__=='__main__':unittest.main()
