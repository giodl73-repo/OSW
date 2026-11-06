"""Verify source anchors, distance interpolation and unsupported route gaps."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_route_projections_v1 as depth


class RouteDepthProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.p=cls.data['projections'][0]
        cls.operator=json.loads((depth.ROOT/depth.OPERATOR).read_bytes())
        cls.source=json.loads((depth.ROOT/cls.operator['depth_register_file']).read_bytes())
        cls.refs={r['id']:r for r in cls.source['evidence']}
        routes=json.loads((depth.ROOT/cls.operator['route_file']).read_bytes())
        cls.route=next(r for r in routes['records'] if r['id']==cls.p['route_id'])

    def test_catalog_inventory_and_source_ownership_preserved(self):
        self.assertEqual(len(self.data['records']),111)
        for record,source in zip(self.data['records'],self.source['records']):
            self.assertEqual(record['entity_id'],source['entity_id'])
            self.assertEqual(record['depth_reference_ids'],source['depth_reference_ids'])
        self.assertEqual(self.data['counts'],{'catalog_identities':111,'identities_with_regional_projection_scenarios':1,'identities_not_yet_projected':110,'regional_projection_scenarios':1,'source_anchor_references':2,'new_depth_measurements':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0})

    def test_geodesic_latitude_gate_maps_to_editorial_route_only(self):
        legs=depth.route_legs(self.route['coordinates_lon_lat'])
        distance,point=depth.latitude_gate(legs,10)
        self.assertAlmostEqual(point[1],10,places=10)
        self.assertGreater(distance,1400);self.assertLess(distance,1700)
        self.assertGreater(self.p['route_length_km'],distance)
        self.assertAlmostEqual(self.p['route_length_km'],1787.691,places=3)
        for latitude in [7,23]:
            with self.assertRaises(ValueError):depth.latitude_gate(legs,latitude)

    def test_interpolate_in_distance_and_keep_unknown_beyond_anchors(self):
        anchors=[{'distance_km':100,'approximate_extent_depth_m':400},{'distance_km':700,'approximate_extent_depth_m':200}]
        self.assertEqual(depth.interpolate(100,anchors),400)
        self.assertEqual(depth.interpolate(400,anchors),300)
        self.assertEqual(depth.interpolate(700,anchors),200)
        self.assertIsNone(depth.interpolate(0,anchors));self.assertIsNone(depth.interpolate(701,anchors))
        samples=self.p['samples'];self.assertEqual(samples[0]['projected_extent_descriptor_m'],400)
        self.assertIsNone(samples[-1]['projected_extent_descriptor_m'])
        self.assertEqual(samples[-1]['status'],'unsupported_no_extrapolation')
        anchored=[s for s in samples if s['status']=='source_anchor_mapped_to_editorial_route']
        self.assertEqual([s['projected_extent_descriptor_m'] for s in anchored],[400,200])
        for s in samples:
            if s['status']=='assumed_linear_interpolation':self.assertTrue(200<=s['projected_extent_descriptor_m']<=400)
            if s['status']=='unsupported_no_extrapolation':self.assertEqual(s['source_reference_ids'],[])

    def test_reversed_route_preserves_mapping_and_ambiguous_route_rejected(self):
        points=self.route['coordinates_lon_lat'];forward=depth.route_legs(points);reverse=depth.route_legs(list(reversed(points)))
        distance,point=depth.latitude_gate(forward,10);opposite,point2=depth.latitude_gate(reverse,10)
        self.assertAlmostEqual(distance+opposite,forward[-1][1],places=7)
        for a,b in zip(point,point2):self.assertAlmostEqual(a,b,places=8)
        for bad in [[[70,10],[71,12],[72,11]],[[70,10],[70,10]],[[70,10],[float('nan'),11]]]:
            with self.assertRaises(ValueError):depth.route_legs(bad)

    def test_source_case_mutations_rejected(self):
        reference_id=self.operator['case']['reference_ids'][0]
        for key,value in [('metric','core_depth'),('approximate_value_m',500),('section_latitude_degrees_north',23),('campaign_window',{'start_month':'2017-01','end_month':'2017-02'}),('phase_label','southwest_monsoon'),('entity_id','current:somali'),('thickness_m',400),('reference_route_projection_eligible',False)]:
            refs=copy.deepcopy(self.refs);refs[reference_id][key]=value
            with self.subTest(field=key),self.assertRaises(ValueError):depth.validate(self.operator,refs,self.route)

    def test_no_geometry_volume_or_annual_admission(self):
        for key,value in [('metric','physical_thickness'),('annual_depth_range_m',[200,400]),('uncertainty_m',100),('extrapolation','constant_endpoint_depth')]:
            operator=copy.deepcopy(self.operator);operator[key]=value
            with self.subTest(field=key),self.assertRaises(ValueError):depth.validate(operator,self.refs,self.route)
        for flag in self.operator['eligibility']:
            operator=copy.deepcopy(self.operator);operator['eligibility'][flag]=True
            with self.subTest(flag=flag),self.assertRaises(ValueError):depth.validate(operator,self.refs,self.route)
        self.assertIsNone(self.p['physical_thickness_profile']);self.assertIsNone(self.p['volume_km3'])
        self.assertFalse(self.p['synoptic_full_route']);self.assertFalse(self.p['exact_section_dates_known'])
        for sample in self.p['samples']:
            self.assertIsNone(sample['physical_thickness_m']);self.assertFalse(sample['volume_eligible'])

    def test_display_rounding_status_and_csv_reproduce(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        raw=depth.csv_bytes(self.data);self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),raw)
        rows=list(csv.DictReader(io.StringIO(raw.decode('utf8'))))
        self.assertEqual(len(rows),len(self.p['samples']))
        self.assertEqual(rows[-1]['projected_extent_descriptor_m'],'')
        self.assertEqual(rows[-1]['status'],'unsupported_no_extrapolation')
        for row in rows:
            self.assertEqual(row['metric'],'projected_reported_vertical_extent_descriptor')
            self.assertEqual(row['volume_eligible'],'False')
            if row['projected_extent_descriptor_m']:self.assertEqual(float(row['projected_extent_descriptor_m'])%10,0)


if __name__=='__main__':unittest.main()
