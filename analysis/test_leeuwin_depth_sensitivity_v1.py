from datetime import datetime
import unittest
import numpy as np
from check_leeuwin_depth_sensitivity_v1 import calendar_day,calendar_profiles,profiles,threshold_descriptor,negative_local_maxima


class AveragingSensitivityTests(unittest.TestCase):
    def test_unequal_month_lengths_have_explicit_weighting(self):
        times=[datetime(2020,1,1),datetime(2020,1,2),datetime(2020,2,1)]
        p=profiles(np.array([[0.],[0.],[3.]]),times,[1,2])
        self.assertEqual(p['pooled_daily'][0],1)
        self.assertEqual(p['equal_month_climatologies'][0],1.5)

    def test_year_months_weighted_equally(self):
        times=[datetime(2020,1,1),datetime(2020,1,2),datetime(2021,1,1)]
        p=profiles(np.array([[0.],[0.],[3.]]),times,[1])
        self.assertEqual(p['equal_year_months'][0],1.5)
        self.assertEqual(p['pooled_daily'][0],1)

    def test_calendar_window_wraps_year_end_without_leap_shift(self):
        p=calendar_profiles(np.array([[2.],[4.]]),[datetime(2020,12,31),datetime(2021,1,1)])
        self.assertEqual(p[0,0],3);self.assertEqual(p[-1,0],3)
        self.assertIsNone(calendar_day(datetime(2020,2,29)))
        self.assertEqual(calendar_day(datetime(2020,3,1)),59)

    def test_threshold_assumption_not_strict_zero(self):
        z=np.array([0,100,200]);v=np.array([-.2,-.1,-.001])
        self.assertIsNone(threshold_descriptor(z,v,[0,100],0)['boundary_depth_m'])
        self.assertIsNotNone(threshold_descriptor(z,v,[0,100],.005)['boundary_depth_m'])
        with self.assertRaises(ValueError):threshold_descriptor(z,v,[0,100],-.01)

    def test_negative_local_maximum_not_boundary(self):
        peaks=negative_local_maxima(np.array([0,100,200,300]),np.array([-.2,-.1,-.001,-.01]),[0,100])
        self.assertEqual(peaks,[{'depth_m':200.,'velocity_m_s':-.001,'is_flow_boundary':False}])

    def test_missing_calendar_window_stays_unknown(self):
        p=calendar_profiles(np.array([[2.]]),[datetime(2020,1,1)])
        self.assertTrue(np.isnan(p[100,0]))


if __name__=='__main__':unittest.main()
