import copy
import json
import tempfile
import unittest
from pathlib import Path
import gsw
import convert_canary_pies_depth_v1 as conversion


class CanaryPressureConversionTests(unittest.TestCase):
    def test_official_example_sign_and_inverse(self):
        self.assertAlmostEqual(-float(gsw.z_from_p(1000,4)),992.09217795512,places=8)
        for row in conversion.build()['records']:
            p=float(gsw.p_from_z(-row['computed_depth_m'],row['conversion_latitude_degrees_north'],0,0))
            self.assertAlmostEqual(p,row['source_pressure_dbar'],places=5)

    def test_native_scopes_remain_distinct(self):
        rows=conversion.build()['records']
        self.assertEqual([r['source_pressure_dbar'] for r in rows],[810,480,690])
        self.assertEqual([r['display_approximate_depth_m'] for r in rows],[800,480,680])
        self.assertNotEqual(rows[1]['averaging_condition'],rows[2]['averaging_condition'])
        self.assertNotEqual(rows[0]['branch_scope'],rows[1]['branch_scope'])

    def test_latitude_sensitivity_is_not_uncertainty(self):
        for row in conversion.build()['records']:
            low,high=row['endpoint_latitude_sensitivity_depths_m']
            self.assertLessEqual(low,row['computed_depth_m']);self.assertLessEqual(row['computed_depth_m'],high)
            self.assertLess(high-low,0.1)
            self.assertFalse(row['sensitivity_is_uncertainty_interval'])
            self.assertIsNone(row['physical_depth_uncertainty_m'])

    def test_no_automatic_physical_or_seasonal_promotion(self):
        for row in conversion.build()['records']:
            self.assertIsNone(row['physical_thickness_m']);self.assertIsNone(row['seasonal_depth_range_m'])
            self.assertFalse(row['volume_eligible']);self.assertFalse(row['reference_route_projection_eligible'])
            self.assertEqual(row['atmospheric_pressure_subtracted_dbar'],0)
            self.assertNotEqual(row['computed_depth_m'],row['source_pressure_dbar'])

    def test_reject_unit_scope_and_correction_mutations(self):
        for file,key,value,index in [(conversion.SOURCE,'unit','m',0),(conversion.SOURCE,'approximate_value',700,0),(conversion.SOURCE,'averaging_condition','monthly',2),(conversion.OPERATOR,'assumed_dynamic_height_m2_s2',10,None),(conversion.OPERATOR,'latitude_rule','assume_equator',None)]:
            with self.subTest(key=key),tempfile.TemporaryDirectory() as directory:
                root=Path(directory)
                for path in [conversion.SOURCE,conversion.OPERATOR]:
                    target=root/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((conversion.ROOT/path).read_bytes())
                d=json.loads((root/file).read_bytes());target=d if index is None else d['references'][index];target[key]=value
                (root/file).write_text(json.dumps(d),encoding='utf8')
                with self.assertRaises(ValueError):conversion.build(root)

    def test_output_reproduces_if_retained(self):
        output=conversion.ROOT/conversion.OUTPUT
        self.assertTrue(output.exists(),'Cloud conversion output must be generated before review')
        self.assertEqual(conversion.build(),json.loads(output.read_bytes()))


if __name__=='__main__':unittest.main()
