import unittest
from datetime import datetime
from measure_caribbean_depth_layers_v1 import measure_layer,audit_time


class VelocityLayerTests(unittest.TestCase):
    def test_bracketed_layer_and_thickness(self):
        r=measure_layer([5,15,25,35,45],[0,-.2,-.3,-.2,0],.1)
        self.assertEqual(r['upper']['bracket_m'],[5,15]);self.assertEqual(r['lower']['bracket_m'],[35,45])
        self.assertAlmostEqual(r['layer_thickness_m'],30)
        self.assertEqual(r['layer_thickness_discretization_bracket_m'],[20,40])

    def test_sampling_edges_cannot_become_zero_and_bottom(self):
        r=measure_layer([5,15,25],[-.2,-.3,-.2],.1)
        self.assertEqual(r['upper']['status'],'sampling_edge_censored')
        self.assertEqual(r['lower']['supported_depth_m'],25);self.assertEqual(r['lower']['boundary_depth_operator'],'>=')
        self.assertIsNone(r['layer_thickness_m'])

    def test_missing_samples_are_not_bridged(self):
        r=measure_layer([5,15,25,35,45],[None,-.2,-.3,-.2,float('nan')],.1)
        self.assertEqual(r['upper']['status'],'missing_data_censored');self.assertEqual(r['lower']['status'],'missing_data_censored')
        self.assertIsNone(r['layer_thickness_m'])

    def test_short_strongest_component_not_replaced_with_weaker_component(self):
        r=measure_layer([5,15,25,35,45,55],[-.2,-.2,-.2,0,-.5,0],.1)
        self.assertEqual(r['status'],'strongest_component_insufficient_vertical_support')
        self.assertEqual(r['threshold_components'],2)

    def test_threshold_and_direction_change_results(self):
        self.assertEqual(measure_layer([5,15,25],[.3,.4,.3],.1)['status'],'no_threshold_layer_detected')
        self.assertEqual(measure_layer([5,15,25],[-.08,-.09,-.08],.1)['status'],'no_threshold_layer_detected')
        self.assertEqual(measure_layer([5,15,25],[-.08,-.09,-.08],.05)['status'],'velocity_defined_layer')

    def test_disjoint_layers_remain_separate(self):
        r=measure_layer([5+10*i for i in range(9)],[0,-.2,-.3,-.2,0,-.2,-.4,-.2,0],.1)
        self.assertEqual(r['core_depth_m'],65);self.assertEqual(r['threshold_components'],2)
        self.assertEqual(r['upper']['bracket_m'],[45,55])

    def test_interval_containment_and_source_time_preserved(self):
        d=lambda x:datetime.fromisoformat('2024-05-18T'+x)
        windows=[('one',d('00:00:00'),d('12:00:00')),('two',d('12:00:00'),d('23:00:00'))]
        r=audit_time(d('10:00:00'),d('11:00:00'),d('11:00:00'),windows)
        self.assertEqual(r['contained_transect'],'one');self.assertTrue(r['reported_matches_end'])
        self.assertEqual(r['derived_midpoint'],'2024-05-18T10:30:00');self.assertFalse(r['reported_matches_midpoint'])
        self.assertIsNone(audit_time(d('11:00:00'),d('13:00:00'),d('13:00:00'),windows)['contained_transect'])

    def test_invalid_depths_and_time_fail(self):
        with self.assertRaises(ValueError):measure_layer([5,5,15],[-.2]*3,.1)
        with self.assertRaises(ValueError):measure_layer([5,15],[-.2],.1)
        with self.assertRaises(ValueError):audit_time(datetime(2024,2,1),datetime(2024,1,1),datetime(2024,1,1),[])


if __name__=='__main__':unittest.main()
