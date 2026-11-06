import copy
import json
import unittest
from pyproj import Geod
import nwasc_source_anchor_route as n


class SourceAnchorRoute(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc, cls.pins = n.verify_inputs()

    def test_source_coordinates_sign_and_order(self):
        self.assertEqual(self.doc['source_anchor_ids'], ['P1', 'P2', 'S1'])
        self.assertEqual(self.doc['coordinates_lon_lat'], [[-.5, 62], [3, 62 + 40 / 60], [4.25, 62.8]])
        self.assertEqual(self.doc['reference_period']['start_month'], '2007-08')
        self.assertEqual(self.doc['reference_period']['end_month'], '2010-07')

    def test_wgs84_distance_and_public_rounding(self):
        g = Geod(ellps='WGS84')
        expected = sum(g.inv(*a, *b)[2] for a,b in zip(n.ANCHORS,n.ANCHORS[1:])) / 1000
        self.assertAlmostEqual(self.doc['nominal_reference_path_km'], expected, places=6)
        self.assertEqual(self.doc['reported_approximate_reference_path_km'], 260)
        self.assertEqual(self.doc['reported_scenario_range_km'], [260, 270])

    def test_all_nine_probes_hold_original_anchors(self):
        cases = self.doc['scenarios']
        self.assertEqual(len(cases), 9)
        self.assertEqual({tuple(c['bend_offsets_km']) for c in cases}, {(a,b) for a in [-10,0,10] for b in [-10,0,10]})
        for case in cases:
            for i, anchor in zip([0,2,4],n.ANCHORS):
                self.assertEqual(case['coordinates_lon_lat'][i],anchor)
            self.assertGreaterEqual(case['length_km'] + 1e-6,self.doc['nominal_reference_path_km'])
            self.assertFalse(case['finer_land_contact'])
            self.assertFalse(case['coarse_land_contact'])
            self.assertFalse(any(case['rounded_geometry_land_contacts'].values()))

    def test_reference_is_not_width_axis_or_annual_range(self):
        for flag in ['physical_current_axis_admitted','physical_current_edges_admitted','physical_state_join_eligible','seasonal_playback_eligible','rank_eligible','bend_sensitivity_is_uncertainty']:
            self.assertIs(self.doc[flag],False)
        self.assertIsNone(self.doc['whole_current_length_km'])
        self.assertIsNone(self.doc['annual_length_range_km'])
        self.assertIsNone(self.doc['source_coordinate_uncertainty_km'])

    def test_frozen_catalogue_bytes_and_previous_rows_preserved(self):
        base=json.loads((n.ROOT/n.BASE).read_bytes());before=copy.deepcopy(base)
        current=n.extend_catalogue(base,self.doc)
        self.assertEqual(base,before)
        self.assertEqual([r for r in current['candidates'] if r['id']!=n.ROUTE],base['candidates'])
        self.assertEqual(len(current['candidates']),78)
        self.assertEqual(len({r['current_id'] for r in current['candidates']}),72)
        self.assertEqual(current['counts']['accepted_current_names'],102)
        self.assertEqual(current['counts']['currents_without_any_reference_card'],30)
        self.assertEqual(current['reference_route_length_order'],base['reference_route_length_order'])
        self.assertEqual(current['remaining_current_decisions'][-1]['candidate_ids'],[n.ROUTE])

    def test_checked_pins_and_exact_route_binding(self):
        for path, pin in self.pins.items():
            self.assertEqual(n.digest(path),pin,path)
        row=n.route_record(self.doc)
        self.assertEqual(row['candidate_sha256'],n.digest(n.FILE))
        self.assertEqual(row['source_ids'],['source:hansen-asar-2011',n.METHOD])
        self.assertEqual(row['comparison_group'],'osw_source_anchor_connections')
        self.assertFalse(row['rank_eligible'])
        self.assertEqual(self.doc['canonical_spatial_geometry']['coordinates'][0],n.ANCHORS[0])


if __name__=='__main__':
    unittest.main()
