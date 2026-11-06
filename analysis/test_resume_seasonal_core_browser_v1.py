import copy
import unittest
from unittest.mock import patch
import resume_seasonal_core_browser_v1 as m


class BrowserResumeTests(unittest.TestCase):
    def fixture(self):
        paths=['almanac/published-current-speeds.js','almanac/query.html','almanac/reference-routes.html','almanac/seasons.html']
        parent={'schema':'osw.query-engine-manifest.v1','saved_namespace':{'preserve':True},
                'sha256':{'almanac/query-engine.wasm':'6caf567278cb644eed9a45c89028bcadf7d919bb4adba6381503af34fe3e0c16','research/science.json':'c'*64,**{p:'a'*64 for p in paths}}}
        revision={'runtime_source_changes':{p:{'historical_sha256':'a'*64,'candidate_sha256':'b'*64,'archive_path':'archive/'+p} for p in paths}}
        return parent,revision

    def test_local_execution_refused_before_artifact_download(self):
        with patch.dict(m.os.environ,{'GITHUB_ACTIONS':'false'}):
            with self.assertRaisesRegex(ValueError,'Exact cloud'):m.controls()

    def test_only_four_ui_pins_change_and_existing_namespaces_survive(self):
        parent,revision=self.fixture();before=copy.deepcopy(parent)
        result=m.revise_manifest(parent,revision,source_commit='d'*40,verification_inputs={'qa.py':'e'*64})
        self.assertEqual(parent,before)
        self.assertEqual(result['saved_namespace'],parent['saved_namespace'])
        self.assertEqual(result['sha256']['research/science.json'],'c'*64)
        self.assertEqual(result['sha256']['almanac/query-engine.wasm'],parent['sha256']['almanac/query-engine.wasm'])
        self.assertIs(result[m.KEY]['native_or_wasm_rebuild'],False)

    def test_wrong_binary_missing_asset_and_rebound_parent_fail(self):
        for change in [lambda p,r:p['sha256'].update({'almanac/query-engine.wasm':'0'*64}),
                       lambda p,r:r['runtime_source_changes'].pop('almanac/query.html'),
                       lambda p,r:r['runtime_source_changes']['almanac/query.html'].update(historical_sha256='0'*64)]:
            parent,revision=self.fixture();change(parent,revision)
            with self.assertRaises(ValueError):m.revise_manifest(parent,revision,source_commit='d'*40,verification_inputs={})


if __name__=='__main__':unittest.main()
