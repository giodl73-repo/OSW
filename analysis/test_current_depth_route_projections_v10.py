import copy,csv,io,json
import unittest
import build_current_depth_route_projections_v9 as previous
import build_current_depth_route_projections_v10 as profile


class BrazilHistoricalConnectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=profile.build();cls.p=cls.data['projections'][-1]
        cls.op=json.loads((profile.ROOT/profile.OPERATOR).read_bytes())
        cls.refs={r['id']:r for r in json.loads((profile.ROOT/cls.op['depth_register_file']).read_bytes())['evidence']}

    def test_previous_eleven_profiles_and_volume_inventory_preserved(self):
        prior=previous.build();self.assertEqual(self.data['projections'][:11],prior['projections'])
        self.assertEqual(self.data['counts'],{'catalog_identities':111,'identities_with_regional_projection_scenarios':11,'identities_not_yet_projected':100,'regional_projection_scenarios':12,'source_anchor_references':35,'new_depth_measurements':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0,'regional_reference_geometry_volume_scenarios':2})
        self.assertEqual(self.data['regional_volume_scenario_file'],prior['regional_volume_scenario_file'])

    def test_author_extents_at_nominal_source_sites_not_current_axis(self):
        self.assertEqual([(a['source_mooring_id'],a['reported_extent_m']) for a in self.p['anchors']],[('MARLIM',350),('DFBS',400),('C3',550),('W333',850)])
        self.assertEqual(self.p['geometry_role'],'nominal_source_mooring_connector_not_current_axis');self.assertFalse(self.p['whole_current_length_replaced'])
        for a in self.p['anchors']:
            sample=next(s for s in self.p['samples'] if s['distance_along_reference_route_km']==a['distance_km'])
            self.assertEqual(sample['projected_depth_descriptor_m'],a['reported_extent_m']);self.assertEqual(sample['nominal_reference_connector_lon_lat'],a['nominal_lon_lat'])

    def test_different_site_periods_remain_per_sample_not_common_period(self):
        self.assertEqual([a['record_month_bounds'] for a in self.p['anchors']],[['1992-02','1992-12'],['2003-01','2004-05'],['1992-12','1994-03'],['1991-01','1992-11']])
        self.assertIsNone(self.p['common_record_period']);self.assertFalse(self.p['simultaneous_record_period_established'])
        for sample in self.p['samples']:
            self.assertIsNone(sample['common_record_period']);self.assertEqual([p['reference_id'] for p in sample['source_record_periods']],sample['source_reference_ids'])
            for p in sample['source_record_periods']:self.assertEqual(p['record_month_bounds'],self.refs[p['reference_id']]['source_record_month_bounds'])

    def test_dfbs_filter_leaves_both_adjacent_segments_unknown_without_bridging(self):
        c3=self.p['anchors'][2]['distance_km']
        affected=[s for s in self.p['samples'] if 0<s['distance_along_reference_route_km']<c3]
        self.assertGreater(len(affected),2)
        for sample in affected:
            self.assertIsNone(sample['depth_descriptor_excluding_flagged_mean_m']);self.assertIn('includes_source_low_statistical_significance_DFBS',sample['source_mean_reliability_flags'])
        for a in [self.p['anchors'][0],self.p['anchors'][2],self.p['anchors'][3]]:
            s=next(s for s in self.p['samples'] if s['distance_along_reference_route_km']==a['distance_km']);self.assertEqual(s['depth_descriptor_excluding_flagged_mean_m'],a['reported_extent_m'])
        case=copy.deepcopy(self.op['case']);case['anchors'].pop(1)
        with self.assertRaises(ValueError):profile.validate_case(case,self.refs)

    def test_piecewise_interpolation_and_outside_support_unknown(self):
        a,b=self.p['anchors'][2:]
        value,used,status=profile.descriptor_at_distance(self.p['anchors'],(a['distance_km']+b['distance_km'])/2)
        self.assertEqual(value,700);self.assertEqual([r['reference_id'] for r in used],[a['reference_id'],b['reference_id']]);self.assertEqual(status,'assumed_linear_between_different_site_record_means')
        for distance in [-1,self.p['reference_connector_length_km']+1]:self.assertIsNone(profile.descriptor_at_distance(self.p['anchors'],distance)[0])

    def test_cruise_depth_date_reliability_and_sampling_substitutions_rejected(self):
        for index,key,value in [(2,'reported_extent_m',450),(3,'reported_extent_m',885),(1,'source_mean_reliability','statistically_significant'),(0,'record_month_bounds',['2009-01','2009-12'])]:
            case=copy.deepcopy(self.op['case']);case['anchors'][index][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):profile.validate_case(case,self.refs)

    def test_no_thickness_uncertainty_annual_envelope_or_volume_admission(self):
        self.assertFalse(any(self.p['eligibility'].values()));self.assertIsNone(self.p['physical_thickness_m']);self.assertIsNone(self.p['uncertainty_m']);self.assertIsNone(self.p['annual_range_m']);self.assertIsNone(self.p['calendar_months'])
        for s in self.p['samples']:self.assertIsNone(s['depth_uncertainty_m']);self.assertIsNone(s['physical_thickness_m']);self.assertFalse(s['volume_eligible'])
        register=json.loads((profile.ROOT/self.op['depth_register_file']).read_bytes());self.assertEqual(register['counts']['depth_references'],347)
        for r in self.data['records']:self.assertEqual(r['depth_reference_ids'],next(a['depth_reference_ids'] for a in register['records'] if a['entity_id']==r['entity_id']))

    def test_json_csv_preserve_old_cells_periods_and_support_filter(self):
        self.assertEqual(self.data,json.loads((profile.ROOT/profile.OUTPUT).read_bytes()))
        raw=profile.csv_bytes(self.data);self.assertEqual(raw,(profile.ROOT/profile.CSV).read_bytes())
        old=list(csv.DictReader(io.StringIO((profile.ROOT/previous.CSV).read_text(encoding='utf8'))));new=list(csv.DictReader(io.StringIO(raw.decode('utf8'))))
        for a,b in zip(old,new):self.assertEqual(a,{k:b[k] for k in a})
        for r,s in zip(new[len(old):],self.p['samples']):
            self.assertEqual(json.loads(r['source_record_periods']),s['source_record_periods']);self.assertEqual(json.loads(r['source_mean_reliability_flags']),s['source_mean_reliability_flags'])
            if s['depth_descriptor_excluding_flagged_mean_m'] is None:self.assertEqual(r['depth_descriptor_excluding_flagged_mean_m'],'')


if __name__=='__main__':unittest.main()
