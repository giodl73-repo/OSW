import copy,csv,hashlib,io,json,unittest
import build_current_depth_route_projections_v54 as p
from load_current_depth_projection_inventory_v1 import load_inventory,combined_csv_bytes
from build_current_depth_route_projections_v12 import interpolate
from dwbc_abaco_depth_contexts_v1 import diagnose_contexts
from sample_eac_hycom_route_depth_v1 import canonical_hash


class DwbcAbacoContextProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read=staticmethod(lambda f:(p.ROOT/f).read_bytes())
        cls.op=json.loads(cls.read(p.OPERATOR));cls.old=json.loads(cls.read(cls.op['previous_inventory_file']))
        cls.previous=load_inventory(cls.old,cls.read)
        cls.manifest,cls.addendum,cls.pieces,cls.view=p.build()
        cls.cases=cls.addendum['projections']+cls.addendum['unresolved_reference_cases']
        cls.source_manifest=json.loads(cls.read(cls.op['source_manifest_file']))
        cls.chunks={f:json.loads(cls.read(f)) for f in cls.op['section_files']}

    def reader(self,f):return self.pieces[f] if f in self.pieces else self.read(f)

    def resolve(self,ref):
        f,pointer=ref.split('#');data=json.loads(self.read(f))
        for key in pointer.strip('/').split('/'):data=data[int(key)] if isinstance(data,list) else data[key]
        return data

    def test_previous258_supported19_unresolved_and_all_ownership_preserved(self):
        self.assertEqual(self.view['projections'][:258],self.previous['projections'])
        self.assertEqual(self.view['unresolved_reference_cases'][:19],self.previous['unresolved_reference_cases'])
        self.assertEqual([(r['entity_id'],r['depth_reference_ids']) for r in self.view['records']],[(r['entity_id'],r['depth_reference_ids']) for r in self.previous['records']])
        self.assertEqual(self.manifest['base'],self.old['base']);self.assertEqual(self.manifest['addenda'][:39],self.old['addenda'])

    def test_eight_context_date_cases_reuse16_sources_with32_anchors_one_owner(self):
        self.assertEqual(len(self.cases),8);self.assertEqual(sum(len(c['anchors']) for c in self.cases),32)
        self.assertEqual(len({c['id'] for c in self.cases}),8)
        self.assertEqual({c['entity_id'] for c in self.cases},{'current:deep-western-boundary'})
        self.assertEqual({c['diagnostic_context_id'] for c in self.cases},{'upper','lower'})
        for key in ['upper','lower']:self.assertEqual(sum(c['diagnostic_context_id']==key for c in self.cases),4)
        self.assertEqual(len(self.chunks),16);self.assertEqual(len(self.source_manifest['sections']),16)
        self.assertEqual(self.source_manifest['transport']['successfully_returned_component_values'],2*self.source_manifest['decoded_velocity_cell_pairs'])

    def test_every_manifest_profile_and_connected_layer_pointer_resolves_exact_context(self):
        for case in self.cases:
            context=case['diagnostic_context_id']
            for anchor in case['anchors']:
                entry=self.resolve(anchor['source_profile_refs'][0])
                self.assertEqual(entry['context_id'],context)
                diagnosis=entry['diagnosis'];idx=diagnosis['selected_column_index']
                self.assertEqual(anchor['source_horizontal_selection_status'],diagnosis['horizontal_selection_status'])
                if idx is None:
                    self.assertIsNone(anchor['source_model_profile_ref']);self.assertIsNone(anchor['model_lower_depth_m'])
                    self.assertTrue(anchor['reference_geometry_is_unselected_gate_midpoint'])
                else:
                    profile=self.resolve(anchor['source_model_profile_ref']);layer=self.resolve(anchor['source_connected_diagnosis_ref'])
                    self.assertIn('/context_diagnoses/'+context+'/diagnosis/',anchor['source_connected_diagnosis_ref'])
                    self.assertEqual(profile['sampled_lon_lat'],anchor['reference_lon_lat'])
                    self.assertEqual(layer['threshold_m_s'],.1)
                    self.assertEqual(layer['lower_depth_m'],anchor['model_lower_depth_m'])
                    self.assertEqual(layer['upper_depth_m'],anchor['model_upper_depth_m'])
                    self.assertEqual(layer['layer_thickness_m'],anchor['model_layer_thickness_m'])

    def test_primary_edges_censoring_and_no_selection_are_never_filled(self):
        for case in self.cases:
            for anchor in case['anchors']:
                eligible=anchor['source_horizontal_selection_status']==p.INTERIOR and anchor['model_lower_depth_m'] is not None
                self.assertEqual(anchor['lower_projection_eligible'],eligible)
                self.assertEqual(anchor['layer_projection_eligible'],eligible and anchor['model_layer_thickness_m'] is not None)
            self.assertEqual(case in self.addendum['projections'],any(a['lower_projection_eligible'] for a in case['anchors']))

    def test_only_adjacent_same_context_anchors_interpolate_and_all_gaps_remain(self):
        for case in self.cases:
            for a,b,segment in zip(case['anchors'],case['anchors'][1:],case['segments']):
                value,used,status=interpolate(case['anchors'],(a['distance_km']+b['distance_km'])/2)
                self.assertEqual(used,[a,b]);self.assertEqual(segment['source_anchor_ids'],[a['id'],b['id']])
                self.assertEqual(a['source_diagnostic_context_id'],case['diagnostic_context_id']);self.assertEqual(b['source_diagnostic_context_id'],case['diagnostic_context_id'])
                if not(a['lower_projection_eligible'] and b['lower_projection_eligible']):self.assertIsNone(value['model_lower_depth_m']);self.assertEqual(segment['projection_status'],'gap_no_projection')

    def test_context_windows_non_additivity_and_unknown_physical_quantities_preserved(self):
        for case in self.cases:
            expected=[1000,3000] if case['diagnostic_context_id']=='upper' else [3000,5000]
            self.assertEqual(case['selection_depth_interval_m'],expected);self.assertEqual(case['core_search_depth_interval_m'],expected)
            self.assertFalse(case['vertical_contexts_are_additive']);self.assertFalse(case['contexts_are_independent_observations'])
            self.assertFalse(any(case['eligibility'].values()));self.assertIsNone(case['physical_thickness_m']);self.assertIsNone(case['annual_range_m'])
            self.assertFalse(case['whole_current_representative']);self.assertFalse(case['canonical_route_replaced'])
            self.assertEqual(case['primary_threshold_m_s'],.1);self.assertIsNone(case['source_surface_component_gate_m_s'])
        self.assertEqual(self.view['counts']['whole_route_physical_depth_profiles'],0);self.assertEqual(self.view['counts']['volume_estimates'],0)
        self.assertEqual(len({c['comparison_group'] for c in self.cases}),2)

    def test_default_schema_owner_frame_and_deep_diagnosis_mutations_rejected(self):
        for kind in ['schema','owner','frame','default','lower','additive']:
            chunks=copy.deepcopy(self.chunks);source=chunks[next(iter(chunks))]
            if kind=='schema':source['schema']='osw.mixed-interval-depth-section.v1'
            if kind=='owner':source['entity_id']='current:atlantic-south-equatorial-undercurrent'
            if kind=='frame':source['component_bearing_degrees_true']=270
            if kind=='default':source['default_diagnostic_context_id']='lower'
            if kind=='lower':source['context_diagnoses']['lower']['diagnosis']['selected_column_index']=9999
            if kind=='additive':source['vertical_contexts_are_additive']=True
            with self.subTest(kind=kind),self.assertRaises((ValueError,IndexError)):p.context_cases(self.source_manifest,chunks,self.op)

    def test_missing_duplicate_or_relabelled_manifest_context_is_rejected(self):
        for kind in ['missing','duplicate','context']:
            manifest=copy.deepcopy(self.source_manifest)
            if kind=='missing':manifest['sections'].pop()
            if kind=='duplicate':manifest['sections'][-1]=copy.deepcopy(manifest['sections'][0])
            if kind=='context':manifest['sections'][0]['context_diagnoses']['lower']['context_id']='upper'
            with self.subTest(kind=kind),self.assertRaises(ValueError):p.context_cases(manifest,self.chunks,self.op)

    def test_active_context_pointer_frame_primary_or_source_hash_mutation_rejected(self):
        active=p.context_operator(self.op,'lower');facts=p.context_facts(self.source_manifest,self.chunks,active)
        for key,value in [('source_diagnosis_pointer','/diagnosis'),('primary_threshold_m_s',.05),('component_bearing_degrees_true',270),('source_sha256','0'*64),('diagnostic_context_id','upper')]:
            changed=copy.deepcopy(facts);changed['descriptors'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):p.full_section_cases(changed,self.chunks,active)

    def test_synthetic_weak_quarter_stays_unresolved_in_both_contexts(self):
        chunks=copy.deepcopy(self.chunks);manifest=copy.deepcopy(self.source_manifest);op=copy.deepcopy(self.op);stamp=op['snapshot_times_utc'][0]
        for entry in manifest['sections']:
            if entry['snapshot_time_utc']!=stamp:continue
            file=op['source_section_directory']+entry['file'];source=chunks[file]
            for column in source['columns']:
                # Weak southward components qualify at5cm/s but not the primary10cm/s.
                column['eastward_velocity_m_s']=[0.0]*len(source['depth_levels_m']);column['northward_velocity_m_s']=[-.07]*len(source['depth_levels_m']);column['signed_reference_component_m_s']=[.07]*len(source['depth_levels_m'])
            source['decoded_columns_sha256']=canonical_hash(source['columns'])
            cfg={**op['source_audit_config'],**op['currents'][source['entity_id']]}
            source['context_diagnoses']=diagnose_contexts(source['depth_levels_m'],[c['signed_reference_component_m_s'] for c in source['columns']],cfg);source['diagnosis']=source['context_diagnoses']['upper']['diagnosis']
            entry['context_diagnoses']=copy.deepcopy(source['context_diagnoses'])
            entry.update(selected_column_index=None,horizontal_selection_status=source['diagnosis']['horizontal_selection_status'],selected_column_threshold_layers=[])
            pin=hashlib.sha256(json.dumps(source,sort_keys=True).encode()).hexdigest();entry['sha256']=pin;op['input_sha256'][file]=pin
        supported,blocked=p.context_cases(manifest,chunks,op)
        cases=[c for c in blocked if c['snapshot_time_utc']==stamp];self.assertEqual(len(cases),2)
        self.assertTrue(all(not a['lower_projection_eligible'] and a['model_lower_depth_m'] is None for c in cases for a in c['anchors']))
        self.assertTrue(all(s['projection_status']=='gap_no_projection' for c in cases for s in c['segments']))

    def test_csv_preserves_old_cells_and_carries_context_flags_without_new_ownership(self):
        before=list(csv.DictReader(io.StringIO(combined_csv_bytes(self.old,self.read).decode())))
        after=list(csv.DictReader(io.StringIO(combined_csv_bytes(self.manifest,self.reader).decode())))
        for a,b in zip(before,after):self.assertEqual(a,{k:b[k] for k in a})
        cases={c['id']:c for c in self.addendum['projections']}
        for row in after[len(before):]:
            c=cases[row['projection_id']];self.assertEqual(row['diagnostic_context_id'],c['diagnostic_context_id']);self.assertEqual(row['vertical_contexts_are_additive'],'False');self.assertEqual(row['contexts_are_independent_observations'],'False')
            self.assertEqual(row['method_id'],c['method_id']);self.assertEqual(row['comparison_group'],c['comparison_group'])
        self.assertEqual(self.view['counts']['identities_with_regional_projection_scenarios'],87+bool(self.addendum['projections']))

    def test_pins_caps_and_inventory_corruption_checks(self):
        for f,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256(self.read(f)).hexdigest(),pin,f)
        self.assertTrue(all(len(raw)<2500000 for raw in self.pieces.values()))
        with self.assertRaises(ValueError):load_inventory(self.manifest,lambda f:self.reader(f)+b' ' if f==p.ADDENDUM else self.reader(f))
        bad=copy.deepcopy(self.manifest);bad['counts']['regional_projection_scenarios']+=1
        with self.assertRaises(ValueError):load_inventory(bad,self.reader)


if __name__=='__main__':unittest.main()
