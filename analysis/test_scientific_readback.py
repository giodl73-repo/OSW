"""Declared calculation readback cannot round original data or hide outcomes."""
import copy
import math
import unittest
from unittest.mock import patch
import scientific_readback as readback


class ReadbackTests(unittest.TestCase):
    def test_observed_geometry_only_preserves_native_profiles_and_metadata(self):
        source={'schema':'osw.observed-vector-section.v1','input_sha256':{'original.nc':'source-pin'},
                'track_legs':[{'straight_distance_between_hourly_mean_positions_km':1.123456789,
                    'bearing_between_hourly_mean_positions_degrees_true':181.123456789}],
                'profiles':[{'eastward_m_s':.1234567891234567,'northward_m_s':-0.0,'qc':2}],
                'current_association_verified':False,'new_numeric_field':.1234567891234567}
        before=copy.deepcopy(source);result=readback.canonicalize(source)
        self.assertEqual(source,before)
        self.assertEqual(result['track_legs'][0]['straight_distance_between_hourly_mean_positions_km'],1.123457)
        self.assertEqual(result['track_legs'][0]['bearing_between_hourly_mean_positions_degrees_true'],181.123457)
        self.assertEqual(result['profiles'],source['profiles'])
        self.assertEqual(result['profiles'][0]['northward_m_s'].hex(),(-0.0).hex())
        self.assertEqual(result['new_numeric_field'],source['new_numeric_field'])
        self.assertIs(result['current_association_verified'],False)
        self.assertEqual(result['input_sha256']['original.nc'],'source-pin')
        self.assertIn('analysis/scientific_readback.py',result['input_sha256'])

    def test_loop_corner_vectors_and_original_geometry_are_exact(self):
        raw=.1234567891234567
        vector={'eastward_m_s':raw,'northward_m_s':raw,'bilinear_weights':[raw],
                'corner_eastward_northward_m_s':[[raw,-0.0]],'cell_row_column':[2,3]}
        sample={'piece_length_m':1234.123456,'longitude_latitude':[-86.12345678912,23.12345678912],
                'tangent_azimuth_degrees':35.123456789,'along_path_m_s':raw,'vector_speed_m_s':raw,'velocity':vector}
        source={'schema':'osw.loop-durante-composite-contour-paths.v1','input_sha256':{},
                'source_contours':[[[raw,raw]]],'cases':[{'status':'unique_supported_path','components':[
                    {'coordinates_lon_lat':[[raw,raw]],'midpoint_samples':[sample]}]}]}
        result=readback.canonicalize(source);actual=result['cases'][0]['components'][0]['midpoint_samples'][0]
        self.assertEqual(actual['velocity']['corner_eastward_northward_m_s'],vector['corner_eastward_northward_m_s'])
        self.assertEqual(actual['velocity']['corner_eastward_northward_m_s'][0][1].hex(),(-0.0).hex())
        self.assertEqual(actual['velocity']['cell_row_column'],[2,3])
        self.assertEqual(result['source_contours'],source['source_contours'])
        self.assertEqual(result['cases'][0]['components'][0]['coordinates_lon_lat'],[[raw,raw]])
        self.assertLessEqual(abs(actual['piece_length_m']-sample['piece_length_m']),.0005)
        self.assertLessEqual(abs(actual['along_path_m_s']-raw),.5e-8)

    def test_unknown_schema_and_invalid_selected_values_fail(self):
        with self.assertRaisesRegex(ValueError,'No explicit'):readback.canonicalize({'schema':'new.schema'})
        for value in [math.nan,math.inf,True,'1.0']:
            with self.subTest(value=value),self.assertRaisesRegex(ValueError,'Invalid computed'):
                readback.canonicalize({'schema':'osw.observed-vector-section.v1','input_sha256':{},'maximum_position_spacing_km':value})

    def test_protocol_changes_fail_and_selected_signed_zero_is_canonical(self):
        with patch.object(readback,'PROTOCOL_SHA','0'*64),self.assertRaisesRegex(ValueError,'Changed scientific'):
            readback.dependency_pins()
        result=readback.canonicalize({'schema':'osw.observed-vector-section.v1','input_sha256':{},'maximum_position_spacing_km':-0.0})
        self.assertEqual(result['maximum_position_spacing_km'].hex(),(0.0).hex())


if __name__=='__main__':unittest.main()
