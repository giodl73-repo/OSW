import copy
import json
from pathlib import Path
import tempfile
import unittest
from acquire_a20_gulf_stream_cast_headers_v1 import ROOT, OP, validate_operator, reserve, acquire, header


class CastCustodyChecks(unittest.TestCase):
    def test_original_whole_case_caps_and_exact_targets(self):
        op = json.loads((ROOT / OP).read_bytes()); validate_operator(op)
        for k, v in [('case_operation_cap', 4), ('future_selected_levels_per_cast_cap', 100),
                     ('case_response_byte_cap', 700000)]:
            bad = copy.deepcopy(op); bad[k] = v
            with self.assertRaises(ValueError): validate_operator(bad)

    def test_reservation_is_durable_and_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name); journal = {'operations': []}; target = {'station': '014', 'url': 'https://example.invalid/a.nc'}
            reserve(journal, folder, target)
            self.assertEqual(json.loads((folder / 'journal.json').read_bytes())['operations'][0]['status'], 'reserved_before_request')
            with self.assertRaises(ValueError): reserve(journal, folder, target)

    def test_failed_body_retained_and_never_accepted_as_netcdf(self):
        class Reply:
            status = 404
            def __enter__(self): return self
            def __exit__(self, *a): pass
            def read(self, n):
                if hasattr(self, 'done'): return b''
                self.done = True; return b'missing'
        class Opener:
            def open(self, *a, **k): return Reply()
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name); journal = {'operations': [], 'case_time_charge_seconds': 0}
            with self.assertRaises(ValueError): acquire({'station': '014', 'url': 'https://example.invalid/a.nc'}, folder, journal, Opener())
            self.assertEqual((folder / '014.nc').read_bytes(), b'missing')
            self.assertEqual(journal['operations'][0]['status'], 'failed_or_interrupted_no_retry')

    def test_headers_do_not_read_variable_values(self):
        import netCDF4
        with tempfile.TemporaryDirectory() as name:
            p = Path(name) / 'test.nc'
            with netCDF4.Dataset(p, 'w') as d:
                d.createDimension('z', 500)
                v = d.createVariable('u', 'f8', ('z',)); v.units = 'm s-1'
            result = header(p)
            self.assertEqual(result['variables']['u']['shape'], [500])
            self.assertEqual(result['native_velocity_values_read'], 0)
            self.assertEqual(result['native_depth_axis_values_read'], 0)


if __name__ == '__main__':
    unittest.main()
