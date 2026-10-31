"""Boundary failures, temporal crossings and source custody must remain visible."""
import copy
from datetime import datetime,timedelta,timezone
from pathlib import Path
import unittest
from unittest.mock import patch
import build_p14n_component_spans as spans

def rows(values,latitudes=None):
    epoch=datetime(1993,7,14,tzinfo=timezone.utc)
    return [{'source_time_index':i,'observed_at':(epoch+timedelta(hours=i)).isoformat(),
             'latitude_degrees_north':latitudes[i] if latitudes else 46-i*.25,'longitude_degrees_east':179.,
             'layer_mean':{'eastward_m_s':u,'northward_m_s':.1,'joint_valid_thickness_m':200 if u is not None else 0}}
            for i,u in enumerate(values)]

class ComponentSpanTests(unittest.TestCase):
    def test_reconstruct_source_and_all_fourteen_scenarios(self):
        report=spans.verify()
        self.assertEqual(len(report['retained_samples']),132)
        for branch in report['branches']:
            self.assertEqual(len(branch['boundary_choice_scenarios']),3)
            self.assertEqual(len(branch['velocity_sensitivity_scenarios']),4)
            self.assertTrue(all(s['status']=='resolved' for s in branch['boundary_choice_scenarios']+branch['velocity_sensitivity_scenarios']))
        for flag in ['current_association_verified','new_width_record_admitted','width_rank_eligible','physical_edge_geometry_admitted','seasonal_playback_supported','sensitivity_is_confidence_interval','observed_track_reordered_by_latitude']:
            self.assertFalse(report[flag])
        self.assertIsNone(report['whole_current_width_km'])
        self.assertIsNone(report['annual_width_range_km'])
    def test_interpolation_and_known_equatorial_geodesic(self):
        source=rows([0,1,0],[0,0,0])
        for row,lon in zip(source,[0,1,2]):row['longitude_degrees_east']=lon
        result=spans.scenario(source,1,[-1,1],.5)
        self.assertAlmostEqual(result['before_peak']['crossing']['longitude_degrees_east'],.5)
        self.assertAlmostEqual(result['after_peak']['crossing']['longitude_degrees_east'],1.5)
        self.assertAlmostEqual(result['endpoint_separation_km'],111.31949079327357,places=8)
        self.assertTrue(result['fewer_than_four_native_spacings'])
    def test_nearest_crossing_does_not_merge_disjoint_lobes(self):
        source=rows([0,.8,0,1,0])
        result=spans.scenario(source,3,[44,46],.5)
        self.assertEqual(result['before_peak']['outside']['source_time_index'],2)
        self.assertEqual(result['lobe_source_time_indices'],[3])
    def test_missing_window_and_time_gap_preserve_unresolved(self):
        for case in ['missing','window','gap']:
            source=rows([0,.7,1,.7,0])
            window=[44,46]
            if case=='missing':source[1]['layer_mean']['eastward_m_s']=None
            elif case=='window':window=[44,45.6]
            else:source[1]['observed_at']='1993-07-14T00:29:59+00:00'
            result=spans.scenario(source,2,window,.5)
            with self.subTest(case=case):
                self.assertEqual(result['before_peak']['status'],{'missing':'missing_mean','window':'window_edge','gap':'time_gap'}[case])
                self.assertIsNone(result['endpoint_separation_km'])
                self.assertIsNone(result['display_endpoint_separation_km'])
        source=rows([0,1,0]);source[0]['observed_at']='1993-07-13T23:30:00+00:00'
        self.assertEqual(spans.scenario(source,1,[44,46],.5)['status'],'resolved')
    def test_ties_use_source_order_without_sorting_latitude(self):
        source=rows([0,1,1,.8,0],[46,45.5,45.6,45.2,45])
        result=spans.branch(source,'synthetic',[44,46])
        self.assertEqual(result['selected_peak']['source_time_index'],1)
        nominal=result['boundary_choice_scenarios'][1]
        self.assertEqual(nominal['lobe_source_time_indices'],[1,2,3])
        self.assertEqual(nominal['northward_steps_including_brackets'],1)
        self.assertGreater(nominal['track_length_to_endpoint_distance_ratio'],1)
    def test_weak_peak_ineligible_offsets_and_incomplete_envelope(self):
        self.assertEqual(spans.branch(rows([0,.019,0]),'weak',[44,46])['status'],'below_peak_floor')
        source=rows([.45,1,0])
        result=spans.branch(source,'partial',[44,46])
        self.assertIsNone(result['complete_boundary_choice_envelope_km'])
        self.assertEqual(result['boundary_choice_scenarios'][0]['status'],'unresolved')
        for offset in [-1,1]:self.assertEqual(spans.scenario(source,1,[44,46],.5,offset)['status'],'ineligible_threshold')
    def test_common_velocity_offset_matches_comparator_algebra(self):
        source=rows([0,.7,1,.7,0]);shifted=copy.deepcopy(source)
        for row in shifted:row['layer_mean']['eastward_m_s']+=.04
        a=spans.scenario(shifted,2,[44,46],.5)
        b=spans.scenario(source,2,[44,46],.5,-.02)
        self.assertAlmostEqual(a['endpoint_separation_km'],b['endpoint_separation_km'],places=8)
    def test_all_five_source_and_protocol_pins_are_enforced(self):
        original=Path.read_bytes
        for name in spans.FROZEN_INPUTS:
            target=spans.ROOT/name
            def altered(path):return original(path)+(b'x' if path==target else b'')
            with self.subTest(path=name),patch.object(Path,'read_bytes',altered),self.assertRaises(ValueError):spans.build()

if __name__=='__main__':unittest.main()
