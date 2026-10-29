import ast
from collections import Counter
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import chen_indian_sec_browser_contract_v2 as contract

ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_bytes())
def function(version,name):
    tree=ast.parse((ROOT/f'analysis/check_chen_indian_sec_browser_v{version}.py').read_text(encoding='utf8'))
    return next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)


class ResponsiveBrowserContract(unittest.TestCase):
    def test_overlay_changes_only_five_sources_and_one_added_stylesheet(self):
        old=read('research/chen-indian-sec-delivery-run-v4/engine-manifest.json')
        scope=read('research/chen-indian-sec-responsive-source-scope-v1.json')
        new=contract.presentation_manifest(old,scope,'browser-source')
        self.assertEqual(set(new)-set(old),{contract.KEY})
        for key in old:
            if key!='sha256':self.assertEqual(new[key],old[key])
        self.assertEqual({p for p in old['sha256'] if old['sha256'][p]!=new['sha256'][p]},contract.CHANGED)
        self.assertEqual(set(new['sha256'])-set(old['sha256']),contract.ADDED)
        self.assertEqual(new['sha256']['almanac/query-engine.wasm'],contract.BINARY)
        for change in ('parent','extra','science'):
            broken=copy.deepcopy(scope)
            if change=='parent':broken['source_changes']['almanac/query.js']['parent_sha256']='0'*64
            elif change=='extra':broken['source_changes']['unrelated.js']={}
            else:broken['scientific_inputs_changed']=True
            with self.subTest(change=change),self.assertRaises(ValueError):contract.presentation_manifest(old,broken,'source')

    def test_existing_browser_guards_actions_and_extraction_are_preserved(self):
        def inventory(version):
            tree=function(version,'browser_review');items=[]
            for node in ast.walk(tree):
                if isinstance(node,ast.If):items.append(('if',ast.dump(node.test,include_attributes=False)))
                if isinstance(node,ast.For):items.append(('for',ast.dump(node.iter,include_attributes=False)))
                if isinstance(node,ast.Call):
                    name=node.func.id if isinstance(node.func,ast.Name) else node.func.attr if isinstance(node.func,ast.Attribute) else ''
                    if name in ('expect','ValueError','append') or name.startswith('to_'):
                        items.append(('call',ast.dump(node,include_attributes=False)))
            return Counter(items)
        self.assertFalse(inventory(3)-inventory(4))
        self.assertEqual(ast.dump(function(3,'extract_saved'),include_attributes=False),ast.dump(function(4,'extract_saved'),include_attributes=False))

    def test_v4_refuses_local_browser_before_access(self):
        import check_chen_indian_sec_browser_v4 as browser
        with patch.dict('os.environ',{},clear=True),patch.object(browser,'read') as read:
            with self.assertRaisesRegex(ValueError,'Scoped cloud browser only'):browser.controls()
            read.assert_not_called()


if __name__=='__main__':unittest.main()
