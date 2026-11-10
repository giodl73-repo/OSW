import copy
import csv
import hashlib
import io
import json
import math
import unittest
import build_current_depth_route_projections_v12 as p


class DatedModelDepthProjections(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes());cls.data=p.build()
        cls.new=cls.data['projections'][25:]
        cls.eac=json.loads((p.ROOT/cls.op['eac_join_file']).read_bytes())
        cls.model=json.loads((p.ROOT/cls.op['eac_model_file']).read_bytes())
        cls.kuroshio=json.loads((p.ROOT/cls.op['kuroshio_source_file']).read_bytes())

    def test_previous25_and_inventory_preserved_with_new_owner(self):
        old=json.loads((p.ROOT/self.op['previous_projection_file']).read_bytes())
        self.assertEqual(self.data['projections'][:25],old['projections'])
        for key,value in [('catalog_identities',111),('regional_projection_scenarios',29),('identities_with_regional_projection_scenarios',13),('new_model_profile_anchors',24),('new_projection_eligible_source_nodes',12),('new_conditional_adjacent_segments',4),('new_gap_segments',16)]:self.assertEqual(self.data['counts'][key],value)
        register=json.loads((p.ROOT/self.op['depth_register_file']).read_bytes())
        self.assertEqual({r['entity_id']:r['depth_reference_ids'] for r in self.data['records']},{r['entity_id']:r['depth_reference_ids'] for r in register['records']})
        self.assertEqual(self.data['fitted_phase_depth_sample_spans'],old['fitted_phase_depth_sample_spans'])

    def test_case_dates_thresholds_and_frames_are_not_pooled(self):
        self.assertEqual([(r['entity_id'],r['snapshot_time_utc'],r['primary_threshold_m_s']) for r in self.new],[
            ('current:east-australian','2022-01-15T00:00:00Z',.05),('current:east-australian','2022-07-15T00:00:00Z',.05),
            ('current:kuroshio','2024-01-15T00:00:00Z',.1),('current:kuroshio','2024-07-15T00:00:00Z',.1)])
        for case in self.new:
            for anchor in case['anchors']:self.assertIsInstance(anchor['source_component_bearing_degrees_true'],(int,float))
            self.assertIsNone(case['annual_range_m']);self.assertFalse(case['model_products_are_statistically_independent'])

    def test_eac_gates_values_and_frozen_eligible_segments_preserved(self):
        for case in self.new[:2]:
            nodes=[n for n in self.eac['nodes'] if n['source_date']==case['snapshot_time_utc'][:10]]
            for anchor,node in zip(case['anchors'],nodes):
                self.assertEqual(anchor['lower_projection_eligible'],node['conditional_lower_depth_projection_node_eligible'])
                self.assertEqual(anchor['model_lower_depth_m'],node['model_primary_lower_isotach_depth_m'])
                self.assertEqual(anchor['source_surface_screen'],node['surface_screen'])
                self.assertEqual(anchor['distance_km'],node['reference_distance_km'])
            eligible=[s for s in case['segments'] if s['projection_status']!='gap_no_projection']
            self.assertEqual(len(eligible),1)
            self.assertEqual(eligible[0]['source_anchor_ids'],[case['anchors'][i]['id'] for i in [4,5]])

    def test_kuroshio_edge_and_censored_gates_block_original_neighbors(self):
        for case in self.new[2:]:
            self.assertEqual([a['source_latitude_gate'] for a in case['anchors']],[18.5,21.5,24.5,27.5,29.5])
            self.assertFalse(case['anchors'][0]['lower_projection_eligible'])
            self.assertFalse(case['anchors'][2]['lower_projection_eligible'])
            self.assertTrue(case['anchors'][1]['lower_projection_eligible'])
            self.assertEqual([s['projection_status'] for s in case['segments']],['gap_no_projection']*3+['conditional_linear_reference_geometry'])
        january,july=self.new[2:]
        self.assertIn('window_edge',january['anchors'][2]['projection_block_reasons'][0])
        self.assertIsNone(july['anchors'][2]['model_lower_depth_m'])
        self.assertIn('primary10cms_lower_boundary_unresolved',july['anchors'][2]['projection_block_reasons'])

    def test_adjacent_midpoint_interpolation_for_three_distinct_quantities(self):
        for case in self.new:
            eligible=[(a,b) for a,b in zip(case['anchors'],case['anchors'][1:]) if a['lower_projection_eligible'] and b['lower_projection_eligible']]
            for a,b in eligible:
                values,used,status=p.interpolate(case['anchors'],(a['distance_km']+b['distance_km'])/2)
                self.assertEqual(used,[a,b]);self.assertIn('assumed_linear',status)
                for q in p.QUANTITIES:self.assertAlmostEqual(values[q],(a[q]+b[q])/2)
                self.assertAlmostEqual(values['model_layer_thickness_m'],values['model_lower_depth_m']-values['model_upper_depth_m'])

    def test_blocked_anchor_prevents_both_adjacent_intervals_and_exact_point(self):
        anchors=copy.deepcopy(self.new[-1]['anchors'])
        anchors[-2]['lower_projection_eligible']=False;anchors[-2]['layer_projection_eligible']=False
        for x in [anchors[-2]['distance_km'],(anchors[-3]['distance_km']+anchors[-2]['distance_km'])/2,(anchors[-2]['distance_km']+anchors[-1]['distance_km'])/2]:
            values,_,_=p.interpolate(anchors,x);self.assertTrue(all(v is None for v in values.values()))

    def test_missing_upper_does_not_erase_lower_or_fabricate_thickness(self):
        anchors=copy.deepcopy(self.new[-1]['anchors'])
        for a in anchors[-2:]:a.update(model_upper_depth_m=None,model_layer_thickness_m=None,layer_projection_eligible=False)
        values,_,_=p.interpolate(anchors,(anchors[-2]['distance_km']+anchors[-1]['distance_km'])/2)
        self.assertIsNotNone(values['model_lower_depth_m']);self.assertIsNone(values['model_upper_depth_m']);self.assertIsNone(values['model_layer_thickness_m'])

    def test_no_extrapolation_and_invalid_distance_or_duplicate_anchors_rejected(self):
        anchors=self.new[-1]['anchors']
        for distance in [-1,anchors[-1]['distance_km']+1]:
            self.assertTrue(all(v is None for v in p.interpolate(anchors,distance)[0].values()))
            self.assertIsNone(p.reference_position(anchors,distance))
        for distance in [math.nan,math.inf]:
            with self.assertRaises(ValueError):p.interpolate(anchors,distance)
        for change in ['distance','id','thickness']:
            bad=copy.deepcopy(anchors)
            if change=='distance':bad[-1]['distance_km']=bad[-2]['distance_km']
            elif change=='id':bad[-1]['id']=bad[-2]['id']
            else:bad[-1]['model_layer_thickness_m']+=10
            with self.assertRaises(ValueError):p.validate_anchors(bad)

    def test_source_reference_geometry_and_selected_model_positions_remain_distinct(self):
        for case in self.new:
            self.assertFalse(case['whole_current_length_replaced'])
            for a in case['anchors']:
                s=next(s for s in case['samples'] if s['distance_along_reference_route_km']==a['distance_km'])
                self.assertEqual(s['nominal_reference_connector_lon_lat'],a['reference_lon_lat'])
                self.assertEqual(p.reference_position(case['anchors'],a['distance_km']),a['reference_lon_lat'])
                if a['lower_projection_eligible']:self.assertAlmostEqual(s['computed_model_lower_depth_m'],a['model_lower_depth_m'],places=6)

    def test_source_profile_pointers_and_actual_selected_nodes_resolve(self):
        sources={self.op['eac_model_file']:self.model,self.op['kuroshio_source_file']:self.kuroshio}
        for case in self.new:
            for a in case['anchors']:
                f,pointer=a['source_model_profile_ref'].split('#');parts=pointer.strip('/').split('/')
                profile=sources[f]['samples'][int(parts[1])]['sampled_profiles'][int(parts[3])]
                self.assertEqual(profile['sampled_lon_lat'],a['selected_model_node_lon_lat'])

    def test_source_missing_duplicate_time_selection_mutations_rejected(self):
        for rows in [self.kuroshio['samples'][:-1],self.kuroshio['samples']+[self.kuroshio['samples'][0]]]:
            with self.assertRaises(ValueError):p.kuroshio_cases(dict(self.kuroshio,samples=rows),self.op)
        changed=copy.deepcopy(self.model);changed['samples'][0]['snapshot_time_utc']='2022-01-15T03:00:00Z'
        with self.assertRaises(ValueError):p.eac_cases(self.eac,changed,self.op)
        changed=copy.deepcopy(self.kuroshio);changed['samples'][0]['source_axis_gate']=None
        with self.assertRaises(ValueError):p.kuroshio_cases(changed,self.op)

    def test_no_physical_thickness_volume_uncertainty_or_global_total(self):
        for case in self.new:
            self.assertFalse(any(case['eligibility'].values()));self.assertIsNone(case['physical_thickness_m'])
            self.assertEqual(case['model_layer_thickness_datum'],'not_applicable_thickness_distance')
            for sample in case['samples']:
                self.assertIsNone(sample['physical_thickness_m']);self.assertIsNone(sample['depth_uncertainty_m']);self.assertFalse(sample['volume_eligible'])
        self.assertEqual(self.data['counts']['whole_route_physical_depth_profiles'],0);self.assertEqual(self.data['counts']['volume_estimates'],0)

    def test_previous_csv_cells_and_new_model_quantity_columns_preserved(self):
        old=list(csv.DictReader(io.StringIO((p.ROOT/self.op['previous_projection_csv']).read_text(encoding='utf8'))))
        new=list(csv.DictReader(io.StringIO(p.csv_bytes(self.data).decode('utf8'))))
        for a,b in zip(old,new):self.assertEqual(a,{k:b[k] for k in a})
        added=new[len(old):];self.assertEqual(len(added),sum(len(r['samples']) for r in self.new))
        for row in added:
            self.assertEqual(row['model_layer_thickness_datum'],'not_applicable_thickness_distance')
            self.assertTrue(row['source_profile_refs']);self.assertEqual(row['physical_thickness_m'],'')
        self.assertTrue(any(r['computed_model_lower_depth_m']=='' for r in added))
        self.assertTrue(any(r['computed_model_layer_thickness_m']!='' for r in added))

    def test_all_direct_input_pins_and_forward_core_definition_clarification(self):
        for f,pin in self.data['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin)
        clarification=self.data['source_definition_clarifications'][0]
        self.assertFalse(clarification['numeric_values_changed']);self.assertIn('10–200m',clarification['correct_definition'])


if __name__=='__main__':unittest.main()
