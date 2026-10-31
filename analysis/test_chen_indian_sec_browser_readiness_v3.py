import ast
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
def function(version,name):
    tree=ast.parse((ROOT/f'analysis/check_chen_indian_sec_browser_v{version}.py').read_text(encoding='utf8'))
    return next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)


class ReadinessScope(unittest.TestCase):
    def test_every_existing_case_and_extraction_check_remains(self):
        class RemoveReadyCalls(ast.NodeTransformer):
            removed=0
            def visit_Expr(self,node):
                if isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Name) and node.value.func.id=='atlas_ready':
                    self.removed+=1;return None
                return self.generic_visit(node)
        remove=RemoveReadyCalls();new=remove.visit(function(3,'browser_review'))
        self.assertEqual(remove.removed,2)
        self.assertEqual(ast.dump(new,include_attributes=False),ast.dump(function(2,'browser_review'),include_attributes=False))
        self.assertEqual(ast.dump(function(3,'extract_saved'),include_attributes=False),ast.dump(function(2,'extract_saved'),include_attributes=False))

    def test_v3_refuses_local_browser_before_access(self):
        import check_chen_indian_sec_browser_v3 as browser
        with patch.dict('os.environ',{},clear=True),patch.object(browser,'read') as read:
            with self.assertRaisesRegex(ValueError,'Scoped cloud browser only'):browser.controls()
            read.assert_not_called()


if __name__=='__main__':unittest.main()
