import unittest
from unittest.mock import patch
import build_gulf_stream_geostrophic_path as algorithm

class TraceCapTests(unittest.TestCase):
    def test_nondivisible_distance_cap(self):
        with patch.object(algorithm, 'MAX_DISTANCE_KM', 35), patch.object(algorithm, 'sample_velocity', return_value=(-1.0,0.0)):
            result = algorithm.trace({}, {}, 36.875, 10)
        self.assertEqual(result['stop_reason'], 'distance_cap')
        self.assertEqual(result['segment_length_km'], 35)
        self.assertEqual(result['point_count'], 5)
        last = algorithm.GEOD.inv(*result['coordinates_lon_lat'][-2], *result['coordinates_lon_lat'][-1])[2] / 1000
        self.assertAlmostEqual(last, 5, places=3)

    def test_invalid_steps(self):
        for step in [0,-1,float('nan'),float('inf')]:
            with self.subTest(step=step),self.assertRaises(ValueError):
                algorithm.trace({}, {}, 36.875, step)
