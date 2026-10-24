"""Published filtering and graphical sampling cannot become raw monthly data."""
from pathlib import Path
from unittest.mock import patch
import copy,hashlib,json,math,unittest,xml.etree.ElementTree as ET
import build_kuroshio_filtered_width_series as filtered

def segment(index,a,b):
 return {'segment_index':index,'source_path_index':0,'path_segment_index':index,'start_pdf_points':a,'end_pdf_points':b}

class FilteredWidthTests(unittest.TestCase):
 def test_independent_axis_interpolation_rounding_and_reading_allowance(self):
  config={'axis_y_points':[0,10],'axis_width_km':[100,0],'coordinate_tolerance_points':.0001,'rounding_km':5,'reading_allowance_km':5}
  result=filtered.reading([segment(0,[0,2],[10,8])],5,config)
  self.assertEqual(result['raw_plot_width_km'],50.)
  self.assertEqual(result['approximate_width_km'],50)
  self.assertEqual(result['plot_reading_interval_km'],[45,55])
  self.assertEqual(result['brackets'][0]['fraction_from_segment_start'],.5)

 def test_graph_break_is_retained_without_added_segment_or_gap_value(self):
  config={'axis_y_points':[0,10],'axis_width_km':[100,0],'coordinate_tolerance_points':.0001,'rounding_km':5,'reading_allowance_km':5}
  segments=[segment(0,[0,2],[2,3]),segment(1,[3,4],[5,5])]
  gaps=filtered.validate_trace(segments,.0001)
  self.assertEqual(len(gaps),1);self.assertIs(gaps[0]['link_added'],False)
  missing=filtered.reading(segments,2.5,config)
  self.assertEqual(missing['status'],'unresolved_no_source_segment')
  self.assertIsNone(missing['approximate_width_km'])
  self.assertEqual(len(segments),2)

 def test_shared_vertex_is_one_reading_but_different_crossings_are_unknown(self):
  config={'axis_y_points':[0,10],'axis_width_km':[100,0],'coordinate_tolerance_points':.0001,'rounding_km':5,'reading_allowance_km':5}
  shared=[segment(0,[0,2],[5,5]),segment(1,[5,5],[10,8])]
  value=filtered.reading(shared,5,config)
  self.assertEqual(value['approximate_width_km'],50);self.assertEqual(len(value['brackets']),2)
  ambiguous=filtered.reading([segment(0,[0,2],[10,4]),segment(1,[0,5],[10,7])],5,config)
  self.assertEqual(ambiguous['status'],'unresolved_distinct_source_crossings')
  self.assertIsNone(ambiguous['approximate_width_km'])

 def test_reversed_overlapping_and_nonfinite_source_paths_reject(self):
  for segments in [[segment(0,[1,2],[0,3])],[segment(0,[0,2],[3,3]),segment(1,[2,4],[5,5])],
   [segment(0,[0,2],[math.nan,4])]]:
   with self.assertRaises(ValueError):filtered.validate_trace(segments,.0001)

 def test_source_style_and_calibration_cannot_silently_switch_panels(self):
  config=json.loads((filtered.ROOT/filtered.CONFIG).read_bytes())
  for key,value in [('curve_path_indices',[0,475,476]),('axis_year_x_points',[0]*17),('curve_stroke_width_points',.5)]:
   changed=copy.deepcopy(config);changed[key]=value
   with self.subTest(key=key),self.assertRaises(ValueError):filtered.read_curve(changed)

 def test_complete_curve_readings_keep_filter_dates_and_unknowns(self):
  result=filtered.verify();self.assertEqual(result['sample_count'],192);self.assertEqual(result['resolved_sample_count'],192)
  self.assertEqual(result['source_curve_segment_count'],755)
  self.assertEqual(len(result['source_curve_breaks']),1)
  self.assertIs(result['source_curve_breaks_bridged'],False)
  self.assertEqual([(s['plot_year_label'],s['plot_month_label']) for s in result['samples']],[(y,m) for y in range(1993,2009) for m in range(1,13)])
  self.assertTrue(all(s['sample_time_is_observation_date'] is False for s in result['samples']))
  self.assertTrue(all(s['plot_reading_interval_km']==[s['approximate_width_km']-5,s['approximate_width_km']+5] for s in result['samples']))
  self.assertEqual(result['source_temporal_filter']['source_label'],'1/2 year filtered mean')
  for field in ['kernel','window_alignment','endpoint_treatment']:self.assertIsNone(result['source_temporal_filter'][field])
  for field in ['samples_are_raw_monthly_means','monthly_sampling_is_new_source_resolution',
   'new_inventory_width_record_admitted','whole_current_representative','is_confidence_interval','annual_extrema_eligible','seasonal_playback_eligible','geographic_playback_eligible']:
   self.assertIs(result[field],False)
  for field in ['observed_period','independent_sample_count','measurement_uncertainty_km','geographic_boundary_coordinates','annual_width_range_km','whole_current_width_km']:
   self.assertIsNone(result[field])

 def test_independent_visual_grid_checks_on_original_published_curve(self):
  config=json.loads((filtered.ROOT/filtered.CONFIG).read_bytes());segments,_=filtered.read_curve(config)
  # Broad manual readings against the original 10km grid, before individual sample inspection.
  for year,bounds in [(1993,[205,215]),(1994,[185,200]),(2008,[210,225])]:
   i=year-1993;x=(config['axis_year_x_points'][i]+config['axis_year_x_points'][i+1])/2
   value=filtered.reading(segments,x,config)['raw_plot_width_km']
   self.assertGreaterEqual(value,bounds[0]);self.assertLessEqual(value,bounds[1])

 def test_source_rebinding_and_promoted_saved_report_reject(self):
  with patch.object(filtered,'digest',return_value='0'*64),self.assertRaisesRegex(ValueError,'Changed Kuroshio filtered-curve input'):
   filtered.build()
  target=filtered.ROOT/filtered.OUTPUT;original=Path.read_bytes;bad=json.loads(original(target));bad['samples_are_raw_monthly_means']=True
  def altered(path):return filtered.encoded(bad) if path==target else original(path)
  with patch.object(Path,'read_bytes',altered),self.assertRaisesRegex(ValueError,'Stale Kuroshio filtered-width readings'):
   filtered.verify()

 def test_query_projection_preserves_graphical_time_and_avoids_bulk_context_duplication(self):
  from build_query_width_samples import build
  from kuroshio_filtered_width import record
  document=filtered.verify();rows=build([record(document)])
  self.assertEqual(len(rows),192)
  self.assertTrue(all(r['observation_date'] is None and r['month'] is None and r['year'] is None for r in rows))
  self.assertTrue(all(r['sample_time_is_observation_date'] is False and r['samples_are_raw_monthly_means'] is False for r in rows))
  self.assertNotIn('samples',rows[0]['source_context'])
  self.assertEqual(rows[0]['plot_month_label'],1);self.assertEqual(rows[-1]['plot_year_label'],2008)
  self.assertEqual(rows[0]['source_temporal_filter'],document['source_temporal_filter'])

 def test_figure_and_registration_keep_filtering_and_unknown_uncertainty(self):
  from kuroshio_filtered_width import verify_inputs
  document,figure,inputs=verify_inputs()
  self.assertEqual(figure['sample_count'],192);self.assertFalse(figure['samples_are_raw_monthly_means'])
  self.assertFalse(figure['source_uncertainty_inferred']);self.assertFalse(figure['annual_extrema_inferred'])
  self.assertEqual(document['source_method_context']['original_grid_degrees'],1/3)
  self.assertFalse(document['source_method_context']['grid_interpolation_is_new_observation_resolution'])
  for path,pin in inputs.items():self.assertEqual(hashlib.sha256((filtered.ROOT/path).read_bytes()).hexdigest(),pin)
  svg=ET.fromstring((filtered.ROOT/figure['figures']['.svg']['file']).read_bytes())
  self.assertEqual(svg.attrib['role'],'img')
  self.assertIn('not raw monthly means',svg.find('{http://www.w3.org/2000/svg}desc').text)

if __name__=='__main__':unittest.main()
