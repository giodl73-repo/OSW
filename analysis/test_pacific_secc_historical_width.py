"""Historical SECC range cannot acquire midpoint, seasonal edges or another owner."""
import copy
import hashlib
import json
import unittest
from pathlib import Path
import pymupdf
from check_pacific_secc_historical_width import ROOT, AUDIT, PIN, validate_row
from check_current_width_inventory import validate as validate_inventory


class PacificSeccHistoricalTests(unittest.TestCase):
    def setUp(self):
        self.inventory=json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())
        self.row=next(r for r in self.inventory['measurements'] if r['id']=='pacific-secc-rotschi-1972-170e-width-range')
        self.audit=json.loads((ROOT/AUDIT).read_bytes())

    def test_unchanged_original_and_visual_passage(self):
        self.assertEqual(hashlib.sha256((ROOT/AUDIT).read_bytes()).hexdigest(),PIN)
        raw=(ROOT/self.audit['source_document_file']).read_bytes()
        self.assertEqual(len(raw),4021588)
        self.assertEqual(hashlib.sha256(raw).hexdigest(),'f2d8d1c8ba9655146319829b942278a13ac792b4a634e6d547a2cd17bc6b24fe')
        with pymupdf.open(stream=raw,filetype='pdf') as pdf:
            self.assertEqual(len(pdf),120)
            text=pdf[12].get_text()
            self.assertIn('300 km to 900 km',text)
            self.assertIn('South Equatorial Countercurrent',text)
        validate_row(self.row)

    def test_current_and_neighbouring_flow_stay_distinct(self):
        self.assertEqual(self.row['width_range_km'],[300,900])
        self.assertIsNone(self.row['approximate_width_km'])
        self.assertIsNone(self.row['observed_period'])
        self.assertIsNone(self.row['fixed_layer_bounds_m'])
        decision=next(r for r in self.inventory['current_decisions'] if r['current_id']=='pacific-south-equatorial-countercurrent')
        self.assertEqual(decision['measurement_ids'],[self.row['id']])
        family=next(r for r in self.inventory['current_decisions'] if r['current_id']=='south-equatorial-countercurrent')
        self.assertEqual(family['measurement_ids'],[])

    def test_all_scope_promotions_rejected(self):
        mutations=[('approximate_width_km',600),('width_range_km',[300,1000]),('range_kind','annual_width_extrema'),
                   ('current_id','south-equatorial-countercurrent'),('current_id','pacific-south-subsurface-countercurrent'),
                   ('fixed_layer_bounds_m',[0,300]),('calendar_months',[3,4,5]),('observed_period',{'start':'1965-11-26','end':'1968-05-10'}),
                   ('width_rank_eligible',True),('whole_current_representative',True),('seasonal_playback_eligible',True),('original_regional_context',{})]
        for key,value in mutations:
            bad=copy.deepcopy(self.row);bad[key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):validate_row(bad)

    def test_consistently_changed_audit_rejected(self):
        bad=copy.deepcopy(self.audit);bad['measurement']['approximate_width_km']=600
        with self.assertRaises(ValueError):validate_row(self.row,bad)

    def test_inventory_classification_is_complete(self):
        validate_inventory(self.inventory,json.loads((ROOT/'research/ocean-current-almanac.json').read_bytes()))


if __name__=='__main__':
    unittest.main()
