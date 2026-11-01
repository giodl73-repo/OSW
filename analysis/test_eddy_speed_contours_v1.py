import math
import unittest

import numpy as np

from eddy_speed_contours_v1 import (GRAVITY_M_S2, OMEGA_RAD_S, RADIUS_M,
    ReviewRejected, compare_steps, contour_mean_speed, geostrophic_velocity,
    select_peak, speed_profile)


class SpeedContourTests(unittest.TestCase):
    def mound(self,n=121):
        lon=np.linspace(-92,-88,n);lat=np.linspace(23,27,n)
        x,y=np.meshgrid(RADIUS_M*math.cos(math.radians(25))*np.deg2rad(lon+90),RADIUS_M*np.deg2rad(lat-25))
        return lon,lat,.3*np.exp(-(x*x+y*y)/(2*40000**2))

    def test_gaussian_known_speed_radius_and_units(self):
        lon,lat,z=self.mound();r,_=speed_profile(lon,lat,z,[-90,25])
        self.assertEqual(r['status'],'PASS_SPEED_CORE_DIAGNOSTIC')
        expected=GRAVITY_M_S2*.3/(2*OMEGA_RAD_S*math.sin(math.radians(25))*40000)*math.exp(-.5)
        self.assertLess(abs(r['selected']['speed_equivalent_radius_km']/40-1),.025)
        self.assertLess(abs(r['selected']['mean_geostrophic_speed_m_s']/expected-1),.03)
        self.assertEqual(r['selected']['enclosed_strict_maxima'],1)

    def test_constant_height_offset_cancels(self):
        lon,lat,z=self.mound(81)
        a,_=speed_profile(lon,lat,z,[-90,25],step_m=.01)
        b,_=speed_profile(lon,lat,z+5,[-90,25],step_m=.01)
        self.assertEqual(a['status'],b['status']);self.assertEqual(a['status'],'PASS_SPEED_CORE_DIAGNOSTIC')
        for k in ['area_km2','mean_geostrophic_speed_m_s','speed_equivalent_radius_km']:
            self.assertTrue(math.isclose(a['selected'][k],b['selected'][k],rel_tol=1e-8),k)

    def test_grid_and_level_refinement_converge(self):
        errors=[]
        expected=GRAVITY_M_S2*.3/(2*OMEGA_RAD_S*math.sin(math.radians(25))*40000)*math.exp(-.5)
        for n in [51,121]:
            lon,lat,z=self.mound(n);coarse,_=speed_profile(lon,lat,z,[-90,25],step_m=.005)
            fine,_=speed_profile(lon,lat,z,[-90,25],step_m=.0025)
            self.assertEqual(compare_steps(coarse,fine)['status'],'PASS_STEP_CONVERGENCE_DIAGNOSTIC')
            errors.append(abs(fine['selected']['mean_geostrophic_speed_m_s']-expected))
        self.assertLess(errors[1],errors[0])

    def test_masked_neighbor_and_outer_derivatives_are_not_zero_filled(self):
        lon,lat,z=self.mound(51);z[25,25]=np.nan;u,v=geostrophic_velocity(lon,lat,z)
        for iy,ix in [(25,25),(24,25),(26,25),(25,24),(25,26)]:
            self.assertTrue(np.isnan(u[iy,ix]) and np.isnan(v[iy,ix]))
        self.assertTrue(np.all(np.isnan(u[0,:])) and np.all(np.isnan(v[:,-1])))

    def test_missing_velocity_segment_rejects_whole_average(self):
        lon=np.array([-91.,-90.,-89.]);lat=np.array([24.,25.,26.]);u=np.ones((3,3));v=u.copy();u[1,1]=np.nan
        points=np.array([[-90.5,24.5],[-89.5,24.5],[-89.5,25.5],[-90.5,25.5],[-90.5,24.5]])
        with self.assertRaisesRegex(ReviewRejected,'missing_velocity_support'):contour_mean_speed(lon,lat,u,v,points)

    def test_competing_peaks_are_not_resolved_by_nearest_choice(self):
        lon,lat,z=self.mound(121);x,y=np.meshgrid(lon,lat)
        z=np.exp(-((x+90.5)**2+(y-25)**2)/.04)+np.exp(-((x+89.5)**2+(y-25)**2)/.04)
        with self.assertRaisesRegex(ReviewRejected,'multiple_peaks'):select_peak(lon,lat,z,[-90,25])

    def test_plateau_is_not_broken_by_array_order(self):
        lon,lat,z=self.mound(51);z[25,26]=z[25,25]
        with self.assertRaisesRegex(ReviewRejected,'plateau_or_tied_peak'):select_peak(lon,lat,z,[-90,25])

    def test_missing_peak_location_is_not_a_name_match(self):
        lon,lat,z=self.mound(51)
        with self.assertRaisesRegex(ReviewRejected,'no_strict_peak'):select_peak(lon,lat,z,[-98,30])

    def test_insufficient_sampled_interior_rejected(self):
        lon,lat,z=self.mound(51);r,_=speed_profile(lon,lat,z,[-90,25],minimum_interior_samples=100000)
        self.assertEqual(r['status'],'REJECTED');self.assertEqual(r['reason'],'insufficient_supported_contours')

    def test_sweep_endpoint_does_not_become_radius(self):
        lon,lat,z=self.mound();r,p=speed_profile(lon,lat,z,[-90,25],maximum_drop_m=.03)
        self.assertEqual(r['status'],'REJECTED');self.assertEqual(r['reason'],'maximum_at_supported_sweep_boundary');self.assertIsNone(p)

    def test_open_domain_truncation_cannot_supply_speed_core(self):
        lon,lat,z=self.mound();stop=67
        r,p=speed_profile(lon[:stop],lat,z[:,:stop],[-90,25])
        self.assertEqual(r['status'],'REJECTED');self.assertIsNone(p)

    def test_merged_contours_with_two_maxima_are_excluded(self):
        lon,lat,z=self.mound();x,y=np.meshgrid(lon,lat)
        z=.3*np.exp(-((x+90.5)**2+(y-25)**2)/.12)+.25*np.exp(-((x+89.5)**2+(y-25)**2)/.12)
        r,_=speed_profile(lon,lat,z,[-90.5,25],search_radius_km=40)
        self.assertGreater(r['exclusions'].get('multiple_enclosed_maxima',0),0)
        self.assertTrue(all(c['enclosed_strict_maxima']==1 for c in r['profile']))


if __name__=='__main__':unittest.main()
