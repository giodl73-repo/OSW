import copy
import csv
import hashlib
import io
import json
import unittest
import build_current_depth_route_projections_v36 as p
import load_current_depth_projection_inventory_v1 as loader
from build_current_depth_route_projections_v12 import interpolate


class SouthernCountercurrentIntervalAdditiveProjectionTests(unittest.TestCase):
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

    def test_previous125_scenarios_previous_unresolved_and_all_ownership_lists_preserved(self):
        self.assertEqual(self.view['projections'][:125],self.previous['projections'])
        self.assertEqual(self.view['unresolved_reference_cases'][:len(self.previous['unresolved_reference_cases'])],self.previous['unresolved_reference_cases'])
        self.assertEqual([(r['entity_id'],r['depth_reference_ids']) for r in self.view['records']],[(r['entity_id'],r['depth_reference_ids']) for r in self.previous['records']])
        for c in self.cases:
            owner=next(r for r in self.view['records'] if r['entity_id']==c['entity_id'])
            self.assertIn(c['id'],owner['projection_ids'] if c in self.addendum['projections'] else owner['unresolved_reference_case_ids'])

    def test_all40_original_sections_and_eight_current_date_cases_retained(self):
        self.assertEqual(len(self.cases),8);self.assertEqual(sum(len(c['anchors']) for c in self.cases),40)
        self.assertEqual(len({c['id'] for c in self.cases}),8)
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

        # Exercise a genuinely unselected complete quarter,even if every real source
        # section has a qualifying candidate. Synthetic changes stay in cloud memory.
        from interval_depth_diagnostic_v1 import diagnose
        from sample_eac_hycom_route_depth_v1 import canonical_hash
        facts=copy.deepcopy(self.facts);chunks=copy.deepcopy(self.chunks);op=copy.deepcopy(self.op)
        entity='current:indian-south-equatorial-countercurrent';stamp=op['snapshot_times_utc'][0];config={**op['source_audit_config'],**op['currents'][entity]}
        for row in facts['descriptors']:
            if row['entity_id']!=entity or row['snapshot_time_utc']!=stamp:continue
            source=chunks[row['source_file']]
            for column in source['columns']:
                for key in ['eastward_velocity_m_s','northward_velocity_m_s','signed_reference_component_m_s']:
                    column[key]=[0.0]*len(source['depth_levels_m'])
            source['decoded_columns_sha256']=canonical_hash(source['columns'])
            source['diagnosis']=diagnose(source['depth_levels_m'],[c['signed_reference_component_m_s'] for c in source['columns']],config)
            row.update(selected_column_index=None,selected_lon_lat=None,source_profile_pointer=None,
                selected_column_threshold_layers=[],primary_lower_depth_m=None,primary_layer_thickness_m=None,
                primary_lower_status=None,primary_supported_reach_bound_m=None,
                horizontal_selection_status=source['diagnosis']['horizontal_selection_status'])
            row['source_sha256']=hashlib.sha256(json.dumps(source,sort_keys=True).encode()).hexdigest()
            op['input_sha256'][row['source_file']]=row['source_sha256']
        supported,unresolved=p.full_section_cases(facts,chunks,op)
        case=next(c for c in unresolved if c['entity_id']==entity and c['snapshot_time_utc']==stamp)
        self.assertEqual(len(case['anchors']),5)
        for anchor in case['anchors']:
            self.assertTrue(anchor['reference_geometry_is_unselected_gate_midpoint'])
            self.assertEqual(anchor['reference_lon_lat'][1],-6)
            self.assertIsNone(anchor['source_model_profile_ref']);self.assertIsNone(anchor['model_lower_depth_m'])
            self.assertFalse(anchor['lower_projection_eligible'])
        self.assertTrue(all(s['projection_status']=='gap_no_projection' for s in case['segments']))

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
        self.assertEqual(self.manifest['addenda'][:21],self.previous_manifest['addenda'])
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


    def test_distinct_current_frames_cutoffs_and_transport_are_pinned(self):
        self.assertEqual({c['entity_id'] for c in self.cases},{'current:indian-south-equatorial-countercurrent','current:pacific-south-equatorial-countercurrent'})
        for case in self.cases:
            self.assertEqual(len(case['anchors']),5)
            self.assertTrue(all(a['source_component_bearing_degrees_true']==90 for a in case['anchors']))
            self.assertEqual(case['source_surface_component_gate_m_s'],None)
            self.assertEqual(case['primary_threshold_m_s'],.1)
            self.assertIsNone(case['annual_range_m'])
        file='research/source-data/southern-countercurrent-interval-depth-sections-v1/transport-ledger.json'
        self.assertIn(file,self.op['input_sha256']);ledger=json.loads((p.ROOT/file).read_bytes())
        self.assertTrue(all('longitude_index' in r and 'latitude_indices_inclusive' in r for r in ledger['requests'] if r['status']=='success'))
        self.assertLessEqual(ledger['actual_requested_component_values'],ledger['maximum_requested_component_values'])
        self.assertLessEqual(ledger['conservative_all_target_plus_retries_decoded_byte_bound'],ledger['maximum_decoded_byte_bound'])
        self.assertEqual(ledger['successfully_returned_component_values'],2*self.facts['counts']['decoded_velocity_cell_pairs'])
        self.assertIn('research/wsc-interval20-500-depth-reanalysis-v1.json',self.op['input_sha256'])


    def test_interval_source_audit_method_metadata_and_surface_substitution_rejection(self):
        for c in self.cases:
            interval=self.op['currents'][c['entity_id']]['selection_depth_interval_m'];self.assertFalse(c['canonical_route_replaced']);self.assertFalse(c['canonical_route_extrapolation_performed']);self.assertEqual(c['reference_geometry_scope'],'independent_regional_connector_between_original_sections');self.assertEqual(c['core_search_depth_interval_m'],interval);self.assertEqual(c['selection_depth_interval_m'],interval);self.assertIn('quarterly',c['source_time_basis'])
            self.assertEqual(c['comparison_group'],'model_interval_'+str(interval[0])+'_'+str(interval[1])+'_no_surface_gate')
            self.assertEqual(c['method_id'],'interval_'+str(interval[0])+'_'+str(interval[1])+'-no-surface-gate-v1');self.assertIsNone(c['source_surface_component_gate_m_s'])
        self.assertEqual({c['snapshot_time_utc'] for c in self.cases},set(self.op['snapshot_times_utc']))
        for source in self.chunks.values():
            self.assertFalse(source['diagnosis']['surface_velocity_qualification_applied'])
        chunks=copy.deepcopy(self.chunks);key=next(iter(chunks));chunks[key]['diagnosis']['surface_velocity_qualification_applied']=True
        with self.assertRaises(ValueError):p.full_section_cases(self.facts,chunks,self.op)
        chunks=copy.deepcopy(self.chunks);chunks[key]['operator_file']='invented'
        with self.assertRaises(ValueError):p.full_section_cases(self.facts,chunks,self.op)


if __name__=='__main__':unittest.main()
