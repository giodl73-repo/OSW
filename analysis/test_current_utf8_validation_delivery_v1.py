import os
import unittest
from unittest.mock import patch
import check_current_utf8_validation_delivery_v1 as delivery

class Utf8DeliveryScopeTests(unittest.TestCase):
    def test_local_delivery_refuses_before_payload_access(self):
        with patch.object(os, 'name', 'nt'), patch.object(delivery.Path, 'read_bytes', side_effect=AssertionError('No local packet reads')):
            with self.assertRaisesRegex(ValueError, 'Scoped cloud UTF-8'):
                delivery.run()

if __name__ == '__main__':
    unittest.main()
