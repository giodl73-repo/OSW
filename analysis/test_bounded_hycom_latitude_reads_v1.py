import tempfile
from pathlib import Path
import unittest
import numpy as np
from bounded_hycom_latitude_reads_v1 import BoundedLatitudeReads


class Variable:
    name='water_u'
    def __init__(self,failures=0,wrong_shape=False,error='NetCDF: I/O failure'):
        self.failures=failures;self.wrong_shape=wrong_shape;self.error=error;self.calls=[]
    def __getitem__(self,key):
        self.calls.append(key)
        if len(self.calls)<=self.failures:raise RuntimeError(self.error)
        return np.ones((39 if self.wrong_shape else 40,1,3),dtype=np.float32)


class BoundedLatitudeReadTests(unittest.TestCase):
    def setUp(self):self.op={'maximum_total_cell_pairs':1000,'maximum_total_decoded_velocity_bytes':32000,'maximum_component_read_attempts':3}

    def test_retries_exact_same_slice_without_rereading_successful_other_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            delays=[];reads=BoundedLatitudeReads(240,self.op,Path(tmp)/'receipt.json',delays.append)
            u=Variable();v=Variable(2);v.name='water_v'
            reads.read(u,7,99,10,12);result=reads.read(v,7,99,10,12)
            self.assertEqual(result.shape,(40,3));self.assertEqual(len(u.calls),1);self.assertEqual(len(v.calls),3)
            self.assertEqual(v.calls,[v.calls[0]]*3);self.assertEqual(v.calls[0],(7,slice(None),slice(99,100),slice(10,13)))
            self.assertEqual(reads.receipt()['geometry'],'fixed_native_latitude_contiguous_native_longitudes')
            self.assertEqual(reads.requests[-1]['latitude_index'],99);self.assertEqual(reads.requests[-1]['longitude_indices_inclusive'],[10,12]);self.assertEqual(delays,[2,5])
            self.assertEqual(reads.extra_values,240);self.assertEqual(reads.requested_values,480)
            self.assertEqual(reads.returned_values,240);self.assertEqual(reads.receipt()['conservative_all_target_plus_retries_decoded_byte_bound'],5760)

    def test_global_reserve_denies_retry_before_spending_future_target_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            reads=BoundedLatitudeReads(1000,self.op,Path(tmp)/'receipt.json',lambda delay:None);var=Variable(3)
            with self.assertRaisesRegex(ValueError,'reserved'):reads.read(var,0,0,0,2)
            self.assertEqual(len(var.calls),1);self.assertEqual(reads.extra_values,0)
            self.assertEqual(reads.requests[-1]['status'],'retry_denied_before_read_by_full_target_budget')

    def test_byte_bound_denies_retry_even_if_pair_reserve_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            op={**self.op,'maximum_total_decoded_velocity_bytes':3840}
            reads=BoundedLatitudeReads(240,op,Path(tmp)/'receipt.json',lambda delay:None);var=Variable(2)
            with self.assertRaises(ValueError):reads.read(var,0,0,0,2)
            self.assertEqual(len(var.calls),1)

    def test_non_transport_error_and_shape_error_are_never_retried(self):
        with tempfile.TemporaryDirectory() as tmp:
            for var in [Variable(2,error='Scientific metadata mismatch'),Variable(wrong_shape=True)]:
                reads=BoundedLatitudeReads(240,self.op,Path(tmp)/'receipt.json',lambda delay:None)
                with self.assertRaises((ValueError,RuntimeError)):reads.read(var,0,0,0,2)
                self.assertEqual(len(var.calls),1)

    def test_retry_limit_and_invalid_declaration_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'receipt.json';var=Variable(9);reads=BoundedLatitudeReads(240,self.op,path,lambda delay:None)
            with self.assertRaises(RuntimeError):reads.read(var,0,0,0,2)
            self.assertEqual(len(var.calls),3);self.assertEqual(reads.returned_values,0)
            for op in [{**self.op,'maximum_component_read_attempts':4},{**self.op,'maximum_total_cell_pairs':1}]:
                with self.assertRaises(ValueError):BoundedLatitudeReads(240,op,path)


if __name__=='__main__':unittest.main()
