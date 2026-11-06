"""Derived array-distance readback leaves original source fields unchanged."""
import unittest
from unittest.mock import patch
import numpy as np
from pyproj import Geod
import check_eac_100m_source as producer


class EacArrayReadbackTests(unittest.TestCase):
    def test_only_declared_geometry_fields_have_distance_readback(self):
        report=producer.build();_,_,arrays=producer.load()
        points=list(zip(arrays['LONGITUDE'].tolist(),arrays['LATITUDE'].tolist()))
        geod=Geod(ellps='WGS84')
        segments=[geod.inv(*a,*b)[2] for a,b in zip(points,points[1:])]
        geometry=report['fixed_source_geometry']
        self.assertEqual(geometry['longitude_latitude_points'],[list(p) for p in points])
        self.assertEqual(geometry['bottom_depth_m'],arrays['BOTTOM_DEPTH'].tolist())
        expected=[0.,*np.cumsum(segments).tolist()]
        self.assertEqual(geometry['distance_from_first_grid_point_m'],[round(v,3) for v in expected])
        self.assertTrue(all(abs(a-b)<=.0005 for a,b in zip(expected,geometry['distance_from_first_grid_point_m'])))
        self.assertEqual(geometry['grid_segment_distance_m_range'],[round(min(segments),3),round(max(segments),3)])
        self.assertEqual(geometry['source_array_polyline_length_km'],round(sum(segments)/1000,6))
        for name in producer.FIELDS:
            values=arrays[name][np.isfinite(arrays[name])]
            self.assertEqual(report['fields'][name]['minimum_finite'],float(values.min()))
            self.assertEqual(report['fields'][name]['maximum_finite'],float(values.max()))
        self.assertFalse(report['width_measurement_admitted'])
        self.assertIsNone(report['annual_width_range_km'])

    def test_changed_protocol_rejects(self):
        with patch.object(producer,'READBACK_SHA','0'*64),self.assertRaisesRegex(ValueError,'readback protocol'):
            producer.build()


if __name__=='__main__':unittest.main()
