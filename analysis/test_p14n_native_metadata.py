"""Native source custody and header semantics precede any new field operator."""
from pathlib import Path
import unittest
from unittest.mock import patch
import xarray as xr
import build_p14n_native_metadata as native

class NativeMetadataTests(unittest.TestCase):
    def test_reconstruction_and_frames_are_distinct(self):
        report=native.verify()
        self.assertEqual(len(report['products']),2)
        short,long=report['products']
        self.assertEqual(short['dimensions'],{'time':11455,'depth_cell':120})
        self.assertEqual(short['variables']['depth']['dimensions'],['time','depth_cell'])
        self.assertIn('uship',short['variables'])
        self.assertIn('ACCESS_U_ship_absolute',long['variables'])
        self.assertFalse(report['profile_flags_are_woce_ctd_quality_codes'])
        self.assertEqual(report['profile_flag_bit_meanings']['4'],'below bottom')
        self.assertFalse(report['ocean_and_ship_velocity_arrays_inspected'])
        self.assertFalse(report['new_width_record_admitted'])
        self.assertIsNone(report['selected_local_profile_count'])
        self.assertIsNone(report['whole_current_width_km'])
    def test_header_audit_does_not_access_variable_values_or_data(self):
        def denied(variable):raise AssertionError('Header audit accessed a variable array')
        # xarray installs lazy backend wrappers through the data setter while
        # opening a dataset. Preserve setters and prohibit every array getter.
        values=xr.Variable.values;data=xr.Variable.data
        with patch.object(xr.Variable,'values',property(denied,values.fset)),patch.object(xr.Variable,'data',property(denied,data.fset)):
            self.assertEqual(native.build(),native.verify())
    def test_each_native_original_receipt_producer_and_declaration_is_bound(self):
        original=Path.read_bytes
        for name in native.FROZEN_INPUTS:
            target=native.ROOT/name
            def changed(path):return original(path)+(b'x' if path==target else b'')
            with self.subTest(path=name),patch.object(Path,'read_bytes',changed),self.assertRaises(ValueError):native.build()

if __name__=='__main__':unittest.main()
