import copy
import csv
import hashlib
import io
import json
import unittest
import build_current_depth_route_projections_v15 as p
import load_current_depth_projection_inventory_v1 as loader
from build_current_depth_route_projections_v12 import interpolate


class NorthBrazilAdditiveInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes())
        cls.manifest,cls.addendum,cls.pieces,cls.view=p.build()
        cls.base=json.loads((p.ROOT/cls.op['base_projection_file']).read_bytes())
        cls.facts=json.loads((p.ROOT/cls.op['source_facts_file']).read_bytes())
        cls.chunks={f:json.loads((p.ROOT/f).read_bytes()) for f in cls.op['section_files']}

    def reader(self,file):return self.pieces[file] if file in self.pieces else (p.ROOT/file).read_bytes()

    def repin_addendum(self,changed):
        manifest=copy.deepcopy(self.manifest);pieces=dict(self.pieces);raw=p.encoded(changed);pieces[p.ADDENDUM]=raw
        manifest['addenda'][0]['json'].update(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
        return manifest,lambda f:pieces[f] if f in pieces else (p.ROOT/f).read_bytes()

    def test_all38_previous_objects_and_three_unresolved_cases_preserved(self):
        self.assertEqual(self.view['projections'][:38],self.base['projections'])
        self.assertEqual(self.view['unresolved_reference_cases'],self.base['unresolved_reference_cases'])
        self.assertEqual(len(self.view['projections']),40)
        self.assertEqual(self.view['counts']['identities_with_regional_projection_scenarios'],18)
        self.assertEqual(self.view['counts']['identities_not_yet_projected'],93)
        self.assertEqual(self.view['counts']['identities_with_only_blocked_reference_cases'],0)
        old={r['entity_id']:r['depth_reference_ids'] for r in self.base['records']}
        self.assertEqual({r['entity_id']:r['depth_reference_ids'] for r in self.view['records']},old)

    def test_two_new_method_ids_do_not_collide_with_old_pilot(self):
        nbc=next(r for r in self.view['records'] if r['entity_id']=='current:north-brazil')
        self.assertEqual(len(nbc['projection_ids']),2);self.assertEqual(len(nbc['unresolved_reference_case_ids']),2)
        self.assertFalse(set(nbc['projection_ids'])&set(nbc['unresolved_reference_case_ids']))
        for case in self.addendum['projections']:
            self.assertIn('full-sections',case['id']);self.assertIn('nw315',case['id'])
            self.assertTrue(case['method_frame_differs_from_earlier_corridor_pilot'])
            self.assertIn(case['earlier_unresolved_pilot_case_id'],nbc['unresolved_reference_case_ids'])

    def test_all14_original_sections_and_primary_source_values_and_pointers(self):
        self.assertEqual(sum(len(r['anchors']) for r in self.addendum['projections']),14)
        facts={(r['snapshot_time_utc'],r['section_id']):r for r in self.facts['descriptors']}
        for case in self.addendum['projections']:
            self.assertEqual([a['source_section_id'] for a in case['anchors']],self.op['section_ids'])
            for a in case['anchors']:
                fact=facts[case['snapshot_time_utc'],a['source_section_id']]
                self.assertEqual(a['reference_lon_lat'],fact['selected_lon_lat'])
                self.assertEqual(a['model_lower_depth_m'],fact['primary10cms_lower_depth_m'])
                self.assertEqual(a['model_layer_thickness_m'],fact['primary10cms_layer_thickness_m'])
                self.assertEqual(a['source_component_bearing_degrees_true'],315)
                file,pointer=a['source_model_profile_ref'].split('#')
                profile=self.chunks[file]['columns'][int(pointer.split('/')[-1])]
                self.assertEqual(a['selected_model_node_lon_lat'],profile['sampled_lon_lat'])

    def test_censored_primary_depths_remain_unknown_and_alternates_not_substituted(self):
        eligible=0
        for case in self.addendum['projections']:
            for a in case['anchors']:
                sample=next(s for s in case['samples'] if s['distance_along_reference_route_km']==a['distance_km'])
                if a['model_lower_depth_m'] is None:
                    self.assertFalse(a['lower_projection_eligible']);self.assertIsNone(sample['computed_model_lower_depth_m'])
                    self.assertIsNone(sample['computed_model_layer_thickness_m'])
                else:
                    eligible+=1;self.assertTrue(a['lower_projection_eligible'])
                    self.assertAlmostEqual(sample['computed_model_lower_depth_m'],a['model_lower_depth_m'],places=6)
        self.assertEqual(eligible,12)
        self.assertEqual(self.view['counts']['new_projection_eligible_source_nodes'],12)

    def test_only_adjacent_supported_original_nodes_interpolate(self):
        eligible_segments=0;gaps=0
        for case in self.addendum['projections']:
            for a,b,segment in zip(case['anchors'],case['anchors'][1:],case['segments']):
                self.assertEqual(segment['source_anchor_ids'],[a['id'],b['id']])
                value,used,status=interpolate(case['anchors'],(a['distance_km']+b['distance_km'])/2)
                self.assertEqual(used,[a,b])
                if a['lower_projection_eligible'] and b['lower_projection_eligible']:
                    eligible_segments+=1;self.assertAlmostEqual(value['model_lower_depth_m'],(a['model_lower_depth_m']+b['model_lower_depth_m'])/2)
                else:gaps+=1;self.assertIsNone(value['model_lower_depth_m'])
        self.assertEqual(eligible_segments,self.view['counts']['new_conditional_adjacent_segments'])
        self.assertEqual(gaps,self.view['counts']['new_gap_segments']);self.assertEqual(eligible_segments+gaps,12)

    def test_integrity_rejects_changed_bytes_sizes_counts_and_repeated_parts(self):
        with self.assertRaises(ValueError):loader.load_inventory(self.manifest,lambda f:self.reader(f)+b' ' if f==p.ADDENDUM else self.reader(f))
        bad=copy.deepcopy(self.manifest);bad['addenda'][0]['json']['bytes']+=1
        with self.assertRaises(ValueError):loader.load_inventory(bad,self.reader)
        bad=copy.deepcopy(self.manifest);bad['counts']['regional_projection_scenarios']+=1
        with self.assertRaises(ValueError):loader.load_inventory(bad,self.reader)
        bad=copy.deepcopy(self.manifest);bad['addenda'].append(bad['addenda'][0])
        with self.assertRaises(ValueError):loader.load_inventory(bad,self.reader)

    def test_rejects_case_collision_unknown_owner_wrong_base_and_physical_promotion(self):
        for field,value in [('id',self.base['unresolved_reference_cases'][0]['id']),('entity_id','current:invented'),('physical_thickness_m',100)]:
            changed=copy.deepcopy(self.addendum);changed['projections'][0][field]=value
            manifest,reader=self.repin_addendum(changed)
            with self.assertRaises(ValueError):loader.load_inventory(manifest,reader)
        changed=copy.deepcopy(self.addendum);changed['base_snapshot_sha256']='0'*64
        manifest,reader=self.repin_addendum(changed)
        with self.assertRaises(ValueError):loader.load_inventory(manifest,reader)

    def test_csv_view_preserves_every_old_cell_and_adds_only_new_samples(self):
        raw=loader.combined_csv_bytes(self.manifest,self.reader)
        old=list(csv.DictReader(io.StringIO((p.ROOT/self.op['base_projection_csv']).read_text(encoding='utf8'))))
        new=list(csv.DictReader(io.StringIO(raw.decode('utf8'))))
        for a,b in zip(old,new):self.assertEqual(a,{k:b[k] for k in a})
        rows=new[len(old):];self.assertEqual(len(rows),sum(len(r['samples']) for r in self.addendum['projections']))
        for row in rows:
            self.assertEqual(row['source_component_reference_frame'],'fixed_geographic_315degree_true_northwest_held_through_depth')
            self.assertEqual(row['physical_thickness_m'],'')

    def test_source_metadata_mutations_rejected_before_projection(self):
        for key,value in [('component_bearing_degrees_true',0),('source_profile_pointer','/columns/0'),('primary10cms_lower_depth_m',1),('section_id','invented')]:
            facts=copy.deepcopy(self.facts);facts['descriptors'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):p.full_section_cases(facts,self.chunks,self.op)
        facts=copy.deepcopy(self.facts);facts['descriptors'].pop()
        with self.assertRaises(ValueError):p.full_section_cases(facts,self.chunks,self.op)

    def test_immutable_piece_output_caps_and_round_trip_without_full_snapshot_copy(self):
        self.assertEqual(set(self.pieces),{p.INVENTORY,p.ADDENDUM,p.SAMPLES_CSV})
        self.assertTrue(all(len(raw)<2500000 for raw in self.pieces.values()))
        self.assertEqual(loader.load_inventory(json.loads(self.pieces[p.INVENTORY]),self.reader),self.view)
        self.assertNotIn('projections',self.manifest);self.assertEqual(len(self.manifest['addenda']),1)

    def test_model_layer_span_is_not_physical_current_thickness_or_annual_range(self):
        for case in self.addendum['projections']:
            self.assertFalse(any(case['eligibility'].values()));self.assertIsNone(case['physical_thickness_m']);self.assertIsNone(case['annual_range_m'])
            self.assertEqual(case['model_layer_thickness_datum'],'not_applicable_thickness_distance')
        self.assertEqual(self.view['counts']['whole_route_physical_depth_profiles'],0);self.assertEqual(self.view['counts']['volume_estimates'],0)

    def test_declared_source_input_pins_and_inventory_metadata_cannot_override_collections(self):
        for file,pin in self.addendum['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/file).read_bytes()).hexdigest(),pin)
        bad=copy.deepcopy(self.manifest);bad['view_metadata']['projections']=[]
        with self.assertRaises(ValueError):loader.load_inventory(bad,self.reader)
        bad=copy.deepcopy(self.manifest);bad['view_metadata']['full_goal_complete']=True
        with self.assertRaises(ValueError):loader.load_inventory(bad,self.reader)


if __name__=='__main__':unittest.main()
