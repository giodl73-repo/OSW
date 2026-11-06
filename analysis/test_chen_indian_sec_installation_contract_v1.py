import copy
import json
from pathlib import Path
import unittest
import chen_indian_sec_installation_contract_v1 as contract

ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_bytes())


class InstallationEvidence(unittest.TestCase):
    def fixture(self):
        e='research/chen-indian-sec-delivery-run-v4/';b='research/chen-indian-sec-browser-run-v5/'
        return [read(e+'result.json'),{k:read(e+'compare-'+k+'.json') for k in ('main','index')},
                read(b+'result.json'),read(b+'browser.json'),read('research/chen-indian-sec-browser-visual-review-v5.json'),
                read(e+'engine-manifest.json'),read(b+'engine-manifest-presentation.json'),
                read('research/chen-indian-sec-responsive-source-scope-v2.json'),(ROOT/b/'engine-manifest-presentation.json').stat().st_size]

    def test_actual_complete_evidence_is_accepted(self):
        files=contract.verify_evidence(*self.fixture())
        self.assertEqual(len(files),18)
        self.assertEqual(files['almanac/query-engine.manifest.json']['sha256'],contract.FINAL_MANIFEST)
        self.assertEqual(files['almanac/query-engine.wasm']['sha256'],contract.BINARY)

    def test_incomplete_engine_browser_and_visual_evidence_is_refused(self):
        for change in ('parity','viewport','font','cell','visual','namespace'):
            args=self.fixture()
            if change=='parity':args[1]['main']['checks'].pop()
            elif change=='viewport':args[3]['checks']=[r for r in args[3]['checks'] if r['width']==1100]
            elif change=='font':next(r for r in args[3]['legibility'] if 'minimum_font_css_px' in r)['minimum_font_css_px']=4
            elif change=='cell':next(r for r in args[3]['legibility'] if 'cells' in r)['invalid_cells']=1
            elif change=='visual':args[4]['blocking_issues']=['unresolved']
            else:args[6]['unrelated_scientific_namespace']={}
            with self.subTest(change=change),self.assertRaises(ValueError):contract.verify_evidence(*args)


if __name__=='__main__':unittest.main()
