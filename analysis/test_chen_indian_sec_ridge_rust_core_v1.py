import os
import unittest
from unittest.mock import patch
import check_chen_indian_sec_ridge_rust_core_v1 as subject


class CloudOnlyNativeGate(unittest.TestCase):
    def test_local_refusal_precedes_files_and_subprocesses(self):
        with patch.dict(os.environ,{},clear=True),patch.object(subject,'read',side_effect=AssertionError('early read')),patch.object(subject.subprocess,'check_output',side_effect=AssertionError('early compiler')):
            with self.assertRaises(ValueError):subject.controls()


if __name__=='__main__':unittest.main()
