"""Verify the audit never reads science arrays, including single-level fields."""
import json
import sys
import types
import unittest
from unittest.mock import patch

import inspect_eddy_altimetry_source_v1 as audit


class ScienceVariable:
    dtype = 'float64'
    dimensions = ('time', 'latitude', 'longitude')
    shape = (9861, 120, 160)

    def ncattrs(self):
        return ['units']

    def getncattr(self, name):
        return 'm'

    def __getitem__(self, key):
        raise AssertionError('The header audit must not read ADT values')


class Source:
    data_model = 'NETCDF4'
    dimensions = {'time': range(9861), 'latitude': range(120), 'longitude': range(160)}
    variables = {'adt': ScienceVariable()}
    groups = {}

    def ncattrs(self):
        return []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class AuditTests(unittest.TestCase):
    def test_header_never_reads_science_array(self):
        with patch.dict(sys.modules, {'netCDF4': types.SimpleNamespace(Dataset=lambda p: Source())}):
            header = audit.inspect_header('mock.nc')
        self.assertEqual(header['variables']['adt']['shape'], [9861, 120, 160])
        self.assertNotIn('coordinate', header['variables']['adt'])

    def test_nonfinite_attributes_are_explicit_json_strings(self):
        value = audit.plain([float('nan'), float('inf'), b'm'])
        self.assertEqual(json.loads(json.dumps(value, allow_nan=False)), ['nan', 'inf', 'm'])

    def test_download_refuses_local_execution(self):
        with patch.dict(audit.os.environ, {'GITHUB_ACTIONS': 'false'}):
            with self.assertRaisesRegex(AssertionError, 'cloud-only'):
                audit.main()


if __name__ == '__main__':
    unittest.main()
