"""A branch section profile must not invent map geometry or physical thickness."""
import copy,csv,io,json
import unittest
import build_current_depth_route_projections_v6 as previous
import build_current_depth_route_projections_v7 as profile


class PCUCLatitudeProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=profile.build();cls.p=cls.data['projections'][-1]
        cls.op=json.loads((profile.ROOT/profile.OPERATOR).read_bytes())
        cls.refs={r['id']:r for r in json.loads((profile.ROOT/cls.op['depth_register_file']).read_bytes())['evidence']}

    def test_previous_eight_records_and_volume_scenario_preserved(self):
        prior=previous.build();self.assertEqual(self.data['projections'][:8],prior['projections'])
        self.assertEqual(self.data['counts'],{'catalog_identities':111,'identities_with_regional_projection_scenarios':9,'identities_not_yet_projected':102,'regional_projection_scenarios':9,'source_anchor_references':26,'new_depth_measurements':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0,'regional_reference_geometry_volume_scenarios':1})
        self.assertEqual(self.data['regional_volume_scenario_file'],prior['regional_volume_scenario_file'])

    def test_six_section_isotach_depths_not_core_depths_or_pv_stars(self):
        self.assertEqual([(a['section_name'],a['section_latitude_degrees_north'],a['approximate_depth_descriptor_m']) for a in self.p['anchors']],[('Punta Falsa',-6,240),('Chimbote',-9.4,280),('Callao',-12.1,310),('Pisco',-14,470),('San Juan',-15.7,550),('Arica',-18.6,620)])
        for a in self.p['anchors']:
            self.assertEqual(a['source_context']['boundary_definition']['speed_m_s'],.02)
            self.assertFalse(a['source_context']['potential_vorticity_prediction_used'])

    def test_piecewise_latitude_interpolation_and_exact_anchors(self):
        anchors=self.p['anchors']
        value,refs,status=profile.interpolate_latitude(anchors,-13.05)
        self.assertEqual(value,390);self.assertEqual(refs,[anchors[2]['reference_id'],anchors[3]['reference_id']])
        self.assertEqual(status,'assumed_linear_in_source_section_latitude')
        for a in anchors:
            value,refs,status=profile.interpolate_latitude(anchors,a['section_latitude_degrees_north'])
            self.assertEqual(value,a['approximate_depth_descriptor_m']);self.assertEqual(refs,[a['reference_id']]);self.assertEqual(status,'source_reported_section_anchor')

    def test_extrapolated_sections_stay_unknown(self):
        unknown=[s for s in self.p['samples'] if s['projected_depth_descriptor_m'] is None]
        self.assertEqual([s['section_latitude_degrees_north'] for s in unknown],[-5,-19,-20])
        for s in unknown:self.assertEqual(s['source_reference_ids'],[])
        self.assertIsNone(profile.interpolate_latitude(self.p['anchors'],-30)[0])
        with self.assertRaises(ValueError):profile.interpolate_latitude(list(reversed(self.p['anchors'])),-10)

    def test_section_latitude_does_not_invent_longitude_distance_or_thickness(self):
        self.assertIsNone(self.p['route_id']);self.assertIsNone(self.p['route_length_km'])
        self.assertEqual(self.p['coordinate_kind'],'source_cross_section_latitude_not_geographic_point')
        for s in self.p['samples']:
            self.assertIsNone(s['longitude']);self.assertIsNone(s['distance_along_reference_route_km']);self.assertIsNone(s['physical_thickness_m']);self.assertIsNone(s['depth_uncertainty_m']);self.assertFalse(s['volume_eligible'])
        self.assertFalse(any(self.p['eligibility'].values()))

    def test_branch_model_period_and_definition_mutations_fail(self):
        for field,value in [('source_branch','peru_coastal_current'),('entity_id','current:peru-oceanic-current')]:
            changed=copy.deepcopy(self.op['case']);changed[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):profile.validate_case(changed,self.refs)
        for field,value in [('approximate_value_m',340),('model_analysis_years',[1993,2022]),('potential_vorticity_prediction_used',True),('source_branch','peru_coastal_current')]:
            changed=copy.deepcopy(self.op['case']);changed['anchors'][1]['source_context'][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):profile.validate_case(changed,self.refs)
        self.assertEqual(self.p['model_analysis_years'],[3,10]);self.assertFalse(self.p['model_years_are_calendar_years']);self.assertIsNone(self.p['calendar_months'])

    def test_record_ownership_updates_to_latest_register_without_system_scalar(self):
        current=next(r for r in self.data['records'] if r['entity_id']=='current:peru-humboldt')
        self.assertIn(self.p['id'],current['projection_ids'])
        self.assertEqual(self.p['source_branch'],'peru_chile_undercurrent');self.assertFalse(self.p['whole_current_representative'])
        register=json.loads((profile.ROOT/self.op['depth_register_file']).read_bytes())
        for r in self.data['records']:
            source=next(s for s in register['records'] if s['entity_id']==r['entity_id'])
            self.assertEqual(r['depth_reference_ids'],source['depth_reference_ids'])

    def test_json_csv_and_prior_quantity_cells_reproduce(self):
        self.assertEqual(self.data,json.loads((profile.ROOT/profile.OUTPUT).read_bytes()))
        raw=profile.csv_bytes(self.data);self.assertEqual(raw,(profile.ROOT/profile.CSV).read_bytes())
        old=list(csv.DictReader(io.StringIO((profile.ROOT/previous.CSV).read_text(encoding='utf8'))));new=list(csv.DictReader(io.StringIO(raw.decode('utf8'))))
        for a,b in zip(old,new):self.assertEqual(a,{k:b[k] for k in a})
        added=new[len(old):];self.assertEqual(len(added),len(self.p['samples']))
        for row in added:
            self.assertEqual(row['longitude'],'');self.assertEqual(row['distance_along_reference_route_km'],'');self.assertEqual(row['source_branch'],'peru_chile_undercurrent');self.assertEqual(json.loads(row['model_analysis_years']),[3,10])


if __name__=='__main__':unittest.main()
