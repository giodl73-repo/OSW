"""Small publication fixtures: real source pins, tiny generated transport."""
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import prepare_davidson_width_delivery as delivery
from query_packet import write_packet

ROOT = Path(__file__).resolve().parents[1]


def fixture(root):
    contract = json.loads((ROOT / delivery.admission.FILE).read_bytes())
    required = delivery.REQUIRED_INPUTS | set(contract['input_sha256'])
    for path in required:
        target = root / path; target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((ROOT / path).read_bytes())
    for path in delivery.GENERATED - {delivery.INSTALLED_PROOF,'almanac/query-data.json',
                                      'almanac/query-engine.manifest.json'}:
        target = root / path; target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(b'fixture')
    (root / delivery.metadata.DASHBOARD).write_bytes(delivery.metadata.encoded({'counts':{
        'named_current':106,'named_eddy':136,'operational_eddy_detection':4}}))
    packet = write_packet(root / 'almanac/query-data.json',
                          b'{"schema":"osw.query-bundle.v1","collections":{}}\n')
    generated = delivery.GENERATED - {delivery.INSTALLED_PROOF,'almanac/query-engine.manifest.json'}
    pins = {path:delivery.digest(root / path) for path in required | generated}
    pins.update({'almanac/' + row['path']:row['sha256'] for row in packet['parts']})
    (root / 'almanac/query-engine.manifest.json').write_text(json.dumps({
        'schema':'osw.query-engine-manifest.v1','engine':'rust-osw-query-v1','abi_version':1,'sha256':pins}),encoding='utf-8')
    sha = packet['logical_sha256']
    source = {'schema':'osw.davidson-width-candidate.v1','status':'PASS','published':False,
              'parent_logical_sha256':delivery.metadata.PARENT_SHA,
              'candidate':{'rows':108530,'objects':246,'named_currents':106,'widths':172,
                           'logical_sha256':sha,'logical_bytes':packet['logical_byte_length']},
              'admission':{'added_rows':{'sources':3,'widths':1,'claims':1,'current_measurement_admissions':1},
                           'raw_samples_added':0,'annual_ranges_added':0,'geometry_or_state_joins_added':0,
                           'complete_parent_packet_verified':True,
                           'preservation':{'all_prior_nonobject_rows_exact':True,
                                           'physical_fields_and_capabilities_preserved_except_scoped_width_count':True,
                                           'unchanged_objects_verified':245,'prior_rows_verified':108278}},
              'index_extension':{'original_sources_verified':572,'original_source_strings_preserved':571,
                                 'replaced_source_paths':[delivery.metadata.DASHBOARD],
                                 'scientific_source_documents_replaced':0},
              'source_originals_redistributed':False,'scientific_release_published':False}
    browser = {'status':'PASS','bundle_sha256':sha,'native_wasm_card_equal':True,
               'historical_width_preserved':True,'source_caption_browser_visible':True,
               'keyboard_width_query':True,'source_link_focusable':True,
               'phone_horizontal_overflow':False,'errors':[],'original_downloads':[],
               'source_scalar_sha256':delivery.admission.FROZEN_OUTPUTS[delivery.admission.FIGURE]}
    prior = {'status':'PASS','named_currents':106,'bundle_sha256':sha,
             'native_wasm_object_views_equal':['west-india-coastal','east-india-coastal','east-african-coastal','south-java','brazil'],
             'keyboard_evidence_query':True,'dashboard_all_106_currents':True,'dashboard_alias_native_wasm_parity':True,
             'phone_horizontal_overflow':False,'errors':[],'original_downloads':[],
             'source_scoped_widths':3,'qualitative_calendar_months':24,'scoped_t24_width_records':1,
             'raw_width_samples_added':0,'annual_width_ranges_added':0,'source_context_coverage_modes_verified':4}
    run = {'id':123,'head_sha':'a'*40,'head_branch':delivery.BRANCH,'event':'push',
           'path':delivery.WORKFLOW,'html_url':'https://example.invalid/run/123'}
    jobs = {'total_count':2,'jobs':[{'name':delivery.REQUIRED_JOB,'status':'completed','conclusion':'success'},
                                  {'name':'publish-davidson-working-data','status':'in_progress','conclusion':None}]}
    return [root,source,browser,prior,run,jobs,'a'*40]


