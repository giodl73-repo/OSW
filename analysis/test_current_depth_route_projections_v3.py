"""Verify date-line geometry, site periods and selected-core semantics."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_route_projections_v2 as previous
import build_current_depth_route_projections_v3 as depth


class PacificEUCSiteConnectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.p=cls.data['projections'][-1]
        cls.operator=json.loads((depth.ROOT/depth.OPERATOR).read_bytes());cls.case=cls.operator['case']
        cls.source=json.loads((depth.ROOT/cls.operator['depth_register_file']).read_bytes());cls.refs={r['id']:r for r in cls.source['evidence']}

    def test_previous_four_scenarios_preserved_and_catalog_refs_refreshed(self):
        prior=previous.build();self.assertEqual(self.data['projections'][:4],prior['projections'])
        self.assertEqual(len(self.data['records']),111)
        for record,source in zip(self.data['records'],self.source['records']):
            self.assertEqual(record['entity_id'],source['entity_id']);self.assertEqual(record['depth_reference_ids'],source['depth_reference_ids'])
        self.assertEqual(self.data['counts'],{'catalog_identities':111,'identities_with_regional_projection_scenarios':5,'identities_not_yet_projected':106,'regional_projection_scenarios':5,'source_anchor_references':14,'new_depth_measurements':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0})

    def test_anchors_keep190_155_105_75_without_ten_metre_rounding(self):
        self.assertEqual([a['approximate_depth_descriptor_m'] for a in self.p['anchors']],[190,155,105,75])
        anchored=[s for s in self.p['samples'] if s['status']=='source_anchor_at_nominal_observing_site']
        self.assertEqual([s['projected_depth_descriptor_m'] for s in anchored],[190,155,105,75])
        self.assertEqual(self.p['metric'],'projected_comparison_selected_core_level_descriptor')

    def test_eastward_date_line_crossing_uses85_degrees_not275(self):
        points=[a['nominal_lon_lat'] for a in self.case['anchors']]
        legs,unwrapped=depth.longitude_legs(points)
        self.assertEqual(unwrapped,[165,190,220,250])
        self.assertAlmostEqual(legs[-1][1],9462.157,places=3)
        self.assertAlmostEqual(self.p['route_length_km'],9462.157,places=3)
        for sample in self.p['samples']:
            lon,lat=sample['editorial_route_lon_lat'];self.assertEqual(lat,0)
            self.assertTrue(lon>=165 or lon<=-110)
        for bad in [[[165,0],[-170,1]],[[-170,0],[165,0]],[[165,0],[165,0]],[[float('nan'),0],[-170,0]]]:
            with self.assertRaises(ValueError):depth.longitude_legs(bad)

    def test_per_site_gapped_windows_follow_adjacent_sample_provenance(self):
        expected=[{'start':'1996-01-01','end':'2007-12-31'},{'start':'1995-01-01','end':'2005-12-31'},{'start':'1997-01-01','end':'2010-12-31'},{'start':'1996-01-01','end':'2005-12-31'}]
        self.assertEqual([a['source_record_period'] for a in self.p['anchors']],expected)
        self.assertIsNone(self.p['common_record_period']);self.assertFalse(self.p['common_period_reanalysis_performed'])
        ids=[a['reference_id'] for a in self.p['anchors']]
        adjacent=[ids[i:i+2] for i in range(3)]
        for sample in self.p['samples']:
            self.assertEqual(set(sample['source_reference_ids']),set(sample['source_record_periods']))
            if sample['status'].startswith('assumed_'):self.assertIn(sample['source_reference_ids'],adjacent)
            for ref,period in sample['source_record_periods'].items():self.assertEqual(period,self.refs[ref]['source_record_period'])

    def test_comparison_selection_site_and_period_mutations_rejected(self):
        ref_id=self.case['anchors'][0]['reference_id']
        for key,value in [('core_definition',{'kind':'instantaneous_argmax'}),('approximate_value_m',200),('source_record_period',{'start':'1995-01-01','end':'2010-12-31'}),('source_record_period_has_gaps',False),('section_longitude_degrees_east',160),('metric','reported_vertical_extent')]:
            refs=copy.deepcopy(self.refs);refs[ref_id][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):depth.validate_case(self.case,refs)
        for key,value in [('geometry_role','selected_whole_current_route'),('display_depth_rounding_m',10),('interpolation','extrapolate_to_south_america')]:
            case=copy.deepcopy(self.case);case[key]=value
            with self.subTest(case_key=key),self.assertRaises(ValueError):depth.validate_case(case,self.refs)

    def test_connector_does_not_replace_reported14000km_current_extent(self):
        lengths=json.loads((depth.ROOT/'research/current-length-estimate-register-v1.json').read_bytes())
        record=next(r for r in lengths['records'] if r['entity_id']=='current:pacific-equatorial-undercurrent')
        self.assertEqual(record['length_estimate_km'],14000);self.assertIsNone(record['selected_route_id'])
        self.assertIsNone(self.p['full_current_length_km'])
        self.assertEqual(self.p['geometry_role'],'nominal_observing_site_connector_not_selected_whole_current_route')
        self.assertEqual(self.p['supported_reference_distance_interval_km'],[0.0,9462.157])
        self.assertIn('not full Pacific EUC coverage',self.p['fraction_interpretation'])

    def test_no_common_season_thickness_volume_or_synoptic_profile(self):
        self.assertFalse(any(self.p['eligibility'].values()));self.assertFalse(self.p['synoptic_full_route'])
        for key in ['physical_lower_boundary_profile','physical_thickness_profile','volume_km3','annual_depth_range_m','calendar_months','campaign_window']:self.assertIsNone(self.p[key])
        for sample in self.p['samples']:
            self.assertIsNone(sample['physical_thickness_m']);self.assertIsNone(sample['depth_uncertainty_m']);self.assertFalse(sample['volume_eligible'])

    def test_json_csv_reproduce_with_per_sample_periods_and_geometry_role(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        raw=depth.csv_bytes(self.data);self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),raw)
        rows=[r for r in csv.DictReader(io.StringIO(raw.decode('utf8'))) if r['entity_id']=='current:pacific-equatorial-undercurrent']
        self.assertEqual(len(rows),len(self.p['samples']))
        for row,sample in zip(rows,self.p['samples']):
            self.assertEqual(json.loads(row['source_record_periods']),sample['source_record_periods'])
            self.assertEqual(row['common_record_period'],'');self.assertEqual(row['geometry_role'],self.p['geometry_role'])
            self.assertEqual(row['metric'],self.p['metric'])


if __name__=='__main__':unittest.main()
