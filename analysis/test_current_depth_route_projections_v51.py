import copy,csv,hashlib,io,json,unittest
from unittest.mock import patch
import build_current_depth_route_projections_v51 as p
from load_current_depth_projection_inventory_v1 import load_inventory,combined_csv_bytes
from build_current_depth_route_projections_v12 import interpolate
from sample_eac_hycom_route_depth_v1 import along_velocity


class NgccDirectionalProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read=staticmethod(lambda f:(p.ROOT/f).read_bytes())
        cls.op=json.loads(cls.read(p.OPERATOR));cls.old=json.loads(cls.read(cls.op['previous_inventory_file']));cls.previous=load_inventory(cls.old,cls.read)
        with patch('netCDF4.Dataset',side_effect=AssertionError('No field retrieval')):cls.manifest,cls.addendum,cls.pieces,cls.view=p.build()
        cls.sourceop=json.loads(cls.read(cls.op['source_operator_file']));cls.nativeop=json.loads(cls.read(cls.sourceop['native_operator_file']))
        cls.source_manifest=json.loads(cls.read(cls.op['source_manifest_file']));cls.chunks={f:json.loads(cls.read(f)) for f in cls.op['section_files']};cls.natives={f:json.loads(cls.read(f)) for f in cls.sourceop['native_section_files']}
        cls.lookup=p.checked_sources(cls.source_manifest,cls.chunks,cls.natives,cls.sourceop,cls.nativeop,cls.op)
        cls.cases=cls.addendum['projections']+cls.addendum['unresolved_reference_cases']

    def reader(self,f):return self.pieces[f] if f in self.pieces else self.read(f)

    def resolve(self,ref):
        f,pointer=ref.split('#');data=json.loads(self.read(f))
        for key in pointer.strip('/').split('/'):data=data[int(key)] if isinstance(data,list) else data[key]
        return data

    def test_previous235_supported18_unresolved_base36_addenda_and_ownership_preserved(self):
        self.assertEqual(self.view['projections'][:235],self.previous['projections']);self.assertEqual(self.view['unresolved_reference_cases'][:18],self.previous['unresolved_reference_cases'])
        self.assertEqual(self.manifest['base'],self.old['base']);self.assertEqual(self.manifest['addenda'][:36],self.old['addenda'])
        self.assertEqual([(r['entity_id'],r['depth_reference_ids']) for r in self.view['records']],[(r['entity_id'],r['depth_reference_ids']) for r in self.previous['records']])
        before=next(r for r in self.previous['records'] if r['entity_id']==p.NATIVE_OWNER);after=next(r for r in self.view['records'] if r['entity_id']==p.NATIVE_OWNER)
        self.assertEqual(before,after)

    def test_eight_direction_date_cases32_anchors_reuse16_sources_one_new_owner(self):
        self.assertEqual(len(self.cases),8);self.assertEqual(sum(len(c['anchors']) for c in self.cases),32);self.assertEqual(len({c['id'] for c in self.cases}),8)
        self.assertEqual({c['entity_id'] for c in self.cases},{p.TARGET});self.assertNotEqual(p.TARGET,p.NATIVE_OWNER)
        self.assertEqual(len(self.lookup),16)
        for key in ['southeastward','northwestward']:self.assertEqual(sum(c['diagnostic_context_id']==key for c in self.cases),4)
        self.assertEqual(self.view['counts']['identities_with_regional_projection_scenarios'],84+bool(self.addendum['projections']))

    def test_every_manifest_derived_native_and_layer_pointer_resolves_correct_frame(self):
        for case in self.cases:
            bearing=110 if case['diagnostic_context_id']=='southeastward' else 290
            for a in case['anchors']:
                entry=self.resolve(a['source_profile_refs'][0]);self.assertEqual(entry['context_id'],case['diagnostic_context_id']);self.assertEqual(entry['component_bearing_degrees_true'],bearing)
                if a['source_model_profile_ref'] is None:
                    self.assertIsNone(a['source_native_model_profile_ref']);self.assertIsNone(a['model_lower_depth_m']);self.assertTrue(a['reference_geometry_is_unselected_gate_midpoint']);continue
                derived=self.resolve(a['source_model_profile_ref']);native=self.resolve(a['source_native_model_profile_ref']);layer=self.resolve(a['source_connected_diagnosis_ref'])
                self.assertIn('/direction_contexts/'+case['diagnostic_context_id']+'/profiles/',a['source_model_profile_ref'])
                self.assertEqual(derived['source_native_profile_ref'],a['source_native_model_profile_ref']);self.assertEqual(derived['sampled_lon_lat'],native['sampled_lon_lat']);self.assertEqual(a['reference_lon_lat'],derived['sampled_lon_lat'])
                self.assertEqual(derived['component_bearing_degrees_true'],bearing)
                for u,v,signed in zip(native['eastward_velocity_m_s'],native['northward_velocity_m_s'],derived['signed_reference_component_m_s']):
                    if u is None or v is None:self.assertIsNone(signed)
                    else:self.assertAlmostEqual(along_velocity(u,v,bearing),signed,places=12)
                self.assertEqual(layer['threshold_m_s'],.1);self.assertEqual(layer['upper_depth_m'],a['model_upper_depth_m']);self.assertEqual(layer['lower_depth_m'],a['model_lower_depth_m']);self.assertEqual(layer['layer_thickness_m'],a['model_layer_thickness_m'])

    def test_original_edges_censoring_and_no_selection_remain_ineligible(self):
        for c in self.cases:
            for a in c['anchors']:
                eligible=a['source_horizontal_selection_status']==p.INTERIOR and a['model_lower_depth_m'] is not None
                self.assertEqual(a['lower_projection_eligible'],eligible);self.assertEqual(a['layer_projection_eligible'],eligible and a['model_layer_thickness_m'] is not None)
            self.assertEqual(c in self.addendum['projections'],any(a['lower_projection_eligible'] for a in c['anchors']))

    def test_adjacent_only_interpolation_preserves_gaps_and_direction_lineage(self):
        for c in self.cases:
            for a,b,s in zip(c['anchors'],c['anchors'][1:],c['segments']):
                values,used,status=interpolate(c['anchors'],(a['distance_km']+b['distance_km'])/2);self.assertEqual(used,[a,b]);self.assertEqual(s['source_anchor_ids'],[a['id'],b['id']])
                self.assertEqual(a['source_diagnostic_context_id'],c['diagnostic_context_id']);self.assertEqual(b['source_diagnostic_context_id'],c['diagnostic_context_id'])
                if not(a['lower_projection_eligible'] and b['lower_projection_eligible']):self.assertIsNone(values['model_lower_depth_m']);self.assertEqual(s['projection_status'],'gap_no_projection')

    def test_opposing_methods_are_distinct_and_no_season_is_forced(self):
        self.assertEqual(len({c['method_id'] for c in self.cases}),2);self.assertEqual(len({c['comparison_group'] for c in self.cases}),2)
        for c in self.cases:
            bearing=110 if c['diagnostic_context_id']=='southeastward' else 290
            self.assertIn('component'+str(bearing),c['method_id']);self.assertEqual(c['selection_depth_interval_m'],[0,100]);self.assertIsNone(c['source_surface_component_gate_m_s']);self.assertEqual(c['primary_threshold_m_s'],.1)
            self.assertIn('not seasonal means',c['source_time_basis']);self.assertIsNone(c['annual_range_m']);self.assertTrue(all(a['source_component_bearing_degrees_true']==bearing for a in c['anchors']))

    def test_source_owner_schema_profile_component_and_flags_mutations_rejected(self):
        for kind in ['owner','schema','profile','frame','native','additive']:
            chunks=copy.deepcopy(self.chunks);d=chunks[next(iter(chunks))]
            if kind=='owner':d['entity_id']=p.NATIVE_OWNER
            if kind=='schema':d['schema']='osw.mixed-interval-depth-section.v1'
            if kind=='profile':d['direction_contexts']['southeastward']['profiles'][1]['signed_reference_component_m_s'][0]=999
            if kind=='frame':d['direction_contexts']['southeastward']['component_bearing_degrees_true']=290
            if kind=='native':d['native_field_sha256']='0'*64
            if kind=='additive':d['direction_contexts_are_additive']=True
            with self.subTest(kind=kind),self.assertRaises(ValueError):p.checked_sources(self.source_manifest,chunks,self.natives,self.sourceop,self.nativeop,self.op)

    def test_missing_duplicate_or_relabelled_manifest_native_fields_rejected(self):
        for kind in ['missing','duplicate','context']:
            m=copy.deepcopy(self.source_manifest)
            if kind=='missing':m['sections'].pop()
            if kind=='duplicate':m['sections'][-1]=copy.deepcopy(m['sections'][0])
            if kind=='context':m['sections'][0]['direction_contexts']['northwestward']['context_id']='southeastward'
            with self.subTest(kind=kind),self.assertRaises(ValueError):p.checked_sources(m,self.chunks,self.natives,self.sourceop,self.nativeop,self.op)
        native=copy.deepcopy(self.natives);native[next(iter(native))]['columns'][1]['eastward_velocity_m_s'][0]=999
        with self.assertRaises(ValueError):p.checked_sources(self.source_manifest,self.chunks,native,self.sourceop,self.nativeop,self.op)

    def test_unselected_direction_never_borrows_opposite_context_or_underlying_depth(self):
        lookup=copy.deepcopy(self.lookup);stamp=self.sourceop['snapshot_times_utc'][0]
        originals={identity:copy.deepcopy(row[3]['direction_contexts']['northwestward']) for identity,row in lookup.items()}
        for identity,row in lookup.items():
            if identity[0]!=stamp:continue
            row[3]['direction_contexts']['southeastward']['diagnosis'].update(selected_column_index=None,horizontal_selection_status='no_qualifying_interval_component_column',selected_column_threshold_layers=[])
        case=p.direction_case(stamp,'southeastward',lookup,self.sourceop,self.op)
        self.assertTrue(all(a['reference_geometry_is_unselected_gate_midpoint'] and a['model_lower_depth_m'] is None and not a['lower_projection_eligible'] for a in case['anchors']))
        self.assertTrue(all(s['projection_status']=='gap_no_projection' for s in case['segments']))
        for identity,row in lookup.items():self.assertEqual(row[3]['direction_contexts']['northwestward'],originals[identity])

    def test_no_physical_independent_annual_or_volume_promotion_and_zero_field_reads(self):
        for c in self.cases:
            self.assertFalse(any(c['eligibility'].values()));self.assertIsNone(c['physical_thickness_m']);self.assertIsNone(c['annual_range_m']);self.assertFalse(c['whole_current_representative'])
            for key in ['direction_contexts_are_additive','contexts_are_independent_observations','undercurrent_depth_values_inherited','surface_undercurrent_separation_performed','water_mass_classification_performed']:self.assertFalse(c[key])
            self.assertEqual(c['new_velocity_field_requests'],0);self.assertEqual(c['new_independent_observations'],0)
        self.assertEqual(self.view['counts']['whole_route_physical_depth_profiles'],0);self.assertEqual(self.view['counts']['volume_estimates'],0)

    def test_old_csv_cells_preserved_and_new_csv_carries_all_direction_flags(self):
        before=list(csv.DictReader(io.StringIO(combined_csv_bytes(self.old,self.read).decode())));after=list(csv.DictReader(io.StringIO(combined_csv_bytes(self.manifest,self.reader).decode())))
        for a,b in zip(before,after):self.assertEqual(a,{k:b[k] for k in a})
        cases={c['id']:c for c in self.addendum['projections']}
        for row in after[len(before):]:
            c=cases[row['projection_id']];self.assertEqual(row['diagnostic_context_id'],c['diagnostic_context_id']);self.assertEqual(row['method_id'],c['method_id']);self.assertEqual(row['comparison_group'],c['comparison_group'])
            for key in ['direction_contexts_are_additive','contexts_are_independent_observations','undercurrent_depth_values_inherited','surface_undercurrent_separation_performed']:self.assertEqual(row[key],'False')

    def test_pins_caps_count_and_piece_corruption_rejected(self):
        for file,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256(self.read(file)).hexdigest(),pin,file)
        self.assertTrue(all(len(raw)<2500000 for raw in self.pieces.values()))
        with self.assertRaises(ValueError):load_inventory(self.manifest,lambda f:self.reader(f)+b' ' if f==p.ADDENDUM else self.reader(f))
        bad=copy.deepcopy(self.manifest);bad['counts']['regional_projection_scenarios']+=1
        with self.assertRaises(ValueError):load_inventory(bad,self.reader)


if __name__=='__main__':unittest.main()
