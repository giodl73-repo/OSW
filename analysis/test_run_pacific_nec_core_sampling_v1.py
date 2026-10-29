import unittest
from unittest.mock import patch
import run_pacific_nec_core_sampling_v1 as driver


class CloudBoundary(unittest.TestCase):
    def test_local_refusal_precedes_files_and_source_access(self):
        with patch.dict(driver.os.environ,{},clear=True),patch.object(driver,'read',side_effect=AssertionError('No input reads')), \
             patch.object(driver.custody,'saved_source',side_effect=AssertionError('No source access')):
            with self.assertRaisesRegex(ValueError,'Cloud-only'):driver.guard()


if __name__=='__main__':unittest.main()
