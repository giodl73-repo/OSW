"""Correspondence support must not turn temporal proximity into a current width."""
import copy
from pathlib import Path
import unittest
from unittest.mock import patch
import numpy as np
import gsw
from pyproj import Geod
import build_p14n_hydrography_companion as hydro
from build_aleutian_p14n_vector_section import verify as verify_vectors

class HydrographyCompanionTests(unittest.TestCase):
 def test_original_reconstruction_and_support(self):
  report=hydro.verify()
  self.assertEqual(report['source_profile_count'],198)
  self.assertEqual(report['selected_cast_count'],17)
  self.assertEqual(report['selected_casts_with_verified_bottom_metadata'],17)
  self.assertEqual(report['context_cells'],3009)
  self.assertEqual(report['joint_acceptable_context_cells'],2525)
  self.assertEqual(report['candidate_pair_count'],84)
  self.assertEqual(report['adcp_profiles_with_candidate_pairs'],84)
  self.assertEqual(report['adcp_profiles_with_multiple_candidate_casts'],0)
  self.assertEqual(report['velocity_section'],verify_vectors())
  self.assertFalse(report['new_width_record_admitted'])
  self.assertFalse(report['current_association_verified'])
  self.assertFalse(report['hydrography_interpolated_to_adcp'])
  self.assertIsNone(report['whole_current_width_km'])
  self.assertIsNone(report['annual_width_range_km'])
 def test_reference_pressure_conversion_retains_units_and_depth_sign(self):
  # TEOS-10 gsw_z_from_p published example at4N, metres rather than dbar.
  expected=[9.9445834469453,49.718089701255,124.2726219409978]
  np.testing.assert_allclose(-gsw.z_from_p([10,50,125],4,0,0),expected,rtol=0,atol=5e-8)
 def test_original_codes_and_edited_values_are_not_erased(self):
  report=hydro.verify();cells=[cell for cast in report['casts'] for cell in cast['cells']]
  edited=[cell for cell in cells if 7 in [cell['temperature_qc'],cell['salinity_qc']]]
  self.assertEqual(len(edited),482)
  self.assertTrue(all(not cell['joint_acceptable'] for cell in edited))
  self.assertTrue(all(cell['practical_salinity_pss78'] is not None for cell in edited))
  questionable=[cell for cell in cells if cell['salinity_qc']==3]
  self.assertEqual(len(questionable),2)
  self.assertTrue(all(not cell['joint_acceptable'] for cell in questionable))
 def test_candidate_boundaries_and_all_qualifying_matches(self):
  cast={'source_profile_index':1,'identity':'synthetic:1:1','nominal_bottom_time_utc':'1993-07-13T12:00:00Z','latitude_degrees_north':45.,'longitude_degrees_east':179.,'bottom_metadata_verified':True}
  geod=Geod(ellps='WGS84')
  def sample(index,metres,when):
   lon,lat,_=geod.fwd(179,45,90,metres)
   return {'source_time_index':index,'observed_at':when,'longitude_degrees_east':lon,'latitude_degrees_north':lat,'layer_mean':{'eastward_m_s':0.}}
  rows=[sample(1,14999,'1993-07-13T15:00:00Z'),sample(2,15001,'1993-07-13T15:00:00Z'),sample(3,100,'1993-07-13T15:00:01Z'),sample(4,100,'1993-07-13T09:00:00Z')]
  pairs=hydro.candidate_pairs([cast,{**cast,'source_profile_index':2,'identity':'synthetic:2:1'}],rows)
  self.assertEqual(len(pairs),4)
  self.assertEqual({row['adcp_source_time_index'] for row in pairs},{1,4})
  self.assertTrue(all(not row['same_depth_sampling_simultaneity_verified'] for row in pairs))
  self.assertTrue(all(not row['independent_width_validation'] for row in pairs))
 def test_summary_event_time_and_hemisphere(self):
  raw='325023_1 P14N 29 1 ROS 071393 0842 BO 47 59.71 N 179 00.01 E GPS'
  result=hydro.summary_events(raw)[('325023_1','29',1)][0]
  self.assertEqual(result['time_utc'],'1993-07-13T08:42:00Z')
  self.assertAlmostEqual(result['latitude_degrees_north'],47+59.71/60)
  self.assertAlmostEqual(result['longitude_degrees_east'],179+.01/60)
 def test_each_original_protocol_and_vector_pin_is_enforced(self):
  original=Path.read_bytes
  for name in hydro.FROZEN_INPUTS:
   target=hydro.ROOT/name
   def altered(path):return original(path)+(b'x' if path==target else b'')
   with self.subTest(path=name),patch.object(Path,'read_bytes',altered),self.assertRaises(ValueError):hydro.build()

if __name__=='__main__':unittest.main()
