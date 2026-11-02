import copy
import csv
import hashlib
import io
import json
import unittest
import build_current_depth_route_projections_v16 as p
import load_current_depth_projection_inventory_v1 as loader
from build_current_depth_route_projections_v12 import interpolate


class ThreeCurrentAdditiveProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes())
        cls.manifest,cls.addendum,cls.pieces,cls.view=p.build()
        cls.previous_manifest=json.loads((p.ROOT/cls.op['previous_inventory_file']).read_bytes())
        cls.previous=loader.load_inventory(cls.previous_manifest,lambda f:(p.ROOT/f).read_bytes())
        cls.facts=json.loads((p.ROOT/cls.op['source_facts_file']).read_bytes())
        cls.chunks={f:json.loads((p.ROOT/f).read_bytes()) for f in cls.op['section_files']}

    def reader(self,f):return self.pieces[f] if f in self.pieces else (p.ROOT/f).read_bytes()

    def test_all40_previous_scenarios_three_blocked_and_111_ownership_lists_preserved(self):
        self.assertEqual(self.view['projections'][:40],self.previous['projections'])
        self.assertEqual(self.view['unresolved_reference_cases'][:3],self.previous['unresolved_reference_cases'])
        self.assertEqual(self.view['counts']['regional_projection_scenarios'],46)
        self.assertEqual(self.view['counts']['identities_with_regional_projection_scenarios'],21)
        self.assertEqual(self.view['counts']['identities_not_yet_projected'],90)
        self.assertEqual([(r['entity_id'],r['depth_reference_ids']) for r in self.view['records']],[(r['entity_id'],r['depth_reference_ids']) for r in self.previous['records']])

    def test_all40_original_sections_and_six_dated_cases_retained(self):
        cases=self.addendum['projections']+self.addendum['unresolved_reference_cases']
        self.assertEqual(len(cases),6);self.assertEqual(sum(len(c['anchors']) for c in cases),40)
        self.assertEqual(len({c['id'] for c in cases}),6)
        for c in cases:
            config=self.op['currents'][c['entity_id']]
            self.assertEqual(c['primary_threshold_m_s'],config['primary_threshold_m_s'])
            self.assertEqual([a['source_section_id'] for a in c['anchors']],[s['id'] for s in config['sections']])
            self.assertEqual(c['temperature_gate'],config['temperature_gate'])
            self.assertEqual(c['branch_scope'],config['branch_scope'])

    def test_primary_values_and_source_profile_pointers_unchanged(self):
        lookup={(r['entity_id'],r['snapshot_time_utc'],r['section_id']):r for r in self.facts['descriptors']}
        eligible=0
        for c in self.addendum['projections']:
            for a in c['anchors']:
                row=lookup[c['entity_id'],c['snapshot_time_utc'],a['source_section_id']]
                self.assertEqual(a['model_lower_depth_m'],row['primary_lower_depth_m'])
                self.assertEqual(a['model_layer_thickness_m'],row['primary_layer_thickness_m'])
                if a['source_model_profile_ref'] is not None:
                    f,pointer=a['source_model_profile_ref'].split('#')
                    actual=self.chunks[f]['columns'][int(pointer.split('/')[-1])]
                    self.assertEqual(a['reference_lon_lat'],actual['sampled_lon_lat'])
                    self.assertFalse(a['reference_geometry_is_unselected_gate_midpoint'])
                eligible+=a['lower_projection_eligible']
        self.assertEqual(eligible,34)

    def test_four_missing_columns_are_explicit_geometry_placeholders_and_never_depth_fills(self):
        missing=[]
        for c in self.addendum['projections']:
            for a in c['anchors']:
                if a['reference_geometry_is_unselected_gate_midpoint']:
                    missing.append(a)
                    self.assertIsNone(a['selected_model_node_lon_lat']);self.assertIsNone(a['source_model_profile_ref'])
                    self.assertIsNone(a['model_lower_depth_m']);self.assertIsNone(a['model_layer_thickness_m'])
                    self.assertFalse(a['lower_projection_eligible']);self.assertFalse(a['layer_projection_eligible'])
                    self.assertIn('no_qualifying_source_column_reference_gate_midpoint_only',a['projection_block_reasons'])
                    self.assertTrue(all(s['computed_model_lower_depth_m'] is None for s in c['samples'] if a['id'] in s['source_anchor_ids']))
        self.assertEqual(len(missing),4)

    def test_two_resolved_depth_gate_edge_cases_remain_ineligible(self):
        edges=[]
        for c in self.addendum['projections']:
            for a in c['anchors']:
                if a['source_horizontal_selection_status']=='section_gate_edge_maximum_axis_unresolved':
                    edges.append(a);self.assertIsNotNone(a['model_lower_depth_m'])
                    self.assertFalse(a['lower_projection_eligible']);self.assertFalse(a['layer_projection_eligible'])
        self.assertEqual(len(edges),2)

    def test_interpolation_uses_only_adjacent_original_supported_anchors_and_preserves_gaps(self):
        for c in self.addendum['projections']:
            for a,b,s in zip(c['anchors'],c['anchors'][1:],c['segments']):
                value,used,status=interpolate(c['anchors'],(a['distance_km']+b['distance_km'])/2)
                self.assertEqual(used,[a,b]);self.assertEqual(s['source_anchor_ids'],[a['id'],b['id']])
                if a['lower_projection_eligible'] and b['lower_projection_eligible']:
                    self.assertAlmostEqual(value['model_lower_depth_m'],(a['model_lower_depth_m']+b['model_lower_depth_m'])/2)
                else:
                    self.assertIsNone(value['model_lower_depth_m']);self.assertEqual(s['projection_status'],'gap_no_projection')

    def test_inventory_keeps_original_base_and_addendum_pins_and_csv_cells(self):
        self.assertEqual(self.manifest['base'],self.previous_manifest['base'])
        self.assertEqual(self.manifest['addenda'][:1],self.previous_manifest['addenda'])
        prior=list(csv.DictReader(io.StringIO(loader.combined_csv_bytes(self.previous_manifest,lambda f:(p.ROOT/f).read_bytes()).decode())))
        new=list(csv.DictReader(io.StringIO(loader.combined_csv_bytes(self.manifest,self.reader).decode())))
        self.assertGreater(len(new),len(prior))
        for a,b in zip(prior,new):self.assertEqual(a,{k:b[k] for k in a})
        self.assertEqual(len(new)-len(prior),sum(len(c['samples']) for c in self.addendum['projections']))

    def test_source_frame_selection_pointer_and_primary_depth_mutations_rejected(self):
        original=next(i for i,r in enumerate(self.facts['descriptors']) if r['selected_column_index'] is not None)
        for key,value in [('component_bearing_degrees_true',0),('source_profile_pointer','/columns/9999'),('primary_lower_depth_m',-1),('section_id','invented')]:
            changed=copy.deepcopy(self.facts);changed['descriptors'][original][key]=value
            with self.subTest(key=key),self.assertRaises((ValueError,IndexError)):p.full_section_cases(changed,self.chunks,self.op)
        changed=copy.deepcopy(self.facts);changed['descriptors'].pop()
        with self.assertRaises(ValueError):p.full_section_cases(changed,self.chunks,self.op)

    def test_pinned_piece_integrity_and_count_mutations_rejected(self):
        with self.assertRaises(ValueError):loader.load_inventory(self.manifest,lambda f:self.reader(f)+b' ' if f==p.ADDENDUM else self.reader(f))
        changed=copy.deepcopy(self.manifest);changed['counts']['regional_projection_scenarios']+=1
        with self.assertRaises(ValueError):loader.load_inventory(changed,self.reader)
        changed=copy.deepcopy(self.manifest);changed['addenda'][-1]['json']['bytes']+=1
        with self.assertRaises(ValueError):loader.load_inventory(changed,self.reader)
        for f,pin in self.addendum['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin)

    def test_model_spans_are_not_physical_thickness_volumes_or_annual_envelopes(self):
        for c in self.addendum['projections']:
            self.assertFalse(any(c['eligibility'].values()));self.assertIsNone(c['physical_thickness_m']);self.assertIsNone(c['annual_range_m'])
            self.assertFalse(c['whole_current_representative']);self.assertFalse(c['whole_current_length_replaced'])
        self.assertEqual(self.view['counts']['whole_route_physical_depth_profiles'],0)
        self.assertEqual(self.view['counts']['volume_estimates'],0)
        self.assertTrue(all(len(raw)<2500000 for raw in self.pieces.values()))
        self.assertEqual(set(self.pieces),{p.INVENTORY,p.ADDENDUM,p.SAMPLES_CSV})


if __name__=='__main__':unittest.main()
