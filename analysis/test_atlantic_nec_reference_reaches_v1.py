import copy
import json
import unittest
import atlantic_nec_reference_reaches_v1 as reaches


class NECReferences(unittest.TestCase):
    def test_interior_gate_cannot_extend_or_interpolate_support(self):
        path=[[-30,17],[-40,14],[-50,13],[-55,13]]
        self.assertEqual(reaches.truncate(path,-50),path[:3])
        for gate in [-45,-60]:
            with self.assertRaises(ValueError):reaches.truncate(path,gate)

    def test_all36_scenarios_retained_and_nominal_reproduced(self):
        source=json.loads((reaches.ROOT/reaches.INPUT).read_bytes());before=copy.deepcopy(source)
        out=reaches.prepare(source);self.assertEqual(source,before)
        cases=out['editorial_sensitivity_cases'];self.assertEqual(len(cases),36)
        self.assertEqual(len({(r['route_id'],r['west_gate'],r['uniform_shift_degrees'],r['interior_shift_degrees']) for r in cases}),36)
        for route in out['routes']:
            nominal=next(r for r in cases if r['route_id']==route['id'] and r['west_gate']==-55 and r['uniform_shift_degrees']==r['interior_shift_degrees']==0)
            self.assertEqual(nominal['coordinates_lon_lat'],route['coordinates_lon_lat'])
            self.assertEqual(nominal['reference_length_km'],route['calculated_reference_length_km'])
            self.assertFalse(route['reference_route_ordering_eligible'])

    def test_wrong_current_family_or_physical_promotion_refused(self):
        source=json.loads((reaches.ROOT/reaches.INPUT).read_bytes())
        for name in ['atlantic-south-equatorial','north-equatorial']:
            bad=copy.deepcopy(source);bad['current_id']=name
            with self.assertRaises(ValueError):reaches.prepare(bad)
        bad=copy.deepcopy(source);bad['annual_length_range_km']=[2600,2900]
        with self.assertRaises(ValueError):reaches.prepare(bad)


if __name__=='__main__':unittest.main()
