"""Small refusal/custody fixtures; no packet, browser, engine or build is opened."""
import copy
import hashlib
import json
import unittest
from unittest.mock import patch

import install_south_java_model_v1 as install


class Installer(unittest.TestCase):
    def request(self):
        return {'schema': 'osw.south-java-model-installation-request.v1',
                'execution_permitted': True, 'working_branch_installation_permitted': True,
                'installation_workflow': install.WORKFLOW, 'max_cloud_jobs': 1, 'max_heavy_local_jobs': 0,
                **{k: False for k in ['native_build_permitted', 'wasm_build_permitted',
                     'browser_automation_permitted', 'scientific_source_processing_permitted',
                     'local_bulk_sync_permitted', 'main_merge_permitted']}}

    def visual(self):
        rows = [{'path': f'card-{i}.png', 'sha256': hashlib.sha256(bytes([i])).hexdigest(), 'bytes': 1}
                for i in range(10)]
        result = {'status': 'PASS', 'browser_verified': True, 'run_id': str(install.CASES[2][0]),
                  'run_attempt': '1', 'source_commit': install.CASES[2][3], 'screenshots': rows,
                  'custody': {'logical_sha256': 'a' * 64, 'active_wasm_sha256': 'b' * 64,
                              'compiled_engine_overlay': {'compiled_manifest_sha256': 'c' * 64}}}
        raw = json.dumps(result).encode()
        review = {'status': 'APPROVED_EXACT_WORKING_BRANCH_DATA_INSTALLATION',
                  'run_id': install.CASES[2][0], 'run_attempt': 1, 'job_id': install.CASES[2][2],
                  'source_commit': install.CASES[2][3], 'visual_review_complete': True,
                  'actual_screenshots_inspected': 10, 'scientific_release_approved': False,
                  'main_merge_approved': False, 'generated_artifact_id': 12582509417,
                  'compiled_engine_artifact_id': 12583798914,
                  'functional_result_sha256': hashlib.sha256(raw).hexdigest(), 'screenshots': rows,
                  'logical_sha256': 'a' * 64, 'wasm_sha256': 'b' * 64, 'engine_manifest_sha256': 'c' * 64}
        return review, raw, {f'card-{i}.png': bytes([i]) for i in range(10)}

    def test_disabled_request_and_boolean_cpu_cannot_publish(self):
        install.verify_request(self.request())
        for key, value in [('execution_permitted', False), ('max_cloud_jobs', True),
                           ('local_bulk_sync_permitted', True), ('wasm_build_permitted', True)]:
            request = self.request(); request[key] = value
            with self.assertRaises(ValueError): install.verify_request(request)

    def test_local_execution_refused_before_any_file_read(self):
        with patch.object(install.Path, 'read_bytes', side_effect=AssertionError('File read')):
            with self.assertRaises(RuntimeError): install.controls({})

    def test_run_attempt_and_job_success_are_both_required(self):
        rid, attempt, jid, source = install.CASES[2]
        run = {'id': rid, 'run_attempt': attempt, 'head_sha': source, 'status': 'completed', 'conclusion': 'success'}
        job = {**run, 'id': jid, 'run_id': rid}
        install.verify_case(run, {'jobs': [job]}, install.CASES[2])
        for changed in [{**job, 'run_attempt': 2}, {**job, 'conclusion': 'failure'}]:
            with self.assertRaises(ValueError): install.verify_case(run, {'jobs': [changed]}, install.CASES[2])

    def test_actual_visual_bytes_and_result_are_required(self):
        review, raw, pictures = self.visual()
        self.assertEqual(install.verify_visual(review, raw, pictures)['status'], 'PASS')
        for field in ['visual_review_complete', 'actual_screenshots_inspected']:
            changed = copy.deepcopy(review); changed[field] = False
            with self.assertRaises(ValueError): install.verify_visual(changed, raw, pictures)
        with self.assertRaises(ValueError): install.verify_visual(review, raw + b' ', pictures)
        pictures['card-9.png'] = b'x'
        with self.assertRaises(ValueError): install.verify_visual(review, raw, pictures)

    def test_unrelated_or_missing_publication_changes_refused(self):
        required = {install.REQUEST, install.PROOF, 'almanac/query-data.json',
                    install.build.MANIFEST, 'almanac/query-engine.wasm'}
        install.verify_changed(required, required)
        with self.assertRaises(ValueError): install.verify_changed(required | {'unrelated.txt'}, required)
        with self.assertRaises(ValueError): install.verify_changed(required - {install.PROOF}, required)

    def test_moved_branch_refused_without_mutation(self):
        with patch.object(install.browser, 'api', return_value={'object': {'sha': 'b' * 40}}):
            with self.assertRaisesRegex(ValueError, 'branch moved'): install.remote_guard('a' * 40)

    def test_path_inventory_cannot_escape_saved_outputs(self):
        fixed = ['almanac/query-data.json', install.build.MANIFEST, 'almanac/index-catalog.json',
                 'almanac/index-sources.json', 'almanac/index-data.json.gz', 'research/ocean-motion-dashboard.json']
        paths = fixed + [f'almanac/query-parts/{i:06d}-' + 'a' * 64 + '.bin' for i in range(12)]
        self.assertEqual(len(install.generated_paths({'artifact_paths': paths})), 19)
        paths[-1] = 'almanac/query-parts/../../escaped.bin'
        with self.assertRaises(ValueError): install.generated_paths({'artifact_paths': paths})


if __name__ == '__main__': unittest.main()
