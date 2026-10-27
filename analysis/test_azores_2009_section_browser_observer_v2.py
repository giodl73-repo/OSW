"""Readiness and capture policy checks without launching a local browser."""
import ast
from pathlib import Path
import unittest
import check_azores_2009_section_browser_v2 as browser


class BrowserObserver(unittest.TestCase):
    def test_clipped_or_empty_capture_refused(self):
        browser.verify_capture_geometry({'width': 356, 'height': 400, 'clipped_axes': []})
        for value in [{'width': 356, 'height': 1600, 'clipped_axes': ['vertical']},
                      {'width': 0, 'height': 400, 'clipped_axes': []},
                      {'width': 356, 'height': 400, 'clipped_axes': ['horizontal']}]:
            with self.assertRaises(ValueError):
                browser.verify_capture_geometry(value)

    def test_worker_wait_and_all_original_semantic_checks_retained(self):
        text = Path(browser.__file__).read_bytes().decode()
        ast.parse(text)
        self.assertIn("locator.wait_for(state='visible', timeout=180000)", text)
        self.assertIn('date conflict remains unresolved', text)
        self.assertIn('annual ranges remain unknown', text)
        self.assertIn('expect(page.locator(\'#season-play\')).to_be_disabled()', text)
        self.assertIn("for width in [320, 390]", text)
        self.assertIn('Actual indexed source-row navigation differs', text)
        self.assertIn('Actual paginated mixed-width query differs', text)
        self.assertNotIn("capture(card, 'azores-' + current + '-atlas.png')", text)


if __name__ == '__main__':
    unittest.main()
