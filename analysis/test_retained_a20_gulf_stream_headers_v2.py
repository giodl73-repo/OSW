from pathlib import Path
import tempfile
import unittest
import netCDF4
from inspect_retained_a20_gulf_stream_headers_v2 import safe_attribute, inspect, prior_failed_read_charge, build


class RetainedHeaderChecks(unittest.TestCase):
    def ledger(self): return {'prior_failed_numeric_attribute_values': 0, 'reconstruction_numeric_attribute_touches': 0, 'new_numeric_attribute_values_touched': 0}

    def test_large_text_hash_does_not_raise_or_silently_truncate(self):
        import hashlib
        text = 'x' * 12001
        row = safe_attribute(text, self.ledger())
        self.assertEqual(row['sha256'], hashlib.sha256(text.encode()).hexdigest())
        self.assertEqual(row['utf8_bytes'], 12001)
        self.assertNotIn(text, str(row))

    def test_prior_touches_and_reconstruction_use_same_case_budget(self):
        ledger = self.ledger(); ledger['prior_failed_numeric_attribute_values'] = 5000
        ledger['reconstruction_numeric_attribute_touches'] = 5000
        with self.assertRaises(ValueError): safe_attribute(1, ledger)

    def test_header_never_slices_variable_values(self):
        with tempfile.TemporaryDirectory() as name:
            p = Path(name) / 'test.nc'
            with netCDF4.Dataset(p, 'w') as d:
                d.station = 14; d.huge_source_text = 'x' * 12001
                d.createDimension('z', 600); d.createVariable('u', 'f8', ('z',)).units = 'm/s'
            self.assertEqual(prior_failed_read_charge(p), 1)
            r = inspect(p, self.ledger())
            self.assertEqual(r['variables']['u']['shape'], [600])
            self.assertEqual(r['native_velocity_values_read'], 0)

    def test_actual_original_byte_custody_and_no_promotion(self):
        r = build()
        self.assertEqual([a['station'] for a in r['headers']], ['014', '015', '016'])
        self.assertEqual(r['original_case_operations_remaining'], 0)
        self.assertEqual(r['new_provider_operations'], 0)
        self.assertEqual(r['native_array_values_decoded'], 0)
        self.assertEqual(r['new_depth_references_admitted'], 0)
        self.assertFalse(r['physical_current_bottom_established'])


if __name__ == '__main__': unittest.main()
