"""Guard threshold-core span units, source statistics and partial route support."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_route_projections_v4 as previous
import build_current_depth_route_projections_v5 as depth


class IndianSEUCCoreSpanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.p=cls.data['projections'][-1]
        cls.operator=json.loads((depth.ROOT/depth.OPERATOR).read_bytes());cls.case=cls.operator['case']
        cls.source=json.loads((depth.ROOT/cls.operator['depth_register_file']).read_bytes());cls.refs={r['id']:r for r in cls.source['evidence']}
        routes=json.loads((depth.ROOT/cls.case['route_file']).read_bytes());cls.route=next(r for r in routes['records'] if r['id']==cls.case['route_id'])

    def test_previous_six_preserved_and_seventh_distance_typed_scenario(self):
        self.assertEqual(self.data['projections'][:6],previous.build()['projections'])
        self.assertEqual(self.data['counts'],{'catalog_identities':111,'identities_with_regional_projection_scenarios':7,'identities_not_yet_projected':104,'regional_projection_scenarios':7,'source_anchor_references':18,'new_depth_measurements':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0})

    def test_source_span_anchors_preserved_without_depth_field_or_rounding(self):
        self.assertEqual([a['source_core_vertical_span_m'] for a in self.p['anchors']],[1719,57])
        self.assertEqual(self.p['vertical_datum'],'not_applicable_thickness_distance')
        self.assertEqual(self.p['metric'],'projected_threshold_core_vertical_span')
        anchored=[s for s in self.p['samples'] if s['status']=='source_threshold_core_span_anchor_mapped_to_reference_route']
        self.assertEqual([s['projected_core_vertical_span_m'] for s in anchored],[1719,57])
        for sample in self.p['samples']:self.assertIsNone(sample['projected_depth_descriptor_m'])

    def test_longitude_gates_map_approximate_context_to_editorial_drawing(self):
        legs=depth.route_legs(self.route['coordinates_lon_lat'])
        for longitude in [74,95]:
            distance,point=depth.longitude_gate(legs,longitude)
            self.assertAlmostEqual(point[0],longitude,places=10)
            self.assertTrue(0<distance<legs[-1][1])
        self.assertEqual(self.p['supported_reference_distance_interval_km'],[1544.135,3854.407])
        for longitude in [59,106]:
            with self.assertRaises(ValueError):depth.longitude_gate(legs,longitude)
        for anchor in self.p['anchors']:self.assertEqual(anchor['source_location_precision'],'approximate_longitude_from_prose')

    def test_nonlocal_median_and_observed_core_depth_band_are_not_anchors(self):
        median='indian-seuc-chen-2022-core-thickness-longitude-median'
        self.assertEqual(self.p['excluded_nonlocal_statistic_reference_ids'],[median])
        self.assertNotIn(median,self.p['source_reference_ids'])
        self.assertNotIn('indian-seuc-chen-2022-observed-core-depth-band',self.p['source_reference_ids'])
        case=copy.deepcopy(self.case);case['anchors'][0]['reference_id']=median
        with self.assertRaises(ValueError):depth.validate_case(case,self.refs)

    def test_threshold_product_phase_and_distance_datum_cannot_change(self):
        ref_id=self.case['anchors'][0]['reference_id']
        for key,value in [('metric','core_depth'),('vertical_datum','local_sea_surface_positive_down'),('velocity_threshold_m_s',0.01),('velocity_threshold_operator','>='),('calendar_months',[9,10,11]),('model_product','ORAS5'),('climatology_years',[2001,2015])]:
            refs=copy.deepcopy(self.refs);refs[ref_id][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):depth.validate_case(self.case,refs)

    def test_unsupported_route_null_and_intermediate_spans_within_source_enclosure(self):
        self.assertIsNone(self.p['samples'][0]['projected_core_vertical_span_m'])
        self.assertIsNone(self.p['samples'][-1]['projected_core_vertical_span_m'])
        for sample in self.p['samples']:
            if sample['status']=='unsupported_no_extrapolation':
                self.assertIsNone(sample['projected_core_vertical_span_m']);self.assertEqual(sample['source_reference_ids'],[])
            else:self.assertTrue(57<=sample['projected_core_vertical_span_m']<=1719)

    def test_seasonal_core_span_is_not_contiguous_full_flow_thickness_or_volume(self):
        self.assertEqual(self.p['calendar_months'],[3,4,5]);self.assertEqual(self.p['climatology_years'],[2001,2018])
        self.assertFalse(any(self.p['eligibility'].values()))
        self.assertIsNone(self.p['physical_lower_boundary_profile']);self.assertIsNone(self.p['physical_thickness_profile']);self.assertIsNone(self.p['volume_km3'])
        for sample in self.p['samples']:self.assertIsNone(sample['physical_thickness_m']);self.assertIsNone(sample['core_span_uncertainty_m'])

    def test_json_csv_distinguish_span_and_absolute_depth_columns(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        raw=depth.csv_bytes(self.data);self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),raw)
        rows=[r for r in csv.DictReader(io.StringIO(raw.decode('utf8'))) if r['entity_id']==self.p['entity_id']]
        self.assertEqual(len(rows),len(self.p['samples']))
        for row,sample in zip(rows,self.p['samples']):
            self.assertEqual(row['projected_depth_descriptor_m'],'')
            self.assertEqual(row['vertical_datum'],'not_applicable_thickness_distance')
            self.assertEqual(json.loads(row['calendar_months']),[3,4,5])
            if sample['projected_core_vertical_span_m'] is not None:self.assertEqual(float(row['projected_core_vertical_span_m']),sample['projected_core_vertical_span_m'])


if __name__=='__main__':unittest.main()
