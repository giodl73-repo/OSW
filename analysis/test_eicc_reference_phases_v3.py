"""Local refusal and browser representation checks; no payload/build/browser."""
import unittest
from unittest.mock import patch

import check_eicc_reference_delivery_v3 as controller
import eicc_reference_browser_values_v3 as values


class EiccPhases(unittest.TestCase):
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