class DeliveryChecks(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.args = fixture(Path(self.temporary.name))

    def test_bound_delivery_preserves_full_gate_limitations_without_writing(self):
        before = copy.deepcopy(self.args[1:])
        result = delivery.verify(*self.args)
        self.assertEqual(before,self.args[1:])
        self.assertFalse(result['scientific_release_published'])
        self.assertFalse(result['main_merged'])
        self.assertIn('HTTP 403',result['full_offline_regression'])
        self.assertEqual(result['cohort_version'],delivery.metadata.VERSION)
        self.assertFalse((self.args[0] / delivery.INSTALLED_PROOF).exists())

    def test_wrong_gate_scope_revision_or_actual_browser_receipts_rejected(self):
        mutations = [
            lambda a:a[1]['admission'].update(raw_samples_added=1),
            lambda a:a[1]['admission']['preservation'].update(unchanged_objects_verified=244),
            lambda a:a[1]['index_extension'].update(scientific_source_documents_replaced=1),
            lambda a:a[1]['candidate'].update(widths=171),
            lambda a:a[2].update(source_caption_browser_visible=False),
            lambda a:a[2].update(bundle_sha256='b'*64),
            lambda a:a[3].update(annual_width_ranges_added=1),
            lambda a:a[4].update(path='.github/workflows/validate.yml'),
            lambda a:a[4].update(head_sha='b'*40),
            lambda a:a[5]['jobs'][0].update(conclusion='failure'),
            lambda a:a[5].update(total_count=3),
        ]
        for index, mutate in enumerate(mutations):
            changed = [self.args[0],*copy.deepcopy(self.args[1:])]; mutate(changed)
            with self.subTest(index=index), self.assertRaises(ValueError):delivery.verify(*changed)

    def test_changed_engine_asset_source_pin_and_omitted_input_rejected(self):
        root = self.args[0]
        wasm = root / 'almanac/query-engine.wasm'; old = wasm.read_bytes()
        wasm.write_bytes(b'changed')
        with self.assertRaises(ValueError):delivery.verify(*self.args)
        wasm.write_bytes(old)
        path = root / 'almanac/query-engine.manifest.json'
        original = path.read_bytes(); manifest = json.loads(original)
        manifest['sha256'].pop(delivery.admission.PROOF)
        path.write_text(json.dumps(manifest),encoding='utf-8')
        with self.assertRaises(ValueError):delivery.verify(*self.args)
        manifest = json.loads(original)
        dependency = next(iter(json.loads((ROOT / delivery.admission.FILE).read_bytes())['input_sha256']))
        manifest['sha256'][dependency] = '0'*64
        path.write_text(json.dumps(manifest),encoding='utf-8')
        with self.assertRaises(ValueError):delivery.verify(*self.args)

    def test_output_scope_rejects_historical_parts_sources_and_prior_receipt(self):
        packet = json.loads((self.args[0] / 'almanac/query-data.json').read_bytes())
        delivery.verify_changed_paths({delivery.INSTALLED_PROOF,'almanac/' + packet['parts'][0]['path']},packet)
        for path in ['research/current-gap-installed-delivery-v1.json','rust/osw-query/src/lib.rs',
                     delivery.admission.REPORT,'almanac/query-parts/000000-'+'0'*64+'.bin']:
            with self.subTest(path=path), self.assertRaises(ValueError):
                delivery.verify_changed_paths({path},packet)

    def test_local_publication_refused_before_git_or_file_work(self):
        with patch.dict(os.environ,{},clear=True), \
                patch('sys.argv',['delivery','--publish','--audit-dir','missing']), \
                patch.object(delivery.subprocess,'check_output') as git, \
                contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):delivery.main()
        git.assert_not_called()


if __name__ == '__main__':unittest.main()
