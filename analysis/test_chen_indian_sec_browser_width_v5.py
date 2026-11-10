import ast
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import chen_indian_sec_browser_contract_v2 as contract

ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads((ROOT/path).read_bytes())
def function(version,name):
    tree=ast.parse((ROOT/f'analysis/check_chen_indian_sec_browser_v{version}.py').read_text(encoding='utf8'))
    return next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)


class WidthCorrection(unittest.TestCase):
    def test_every_browser_case_plot_check_and_extraction_remains_identical(self):
        for name in ('browser_review','extract_saved','plot_legibility','verify_reflow'):
            with self.subTest(name=name):
                self.assertEqual(ast.dump(function(4,name),include_attributes=False),ast.dump(function(5,name),include_attributes=False))

    def test_revised_scope_keeps_engine_and_declares_same_five_plus_one_assets(self):
        parent=read('research/chen-indian-sec-delivery-run-v4/engine-manifest.json')
        scope=read('research/chen-indian-sec-responsive-source-scope-v2.json')
        result=contract.presentation_manifest(parent,scope,'browser-source')
        for key in parent:
            if key!='sha256':self.assertEqual(result[key],parent[key])
        self.assertEqual(result['sha256']['almanac/query-engine.wasm'],contract.BINARY)
        self.assertEqual({p for p in parent['sha256'] if parent['sha256'][p]!=result['sha256'][p]},contract.CHANGED)
        self.assertEqual(set(result['sha256'])-set(parent['sha256']),contract.ADDED)

    def test_v5_refuses_local_execution_before_access(self):
        import check_chen_indian_sec_browser_v5 as browser
        with patch.dict('os.environ',{},clear=True),patch.object(browser,'read') as read:
            with self.assertRaisesRegex(ValueError,'Scoped cloud browser only'):browser.controls()
            read.assert_not_called()


if __name__=='__main__':unittest.main()
