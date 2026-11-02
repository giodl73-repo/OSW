import unittest
from sample_eac_hycom_route_depth_v2 import check_budget


class HyperslabBudgetTests(unittest.TestCase):
    def test_global_or_cumulative_field_request_rejected_before_read(self):
        with self.assertRaises(ValueError):check_budget((40,4251,4500),0,250000)
        with self.assertRaises(ValueError):check_budget((40,10,10),249000,250000)

    def test_small_positive_patch_and_invalid_axes(self):
        self.assertEqual(check_budget((40,10,10),0,250000),4000)
        with self.assertRaises(ValueError):check_budget((40,0,10),0,250000)


if __name__=='__main__':unittest.main()
