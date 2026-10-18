"""Protect observed vector support and the distinction from current width."""
import copy,json,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import build_aleutian_p14n_vector_section as section

class ObservedVectorSectionTests(unittest.TestCase):
 def test_original_reconstruction_and_scientific_scope(self):
  report=section.verify()
  self.assertEqual(report['retained_time_count'],132)
  self.assertEqual(report['retained_vector_positions'],4092)
  self.assertEqual(report['joint_valid_vector_positions'],4030)
  self.assertEqual(report['northward_latitude_steps'],16)
  self.assertEqual(report['gaps_over90minutes'],1)
  self.assertEqual(report['layer_means_with_complete_required_support'],131)
  self.assertEqual(len(report['track_legs']),131)
  self.assertTrue(all(not r['bearing_is_flow_direction'] for r in report['track_legs']))
  self.assertGreater(report['maximum_position_spacing_km'],report['median_position_spacing_km'])
  self.assertFalse(report['new_width_record_admitted'])
  self.assertFalse(report['current_association_verified'])
  self.assertIsNone(report['whole_current_width_km'])
  self.assertIsNone(report['annual_width_range_km'])
  self.assertEqual([r['latitude_search_window_degrees_north'] for r in report['branches']],[[41,43],[44,46]])
 def test_thickness_weighting_clips_both_boundary_cells(self):
  depth=np.arange(30,331,10,dtype=float);u=np.zeros(31);v=np.ones(31)
  u[7]=2;u[27]=4
  result=section.layer_mean(depth,u,v)
  self.assertAlmostEqual(result['eastward_m_s'],.15)
  self.assertEqual(result['northward_m_s'],1)
  self.assertEqual(result['joint_valid_thickness_m'],200)
 def test_components_share_support_and_do_not_become_speed(self):
  depth=np.arange(30,331,10,dtype=float);u=np.full(31,-3.);v=np.full(31,4.)
  u[10]=np.nan;v[11]=np.nan
  result=section.layer_mean(depth,u,v)
  self.assertEqual(result['joint_valid_thickness_m'],180)
  self.assertEqual(result['eastward_m_s'],-3)
  self.assertEqual(result['northward_m_s'],4)
 def test_incomplete_joint_layer_is_null_not_zero(self):
  depth=np.arange(30,331,10,dtype=float);u=np.ones(31);v=np.ones(31);v[9:14]=np.nan
  result=section.layer_mean(depth,u,v)
  self.assertEqual(result['joint_valid_thickness_m'],150)
  self.assertIsNone(result['eastward_m_s']);self.assertIsNone(result['northward_m_s'])
 def test_exact_80_percent_support_is_retained(self):
  depth=np.arange(30,331,10,dtype=float);u=np.ones(31);v=np.ones(31);v[9:13]=np.nan
  self.assertEqual(section.layer_mean(depth,u,v)['joint_valid_thickness_m'],160)
  self.assertEqual(section.layer_mean(depth,u,v)['eastward_m_s'],1)
 def test_depth_order_and_coverage_cannot_be_silently_changed(self):
  for depth in [np.array([100,100,300]),np.array([300,200,100]),np.array([150,200,250])]:
   with self.subTest(depth=depth),self.assertRaises(ValueError):section.layer_mean(depth,np.ones(len(depth)),np.ones(len(depth)))
 def test_every_original_and_protocol_pin_is_enforced(self):
  original=Path.read_bytes
  for name in section.FROZEN_INPUTS:
   target=section.ROOT/name
   def altered(path):return original(path)+(b'x' if path==target else b'')
   with self.subTest(path=name),patch.object(Path,'read_bytes',altered),self.assertRaises(ValueError):section.build()
 def test_fill_values_and_provider_limits_remain_missing(self):
  class Variable:
   values=np.array([1.,99999.,10.,-10.,np.nan])
   attrs={'_FillValue':99999.,'valid_min':-9.9,'valid_max':9.9}
  _,mask=section.valid_values(Variable())
  self.assertEqual(mask.tolist(),[True,False,False,False,False])

if __name__=='__main__':unittest.main()
