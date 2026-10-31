import copy
import json
import unittest
from pyproj import Geod
import pacific_nec_nominal_width_v1 as m


class NominalWidth(unittest.TestCase):
    def facts(self):return json.loads((m.ROOT/m.FACTS).read_bytes())

    def test_wgs84_meridian_conversion_and_coarse_display(self):
        d=m.prepare(self.facts())
        self.assertTrue(990<d['calculation']['audit_distance_km']<1000)
        self.assertEqual(d['approximate_width_km'],1000)
        self.assertAlmostEqual(m.meridional_km(8,17),Geod(ellps='WGS84').inv(137,8,137,17)[2]/1000,places=8)

    def test_invalid_or_reversed_endpoints_refused(self):
        for pair in [(17,8),(8,8),(-91,8),(8,float('nan')),(True,17),('8',17)]:
            with self.assertRaises(ValueError):m.meridional_km(*pair)

    def test_cannot_mix_related_source_band_or_promote_precision(self):
        for key,value in [('latitude_bounds_deg_north',[7,17]),('source_reported_width_km',1000),('edge_operator','u=0'),('annual_width_range_km',[990,1100]),('seasonal_playback_eligible',True)]:
            facts=copy.deepcopy(self.facts());facts['nominal_surface_width'][key]=value
            with self.assertRaises(ValueError,msg=key):m.prepare(facts)

    def test_unknown_geometry_time_and_ranges_remain_unknown(self):
        d=m.prepare(self.facts())
        for key in ['paired_edge_coordinates','section_geometry','observed_period','sampling_dates','annual_width_range_km','numerical_width_uncertainty_km']:self.assertIsNone(d[key],key)
        for key in ['whole_current_representative','flow_normal_width_diagnosed','width_rank_eligible','annual_extrema_eligible','seasonal_playback_eligible','independent_new_observation','source_figure_digitized','installed']:self.assertIs(d[key],False,key)


if __name__=='__main__':unittest.main()
