"""Synthetic installation-gate tests; no packet, index, WASM or browser reads."""
import copy
import json
import pathlib
import sys
import unittest
from unittest.mock import patch

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'analysis'))
import install_current_utf8_validation_saved_v1 as installer


class InstallationGates(unittest.TestCase):
    def fixture(self):
        # Only compact, retained native proof is real. Browser and visual data
        # are explicitly synthetic test inputs, never written to research/.
        load=lambda p:json.loads((ROOT/p).read_bytes())
        engine=load(installer.ENGINE+'result.json')
        docs={installer.ENGINE+'result.json':engine}
        for mode in ['main','index']:
            docs[installer.ENGINE+'compare-'+mode+'.json']=load(installer.ENGINE+'compare-'+mode+'.json')
        artifact={'id':123,'bytes':456,'sha256':'f'*64}
        frozen={'wasm_sha256':engine['wasm_sha256'],
            'original_engine_manifest_sha256':installer.presentation.PARENT,
            'engine_manifest_sha256':installer.file_sha(ROOT/installer.presentation.FILE),
            'engine':{'artifact':{'id':13006867096,'bytes':99217055,'sha256':'7ca167a241b1ae2185372c700174708f1a349fd97269092e5d7a9d785941875d'}},
            'browser':{'source_commit':'synthetic-browser-source','run_id':999,'artifact':artifact}}
        observed={'status':'PASS_BROWSER_OBSERVATION_VISUAL_REVIEW_PENDING','checks':
            [{'case':f'synthetic positive fixture {i}','width':w} for w in [1100,320] for i in range(9)]+
            [{'case':f'synthetic negative fixture {i}','width':320,'expected_error':e} for i,e in enumerate(['Invalid bundle JSON','Invalid bundle JSON','Unsupported bundle schema'])],
            'screenshots':[{'path':f'synthetic-{i}.png','bytes':1,'sha256':'0'*64} for i in range(30)],
            'viewports':[1100,320],'one_page_and_renderer':True,'page_errors':[],
            'missing_assets':[],'original_science_downloads':[],
            'legibility':[{'kind':kind,'minimum_text_px':11.1} for kind in ['atlas-preview']*4+['full-route-card']*2],
            'atlas_load_observations':[{'cold_browser_context':i==0,'status':{'phase':'ready','settled':True,
                'completed_phases':[{'phase':p,'elapsed_ms':1} for p in ['load','atlas']]}} for i in range(2)]}
        result={'source_commit':'synthetic-browser-source','run_id':'999','run_attempt':'1','status':observed['status'],
            'saved_engine_source':engine['source_commit'],'saved_engine_run':41114274466,
            'saved_artifact':frozen['engine']['artifact'],'logical_sha256':installer.LOGICAL,
            'wasm_sha256':engine['wasm_sha256'],'engine_manifest_sha256':frozen['engine_manifest_sha256'],
            'original_engine_manifest_sha256':installer.presentation.PARENT,'client_transport_updates':sorted(installer.presentation.PATHS),
            'native_or_wasm_rebuild':False,'installed':False,'screenshots':30,'browser_checks':21}
        review={'status':'PASS_ALL_30_ACTUAL_IMAGES_INDIVIDUALLY_INSPECTED','source_commit':result['source_commit'],
            'run_id':999,'artifact':artifact,'screenshots':copy.deepcopy(observed['screenshots']),
            'image_reviews':[{**r,'actually_viewed':True,'observation':'Synthetic fixture only; no real image review claimed.'} for r in observed['screenshots']],
            'actual_images_individually_inspected':30,'blocking_issues':[],'installed':False}
        docs.update({installer.BROWSER+'result.json':result,installer.BROWSER+'browser.json':observed,installer.VISUAL:review})
        return frozen,docs

    def check(self,frozen,docs):
        with patch.object(installer,'read',side_effect=lambda p:copy.deepcopy(docs[p])):
            return installer.evidence(frozen)

    def test_complete_synthetic_review_matches_real_compact_native_custody(self):
        frozen,docs=self.fixture()
        files,raw=self.check(frozen,docs)
        self.assertEqual(len(files),18)
        self.assertEqual(installer.sha(raw),frozen['engine_manifest_sha256'])

    def test_visual_review_missing_images_changed_custody_or_blocking_issue_refused(self):
        frozen,docs=self.fixture()
        for key,value in [('actual_images_individually_inspected',27),('screenshots',[]),
            ('image_reviews',[]),('blocking_issues',['unreadable width field']),('source_commit','another-source')]:
            changed=copy.deepcopy(docs);changed[installer.VISUAL][key]=value
            with self.assertRaises(ValueError):self.check(frozen,changed)

    def test_partial_browser_checks_runtime_errors_or_extended_budget_refused(self):
        frozen,docs=self.fixture()
        for key,value in [('checks',[]),('page_errors',['error']),('missing_assets',['asset']),
            ('legibility',[{'kind':'atlas-preview','minimum_text_px':6}])]:
            changed=copy.deepcopy(docs);changed[installer.BROWSER+'browser.json'][key]=value
            with self.assertRaises(ValueError):self.check(frozen,changed)
        changed=copy.deepcopy(docs)
        changed[installer.BROWSER+'browser.json']['atlas_load_observations'][0]['status']['completed_phases'][0]['elapsed_ms']=90001
        with self.assertRaises(ValueError):self.check(frozen,changed)

    def test_changed_scientific_rows_binary_or_incomplete_parity_refused(self):
        frozen,docs=self.fixture()
        changed=copy.deepcopy(docs)
        changed[installer.ENGINE+'result.json']['packet_comparison']['existing_measurement_rows_changed']=1
        with self.assertRaises(ValueError):self.check(frozen,changed)
        changed=copy.deepcopy(frozen);changed['wasm_sha256']='a'*64
        with self.assertRaises(ValueError):self.check(changed,docs)
        changed=copy.deepcopy(docs);changed[installer.ENGINE+'compare-index.json']['checks'].pop()
        with self.assertRaises(ValueError):self.check(frozen,changed)

    def test_local_installation_refuses_before_any_payload_or_network_access(self):
        with (patch.object(installer.os,'name','nt'),
              patch.object(installer,'read',side_effect=AssertionError('No payload reads')),
              patch.object(installer,'api',side_effect=AssertionError('No network'))):
            with self.assertRaisesRegex(ValueError,'Scoped cloud installation only'):installer.controls()


if __name__=='__main__':
    unittest.main()
