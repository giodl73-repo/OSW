import copy
import math
import unittest
import numpy as np
import sample_atlantic_current_depth_v1 as s


class AtlanticCorridorDepthTests(unittest.TestCase):
    def setUp(self):
        self.case={'current_id':'canary','entity_id':'current:canary','expected_route_vertices':3,
                   'primary_threshold_m_s':.05,'thresholds_m_s':[.05,.1,.2],'core_search_depth_interval_m':[0,200]}
        self.route={'current_id':'canary','coordinates_lon_lat':[[-18,30],[-19,27],[-20,24]]}

    def test_negative_atlantic_longitudes_match_native_zero360_axis(self):
        axis=np.array([0.,90.,180.,270.,322.,346.5,359.9])
        self.assertEqual(s.nearest_longitude_index(axis,-13.5),5)
        self.assertEqual(s.nearest_longitude_index(axis,-38),4)
        self.assertEqual(s.wrapped_longitude(346.5),-13.5)
        self.assertEqual(s.wrapped_longitude(322),-38)
        self.assertEqual(s.nearest_longitude_index(axis,.02),0)

    def test_cyclic_distance_and_first_tie_not_linear_wrong_hemisphere(self):
        self.assertEqual(s.nearest_longitude_index([1,180,359],0),0)
        self.assertEqual(s.nearest_longitude_index([-179,0,179],181),0)
        self.assertEqual(s.nearest_longitude_index([2,20,358],359.9),2)
        self.assertEqual(s.wrapped_longitude(180),-180)

    def test_longitude_invalid_axes_and_nonfinite_targets_rejected(self):
        for axis,target in [([],0),([[1,2]],0),([1,math.nan],0),([1,2],math.inf)]:
            with self.assertRaises(ValueError):s.nearest_longitude_index(axis,target)
        with self.assertRaises(ValueError):s.wrapped_longitude(math.nan)

    def test_exact_owner_order_reference_distances_and_downstream_bearings(self):
        points,distance,bearings=s.route_context(self.route,self.case)
        self.assertEqual(points,self.route['coordinates_lon_lat']);self.assertEqual(distance[0],0)
        self.assertTrue(distance[0]<distance[1]<distance[2])
        self.assertTrue(all(180<b<240 for b in bearings))
        route=copy.deepcopy(self.route);route['current_id']='benguela'
        with self.assertRaises(ValueError):s.route_context(route,self.case)

    def test_dropped_duplicate_nonfinite_or_outside_geographic_vertices_rejected(self):
        for points in [self.route['coordinates_lon_lat'][:-1],[[-18,30],[-18,30],[-20,24]],[[999,30],[-19,27],[-20,24]],[[math.nan,30],[-19,27],[-20,24]]]:
            with self.assertRaises(ValueError):s.route_context(dict(self.route,coordinates_lon_lat=points),self.case)

    def profiles(self,values):
        return [{'along_velocity_m_s':list(values),'normal_offset_km':offset} for offset in [-40,-20,0,20,40]]

    def test_object_specific_primary_threshold_and_equatorward_no_core_label(self):
        profiles=self.profiles([.08,.08,.03,-.1]);z=[0,100,200,400]
        slow=s.diagnoses(z,profiles,self.case)
        self.assertEqual(slow['selected_profile_index'],0)
        fast=s.diagnoses(z,profiles,dict(self.case,primary_threshold_m_s=.1))
        self.assertIsNone(fast['selected_profile_index'])
        self.assertIn('downstream',fast['primary_core_lower_descriptor']['status'])
        self.assertNotIn('poleward',fast['primary_core_lower_descriptor']['status'])
        self.assertIn('poleward',fast['primary_core_lower_descriptor']['frozen_selector_status'])

    def test_same_node_thresholds_fixed_tie_edge_missing_and_counterflow(self):
        profiles=self.profiles([.4,.8,.3,-.2]);z=[0,100,200,400]
        result=s.diagnoses(z,profiles,self.case)
        self.assertEqual(result['selected_profile_index'],0);self.assertEqual(result['horizontal_selection_status'],'edge_maximum_axis_unresolved')
        self.assertEqual(result['selected_profile_threshold_layers'],result['all_profile_threshold_layers'][0]['layers'])
        profiles[2]['along_velocity_m_s']=[.4,1.,None,-.2]
        result=s.diagnoses(z,profiles,self.case)
        self.assertEqual(result['selected_profile_index'],2)
        self.assertIsNone(result['primary_core_lower_descriptor']['lower_isotach_depth_m'])
        self.assertEqual(result['selected_profile_threshold_layers'][0]['lower_status'],'censored_before_missing_or_dry_level')

    def test_global_patch_and_cumulative_budget_rejected_before_source_field_read(self):
        for shape,used in [((40,4251,4500),0),((40,10,10),249000)]:
            with self.assertRaises(ValueError):s.check_budget(shape,used,250000)
        self.assertEqual(s.check_budget((40,10,10),0,250000),4000)

    def test_retained_owner_and_complete_case_keys_rejected_when_changed(self):
        result={'entity_id':'current:brazil','current_case':self.case}
        with self.assertRaises(ValueError):s.validate_retained(result,self.case,{'snapshot_times_utc':['2022-01-15T00:00:00Z']})
        result={'entity_id':'current:canary','current_case':self.case,'samples':[]}
        with self.assertRaises(ValueError):s.validate_retained(result,self.case,{'snapshot_times_utc':['2022-01-15T00:00:00Z']})


if __name__=='__main__':unittest.main()
