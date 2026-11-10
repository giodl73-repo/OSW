import copy
import json
from pathlib import Path
import unittest
import pacific_nec_product_axis_installation_contract_v1 as contract

ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_bytes())


class InstallationEvidence(unittest.TestCase):
    def fixture(self):
        e='research/pacific-nec-product-axis-delivery-run-v1/';b='research/pacific-nec-product-axis-browser-run-v2/'
        return [read(e+'result.json'),{k:read(e+'compare-'+k+'.json') for k in ('main','index')},
                read(b+'result.json'),read(b+'browser.json'),read('research/pacific-nec-product-axis-browser-visual-review-v2.json'),
                read(e+'engine-manifest.json'),read(b+'engine-manifest-presentation.json'),
                read('research/pacific-nec-product-axis-presentation-scope-v1.json'),(ROOT/b/'engine-manifest-presentation.json').stat().st_size]

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
            elif change=='font':next(r for r in args[3]['legibility'] if r['kind']=='plot text')['metrics'][0]['font_css_px']=4
            elif change=='cell':next(r for r in args[3]['legibility'] if r['kind']=='table cells' and r['width']==320)['minimum_cell_width']=1
            elif change=='visual':args[4]['blocking_issues']=['unresolved']
            else:args[6]['unrelated_scientific_namespace']={}
            with self.subTest(change=change),self.assertRaises(ValueError):contract.verify_evidence(*args)


if __name__=='__main__':unittest.main()
