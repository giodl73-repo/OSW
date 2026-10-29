import unittest
from unittest.mock import patch
import check_chen_indian_sec_delivery_v2 as driver


class CloudBoundary(unittest.TestCase):
    def test_refuses_before_any_payload_or_request_access(self):
        with patch.dict('os.environ',{},clear=True), patch.object(driver,'read') as read:
            with self.assertRaisesRegex(ValueError,'Scoped cloud delivery only'):
                driver.controls()
            read.assert_not_called()


if __name__=='__main__':unittest.main()
