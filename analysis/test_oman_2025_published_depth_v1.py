import copy,csv,io,json,unittest
from pathlib import Path
from verify_oman_2025_published_depth_v1 import verify,csv_bytes
ROOT=Path(__file__).resolve().parents[1]
SOURCE='''<html>Hydrographic transformation of the Persian/Arabian Gulf outflow
51 Conductivity profiles 9 and 18 July 2025 composite-tracer approach
threshold of ≥0.3 core is defined by fraction ≥0.55
current measurements are unavailable
top of the outflow occurs at depths of 50–100 m
thickness of 10–30 m
upper depth of the P/AG outflow increases up to 170 m
reaching ∼130–140 m thickness increases up to 200 m</html>'''.encode()
class Tests(unittest.TestCase):
    def setUp(self):self.facts=json.loads((ROOT/'research/oman-2025-published-depth-facts-v1.json').read_bytes())
    def test_spatial_metrics_and_nulls(self):
        rows,_=verify(SOURCE,self.facts)
        self.assertEqual([r['metric'] for r in rows[:3]],['reported_water_mass_plume_upper_boundary_depth']*3)
        self.assertTrue(all(r['lower_boundary_depth_m'] is None and r['volume_m3'] is None and r['annual_depth_range'] is None for r in rows))
        self.assertIsNone(rows[1]['minimum_m'])
    def test_source_change_rejected(self):
        with self.assertRaises(ValueError):verify(SOURCE.replace(b'170',b'180'),self.facts)
    def test_review_change_rejected(self):
        self.facts['rows'][0]['maximum_m']=110
        with self.assertRaises(ValueError):verify(SOURCE,self.facts)
    def test_promotion_selection_and_dates_rejected(self):
        for field,value in [('eligibility',dict(self.facts['eligibility'],volume=True)),('survey_window',['2025-01-01','2025-12-31']),('plume_definition',dict(self.facts['plume_definition'],minimum_fraction=0.55))]:
            facts=copy.deepcopy(self.facts);facts[field]=value
            with self.assertRaises(ValueError):verify(SOURCE,facts)
    def test_csv_null_and_html_hidden_content(self):
        rows,_=verify(SOURCE,self.facts);back=list(csv.DictReader(io.StringIO(csv_bytes(rows).decode())))
        self.assertEqual(back[1]['minimum_m'],'');self.assertEqual(back[1]['maximum_m'],'170')
        with self.assertRaises(ValueError):verify(b'<html><script>'+SOURCE+b'</script></html>',self.facts)
if __name__=='__main__':unittest.main()
