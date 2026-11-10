"""Preserve canonical identities and keep new slope widths on their proposal."""
import copy
import json
import unittest
from check_nordic_section_widths import ROOT, NOR, WSC, records, proposed_records, validate_row, validate_inventory, validate_proposal, visual

class NordicSectionWidthsTests(unittest.TestCase):
    def test_proposed_section_query_has_chart_without_invented_map(self):
        from test_rust_query_browser import native
        result=native({'collection':'proposed_widths','filters':[{'field':'id','op':'eq','value':records(NOR)[0]['id']}]})
        self.assertEqual(result['total'],1)
        self.assertIsNone(result['map_scene'])
        self.assertEqual(result['chart_scene']['kind'],'nordic_section_widths')
        self.assertEqual(result['chart_scene']['panels'][0]['collection'],'proposed_widths')
        self.assertNotIn('current_id',result['rows'][0])
    def test_existing_wsc_records_reused_without_duplicate_or_reinterpretation(self):
        rows=records(WSC)
        self.assertEqual([r['approximate_width_km'] for r in rows],[24,24,21,61,35,10])
        self.assertTrue(all(r['width_range_km'] is None for r in rows))
        self.assertEqual([visual(r)['width_range_km'] for r in rows],[[17,29],None,[11,24],None,[32,37],None])
        for r in rows:validate_row(r)
        document=json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())
        validate_inventory(document)
        self.assertFalse(any(r['current_id'] in {'norwegian','spitsbergen-atlantic'} for r in document['measurements']))

    def test_new_proposed_width_cannot_transfer_names_layers_or_error(self):
        row=records(NOR)[0]
        self.assertNotIn('current_id',row)
        self.assertEqual(row['proposed_current_id'],NOR)
        self.assertEqual(row['width_range_km'],[25,30])
        self.assertIsNone(row['approximate_width_km'])
        cases=[('current_id','norwegian'),('proposed_current_id','norwegian-coastal'),
               ('approximate_width_km',27.5),('width_range_km',[20,30]),('uncertainty_km',4),
               ('fixed_layer_bounds_m',[50,650]),('calendar_months',[7,11,3,6]),
               ('observed_period',{'start':'2016-07-30','end':'2017-06-07'}),
               ('rank_eligible',True),('annual_extrema_eligible',True),
               ('canonical_transfer_eligible',True),('source_feature_name','Norwegian Current')]
        for key,value in cases:
            bad=copy.deepcopy(row);bad[key]=value
            with self.subTest(field=key),self.assertRaises(ValueError):validate_row(bad)

    def test_proposed_collection_and_owner_binding(self):
        self.assertEqual(len(proposed_records()),5)
        self.assertTrue(all('current_id' not in r for r in proposed_records()))
        proposals=json.loads((ROOT/'research/ocean-current-inventory-expansion-candidates.json').read_bytes())
        validate_proposal(proposals)
        for mode in ['missing','duplicate','reassigned']:
            bad=copy.deepcopy(proposals)
            target=next(r for r in bad['entries'] if r['proposed_id']==NOR)
            if mode=='missing':target['section_width_evidence']=[]
            if mode=='duplicate':target['section_width_evidence']*=2
            if mode=='reassigned':target['section_width_evidence'][0]['proposed_current_id']='norwegian'
            with self.subTest(mode=mode),self.assertRaises(ValueError):validate_proposal(bad)
