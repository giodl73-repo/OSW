"""Reject scope promotion, source-calendar substitution and coherent row removal."""
import copy,json,unittest
from pathlib import Path
from check_azores_model_core_widths import validate_row,validate_inventory,ROOT

class AzoresInventoryTests(unittest.TestCase):
    def inventory(self):return json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())
    def test_current_rows_bound_to_review(self):
        inv=self.inventory();validate_inventory(inv)
        rows=[r for r in inv['measurements'] if r['id'].startswith('azores-carracedo-2014-')]
        self.assertEqual([r['approximate_width_km'] for r in rows],[240,400])
        self.assertEqual([r['calendar_months'] for r in rows],[[4,5,6],[10,11,12]])
    def test_changed_source_or_promoted_interpretation_rejected(self):
        row=next(r for r in self.inventory()['measurements'] if r['id']=='azores-carracedo-2014-spring-core-width')
        for key,value in [('calendar_months',[3,4,5]),('approximate_width_km',110),('current_id','azores-countercurrent'),('width_range_km',[240,400]),('uncertainty_km',20),('full_width_inference_eligible',True),('seasonal_playback_eligible',True),('source_url','https://example.invalid/other')]:
            with self.subTest(key=key):
                bad=copy.deepcopy(row);bad[key]=value
                with self.assertRaises(ValueError):validate_row(bad)
    def test_removed_or_renamed_rows_cannot_pass_inventory_gate(self):
        inv=self.inventory();inv['measurements']=[r for r in inv['measurements'] if not r['id'].startswith('azores-carracedo-2014-')]
        with self.assertRaisesRegex(ValueError,'Missing'):validate_inventory(inv)
    def test_seasonal_summary_requires_interpretation(self):
        from check_current_width_inventory import validate
        inv=self.inventory()
        summary=next(r for r in inv['seasonal_summaries'] if r['current_id']=='azores')
        del summary['interpretation']
        ledger=json.loads((ROOT/'research/ocean-current-almanac.json').read_bytes())
        with self.assertRaisesRegex(ValueError,'Missing seasonal interpretation'):validate(inv,ledger)

if __name__=='__main__':unittest.main()
