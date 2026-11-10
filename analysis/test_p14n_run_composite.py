"""Assumed links cannot erase missing support or become observed widths."""
from datetime import datetime,timedelta,timezone
from pathlib import Path
from unittest.mock import patch
import copy,hashlib,json,unittest,xml.etree.ElementTree as ET
import build_p14n_run_composite as composite

EPOCH=datetime(1993,7,14,tzinfo=timezone.utc)
def profile(index,start,end,u,lat=45):
 return {'source_time_index':index,'ensemble_start_utc':composite.stamp(EPOCH+timedelta(seconds=start)),
  'ensemble_end_utc':composite.stamp(EPOCH+timedelta(seconds=end)),
  'latitude_degrees_north':lat,'longitude_degrees_east':-181.,
  'layer_mean':{'eastward_m_s':u,'northward_m_s':2*u},'ctd_event_overlaps':[]}

def row(index,latitude,u):
 start=EPOCH+timedelta(hours=6*index)
 return {'run_index':index,'union_coverage_seconds':7200.,'boundary_eligible_coverage':True,
  'northward_steps':0,'contributor_latitude_range':[latitude-.05,latitude+.05],
  'mean':{'latitude_degrees_north':latitude,'longitude_degrees_east':-181.,'eastward_m_s':u,'northward_m_s':0.},
  'window_start_utc':composite.stamp(start),'window_end_utc':composite.stamp(start+timedelta(hours=2))}

def synthetic():
 rows=[row(i,lat,u) for i,(lat,u) in enumerate([(45.8,.02),(45.4,.2),(45.,.3),(44.6,.2),(44.2,.02)])]
 gaps=[{'status':'eligible_subject_to_time_cap','unobserved_time_gap_hours':4.,'unobserved_endpoint_distance_km':5.} for _ in range(4)]
 return rows,gaps

