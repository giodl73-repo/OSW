import copy
import csv
import io
import json
import math
import unittest
import build_current_depth_route_projections_v11 as p


class GulfStreamRegionalDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op = json.loads((p.ROOT / p.OPERATOR).read_bytes())
        cls.data = p.build()
        cls.new = cls.data['projections'][12:]
        cls.facts = json.loads((p.ROOT / cls.op['source_facts_file']).read_bytes())

    def test_preserves_previous_twelve_and_updates_inventory(self):
        prior = json.loads((p.ROOT / self.op['previous_projection_file']).read_bytes())
        self.assertEqual(self.data['projections'][:12], prior['projections'])
        for key, value in [('catalog_identities',111),('identities_with_regional_projection_scenarios',12),('regional_projection_scenarios',25),('source_anchor_references',35),('new_fitted_source_profile_anchors',65),('new_conditional_adjacent_segments',52)]:
            self.assertEqual(self.data['counts'][key],value)
        depth = json.loads((p.ROOT / self.op['depth_register_file']).read_bytes())
        self.assertEqual({r['entity_id']:r['depth_reference_ids'] for r in self.data['records']}, {r['entity_id']:r['depth_reference_ids'] for r in depth['records']})

    def test_exact_phase_groups_and_source_anchor_facts(self):
        self.assertEqual([r['calendar_month_phase'] for r in self.new],[None]+list(range(1,13)))
        facts = {r['source_file']+'#'+r['source_pointer']:r for r in self.facts['descriptors']}
        for case in self.new:
            self.assertEqual([a['section_id'] for a in case['anchors']],self.op['section_ids'])
            for a in case['anchors']:
                source = facts[a['source_profile_ref']]
                self.assertEqual(a['source_computed_depth_descriptor_m'],source['half_sampled_core_component_decay']['lower_depth_m'])
                self.assertEqual(a['source_native_bracketing_depths_m'],source['half_sampled_core_component_decay']['lower_bracket_m'])
                self.assertEqual(a['source_lon_lat'],source['selected_lon_lat'])
                self.assertEqual(a['locked_reference_direction_at100m_degrees'],source['locked_reference_direction_at100m_degrees'])

    def test_actual_source_pointers_and_tampering_rejected(self):
        chunks = {f:json.loads((p.ROOT/f).read_bytes()) for f in self.op['section_files']}
        p.validate_source_rows(self.facts,chunks)
        for key,value in [('selected_lon_lat',[0,0]),('locked_reference_direction_at100m_degrees',999),('source_pointer','/records/00'),('calendar_month_phase',11)]:
            facts=copy.deepcopy(self.facts);facts['descriptors'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):p.validate_source_rows(facts,chunks)

    def test_missing_and_duplicate_section_phase_rejected(self):
        for rows in [self.facts['descriptors'][:-1],self.facts['descriptors']+[self.facts['descriptors'][0]]]:
            with self.assertRaises(ValueError):p.group_profiles(rows,self.op['section_ids'])

    def test_geometry_is_source_connector_and_includes_exact_anchors(self):
        for case in self.new:
            anchors=case['anchors']
            self.assertEqual(anchors[0]['distance_km'],0)
            self.assertTrue(all(a['distance_km']<b['distance_km'] for a,b in zip(anchors,anchors[1:])))
            for a in anchors:
                sample=next(s for s in case['samples'] if s['distance_along_reference_route_km']==a['distance_km'])
                self.assertEqual(sample['nominal_reference_connector_lon_lat'],a['source_lon_lat'])
                self.assertAlmostEqual(sample['computed_depth_descriptor_m'],a['source_computed_depth_descriptor_m'],places=6)
            self.assertFalse(case['whole_current_length_replaced'])
            self.assertIn('not_observed_current_axis',case['geometry_role'])

    def test_midpoints_and_no_extrapolation(self):
        anchors=self.new[0]['anchors']
        for a,b in zip(anchors,anchors[1:]):
            value,used,status=p.descriptor_at_distance(anchors,(a['distance_km']+b['distance_km'])/2)
            self.assertAlmostEqual(value,(a['source_computed_depth_descriptor_m']+b['source_computed_depth_descriptor_m'])/2)
            self.assertEqual(used,[a,b]);self.assertIn('assumed_linear',status)
        for distance in [-1,anchors[-1]['distance_km']+1]:self.assertIsNone(p.descriptor_at_distance(anchors,distance)[0])
        for distance in [math.nan,math.inf]:
            with self.assertRaises(ValueError):p.descriptor_at_distance(anchors,distance)

    def test_unresolved_or_edge_anchor_blocks_both_neighbors(self):
        for key,value in [('source_computed_depth_descriptor_m',None),('source_lower_status','censored'),('source_horizontal_selection_status','edge_maximum')]:
            anchors=copy.deepcopy(self.new[0]['anchors']);anchors[2][key]=value
            for distance in [anchors[2]['distance_km'],(anchors[1]['distance_km']+anchors[2]['distance_km'])/2,(anchors[2]['distance_km']+anchors[3]['distance_km'])/2]:
                self.assertIsNone(p.descriptor_at_distance(anchors,distance)[0])
            self.assertIsNotNone(p.descriptor_at_distance(anchors,(anchors[3]['distance_km']+anchors[4]['distance_km'])/2)[0])

    def test_phase_context_must_match_and_fraction_is_typed(self):
        rows=p.group_profiles(self.facts['descriptors'],self.op['section_ids'])[1]
        for key,value in [('actual_provider_phase_timestamp_utc','different'),('calendar_month_phase',12)]:
            changed=copy.deepcopy(rows);changed[0][key]=value
            with self.assertRaises(ValueError):p.project_case(changed,self.op)
        changed=copy.deepcopy(rows);changed[0]['half_sampled_core_component_decay']['relative_sampled_core_fraction']=.2
        with self.assertRaises(ValueError):p.project_case(changed,self.op)

    def test_sampled_phase_span_excludes_mean_and_is_not_uncertainty(self):
        for span in self.data['fitted_phase_depth_sample_spans']:
            values=[a['source_computed_depth_descriptor_m'] for case in self.new[1:] for a in case['anchors'] if a['section_id']==span['section_id']]
            self.assertEqual(span['sampled_fitted_phase_depth_span_m'],[min(values),max(values)])
            self.assertEqual(span['fitted_phase_samples'],12)
            self.assertFalse(span['confidence_interval']);self.assertFalse(span['actual_annual_extrema_established'])

    def test_no_physical_thickness_volume_or_inherited_identity(self):
        for case in self.new:
            self.assertEqual(case['entity_id'],'current:gulf-stream')
            self.assertFalse(any(case['eligibility'].values()))
            for key in ['physical_thickness_m','uncertainty_m','annual_range_m']:self.assertIsNone(case[key])
            for sample in case['samples']:
                self.assertIsNone(sample['physical_thickness_m']);self.assertFalse(sample['volume_eligible'])
        self.assertEqual(self.data['counts']['whole_route_physical_depth_profiles'],0)
        self.assertEqual(self.data['counts']['volume_estimates'],0)

    def test_csv_preserves_previous_cells_and_new_profile_links(self):
        old=list(csv.DictReader(io.StringIO((p.ROOT/self.op['previous_projection_csv']).read_text(encoding='utf8'))))
        new=list(csv.DictReader(io.StringIO(p.csv_bytes(self.data).decode('utf8'))))
        for a,b in zip(old,new):self.assertEqual(a,{k:b[k] for k in a})
        added=new[len(old):]
        self.assertEqual(len(added),sum(len(case['samples']) for case in self.new))
        for row in added:
            self.assertTrue(json.loads(row['source_profile_refs']))
            self.assertEqual(row['relative_core_fraction'],'0.5')
            self.assertTrue(row['actual_provider_phase_timestamp_utc'])


if __name__=='__main__':unittest.main()
