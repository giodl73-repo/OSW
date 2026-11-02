import unittest
import numpy as np
from derive_leeuwin_seasonal_depth_v1 import rotate,lower_crossing,mean_profile


class LocalBoundaryTests(unittest.TestCase):
    def test_rotation_true_bearings(self):
        self.assertAlmostEqual(rotate(1,0,90),1)
        self.assertAlmostEqual(rotate(0,1,0),1)
        self.assertLess(rotate(0,-1,348),0)

    def test_interpolated_crossing_not_deep_return(self):
        r=lower_crossing([0,100,200,300,400],[-.2,-.4,-.1,.1,-.1],[0,200])
        self.assertEqual(r['boundary_depth_m'],250)
        self.assertEqual(r['crossing_bracket_m'],[200,300])

    def test_gap_never_bridged(self):
        r=lower_crossing([0,100,200,300],[-.2,-.3,np.nan,.1],[0,100])
        self.assertEqual(r['status'],'gap_before_boundary');self.assertIsNone(r['boundary_depth_m'])

    def test_sampling_limit_not_promoted_to_bottom(self):
        r=lower_crossing([0,100,200],[-.2,-.3,-.1],[0,100])
        self.assertEqual(r['status'],'censored_at_deepest_level');self.assertIsNone(r['boundary_depth_m'])
        self.assertEqual(r['minimum_reach_m'],200)

    def test_no_negative_core_and_duplicate_depths(self):
        self.assertEqual(lower_crossing([0,100],[.1,.2],[0,100])['status'],'no_poleward_core')
        with self.assertRaises(ValueError):lower_crossing([0,0],[-.1,.1],[0,100])

    def test_paired_component_flags_and_counts(self):
        u=np.array([[0.,0.],[0.,0.]]);v=np.array([[-1.,-2.],[-3.,-4.]])
        uq=np.array([[1,1],[4,1]]);vq=np.array([[1,4],[4,9]])
        mean,n,observed=mean_profile(u,v,uq,vq,[True,True],[1,2,3,4],0)
        np.testing.assert_allclose(mean,[-2,-2]);np.testing.assert_array_equal(n,[2,1]);np.testing.assert_array_equal(observed,[1,0])

    def test_empty_phase_unknown_not_zero(self):
        a=np.zeros((1,2));q=np.ones((1,2))
        mean,n,observed=mean_profile(a,a,q,q,[False],[1],0)
        self.assertTrue(np.all(np.isnan(mean)));self.assertEqual(n.tolist(),[0,0])


if __name__=='__main__':unittest.main()
