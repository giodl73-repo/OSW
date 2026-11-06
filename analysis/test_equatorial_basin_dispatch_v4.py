"""Execute the actual workflow selector against small request fixtures."""
import json
import os
from pathlib import Path
import tempfile
import textwrap
import unittest
from unittest.mock import patch
import check_equatorial_basin_delivery_v4 as controller


class Dispatch(unittest.TestCase):
    def workflow(self):
        return (controller.ROOT / controller.WORKFLOW).read_text()

    def selector(self):
        text = self.workflow()
        start = text.index("          python - <<'PY'\n") + len("          python - <<'PY'\n")
        stop = text.index('\n          PY', start)
        return textwrap.dedent(text[start:stop])

    def execute_selector(self, request):
        program = compile(self.selector(), controller.WORKFLOW, 'exec')
        previous = Path.cwd()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / controller.REQUEST
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(request))
            output = root / 'output.txt'
            try:
                os.chdir(root)
                with patch.dict(os.environ, {'GITHUB_OUTPUT': str(output)}):
                    exec(program, {'__name__': '__main__'})
                return output.read_text()
            finally:
                os.chdir(previous)

    def test_trigger_sparse_checkout_executed_reader_and_controller_paths_agree(self):
        text = self.workflow()
        expected = 'research/equatorial-basin-delivery-request-v4.json'
        self.assertEqual(controller.REQUEST, expected)
        self.assertEqual(controller.PREFLIGHT, 'research/equatorial-basin-delivery-preflight-v4.json')
        self.assertEqual(controller.WORKFLOW, '.github/workflows/equatorial-basin-delivery-v4.yml')
        self.assertIn('      - ' + expected, text)
        self.assertIn('sparse-checkout: ' + expected, text)
        self.assertIn("pathlib.Path('" + expected + "').read_bytes()", self.selector())
        self.assertIn("assert r['schema']=='osw.equatorial-basin-delivery-request.v4'", self.selector())
        for version in [1, 2]:
            self.assertNotIn('equatorial-basin-delivery-request-v' + str(version) + '.json', text)

    def test_actual_selector_program_dispatches_only_boolean_true_or_false(self):
        for value in [True, False]:
            actual = self.execute_selector({'schema': 'osw.equatorial-basin-delivery-request.v4', 'execute': value})
            self.assertEqual(actual, 'execute=' + str(value).lower() + '\n')

    def test_actual_selector_rejects_wrong_schema_and_truthy_string(self):
        for request in [{'schema': 'osw.equatorial-basin-delivery-request.v2', 'execute': True},
                        {'schema': 'osw.equatorial-basin-delivery-request.v4', 'execute': 'true'}]:
            with self.assertRaises(AssertionError):
                self.execute_selector(request)

    def test_controller_refuses_local_execution_before_installed_payload_access(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(controller, 'sha', side_effect=AssertionError('early read')):
            with self.assertRaises(ValueError):
                controller.controls()


if __name__ == '__main__':
    unittest.main()
