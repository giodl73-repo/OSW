import copy
import csv
import hashlib
import io
import json
import unittest
import build_current_depth_route_projections_v13 as p
from build_current_depth_route_projections_v12 import interpolate


class AtlanticModelDepthScenarios(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes());cls.data=p.build();cls.new=cls.data['projections'][29:]
        cls.sources={f:json.loads((p.ROOT/f).read_bytes()) for f in cls.op['current_source_files']}

    def test_previous29_and_all_reference_owners_preserved(self):
        old=json.loads((p.ROOT/self.op['previous_projection_file']).read_bytes())
        self.assertEqual(self.data['projections'][:29],old['projections'])
        self.assertEqual(self.data['counts']['regional_projection_scenarios'],35)
        self.assertEqual(self.data['counts']['identities_with_regional_projection_scenarios'],15)
        self.assertEqual(self.data['counts']['new_model_profile_anchors'],48)
        self.assertEqual(self.data['counts']['new_conditional_adjacent_segments']+self.data['counts']['new_gap_segments'],42)
        register=json.loads((p.ROOT/self.op['depth_register_file']).read_bytes())
        self.assertEqual({r['entity_id']:r['depth_reference_ids'] for r in self.data['records']},{r['entity_id']:r['depth_reference_ids'] for r in register['records']})

    def test_six_cases_keep_dates_thresholds_and_branch_scopes(self):
        self.assertEqual(len(self.new),6)
        self.assertEqual(len({r['id'] for r in self.data['projections']}),35)
        for case in self.new:
            self.assertIn(case['snapshot_time_utc'],self.op['snapshot_times_utc'])
            self.assertEqual(case['primary_threshold_m_s'],.1 if case['entity_id']=='current:brazil' else .05)
            self.assertTrue(case['source_current_scope']);self.assertFalse(case['secondary_product_surface_screen_performed'])
            self.assertFalse(case['whole_current_length_replaced']);self.assertIsNone(case['annual_range_m'])

    def test_source_anchors_values_coordinates_frames_and_native_longitudes(self):
        for case in self.new:
            for anchor in case['anchors']:
                file,pointer=anchor['source_profile_refs'][0].split('#');raw=self.sources[file]['samples'][int(pointer.split('/')[-1])]
                self.assertEqual(anchor['distance_km'],raw['reference_distance_km'])
                self.assertEqual(anchor['reference_lon_lat'],raw['editorial_lon_lat'])
                self.assertEqual(anchor['source_component_bearing_degrees_true'],raw['locked_reference_bearing_degrees_true'])
                selected=raw['selected_profile_index']
                if selected is not None:
                    profile=raw['sampled_profiles'][selected]
                    self.assertEqual(anchor['selected_model_node_lon_lat'],profile['sampled_lon_lat'])
                    self.assertEqual(anchor['source_native_longitude_degrees_east'],profile['native_source_longitude_degrees_east'])
                    self.assertEqual(anchor['source_model_profile_ref'],file+'#'+pointer+'/sampled_profiles/'+str(selected))
                    layer=next(r for r in raw['selected_profile_threshold_layers'] if r['threshold_m_s']==case['primary_threshold_m_s'])
                    self.assertEqual(anchor['source_model_connected_layer'],layer)

    def test_source_edge_no_core_and_censored_nodes_never_promoted(self):
        for case in self.new:
            for a in case['anchors']:
                expected=a['source_horizontal_selection_status']=='interior_sampled_maximum_not_independently_validated_axis' and a['model_lower_depth_m'] is not None
                self.assertEqual(a['lower_projection_eligible'],expected)
                if not expected:
                    sample=next(r for r in case['samples'] if r['distance_along_reference_route_km']==a['distance_km'])
                    self.assertIsNone(sample['computed_model_lower_depth_m'])
                    self.assertTrue(a['projection_block_reasons'])

    def test_only_original_neighbors_interpolate_no_gap_bridging(self):
        for case in self.new:
            self.assertEqual(len(case['segments']),len(case['anchors'])-1)
            for a,b,segment in zip(case['anchors'],case['anchors'][1:],case['segments']):
                self.assertEqual(segment['source_anchor_ids'],[a['id'],b['id']])
                values,used,status=interpolate(case['anchors'],(a['distance_km']+b['distance_km'])/2)
                self.assertEqual(used,[a,b])
                if a['lower_projection_eligible'] and b['lower_projection_eligible']:
                    self.assertAlmostEqual(values['model_lower_depth_m'],(a['model_lower_depth_m']+b['model_lower_depth_m'])/2)
                    self.assertEqual(segment['projection_status'],'conditional_linear_reference_geometry')
                else:
                    self.assertIsNone(values['model_lower_depth_m']);self.assertEqual(segment['projection_status'],'gap_no_projection')

    def test_all_blocked_case_is_retained_with_unknown_samples(self):
        raw=copy.deepcopy(next(iter(self.sources.values())))
        for row in raw['samples']:row['horizontal_selection_status']='edge_maximum_axis_unresolved'
        cases=p.current_cases(raw,'source.json',self.op)
        projected=p.project(cases[0],self.op)
        self.assertEqual(len(projected['anchors']),raw['current_case']['expected_route_vertices'])
        self.assertTrue(all(r['computed_model_lower_depth_m'] is None for r in projected['samples']))

    def test_duplicate_dropped_owner_and_threshold_mutations_rejected(self):
        raw=next(iter(self.sources.values()))
        for changed in [dict(raw,samples=raw['samples'][:-1]),dict(raw,samples=raw['samples']+[raw['samples'][0]]),dict(raw,entity_id='current:north-brazil')]:
            with self.assertRaises(ValueError):p.current_cases(changed,'source.json',self.op)
        changed=copy.deepcopy(raw)
        row=next(r for r in changed['samples'] if r['selected_profile_index'] is not None)
        row['primary_core_lower_descriptor']['threshold_m_s']=.99
        with self.assertRaises(ValueError):p.current_cases(changed,'source.json',self.op)

    def test_model_layer_span_is_not_physical_thickness_or_volume(self):
        for case in self.new:
            self.assertFalse(any(case['eligibility'].values()));self.assertIsNone(case['physical_thickness_m']);self.assertIsNone(case['uncertainty_m'])
            self.assertEqual(case['model_layer_thickness_datum'],'not_applicable_thickness_distance')
            for sample in case['samples']:
                self.assertIsNone(sample['physical_thickness_m']);self.assertFalse(sample['volume_eligible'])
        self.assertEqual(self.data['counts']['whole_route_physical_depth_profiles'],0)
        self.assertEqual(self.data['counts']['volume_estimates'],0)

    def test_previous_csv_cells_new_source_links_and_time_keys(self):
        old=list(csv.DictReader(io.StringIO((p.ROOT/self.op['previous_projection_csv']).read_text(encoding='utf8'))))
        new=list(csv.DictReader(io.StringIO(p.csv_bytes(self.data).decode('utf8'))))
        for a,b in zip(old,new):self.assertEqual(a,{k:b[k] for k in a})
        rows=new[len(old):];self.assertEqual(len(rows),sum(len(r['samples']) for r in self.new))
        for row in rows:
            self.assertTrue(json.loads(row['source_profile_refs']));self.assertIn(row['snapshot_time_utc'],self.op['snapshot_times_utc'])
            self.assertEqual(row['physical_thickness_m'],'')

    def test_pinned_inputs_and_forward_clarifications_preserved(self):
        for file,pin in self.data['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/file).read_bytes()).hexdigest(),pin)
        old=json.loads((p.ROOT/self.op['previous_projection_file']).read_bytes())
        self.assertEqual(self.data['source_definition_clarifications'],old['source_definition_clarifications'])


if __name__=='__main__':unittest.main()
