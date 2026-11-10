"""Independent decoding reference and fail-closed CF metadata tests; cloud only."""
import base64,copy,json,unittest
from pathlib import Path
import numpy as np
import hycom_packed_int16_v1 as decoder
import capture_ncc_mid_norway_packed_field_v1 as capture


class Packed(unittest.TestCase):
    def setUp(self):
        self.specs={}
        for name in decoder.FIELDS:
            raw=capture.das(capture.ROOT,8 if name=='salinity' else 2)
            self.specs[name]=decoder.specification(raw,name)
    def test_independent_netCDF4_all_three_fields(self):
        self.assertEqual(len(decoder.conformance(self.specs)['records']),3)
    def test_native_integer_mask_and_salinity_offset(self):
        got=decoder.decode(np.asarray([-30000,0,1000],dtype='i2'),self.specs['salinity'])
        self.assertEqual(got.mask.tolist(),[True,False,False]);self.assertEqual(got[1:].tolist(),[20,21])
    def test_unsigned_and_float_input_rejected(self):
        for dtype in ['u2','f4','i4']:
            with self.assertRaises(ValueError):decoder.decode(np.asarray([1],dtype=dtype),self.specs['water_u'])
    def test_changed_cf_types_or_validity_rejected(self):
        for key,change in [('scale_factor',{'type':'Float64','literal':'0.001'}),('valid_range',{'type':'Int16','literal':'0, 30000'}),('add_offset',{'type':'Float32','literal':'1.0'})]:
            spec=copy.deepcopy(self.specs['water_u']);spec['attributes'][key]=change
            with self.assertRaises(ValueError):decoder.decode(np.asarray([1],dtype='i2'),spec)
    def test_complete_frozen_eight_case_preflight(self):
        specs,plan=capture.full_plan(capture.ROOT)
        self.assertEqual(len(plan['targets']),24);self.assertEqual(len({(t['section_id'],t['snapshot_time_utc']) for t in plan['targets']}),8)
        self.assertEqual(sum(t['scalar_values'] for t in plan['targets']),plan['planned_first_attempt_scalar_values'])
        self.assertLessEqual(plan['joint_reserved_native_cell_units'],250000);self.assertLessEqual(plan['conservative_joint_decoded_bytes'],7000000)
    def test_no_model_numeric_values_in_structure(self):
        raw=b'Dataset {\n Grid {\n } water_u;\n}\n---------------------------------------------\nwater_u.water_u[1][40][1][3]\n[0][0][0], 123, -30000, 7\n'
        report=capture.structure(raw);self.assertEqual(report['data_labels_in_order'],['water_u.water_u[1][40][1][3]','[0][0][0]']);self.assertNotIn('123',json.dumps(report))
    def test_response_url_requires_native_shape(self):
        _,plan=capture.full_plan(capture.ROOT);target=copy.deepcopy(plan['targets'][0]);target['native_shape'][1]=39
        with self.assertRaises(ValueError):capture.field_url(target)


if __name__=='__main__':unittest.main()
