import unittest
from derive_malvinas_bathymetry_screen_v1 import cutoff,screen_rows,parse_grid,grid_index,ORIGIN_LON,STEP


class BathymetryScreenTests(unittest.TestCase):
    def test_point_bed_and_sidelobe_limits_are_distinct(self):
        self.assertEqual(cutoff(200,'bed_only'),192)
        self.assertAlmostEqual(cutoff(200,'sidelobe85'),162.9)
        self.assertIsNone(cutoff(None,'bed_only'));self.assertIsNone(cutoff(5,'bed_only'))

    def test_margin_equality_and_no_bottom_inference(self):
        rows=[[{'depth':192,'v':20},{'depth':192.01,'v':30},{'depth':210,'v':40}]]
        bed=[{'point_depth_m':200,'footprint_shallowest_depth_m':150}]
        result,counts=screen_rows(rows,bed,'bed_only')
        self.assertEqual(result[0][0]['v'],20);self.assertIsNone(result[0][1]['v'])
        self.assertEqual(counts['native_samples_below_point_grid_bed'],1)
        self.assertEqual(rows[0][1]['v'],30)

    def test_shallower_footprint_masks_more_than_point_sidelobe(self):
        rows=[[{'depth':150,'v':20}]];bed=[{'point_depth_m':200,'footprint_shallowest_depth_m':150}]
        self.assertEqual(screen_rows(rows,bed,'point_sidelobe85')[0][0][0]['v'],20)
        self.assertIsNone(screen_rows(rows,bed,'footprint_sidelobe85')[0][0][0]['v'])

    def test_existing_unknown_velocities_remain_unknown(self):
        rows=[[{'depth':20,'v':None}]];bed=[{'point_depth_m':200,'footprint_shallowest_depth_m':150}]
        out,counts=screen_rows(rows,bed,'bed_only');self.assertIsNone(out[0][0]['v']);self.assertEqual(counts['velocity_samples_excluded_by_screen'],0)

    def test_ascii_shape_and_coordinates_are_strict(self):
        raw=b'elevation.elevation[2][2]\n[0], -100, -200\n[1], -300, -400\n\nelevation.lat[2]\n-46, -45\n\nelevation.lon[2]\n-60, -59\n'
        grid,lat,lon=parse_grid(raw,'elevation',2,2)
        self.assertEqual(grid,[[-100,-200],[-300,-400]]);self.assertEqual(lat,[-46,-45])
        with self.assertRaises(ValueError):parse_grid(raw.replace(b'[1],',b'[2],'),'elevation',2,2)
        with self.assertRaises(ValueError):parse_grid(raw,'tid',2,2)

    def test_nearest_cell_ties_go_east(self):
        self.assertEqual(grid_index(ORIGIN_LON+100*STEP,ORIGIN_LON),100)
        self.assertEqual(grid_index(ORIGIN_LON+100.6*STEP,ORIGIN_LON),101)


if __name__=='__main__':unittest.main()
