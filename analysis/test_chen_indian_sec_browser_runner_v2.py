import ast
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]


class RunnerCompatibility(unittest.TestCase):
    def test_browser_cases_and_extraction_are_identical(self):
        def function(version,name):
            tree=ast.parse((ROOT/f'analysis/check_chen_indian_sec_browser_v{version}.py').read_text(encoding='utf8'))
            return ast.dump(next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name),include_attributes=False)
        for name in ('browser_review','extract_saved'):
            with self.subTest(name=name):self.assertEqual(function(1,name),function(2,name))

    def test_v2_refuses_local_browser_before_file_access(self):
        import check_chen_indian_sec_browser_v2 as browser
        with patch.dict('os.environ',{},clear=True),patch.object(browser,'read') as read:
            with self.assertRaisesRegex(ValueError,'Scoped cloud browser only'):browser.controls()
            read.assert_not_called()


if __name__=='__main__':unittest.main()
