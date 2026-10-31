"""Read-only checks of cloud-only entry points and frozen execution policy."""
import ast
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
import check_azores_2009_section_delivery_v1 as delivery


class DeliveryControls(unittest.TestCase):
    def test_local_entry_refuses_before_any_artifact_or_control_read(self):
        with patch.object(delivery, 'read', side_effect=AssertionError('Unexpected file read')):
            with patch.dict(os.environ, {'GITHUB_ACTIONS': 'false'}, clear=False):
                with self.assertRaisesRegex(ValueError, 'Exact cloud'):
                    delivery.controls()

    def test_source_code_parses_and_workflow_keeps_single_shared_job(self):
        for path in ['analysis/check_azores_2009_section_delivery_v1.py',
                     'analysis/check_azores_2009_section_browser_v1.py']:
            ast.parse(Path(path).read_bytes())
        workflow = Path(delivery.WORKFLOW).read_bytes().decode()
        for expected in ['group: osw-current-gap-delivery', 'cancel-in-progress: false',
                         'CARGO_BUILD_JOBS: "1"', 'RUST_TEST_THREADS: "1"', 'nice -n 15',
                         'azores-2009-section-delivery-request-v1.json',
                         'check_azores_2009_section_delivery_v1.py engine',
                         'check_azores_2009_section_delivery_v1.py browser']:
            self.assertIn(expected, workflow)
        self.assertNotIn('contents: write', workflow)
        self.assertNotIn('workflow_dispatch', workflow)


if __name__ == '__main__':
    unittest.main()
