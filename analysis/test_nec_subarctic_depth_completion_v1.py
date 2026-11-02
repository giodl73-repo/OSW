import copy
import json
import unittest
import tempfile
from pathlib import Path
import assemble_nec_subarctic_depth_completion_v1 as s
from acquire_nec_subarctic_depth_completion_v1 import run_with_io_retries


class NECTransportCompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.original,cls.completion,cls.recovery,cls.recovered,cls.remaining=s.validate_recovered()

    def test_exact29_recovered_and5_original_missing_sections(self):
        self.assertEqual(len(self.recovered),29);self.assertEqual(len(self.remaining),5)
        self.assertTrue(all(t=='2022-07-15T00:00:00Z' and entity=='current:aleutian' for t,entity,section in self.remaining))
        self.assertEqual({section for t,entity,section in self.remaining},{'section-180e','section-170w','section-160w','section-150w','section-140w'})

    def test_measurement_params_frozen_and_cutoff_or_gate_change_rejected(self):
        s.parameters_equal(self.original,self.completion)
        bad=copy.deepcopy(self.completion);bad['currents']['current:aleutian']['primary_threshold_m_s']=.2
        with self.assertRaises(ValueError):s.parameters_equal(self.original,bad)
        old={(r['entity_id'],r['id']):r for r in self.original['sections']}
        self.assertTrue(all(r==old[r['entity_id'],r['id']] for r in self.completion['sections']))

    def test_recovered_original_bytes_operators_and_same_first5_values_are_preserved(self):
        prior=self.recovery['attempt1_retained_partial_files']
        for raw,section in self.recovered.values():
            filename=section['snapshot_time_utc'][:10]+'-'+section['entity_id'].split(':')[1]+'-'+section['section_definition']['id']+'.json'
            if filename in prior:self.assertEqual(section['decoded_columns_sha256'],prior[filename]['decoded_columns_sha256'])
            self.assertEqual(section['operator_file'],s.ORIGINAL)
            self.assertFalse(any(section['eligibility'].values()))

    def test_transport_retries_only_actual_io_failure_and_preserves_partial_bytes(self):
        calls=[];delays=[]
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            def call():
                calls.append(1)
                if len(calls)<3:
                    (out/'saved.json').write_bytes(b'{"retained":true}\n')
                    raise RuntimeError('NetCDF: I/O failure')
            receipt=run_with_io_retries(call,out,delays.append)
            self.assertEqual(receipt['successful_attempt'],3);self.assertEqual(delays,[2,5])
            self.assertEqual((out/'failed-transport-attempt-1/saved.json').read_bytes(),b'{"retained":true}\n')
            self.assertEqual(len(receipt['attempts']),3)

    def test_non_transport_errors_are_not_retried_or_hidden(self):
        calls=[]
        def bad():calls.append(1);raise RuntimeError('Scientific input mismatch')
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError,'Scientific input'):run_with_io_retries(bad,Path(tmp),lambda delay:None)
        self.assertEqual(len(calls),1)


if __name__=='__main__':unittest.main()