class RunCompositeTests(unittest.TestCase):
 def test_whole_run_summary_retains_time_weights_and_footprints(self):
  value=composite.summarize([profile(10,0,1800,.1,45.8),profile(11,1800,3600,.3,45.7)],2)
  self.assertAlmostEqual(value['mean']['eastward_m_s'],.2)
  self.assertAlmostEqual(value['mean']['northward_m_s'],.4)
  self.assertEqual([r['source_time_index'] for r in value['contributors']],[10,11])
  self.assertEqual(value['contributor_latitude_range'],[45.7,45.8])
  self.assertEqual(value['union_coverage_seconds'],3600.)
  self.assertEqual(composite.eligibility(value,[44,46]),'eligible')
  self.assertIs(value['summary_position_is_instantaneous_observation'],False)

 def test_short_nonmonotone_and_outside_footprints_remain_barriers(self):
  rows,gaps=synthetic()
  for key,value,reason in [('union_coverage_seconds',3599,'less_than_one_hour_covered'),
   ('northward_steps',1,'nonmonotone_source_track'),('contributor_latitude_range',[45.3,46.01],'outside_branch_footprint'),
   ('boundary_eligible_coverage',False,'insufficient_time_coverage')]:
   bad=copy.deepcopy(rows);bad[1][key]=value
   result=composite.branch(bad,gaps,'northern',[44,46],6)
   primary=result['scenarios'][1]
   self.assertIsNone(primary['endpoint_separation_km'])
   self.assertEqual(primary['before_peak']['status'],reason)
   self.assertEqual(result['selected_peak']['run_index'],2)

 def test_time_cap_changes_assumption_without_changing_peak(self):
  rows,gaps=synthetic()
  tight=composite.branch(rows,gaps,'northern',[44,46],3)
  loose=composite.branch(rows,gaps,'northern',[44,46],6)
  self.assertEqual(tight['selected_peak'],loose['selected_peak'])
  self.assertIsNone(tight['scenarios'][1]['endpoint_separation_km'])
  self.assertEqual(tight['scenarios'][1]['before_peak']['status'],'unobserved_time_gap_exceeds_cap')
  nominal=loose['scenarios'][1]
  self.assertEqual(nominal['status'],'resolved_under_declared_comparability_assumption')
  self.assertAlmostEqual(nominal['before_peak']['crossing']['latitude_degrees_north'],45.51111111111111)
  self.assertAlmostEqual(nominal['after_peak']['crossing']['latitude_degrees_north'],44.48888888888889)
  self.assertEqual(nominal['full_bracketing_observation_period_utc']['hours'],26.)
  self.assertGreater(nominal['endpoint_separation_km'],110)
  self.assertLess(nominal['endpoint_separation_km'],120)

 def test_peak_ties_choose_earliest_and_do_not_skip_a_bad_link(self):
  rows,gaps=synthetic();rows[1]['mean']['eastward_m_s']=.3
  result=composite.branch(rows,gaps,'northern',[44,46],6)
  self.assertEqual(result['selected_peak']['run_index'],1)
  gaps[0]['status']='unsupported_source_layer'
  result=composite.branch(rows,gaps,'northern',[44,46],12)
  self.assertIsNone(result['scenarios'][1]['endpoint_separation_km'])
  self.assertEqual(result['scenarios'][1]['before_peak']['status'],'unsupported_source_layer')

 def test_original_profile_gaps_and_missing_vectors_cannot_be_bridged(self):
  profiles={i:profile(i,i*300,(i+1)*300,.1,45.8-i*.01) for i in range(4)}
  a=composite.summarize([profiles[0]],0);b=composite.summarize([profiles[3]],1)
  self.assertEqual(composite.gap(a,b,profiles)['status'],'eligible_subject_to_time_cap')
  for kind in ['missing','layer','clock']:
   bad=copy.deepcopy(profiles)
   if kind=='missing':del bad[1]
   elif kind=='layer':bad[1]['layer_mean']['northward_m_s']=None
   else:bad[2]['ensemble_end_utc']=bad[1]['ensemble_end_utc']
   self.assertEqual(composite.gap(a,b,bad)['status'],{
    'missing':'missing_source_profile','layer':'unsupported_source_layer','clock':'source_clock_gap_or_reversal'}[kind])

 def test_real_report_keeps_all_cases_and_nominal_failures(self):
  result=composite.verify();self.assertEqual(result['scenario_counts'],{'total':126,'conditionally_resolved':18,'unresolved_or_ineligible':108})
  for experiment in result['experiments']:
   for case in experiment['cases']:
    nominal=case['scenarios'][1]
    self.assertIsNone(nominal['endpoint_separation_km'])
    if case['branch']=='southern':self.assertTrue(all(s['endpoint_separation_km'] is None for s in case['scenarios']))
  self.assertIsNone(result['whole_current_width_km']);self.assertIsNone(result['annual_width_range_km'])
  for key in ['temporal_comparability_verified','source_values_filled','latitude_sorting_applied',
   'new_width_record_admitted','physical_edge_geometry_admitted','flow_normal_width_estimated','seasonal_playback_supported']:
   self.assertIs(result[key],False)

 def test_source_mutation_rejects_before_calculation(self):
  with patch.object(composite,'digest',return_value='0'*64),self.assertRaisesRegex(ValueError,'Changed conditional run-composite input'):
   composite.build()

 def test_promoted_saved_result_is_rejected(self):
  target=composite.ROOT/composite.OUTPUT;original=Path.read_bytes
  changed=json.loads(original(target));changed['new_width_record_admitted']=True
  def altered(path):return composite.encoded(changed) if path==target else original(path)
  with patch.object(Path,'read_bytes',altered),self.assertRaisesRegex(ValueError,'Stale conditional run-composite report'):
   composite.verify()

 def test_figure_preserves_missing_and_conditional_meaning(self):
  receipt=json.loads((composite.ROOT/'research/aleutian-p14n-1993-run-composite-figure.json').read_bytes())
  self.assertEqual(receipt['source_sha256'],composite.digest(composite.OUTPUT))
  self.assertEqual(receipt['nominal_half_peak_resolved_cases'],0)
  self.assertIs(receipt['physical_edges_rendered'],False)
  self.assertIs(receipt['footprints_are_uncertainty'],False)
  for asset in receipt['figures'].values():
   self.assertEqual(hashlib.sha256((composite.ROOT/asset['file']).read_bytes()).hexdigest(),asset['sha256'])
  svg=ET.fromstring((composite.ROOT/receipt['figures']['.svg']['file']).read_bytes())
  self.assertEqual(svg.attrib['role'],'img')
  self.assertIn('not physical current widths',svg.find('{http://www.w3.org/2000/svg}desc').text)

if __name__=='__main__':unittest.main()
