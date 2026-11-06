import ast
import unittest
import check_equatorial_basin_browser_v3 as m
from pathlib import Path


class Page:
    def __init__(self):
        self.events = []
    def goto(self, url):
        self.events.append(('goto', url))
    def wait_for_function(self, predicate, **kwargs):
        self.events.append(('ready', predicate, kwargs))
    def locator(self, selector):
        self.events.append(('locator', selector))
        return 'panel'


class Readiness(unittest.TestCase):
    def test_object_navigation_waits_for_the_requested_object_before_locating_panel(self):
        page = Page()
        self.assertEqual(m.object_page(page, 'http://127.0.0.1:1234', 'current:atlantic-north-equatorial'), 'panel')
        self.assertEqual([e[0] for e in page.events], ['goto', 'ready', 'locator'])
        self.assertTrue(page.events[0][1].endswith('object.html?id=current%3Aatlantic-north-equatorial'))
        self.assertEqual(page.events[1][2], {'arg': 'current:atlantic-north-equatorial', 'timeout': 180000})
        self.assertIn('window.oswObjectView?.ok === true', page.events[1][1])
        self.assertIn('window.oswObjectView.id === id', page.events[1][1])

    def test_followed_family_and_member_links_each_wait_for_their_own_owner(self):
        page = Page()
        for owner in ['current:north-equatorial', 'current:atlantic-north-equatorial']:
            self.assertEqual(m.object_ready(page, owner), 'panel')
        self.assertEqual([e[2]['arg'] for e in page.events if e[0] == 'ready'],
                         ['current:north-equatorial', 'current:atlantic-north-equatorial'])

    def test_content_source_clipping_and_query_assertion_functions_are_unchanged(self):
        root = Path(__file__).resolve().parents[1]
        def functions(path):
            tree = ast.parse((root / path).read_text())
            return {n.name: ast.dump(n, include_attributes=False) for n in ast.walk(tree)
                    if isinstance(n, ast.FunctionDef)}
        old = functions('analysis/check_equatorial_basin_browser_v2.py')
        new = functions('analysis/check_equatorial_basin_browser_v3.py')
        for name in ['panel_matches', 'capture', 'no_overflow', 'query_page']:
            self.assertEqual(old[name], new[name], name)

    def test_capture_count_and_page_error_missing_asset_guards_remain(self):
        root = Path(__file__).resolve().parents[1]
        def count(path):
            return sum(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'capture'
                       for n in ast.walk(ast.parse((root / path).read_text())))
        self.assertEqual(count('analysis/check_equatorial_basin_browser_v2.py'), count('analysis/check_equatorial_basin_browser_v3.py'))
        source = (root / 'analysis/check_equatorial_basin_browser_v3.py').read_text()
        self.assertIn('if errors or missing or originals:', source)
        self.assertIn('for width in [1100, 320]:', source)
        self.assertIn("expect(panel.locator('li[data-entity-id]')).to_have_count(len(scene['members']))", source)


if __name__ == '__main__':
    unittest.main()
