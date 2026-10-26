"""Local refusal and browser representation checks; no payload/build/browser."""
import unittest
import subprocess
from unittest.mock import patch

import check_eicc_reference_delivery_v4 as controller
import eicc_reference_browser_values_v3 as values


class EiccPhases(unittest.TestCase):
    def compile_case(self, fail_inventory=False):
        events = []
        def run(command, **kwargs):
            if 'planning::tests' in command:
                events.append('planning')
                return subprocess.CompletedProcess(command, 0, b'6 passed; 0 failed', b'')
            if 'eicc_extension_' in command:
                events.append('inventory')
                return subprocess.CompletedProcess(command, int(fail_inventory),
                    b'0 passed; 1 failed' if fail_inventory else b'2 passed; 0 failed', b'')
            events.append('wasm' if 'wasm32-unknown-unknown' in command else 'native')
            return subprocess.CompletedProcess(command, 0, b'', b'')
        def smoke(*args, **kwargs):
            events.append('smoke')
            return {'map_scene': {'features': [{}]}}
        with patch.object(controller.subprocess, 'run', side_effect=run), \
                patch.object(controller, 'native_query', side_effect=smoke), \
                patch.object(controller.cases, 'verify_response'), \
                patch.object(controller, 'write'):
            if fail_inventory:
                with self.assertRaisesRegex(ValueError, 'Both global route-inventory tests required'):
                    controller.compile_engine()
            else:
                controller.compile_engine()
        return events

    def test_global_inventory_tests_and_native_smoke_precede_wasm_build(self):
        self.assertEqual(self.compile_case(), ['native', 'planning', 'inventory', 'smoke', 'wasm'])

    def test_global_inventory_failure_prevents_smoke_and_wasm_build(self):
        self.assertEqual(self.compile_case(fail_inventory=True), ['native', 'planning', 'inventory'])

    def test_engine_and_browser_phases_refuse_locally_before_any_source_read(self):
        with patch.object(controller, 'read', side_effect=AssertionError('Unexpected source read')):
            with self.assertRaises(RuntimeError): controller.controls({})
            with self.assertRaises(RuntimeError): controller.browser_phase({})

    def test_browser_number_representation_preserves_boolean_and_null_meanings(self):
        self.assertTrue(values.same({'position': [84.0, 14.0], 'admitted': False},
                                    {'position': [84, 14], 'admitted': False}))
        self.assertFalse(values.same({'admitted': False}, {'admitted': 0}))
        self.assertFalse(values.same({'width': None}, {'width': 0}))
        self.assertFalse(values.same({'value': '19.0'}, {'value': 19}))
        with self.assertRaises(ValueError): values.same({'value': float('nan')}, {'value': None})


if __name__ == '__main__': unittest.main()
