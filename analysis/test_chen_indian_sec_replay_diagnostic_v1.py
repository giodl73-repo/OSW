import os
import unittest
from unittest.mock import patch
import diagnose_chen_indian_sec_replay_v1 as subject

class ReplayDiagnostic(unittest.TestCase):
    def test_local_refusal_before_source_access(self):
        with patch.dict(os.environ,{},clear=True),patch.object(subject,'read',side_effect=AssertionError('early read')):
            with self.assertRaises(ValueError):subject.controls()
    def test_structural_and_numeric_differences_stay_separate(self):
        self.assertEqual(subject.differences({'a':[1.0]},{'a':[1.0]}),[])
        row=subject.differences({'a':[1.0]},{'a':[1.00001]})[0]
        self.assertEqual(row['pointer'],'/a/0');self.assertEqual(row['kind'],'numeric')
        self.assertEqual(subject.differences({'a':None},{'a':0})[0]['kind'],'type')
        self.assertEqual(subject.differences([1],[1,2])[0]['kind'],'length')

if __name__=='__main__':unittest.main()
