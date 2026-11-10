"""Small saved-proof/custody checks; no packet, binary, index or browser load."""
import copy
import json
import os
from pathlib import Path
import tempfile
import textwrap
import unittest
from unittest.mock import patch

import eicc_saved_installation_v1 as rules
import install_eicc_reference_v1 as controller


class EiccSavedInstallation(unittest.TestCase):
    def fixture(self):
        root = controller.ROOT
        read = lambda name: json.loads((root / (rules.PROOF_DIR + name + '.json')).read_bytes())
        return dict(review=json.loads((root / controller.REVIEW).read_bytes()), result=read('result'),
                    engine=read('engine'), browser=read('browser'), custody=read('browser-phase-custody'),
                    parities={mode: read(mode + '-parity') for mode in ['main', 'index', 'snapshots']},
                    preservation=read('snapshot-preservation'))

    def test_complete_actual_saved_evidence_and_visual_review_are_consistent(self):
        args = self.fixture()
        self.assertEqual(len(rules.verify_proofs(**args)), 19)
        self.assertEqual(controller.proofs()[0], args['review'])

    def test_local_refusal_precedes_any_installation_source_or_artifact_read(self):
        with patch.object(controller, 'read', side_effect=AssertionError('Unexpected source read')):
            with self.assertRaises(RuntimeError): controller.controls({})

    def test_missing_query_snapshot_or_corpus_refusal_proof_is_rejected(self):
        for kind in ['main', 'index', 'snapshots', 'refusal', 'preservation']:
            with self.subTest(kind=kind):
                args = self.fixture()
                if kind in ['main', 'index', 'snapshots']:
                    args['parities'][kind]['checks'].pop()
                elif kind == 'refusal':
                    args['parities']['index']['mismatched_corpus_refused'] = False
                else:
                    args['preservation']['atlas']['complete_catalog_matches_source_projection'] = False
                with self.assertRaises(ValueError): rules.verify_proofs(**args)

    def test_changed_artifact_identity_unreviewed_images_or_physical_claims_are_rejected(self):
        for kind in ['source', 'binary', 'screenshot', 'visual', 'rank', 'state']:
            with self.subTest(kind=kind):
                args = self.fixture()
                if kind == 'source': args['result']['source_commit'] = '0' * 40
                elif kind == 'binary': args['engine']['wasm_sha256'] = '0' * 64
                elif kind == 'screenshot': args['review']['screenshots'].pop()
                elif kind == 'visual': args['review']['visual_review_complete'] = False
                elif kind == 'rank': args['result']['new_ranked_lengths'] = 1
                else: args['result']['new_state_intersections'] = 1
                with self.assertRaises(ValueError): rules.verify_proofs(**args)

    def test_archive_inventory_rejects_extra_duplicate_or_readdressed_packet_parts(self):
        result = self.fixture()['result']
        for kind in ['extra', 'duplicate', 'address', 'index']:
            changed = copy.deepcopy(result)
            part = next(p for p in changed['artifact_paths'] if '/query-parts/' in p)
            if kind == 'extra': changed['artifact_paths'].append('../unrelated.json')
            elif kind == 'duplicate': changed['artifact_paths'][-1] = changed['artifact_paths'][0]
            elif kind == 'address': changed['generated_sha256'][part] = '0' * 64
            else:
                replacement = part.replace('/000000-', '/999999-') if '/000000-' in part else part.replace(part.split('/')[-1][:6], '999999')
                changed['artifact_paths'][changed['artifact_paths'].index(part)] = replacement
                changed['generated_sha256'][replacement] = changed['generated_sha256'].pop(part)
            with self.assertRaises(ValueError): rules.generated_paths(changed)

    def test_installation_request_keeps_all_rebuild_browser_and_release_permissions_off(self):
        request = json.loads((controller.ROOT / controller.REQUEST).read_bytes())
        request.update(execution_permitted=True, working_branch_installation_permitted=True)
        rules.verify_request(request)
        for key, value in [('max_cloud_jobs', True), ('max_heavy_local_jobs', 1),
                           ('native_build_permitted', True), ('browser_automation_permitted', True),
                           ('local_bulk_sync_permitted', True), ('main_merge_permitted', True)]:
            with self.assertRaises(ValueError): rules.verify_request({**request, key: value})

    def test_actual_workflow_request_reader_matches_its_request_and_trigger(self):
        workflow = (controller.ROOT / controller.WORKFLOW).read_text()
        self.assertIn(controller.REQUEST, workflow.split('concurrency:', 1)[0])
        script = workflow.split("python - <<'PY'\n", 1)[1].split('\n          PY', 1)[0]
        request = json.loads((controller.ROOT / controller.REQUEST).read_bytes())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'github-output'
            with patch.dict(os.environ, {'GITHUB_OUTPUT': str(path)}):
                exec(compile(textwrap.dedent(script), controller.WORKFLOW, 'exec'), {})
            self.assertEqual(path.read_text(), 'enabled=' + str(request['execution_permitted']).lower() + '\n')


if __name__ == '__main__':
    unittest.main()
