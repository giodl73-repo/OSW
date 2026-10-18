"""Original parity, vector direction and missing pairs remain separate from widths."""
import copy,csv,io,json,math,tempfile,unittest
from pathlib import Path
from necc_paired_vectors import BASE,ROOT,parse
from build_necc_paired_vector_evidence import build,encoded,INVENTORY,REPORT,monthly

class PairedVectorTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.data=parse(BASE/'vectors.csv',BASE/'longitude.csv')
 def modified_csv(self,change):
  rows=list(csv.reader(io.StringIO((BASE/'vectors.csv').read_text(encoding='utf8'))));change(rows)
  stream=io.StringIO();csv.writer(stream,lineterminator='\n').writerows(rows);return stream.getvalue()
 def parse_modified(self,text):
  with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as temporary:
   path=Path(temporary)/'vectors.csv';path.write_text(text,encoding='utf8');return parse(path,BASE/'longitude.csv')
 def test_originals_and_full_offline_reconstruction(self):
  inventory,report=build();self.assertEqual(inventory['vector_positions'],7992);self.assertEqual(inventory['paired_finite_positions'],7992)
  self.assertEqual(report['target_u_values_and_masks_exact'],2664);self.assertEqual(report['summary']['target_monthly_means_equal_old'],12)
  self.assertTrue(all(r['span_absolute_difference_km']==0 for r in report['target_monthly_reproduction']))
  self.assertEqual(encoded(inventory),(ROOT/INVENTORY).read_bytes());self.assertEqual(encoded(report),(ROOT/REPORT).read_bytes())
  self.assertFalse(report['same_product_columns_are_independent_validation']);self.assertFalse(report['component_spans_are_flow_normal_widths']);self.assertIsNone(report['annual_width_range_km'])
 def test_missing_duplicate_and_wrong_units_rejected(self):
  for change in [lambda r:r.pop(),lambda r:r.append(r[-1]),lambda r:r[1].__setitem__(5,'cm/s')]:
   with self.subTest(change=change):
    with self.assertRaises(ValueError):self.parse_modified(self.modified_csv(change))
 def test_target_u_revision_and_nonutc_time_rejected(self):
  def revise(rows):
   row=next(r for r in rows[2:] if float(r[3])==220);row[4]=str(float(row[4])+.001)
  def local_clock(rows):rows[2][0]=rows[2][0].replace('Z','+01:00')
  for change in [revise,local_clock]:
   with self.subTest(change=change):
    with self.assertRaises(ValueError):self.parse_modified(self.modified_csv(change))
 def test_one_missing_meridional_value_invalidates_both_monthly_means(self):
  def missing(rows):
   row=next(r for r in rows[2:] if float(r[3])==220 and float(r[2])==7);row[5]='NaN'
  data=self.parse_modified(self.modified_csv(missing));self.assertEqual(data['paired_finite_positions'],7991)
  row=next(r for r in monthly(data) if r['month']==1 and r['source_longitude_degrees_east']==220)
  cell=next(r for r in row['profile'] if r['latitude']==7);self.assertIsNone(cell['eastward_m_s']);self.assertIsNone(cell['northward_m_s']);self.assertEqual(cell['missing_pair_count'],1)
  self.assertIsNone(row['zero_crossing_component_span']['span_km']);self.assertEqual(row['zero_crossing_component_span']['boundaries']['north']['status'],'missing_before_crossing')
 def test_direction_is_from_east_and_not_a_width_correction(self):
  d=copy.deepcopy(self.data)
  for key in d['vectors']:
   t,lat,lon=key
   if lon==220 and 2<=lat<=10:d['vectors'][key]=(.2,.2) if lat==7 else (.1,0)
  rows=[r for r in monthly(d) if r['source_longitude_degrees_east']==220]
  self.assertEqual(len(rows),12)
  for row in rows:
   self.assertAlmostEqual(row['selected_peak_vector']['direction_degrees_from_east'],45);self.assertTrue(row['selected_peak_vector']['direction_attention_above_15_degrees']);self.assertIsNone(row['flow_normal_width_km']);self.assertIsNone(row['physical_current_width_km'])

if __name__=='__main__':unittest.main()
