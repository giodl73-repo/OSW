import unittest
import numpy as np
import chen_indian_sec_axis_feasibility_v1 as subject


class AxisDiagnosticGuards(unittest.TestCase):
    def grid(self):
        lat=np.arange(-20.,-3.,1.)
        lon=np.arange(60.,111.,1.)
        u=np.ones((len(lat),len(lon)))
        u[8,:]=-2
        return lat,lon,u,np.zeros_like(u)

    def test_straight_westward_core_and_gate_order(self):
        lat,lon,u,v=self.grid();r=subject.trace(lat,lon,u,v,1)
        self.assertFalse(r['failures']);self.assertEqual(r['points'][0]['longitude'],105)
        self.assertEqual(r['points'][-1]['longitude'],65)
        self.assertTrue(all(p['latitude']==-12 for p in r['points']))
        self.assertIsNone(r['length_km']);self.assertFalse(r['physical_axis_admitted'])

    def test_reversing_column_is_a_gap_not_a_bridge(self):
        lat,lon,u,v=self.grid();u[:,20]=1;r=subject.trace(lat,lon,u,v,1)
        self.assertTrue(any(p is None for p in r['points']))
        self.assertTrue(any(f['reason']=='NO_FINITE_WESTWARD_CORE' for f in r['failures']))

    def test_eddy_core_jump_is_flagged(self):
        lat,lon,u,v=self.grid();u[8,20]=1;u[3,20]=-3
        r=subject.trace(lat,lon,u,v,1)
        self.assertTrue(any(f['reason']=='CORE_JUMPS_MORE_THAN_THREE_LATITUDE_CELLS' for f in r['failures']))

    def test_band_boundary_core_is_flagged(self):
        lat,lon,u,v=self.grid();u[2,:]=-4;r=subject.trace(lat,lon,u,v,1)
        self.assertTrue(any(f['reason']=='CORE_TOUCHES_SEARCH_BAND_EDGE' for f in r['failures']))

    def test_smoothing_does_not_fill_missing_center(self):
        field=np.ones((9,9));field[4,4]=np.nan
        self.assertTrue(np.isnan(subject.smooth(field,3)[4,4]))
        self.assertAlmostEqual(subject.smooth(field,3)[3,3],1)

    def test_wrong_shapes_and_coordinate_order_refused(self):
        lat,lon,u,v=self.grid()
        with self.assertRaises(ValueError):subject.trace(lat,lon,u[:-1],v,1)
        with self.assertRaises(ValueError):subject.trace(lat[::-1],lon,u,v,1)
        with self.assertRaises(ValueError):subject.smooth(u,7)


if __name__=='__main__':unittest.main()
