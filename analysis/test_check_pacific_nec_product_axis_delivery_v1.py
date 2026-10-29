import unittest
from unittest.mock import patch
from pathlib import Path
import json
import check_pacific_nec_product_axis_delivery_v1 as delivery
import pacific_nec_product_axis_delivery_contract_v1 as rules

class CandidateDeliveryScope(unittest.TestCase):
    def test_local_candidate_build_refuses_before_any_source_or_payload_read(self):
        with patch.object(delivery.os,'name','nt'),patch.object(delivery.Path,'read_bytes',side_effect=AssertionError('No local data load')):
            with self.assertRaisesRegex(ValueError,'Scoped cloud'):delivery.run()
    def test_pagination_never_changes_the_matching_scene_and_failures_remain_null(self):
        c=json.loads((Path(__file__).resolve().parents[1]/'research/pacific-nec-product-axis-query-contract-v1.json').read_bytes())
        request={'collection':'current_axis_scenarios','filters':[{'field':'length_km','op':'eq','value':None}],'limit':1,'offset':1}
        selected=delivery.selected_rows(request,c);self.assertEqual(len(selected),85)
        scene=rules.query_scene(request['collection'],selected,c);response=delivery.query_response(request,selected,scene)
        self.assertEqual(len(response['rows']),1);self.assertEqual(len(response['chart_scene']['selected_records']),85);self.assertEqual(response['chart_scene']['readings'],[])
        self.assertIsNone(response['rows'][0]['length_km'])
    def test_case_inventory_covers_all_windows_months_and_scenario_families(self):
        c=json.loads((Path(__file__).resolve().parents[1]/'research/pacific-nec-product-axis-query-contract-v1.json').read_bytes())
        cases=delivery.new_requests(c)
        self.assertEqual(len(cases),42)
        for collection in c['collections_added']:
            filtered=[item['request'] for item in cases if item['request']['collection']==collection and item['request']['filters']==[{'field':'rank_eligible','op':'eq','value':True}]]
            self.assertEqual(len(filtered),1);self.assertEqual(delivery.selected_rows(filtered[0],c),[])

if __name__=='__main__':unittest.main()
