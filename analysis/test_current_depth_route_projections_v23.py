import copy
import csv
import hashlib
import io
import json
import unittest
import build_current_depth_route_projections_v23 as p
import load_current_depth_projection_inventory_v1 as loader
from build_current_depth_route_projections_v12 import interpolate


class GreenlandAdditiveProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes())
        cls.manifest,cls.addendum,cls.pieces,cls.view=p.build()
        cls.previous_manifest=json.loads((p.ROOT/cls.op['previous_inventory_file']).read_bytes())
        cls.previous=loader.load_inventory(cls.previous_manifest,lambda f:(p.ROOT/f).read_bytes())
        cls.facts=json.loads((p.ROOT/cls.op['source_facts_file']).read_bytes())
        cls.chunks={f:json.loads((p.ROOT/f).read_bytes()) for f in cls.op['section_files']}
        cls.cases=cls.addendum['projections']+cls.addendum['unresolved_reference_cases']

    def reader(self,f):return self.pieces[f] if f in self.pieces else (p.ROOT/f).read_bytes()

    def test_previous76_scenarios_three_blocked_and_all_ownership_lists_preserved(self):
        self.assertEqual(self.view['projections'][:76],self.previous['projections'])
        self.assertEqual(self.view['unresolved_reference_cases'][:3],self.previous['unresolved_reference_cases'])
        self.assertEqual([(r['entity_id'],r['depth_reference_ids']) for r in self.view['records']],[(r['entity_id'],r['depth_reference_ids']) for r in self.previous['records']])
        for c in self.cases:
            owner=next(r for r in self.view['records'] if r['entity_id']==c['entity_id'])
            self.assertIn(c['id'],owner['projection_ids'] if c in self.addendum['projections'] else owner['unresolved_reference_case_ids'])

    def test_all28_original_sections_and_four_current_date_cases_retained(self):
        self.assertEqual(len(self.cases),4);self.assertEqual(sum(len(c['anchors']) for c in self.cases),28)
        self.assertEqual(len({c['id'] for c in self.cases}),4)
        for c in self.cases:
            config=self.op['currents'][c['entity_id']]
            self.assertEqual(c['primary_threshold_m_s'],config['primary_threshold_m_s'])
            self.assertEqual(c['source_surface_component_gate_m_s'],config['surface_component_gate_m_s'])
            self.assertEqual([a['source_section_id'] for a in c['anchors']],[s['id'] for s in config['sections']])
            self.assertEqual(c['branch_scope'],config['branch_scope']);self.assertIsNone(c['temperature_gate'])
            self.assertTrue(all(a['source_component_bearing_degrees_true']==config['component_bearing_degrees_true'] for a in c['anchors']))

    def test_primary_values_source_positions_and_profile_pointers_unchanged(self):
        lookup={(r['entity_id'],r['snapshot_time_utc'],r['section_id']):r for r in self.facts['descriptors']}
        for c in self.cases:
            for a in c['anchors']:
                row=lookup[c['entity_id'],c['snapshot_time_utc'],a['source_section_id']]
                self.assertEqual(a['model_lower_depth_m'],row['primary_lower_depth_m'])
                self.assertEqual(a['model_layer_thickness_m'],row['primary_layer_thickness_m'])
                if a['source_model_profile_ref'] is not None:
                    f,pointer=a['source_model_profile_ref'].split('#');actual=self.chunks[f]['columns'][int(pointer.split('/')[-1])]
                    self.assertEqual(a['reference_lon_lat'],actual['sampled_lon_lat'])
                    self.assertFalse(a['reference_geometry_is_unselected_gate_midpoint'])

    def test_no_selection_sections_have_only_explicit_midpoint_geometry_and_no_depth_fill(self):
        original=sum(r['selected_column_index'] is None for r in self.facts['descriptors']);missing=[]
        for c in self.cases:
            for a in c['anchors']:
                if a['reference_geometry_is_unselected_gate_midpoint']:
                    missing.append(a);self.assertIsNone(a['selected_model_node_lon_lat']);self.assertIsNone(a['source_model_profile_ref'])
                    self.assertIsNone(a['model_lower_depth_m']);self.assertIsNone(a['model_layer_thickness_m'])
                    self.assertFalse(a['lower_projection_eligible']);self.assertFalse(a['layer_projection_eligible'])
                    self.assertTrue(all(s['computed_model_lower_depth_m'] is None for s in c['samples'] if a['id'] in s['source_anchor_ids']))
        self.assertEqual(len(missing),original)

    def test_horizontal_edge_and_censored_primary_depth_cases_remain_ineligible(self):
        expected=sum(r['horizontal_selection_status']!=p.INTERIOR or r['primary_lower_depth_m'] is None for r in self.facts['descriptors'])
        blocked=0
        for c in self.cases:
            for a in c['anchors']:
                if a['source_horizontal_selection_status']!=p.INTERIOR or a['model_lower_depth_m'] is None:
                    blocked+=1;self.assertFalse(a['lower_projection_eligible']);self.assertFalse(a['layer_projection_eligible'])
                else:self.assertTrue(a['lower_projection_eligible'])
        self.assertEqual(blocked,expected)
        for c in self.addendum['unresolved_reference_cases']:self.assertFalse(any(a['lower_projection_eligible'] for a in c['anchors']))
        for c in self.addendum['projections']:self.assertTrue(any(a['lower_projection_eligible'] for a in c['anchors']))

    def test_adjacent_original_node_interpolation_preserves_all_gaps(self):
        for c in self.cases:
            for a,b,s in zip(c['anchors'],c['anchors'][1:],c['segments']):
                value,used,status=interpolate(c['anchors'],(a['distance_km']+b['distance_km'])/2)
                self.assertEqual(used,[a,b]);self.assertEqual(s['source_anchor_ids'],[a['id'],b['id']])
                if a['lower_projection_eligible'] and b['lower_projection_eligible']:
                    self.assertAlmostEqual(value['model_lower_depth_m'],(a['model_lower_depth_m']+b['model_lower_depth_m'])/2)
                else:self.assertIsNone(value['model_lower_depth_m']);self.assertEqual(s['projection_status'],'gap_no_projection')

    def test_original_base_addendum_pins_and_every_previous_csv_cell_preserved(self):
        self.assertEqual(self.manifest['base'],self.previous_manifest['base'])
        self.assertEqual(self.manifest['addenda'][:8],self.previous_manifest['addenda'])
        prior=list(csv.DictReader(io.StringIO(loader.combined_csv_bytes(self.previous_manifest,lambda f:(p.ROOT/f).read_bytes()).decode())))
        new=list(csv.DictReader(io.StringIO(loader.combined_csv_bytes(self.manifest,self.reader).decode())))
        for a,b in zip(prior,new):self.assertEqual(a,{k:b[k] for k in a})
        self.assertEqual(len(new)-len(prior),sum(len(c['samples']) for c in self.addendum['projections']))

    def test_source_frame_selection_pointer_primary_and_temperature_mutations_rejected(self):
        index=next((i for i,r in enumerate(self.facts['descriptors']) if r['selected_column_index'] is not None),0)
        for key,value in [('component_bearing_degrees_true',(self.facts['descriptors'][index]['component_bearing_degrees_true']+180)%360),('source_profile_pointer','/columns/9999'),('primary_lower_depth_m',-1),('section_id','invented'),('primary_threshold_m_s',-1)]:
            changed=copy.deepcopy(self.facts);changed['descriptors'][index][key]=value
            with self.subTest(key=key),self.assertRaises((ValueError,IndexError)):p.full_section_cases(changed,self.chunks,self.op)
        changed=copy.deepcopy(self.facts);changed['descriptors'].pop()
        with self.assertRaises(ValueError):p.full_section_cases(changed,self.chunks,self.op)

    def test_pinned_source_piece_integrity_and_count_mutations_rejected(self):
        with self.assertRaises(ValueError):loader.load_inventory(self.manifest,lambda f:self.reader(f)+b' ' if f==p.ADDENDUM else self.reader(f))
        changed=copy.deepcopy(self.manifest);changed['counts']['regional_projection_scenarios']+=1
        with self.assertRaises(ValueError):loader.load_inventory(changed,self.reader)
        changed=copy.deepcopy(self.manifest);changed['addenda'][-1]['json']['bytes']+=1
        with self.assertRaises(ValueError):loader.load_inventory(changed,self.reader)
        for f,pin in self.addendum['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin)

    def test_no_physical_thickness_volume_seasonal_or_full_snapshot_promotion(self):
        for c in self.cases:
            self.assertFalse(any(c['eligibility'].values()));self.assertIsNone(c['physical_thickness_m']);self.assertIsNone(c['annual_range_m'])
            self.assertFalse(c['whole_current_representative']);self.assertFalse(c['whole_current_length_replaced'])
        self.assertEqual(self.view['counts']['whole_route_physical_depth_profiles'],0);self.assertEqual(self.view['counts']['volume_estimates'],0)
        self.assertTrue(all(len(raw)<2500000 for raw in self.pieces.values()))
        self.assertEqual(set(self.pieces),{p.INVENTORY,p.ADDENDUM,p.SAMPLES_CSV})


    def test_opposite_greenland_frames_and_actual_latitude_transport_are_pinned(self):
        self.assertEqual({c['entity_id'] for c in self.cases},{'current:east-greenland','current:west-greenland'})
        for case in self.cases:
            east=case['entity_id']=='current:east-greenland'
            self.assertEqual(len(case['anchors']),8 if east else 6)
            self.assertTrue(all(a['source_component_bearing_degrees_true']==(180 if east else 0) for a in case['anchors']))
            self.assertEqual(case['source_surface_component_gate_m_s'],.05)
            self.assertEqual(case['primary_threshold_m_s'],.1)
            self.assertIsNone(case['annual_range_m'])
        file='research/source-data/greenland-depth-sections-v1/transport-ledger.json'
        self.assertIn(file,self.op['input_sha256'])
        ledger=json.loads((p.ROOT/file).read_bytes())
        self.assertEqual(ledger['geometry'],'fixed_native_latitude_contiguous_native_longitudes')
        self.assertLessEqual(ledger['actual_requested_component_values'],ledger['maximum_requested_component_values'])
        self.assertLessEqual(ledger['conservative_all_target_plus_retries_decoded_byte_bound'],ledger['maximum_decoded_byte_bound'])
        self.assertEqual(ledger['successfully_returned_component_values'],2*self.facts['counts']['decoded_velocity_cell_pairs'])
        for request in ledger['requests']:
            if 'source_time_index' in request:
                self.assertIn('latitude_index',request);self.assertIn('longitude_indices_inclusive',request)
                self.assertNotIn('latitude_indices_inclusive',request)


if __name__=='__main__':unittest.main()
