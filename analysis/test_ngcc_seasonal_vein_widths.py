"""Original prose widths retain metric, region, overlapping claims and seasons."""
import copy
import hashlib
import json
import unittest
import pymupdf
from check_ngcc_seasonal_vein_widths import ROOT,AUDIT,PIN,validate_row,validate_inventory

class NgccSeasonalVeinTests(unittest.TestCase):
    def setUp(self):
        self.inventory=json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())
        self.rows=[r for r in self.inventory['measurements'] if r['current_id']=='new-guinea-coastal-current']
        self.audit=json.loads((ROOT/AUDIT).read_bytes())

    def test_complete_original_and_width_passage(self):
        self.assertEqual(hashlib.sha256((ROOT/AUDIT).read_bytes()).hexdigest(),PIN)
        from radenac_hal_source import resolve_source, verify_rendition, ORIGINAL_SHA
        raw=resolve_source().read_bytes()
        receipt=json.loads((ROOT/self.audit['acquisition_file']).read_bytes())
        proof=verify_rendition(raw,receipt)
        if hashlib.sha256(raw).hexdigest()==ORIGINAL_SHA:
            self.assertEqual(len(raw),7675633)
            self.assertEqual(proof['kind'],'exact_reviewed_original')
        else:
            self.assertEqual(proof['kind'],'verified_generated_HAL_cover_rendition')
            self.assertEqual(proof['reviewed_original_sha256'],ORIGINAL_SHA)
            self.assertEqual(proof['journal_graph_sha256'],'fe9a7071fe427195d563a0bc2a84752875ddd88b94252ca6b9aaa46e1b72ca34')
        with pymupdf.open(stream=raw,filetype='pdf') as doc:
            self.assertEqual(len(doc),23)
            text=doc[12].get_text()
            for phrase in ['120 km wide east','100–200 km west','near 200 km','100–150 km wide']:
                self.assertIn(phrase,text)
            self.assertIn('150–500 days',doc[10].get_text())
            self.assertIn('2001 and 2010',doc[10].get_text())
        validate_inventory(self.inventory)

    def test_distinct_metrics_and_nonindependent_regional_descriptors(self):
        self.assertEqual(len(self.rows),4)
        self.assertEqual([r['approximate_width_km'] for r in self.rows],[120,None,200,None])
        self.assertEqual([r['width_range_km'] for r in self.rows],[None,[100,200],None,[100,150]])
        self.assertEqual(len({r['width_metric'] for r in self.rows}),2)
        self.assertEqual(len({r['original_regional_context']['source_claim_id'] for r in self.rows}),2)
        for row in self.rows:
            self.assertIsNone(row['section_geometry'])
            self.assertIsNone(row['calendar_months'])
            self.assertFalse(row['seasonal_playback_eligible'])
            self.assertFalse(row['full_width_inference_eligible'])

    def test_scope_and_metric_promotions_rejected(self):
        tests=[(0,'approximate_width_km',80),(0,'approximate_width_km',340),(0,'current_id','new-guinea-coastal-undercurrent'),
               (1,'approximate_width_km',150),(1,'range_kind','annual_width_extrema'),(2,'approximate_width_km',250),
               (2,'original_regional_context',{}),(3,'width_metric',self.rows[0]['width_metric']),
               (0,'calendar_months',[6,7,8]),(0,'fixed_layer_bounds_m',[0,100]),(0,'uncertainty_km',10),
               (0,'seasonal_playback_eligible',True),(0,'whole_current_representative',True)]
        for i,key,value in tests:
            row=copy.deepcopy(self.rows[i]);row[key]=value
            with self.subTest(i=i,key=key),self.assertRaises(ValueError):validate_row(row)

    def test_erased_records_and_rebound_audit_rejected(self):
        bad=copy.deepcopy(self.inventory);bad['measurements'].remove(next(r for r in bad['measurements'] if r['id']==self.rows[0]['id']))
        with self.assertRaises(ValueError):validate_inventory(bad)
        audit=copy.deepcopy(self.audit);audit['measurements'][1]['approximate_width_km']=150
        with self.assertRaises(ValueError):validate_row(self.rows[1],audit)

if __name__=='__main__':
    unittest.main()
