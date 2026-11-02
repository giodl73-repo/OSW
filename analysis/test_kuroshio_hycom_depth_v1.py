import copy
import math
import unittest
import numpy as np
import sample_kuroshio_hycom_depth_v1 as s


class KuroshioAxisDepthTests(unittest.TestCase):
    def setUp(self):
        self.op={'snapshot_times_utc':['2024-01-15T00:00:00Z','2024-07-15T00:00:00Z'],
                 'latitude_gates':[18.5,21.5,24.5,27.5,29.5],
                 'primary_threshold_m_s':.1,'thresholds_m_s':[.05,.1,.2],
                 'core_search_depth_interval_m':[0,200],'eligibility':{'whole_route_physical_depth':False}}
        self.report={'entity_id':'current:kuroshio','source_year':2024,'cases':[
            {'sample_date':t[:10],'source_level':1,'nominal_depth_m':.49,'latitude':lat,'tangent_half_window_km':14,
             'id':t[:10]+str(lat),'gate':{'point':[123,lat],'segment_km':10},'axis_crossing_count':1,
             'tangent_endpoints':[{'point':[123,lat-.1]},{'point':[123,lat+.1]}],
             'axis_tangent_azimuth_degrees':0.,'status':'boundary_crossing_missing_or_multiple'}
            for t in self.op['snapshot_times_utc'] for lat in self.op['latitude_gates']]}

    def test_exact_dates_gates_and_only_declared_source_level_and_window(self):
        rows=s.axis_cases(self.report,self.op)
        self.assertEqual(len(rows),10);self.assertTrue(all(r['axis_geometry_query_eligible'] for r in rows))
        self.assertEqual(len({r['source_axis_case_pointer'] for r in rows}),10)
        # A boundary-span failure does not invalidate an otherwise resolved axis tangent.
        self.assertTrue(all(r['source_axis_case_status']=='boundary_crossing_missing_or_multiple' for r in rows))
        report=copy.deepcopy(self.report);other=copy.deepcopy(report['cases'][0]);other['source_level']=23;report['cases'].append(other)
        self.assertEqual(s.axis_cases(report,self.op),rows)

    def test_missing_duplicate_wrong_identity_and_level_depth_rejected(self):
        for report in [dict(self.report,cases=self.report['cases'][:-1]),dict(self.report,cases=self.report['cases']+[self.report['cases'][0]]),dict(self.report,entity_id='current:kuroshio-extension'),dict(self.report,source_year=2023)]:
            with self.assertRaises(ValueError):s.axis_cases(report,self.op)
        report=copy.deepcopy(self.report);report['cases'][0]['nominal_depth_m']=0
        with self.assertRaises(ValueError):s.axis_cases(report,self.op)

    def test_axis_gaps_long_legs_reversed_tangent_are_retained_unqueried(self):
        for key,value in [('gate',None),('axis_crossing_count',2),('tangent_endpoints',None),('axis_tangent_azimuth_degrees',math.nan)]:
            report=copy.deepcopy(self.report);report['cases'][0][key]=value
            rows=s.axis_cases(report,self.op);self.assertEqual(len(rows),10);self.assertFalse(rows[0]['axis_geometry_query_eligible'])
        report=copy.deepcopy(self.report);report['cases'][0]['gate']['segment_km']=51
        self.assertFalse(s.axis_cases(report,self.op)[0]['axis_geometry_query_eligible'])
        report=copy.deepcopy(self.report);report['cases'][0]['tangent_endpoints'].reverse()
        self.assertFalse(s.axis_cases(report,self.op)[0]['axis_geometry_query_eligible'])

    def profiles(self):
        return [{'along_velocity_m_s':[.4,.8,.3,-.2],'normal_offset_km':i} for i in [-40,-20,0,20,40]]

    def test_first_offset_tie_and_edge_flags_not_reselected_for_better_depth(self):
        profiles=self.profiles();result=s.diagnose_profiles([0,100,200,400],profiles,self.op)
        self.assertEqual(result['selected_profile_index'],0)
        self.assertEqual(result['horizontal_selection_status'],'edge_maximum_axis_unresolved')
        self.assertEqual(len(result['all_profile_threshold_layers']),5)
        self.assertEqual(len(result['selected_profile_threshold_layers']),3)

    def test_deep_counterflow_stays_signed_and_thresholds_use_same_node(self):
        profiles=self.profiles();profiles[2]['along_velocity_m_s']=[.4,1.,.3,-.2]
        result=s.diagnose_profiles([0,100,200,400],profiles,self.op)
        self.assertEqual(result['selected_profile_index'],2)
        layer=result['selected_profile_threshold_layers'][1]
        self.assertAlmostEqual(layer['lower_depth_m'],280)
        self.assertEqual(layer['upper_depth_m'],0)
        self.assertEqual(result['selected_profile_threshold_layers'],result['all_profile_threshold_layers'][2]['layers'])
        self.assertAlmostEqual(float(s.along_velocity(np.array([1]),np.array([-1]),0)[0]),-1)

    def test_missing_vertical_sample_censors_without_bridging_or_seabed_fill(self):
        profiles=self.profiles()
        for profile in profiles:profile['along_velocity_m_s']=[.4,.8,None,-.2]
        result=s.diagnose_profiles([0,100,200,400],profiles,self.op)
        primary=result['selected_profile_threshold_layers'][1]
        self.assertIsNone(primary['lower_depth_m']);self.assertIsNone(primary['layer_thickness_m'])
        self.assertEqual(primary['lower_last_connected_depth_m'],100)
        self.assertEqual(primary['lower_status'],'censored_before_missing_or_dry_level')

    def test_no_qualifying_current_retains_null_selection(self):
        profiles=self.profiles()
        for profile in profiles:profile['along_velocity_m_s']=[-.1,-.2,-.3,-.4]
        result=s.diagnose_profiles([0,100,200,400],profiles,self.op)
        self.assertIsNone(result['selected_profile_index']);self.assertEqual(result['selected_profile_threshold_layers'],[])

    def test_field_budget_rejects_global_or_excess_before_read(self):
        with self.assertRaises(ValueError):s.check_budget((40,4251,4500),0,250000)
        with self.assertRaises(ValueError):s.check_budget((40,10,10),249000,250000)
        self.assertEqual(s.check_budget((40,10,10),0,250000),4000)


if __name__=='__main__':unittest.main()
