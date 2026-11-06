import copy
import json
import unittest
import atlantic_nsec_reference_reaches_v1 as reaches


class ReachTests(unittest.TestCase):
    def test_wgs84_equatorial_arc_and_reverse_invariance(self):
        self.assertAlmostEqual(reaches.length_km([[0,0],[-1,0]]),111.319490793,places=8)
        path=[[0,2],[-10,2],[-20,3]]
        self.assertAlmostEqual(reaches.length_km(path),reaches.length_km(path[::-1]),places=8)

    def test_gates_must_be_supported_and_do_not_extend_geometry(self):
        path=[[0,2],[-10,2],[-20,3]]
        self.assertEqual(reaches.truncate(path,-10),path[:2])
        for west in [-15,-25]:
            with self.assertRaises(ValueError):reaches.truncate(path,west)
        for bad in [[[0,float('nan')],[-1,0]],[[0,91],[-1,0]]]:
            with self.assertRaises(ValueError):reaches.length_km(bad)

    def test_preparation_retains_scope_and_all_independent_gate_choices(self):
        source=json.loads((reaches.ROOT/reaches.INPUT).read_bytes())
        result=reaches.prepare(source)
        self.assertEqual(len(result['routes']),2)
        self.assertEqual(len(result['editorial_sensitivity_cases']),54)
        self.assertEqual(len({(r['route_id'],r['west_gate'],r['uniform_shift_degrees'],r['interior_shift_degrees']) for r in result['editorial_sensitivity_cases']}),54)
        self.assertTrue(all(r['coordinates_lon_lat'][-1][0]==-35 for r in result['routes']))
        self.assertFalse(any(result['eligibility'].values()))
        bad=copy.deepcopy(source);bad['annual_length_range_km']=[3000,4000]
        with self.assertRaises(ValueError):reaches.prepare(bad)
        bad=copy.deepcopy(source);bad['current_id']='atlantic-north-equatorial'
        with self.assertRaises(ValueError):reaches.prepare(bad)


if __name__=='__main__':unittest.main()
