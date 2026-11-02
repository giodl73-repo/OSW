import copy,csv,io,json,math
import unittest
import build_current_depth_route_projections_v8 as previous
import build_current_depth_route_projections_v9 as profile


class ConditionalCoreSupportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=profile.build();cls.p=cls.data['projections'][-1]
        cls.op=json.loads((profile.ROOT/profile.OPERATOR).read_bytes())
        cls.refs={r['id']:r for r in json.loads((profile.ROOT/cls.op['depth_register_file']).read_bytes())['evidence']}

    def test_previous_ten_profiles_and_two_volumes_preserved(self):
        prior=previous.build();self.assertEqual(self.data['projections'][:10],prior['projections'])
        self.assertEqual(self.data['counts'],{'catalog_identities':111,'identities_with_regional_projection_scenarios':10,'identities_not_yet_projected':101,'regional_projection_scenarios':11,'source_anchor_references':31,'new_depth_measurements':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0,'regional_reference_geometry_volume_scenarios':2})
        self.assertEqual(self.data['regional_volume_scenario_file'],prior['regional_volume_scenario_file'])

    def test_point_band_and_conditional_layer_support_keep_native_meanings(self):
        self.assertEqual([(a['section_name'],a['support_interval_m'],a['native_source_metric']) for a in self.p['anchors']],[('C',[0,100],'core_depth'),('B',[0,20],'reported_vertical_extent'),('A',[150,150],'core_depth')])
        self.assertEqual(self.p['anchors'][1]['constraint_kind'],'conditional_core_within_explicitly_surface_confined_layer')
        self.assertEqual(self.p['anchors'][1]['source_context']['approximate_value_m'],20)
        self.assertIsNone(self.p['anchors'][1]['source_context']['range_m'])

    def test_intervening_shallow_layer_cannot_be_skipped(self):
        sample=next(s for s in self.p['samples'] if s['section_latitude_degrees_north']==16)
        self.assertEqual(sample['projected_core_depth_support_interval_m'],[0,20])
        case=copy.deepcopy(self.op['case']);case['anchors'].pop(1)
        with self.assertRaises(ValueError):profile.validate_case(case,self.refs)

    def test_interval_interpolation_rounds_outward_without_midpoint(self):
        c,d,ids,kind=profile.interval_at_latitude(self.p['anchors'],14)
        self.assertEqual((c,d),([0,60],[0,60]));self.assertEqual(ids,self.p['source_reference_ids'][:2])
        c,d,ids,kind=profile.interval_at_latitude(self.p['anchors'],17.65)
        self.assertAlmostEqual(c[0],75);self.assertAlmostEqual(c[1],85);self.assertEqual(d,[70,90])
        for s in self.p['samples']:
            self.assertIsNone(s['projected_depth_descriptor_m'])
            c,d=s['computed_core_depth_support_interval_m'],s['projected_core_depth_support_interval_m']
            if c is not None:self.assertLessEqual(d[0],c[0]);self.assertGreaterEqual(d[1],c[1])

    def test_missing_support_invalid_order_and_invalid_intervals(self):
        self.assertEqual([s['section_latitude_degrees_north'] for s in self.p['samples'] if s['projected_core_depth_support_interval_m'] is None],[11,20])
        with self.assertRaises(ValueError):profile.interval_at_latitude(list(reversed(self.p['anchors'])),14)
        anchors=copy.deepcopy(self.p['anchors']);anchors[-1]['support_interval_m']=[200,100]
        with self.assertRaises(ValueError):profile.interval_at_latitude(anchors,12)
        with self.assertRaises(ValueError):profile.interval_at_latitude(self.p['anchors'],float('nan'))

    def test_phase_model_quantity_and_nonphysical_limits(self):
        for field,value in [('calendar_months',[10,11,12]),('flow_direction','southward'),('metric','core_lower_boundary_depth')]:
            case=copy.deepcopy(self.op['case']);case['anchors'][1]['source_context'][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):profile.validate_case(case,self.refs)
        self.assertEqual(self.p['calendar_months'],[2,3,4]);self.assertTrue(self.p['phase_mean_not_monthly_time_series']);self.assertIsNone(self.p['model_time_basis']['calendar_years'])
        self.assertFalse(any(self.p['eligibility'].values()));self.assertIsNone(self.p['annual_range_m'])
        for s in self.p['samples']:
            self.assertFalse(s['depth_interval_is_confidence_interval']);self.assertFalse(s['interval_width_is_current_thickness']);self.assertIsNone(s['physical_thickness_m']);self.assertIsNone(s['depth_uncertainty_m']);self.assertIsNone(s['longitude']);self.assertIsNone(s['distance_along_reference_route_km'])

    def test_two_phase_panel_preserves_missing_section_core_and_native_metrics(self):
        compare=profile.build_phase_comparison(self.data)
        self.assertEqual(compare,json.loads((profile.ROOT/'research/eicc-seasonal-depth-comparison-v1.json').read_bytes()))
        a,b,c=compare['sections']
        self.assertIsNone(a['phases'][1]['source_reference_id']);self.assertIsNone(a['phases'][1]['reported_point_m'])
        self.assertEqual(b['phases'][0]['native_source_metric'],'reported_vertical_extent');self.assertEqual(b['phases'][1]['reported_point_m'],150)
        self.assertEqual(c['phases'][0]['reported_band_m'],[0,100]);self.assertEqual(c['phases'][1]['reported_point_m'],100)
        self.assertFalse(compare['regional_reach_assigned_to_unknown_section_core']);self.assertFalse(compare['whole_year_coverage']);self.assertFalse(compare['monthly_interpolation_performed'])
        for s in compare['sections']:self.assertIsNone(s['automatic_core_depth_difference_m'])

    def test_json_csv_preserve_previous_cells_and_interval_type(self):
        self.assertEqual(self.data,json.loads((profile.ROOT/profile.OUTPUT).read_bytes()))
        raw=profile.csv_bytes(self.data);self.assertEqual(raw,(profile.ROOT/profile.CSV).read_bytes())
        old=list(csv.DictReader(io.StringIO((profile.ROOT/previous.CSV).read_text(encoding='utf8'))));new=list(csv.DictReader(io.StringIO(raw.decode('utf8'))))
        for a,b in zip(old,new):self.assertEqual(a,{k:b[k] for k in a})
        for r,s in zip(new[len(old):],self.p['samples']):
            self.assertEqual(json.loads(r['projected_core_depth_support_interval_m']),s['projected_core_depth_support_interval_m']);self.assertEqual(r['projected_depth_descriptor_m'],'');self.assertEqual(json.loads(r['calendar_months']),[2,3,4]);self.assertEqual(r['flow_direction'],'northward')


if __name__=='__main__':unittest.main()
