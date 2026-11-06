import copy
import json
import os
import pathlib
import unittest
from unittest.mock import patch
import test_wicc_winter_reference_query_v1 as fixtures
import wicc_winter_reference_query_v1 as query
import wicc_winter_reference_runtime_v1 as runtime
import wicc_winter_reference_index_v1 as index
import wicc_winter_reference_delivery_v1 as delivery
import check_wicc_winter_reference_delivery_v1 as controller


class Delivery(unittest.TestCase):
    def setUp(self):
        f=fixtures.WiccReferenceContract();f.setUp();self.contract=runtime.build_contract()
        self.parent={'schema':'osw.query-bundle.v1','collections':f.parent,
                     'manifest':{'input_sha256':{runtime.PLANNING:self.contract['input_sha256'][runtime.PLANNING]}}}
        self.child=copy.deepcopy(self.parent)
        runtime.prepare(self.child['collections'],self.child['manifest'],self.contract,parent_logical_sha256=query.PARENT)
        generated={p:json.dumps({'source_count':633}).encode() for p in index.INDEX}
        audit={'added_source_paths':[query.CANDIDATE],'replaced_source_paths':[],
               'original_sources_verified':632,'original_source_strings_preserved':632}
        self.child=index.attach(self.child,generated,audit)

    def test_exact_append_and_unrelated_scientific_rows_protected(self):
        delivery.verify_collections(self.parent,self.child)
        self.child['collections']['widths'][1]['unexpected']=1
        with self.assertRaises(ValueError):delivery.verify_collections(self.parent,self.child)

    def test_range_or_owner_changes_refused(self):
        self.child['collections']['reference_routes'][-1]['annual_length_range_km']=[1500,1600]
        with self.assertRaises(ValueError):delivery.verify_collections(self.parent,self.child)

    def test_local_controller_refuses_before_hashing_payloads(self):
        with patch.dict(os.environ,{},clear=True),patch.object(controller,'sha',side_effect=AssertionError('early read')):
            with self.assertRaises(ValueError):controller.controls()

    def test_dashboard_only_declared_row_changes(self):
        old={'entries':[self.contract['dashboard_before'],{'id':'other','unchanged':42}], 'snapshot_fingerprint':'0'*64}
        before={'ok':True,'bundle_sha256':'old','snapshot_json':json.dumps(old)}
        after={'ok':True,'bundle_sha256':'new','snapshot_json':json.dumps(delivery.projected_dashboard(before['snapshot_json']))}
        delivery.verify_snapshot('dashboard',before,after)
        changed=json.loads(after['snapshot_json']);changed['entries'][1]['unchanged']=43;after['snapshot_json']=json.dumps(changed)
        with self.assertRaises(ValueError):delivery.verify_snapshot('dashboard',before,after)

    def test_workflow_and_reused_harness_flags_and_case_counts_agree(self):
        workflow=(query.ROOT/controller.WORKFLOW).read_text()
        self.assertIn('OSW_WICC_REFERENCE_DELIVERY_V1: "1"',workflow)
        for name in ['parity','snapshots']:
            body=(query.ROOT/f'analysis/check_wicc_winter_reference_{name}_v1.mjs').read_text()
            self.assertIn('OSW_WICC_REFERENCE_DELIVERY_V1',body)
            self.assertNotIn('OSW_EACC_CITED_WIDTH',body)
        self.assertIn("mode==='main'?83:29",(query.ROOT/'analysis/check_wicc_winter_reference_parity_v1.mjs').read_text())


if __name__=='__main__':unittest.main()
