import copy,json,unittest
from pathlib import Path
from check_red_sea_scope import validate

class RedSeaScopeTests(unittest.TestCase):
 def setUp(self):self.data=json.loads((Path(__file__).resolve().parents[1]/'research/red-sea-redsox-branch-reach-scope-audit.json').read_text(encoding='utf-8'))
 def test_reported_reach_and_three_local_components_preserved(self):
  validate(self.data)
  self.assertEqual(self.data['branches'][2]['parent_component'],self.data['branches'][1]['id'])
  self.assertEqual(self.data['reported_reach']['approximate_length_km'],130)
 def test_reject_channel_to_current_and_interval_promotion(self):
  for key,value in [('whole_current_length_km',130),('whole_current_width_km',5),('annual_length_range_km',[115,130]),('channel_values_are_current_dimensions',True),('channel_value_spread_is_uncertainty_interval',True),('seasonal_route_playback_supported',True)]:
   data=copy.deepcopy(self.data);data[key]=value
   with self.subTest(key=key),self.assertRaises(ValueError):validate(data)
  for key,value in [('fixed_depth_bounds_m',[100,250]),('source_velocity_quantity','along_stream_velocity'),('is_synoptic_snapshot',True),('velocity_threshold_m_s',.1),('rank_eligible',True),('geometry',{'type':'LineString'})]:
   data=copy.deepcopy(self.data);data['reported_reach'][key]=value
   with self.subTest(reach_key=key),self.assertRaises(ValueError):validate(data)
 def test_reject_branch_cycle_or_canonical_identity(self):
  data=copy.deepcopy(self.data);data['branches'][1]['parent_component']=data['branches'][2]['id']
  with self.assertRaises(ValueError):validate(data)
  data=copy.deepcopy(self.data);data['branches'][0]['canonical_identity']=True
  with self.assertRaises(ValueError):validate(data)

if __name__=='__main__':unittest.main()
