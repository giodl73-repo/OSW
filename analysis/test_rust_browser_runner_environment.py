"""The full UI gate shares a default browser and preserves user overrides."""
import os
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

import run_rust_query_browser_checks as runner


class BrowserEnvironmentTests(unittest.TestCase):
    def check_environment(self, override):
        initial = {} if override is None else {'OSW_TEST_BROWSER': override}
        chromium = SimpleNamespace(executable_path='/installed/chromium')
        playwright_context = MagicMock()
        playwright_context.__enter__.return_value = SimpleNamespace(chromium=chromium)
        with patch.dict(os.environ, initial, clear=True), \
                patch.object(runner.sys, 'argv', ['browser-checks']), \
                patch.object(runner, 'wait_for_checkout'), \
                patch.object(runner.subprocess, 'run') as child, \
                patch('playwright.sync_api.sync_playwright', return_value=playwright_context):
            runner.main()
            self.assertEqual(child.call_count, len(runner.CHECKS))
            expected = override or '/installed/chromium'
            for call in child.call_args_list:
                self.assertEqual(call.kwargs['env']['OSW_TEST_BROWSER'], expected)
                self.assertTrue(call.kwargs['check'])
            self.assertEqual(dict(os.environ), initial)

    def test_every_child_gets_default_when_override_missing_or_empty(self):
        for value in [None, '']:
            with self.subTest(value=value):
                self.check_environment(value)

    def test_every_child_honors_explicit_browser_without_mutating_parent(self):
        self.check_environment('/selected/browser')


if __name__ == '__main__':
    unittest.main()
