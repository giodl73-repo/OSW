import copy,csv,hashlib,io,json,unittest
from unittest.mock import patch
import build_current_depth_route_projections_v55 as p
from load_current_depth_projection_inventory_v1 import load_inventory,combined_csv_bytes
from build_current_depth_route_projections_v12 import interpolate
from sample_eac_hycom_route_depth_v1 import along_velocity

class MediterraneanBranchProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read=staticmethod(lambda f:(p.ROOT/f).read_bytes());cls.op=json.loads(cls.read(p.OPERATOR));cls.old=json.loads(cls.read(cls.op['previous_inventory_file']));cls.previous=load_inventory(cls.old,cls.read)
        with patch('netCDF4.Dataset',side_effect=AssertionError('No field retrieval')):cls.manifest,cls.addendum,cls.pieces,cls.view=p.build()
        cls.sourceop=json.loads(cls.read(cls.op['source_operator_file']));cls.source_manifest=json.loads(cls.read(cls.op['source_manifest_file']));cls.chunks={f:json.loads(cls.read(f)) for f in cls.op['section_files']};cls.lookup=p.checked_sources(cls.source_manifest,cls.chunks,cls.sourceop,cls.op);cls.cases=cls.addendum['projections']+cls.addendum['unresolved_reference_cases']
    def reader(self,f):return self.pieces[f] if f in self.pieces else self.read(f)
    def resolve(self,ref):
        f,pointer=ref.split('#');d=json.loads(self.read(f))
        for key in pointer.strip('/').split('/'):d=d[int(key)] if isinstance(d,list) else d[key]
        return d
    def test_previous262_supported23_unresolved40addenda_base_and_ownership_preserved(self):
        self.assertEqual(self.view['projections'][:262],self.previous['projections']);self.assertEqual(self.view['unresolved_reference_cases'][:23],self.previous['unresolved_reference_cases']);self.assertEqual(self.manifest['base'],self.old['base']);self.assertEqual(self.manifest['addenda'][:40],self.old['addenda']);self.assertEqual([(r['entity_id'],r['depth_reference_ids']) for r in self.view['records']],[(r['entity_id'],r['depth_reference_ids']) for r in self.previous['records']])
    def test16branch_context_date_cases64anchors32sources_one_owner(self):
        self.assertEqual(len(self.cases),16);self.assertEqual(sum(len(c['anchors']) for c in self.cases),64);self.assertEqual(len({c['id'] for c in self.cases}),16);self.assertEqual(len({c['route_id'] for c in self.cases}),16);self.assertEqual(len(self.lookup),32);self.assertEqual({c['entity_id'] for c in self.cases},{p.TARGET})
        for b in ['south-iberian','west-iberian']:
            for k in ['upper','lower']:self.assertEqual(sum(c['diagnostic_branch_id']==b and c['diagnostic_context_id']==k for c in self.cases),4)
        self.assertEqual(self.view['counts']['identities_with_regional_projection_scenarios'],88+bool(self.addendum['projections']))
    def test_all_manifest_native_profile_layer_pointers_and_signed_frames_resolve(self):
        for c in self.cases:
            bearing=270 if c['diagnostic_branch_id']=='south-iberian' else 0
            for a in c['anchors']:
                e=self.resolve(a['source_profile_refs'][0]);self.assertEqual(e['context_id'],c['diagnostic_context_id']);self.assertEqual(e['diagnosis']['horizontal_selection_status'],a['source_horizontal_selection_status']);self.assertEqual(a['source_section_definition']['diagnostic_branch_id'],c['diagnostic_branch_id']);self.assertEqual(a['source_component_bearing_degrees_true'],bearing)
                if a['source_model_profile_ref'] is None:self.assertIsNone(a['model_lower_depth_m']);self.assertTrue(a['reference_geometry_is_unselected_gate_midpoint']);continue
                native=self.resolve(a['source_model_profile_ref']);layer=self.resolve(a['source_connected_diagnosis_ref']);self.assertEqual(a['source_model_profile_ref'],a['source_native_model_profile_ref']);self.assertEqual(native['sampled_lon_lat'],a['reference_lon_lat']);self.assertIn('/context_diagnoses/'+c['diagnostic_context_id']+'/diagnosis/',a['source_connected_diagnosis_ref'])
                for u,v,s in zip(native['eastward_velocity_m_s'],native['northward_velocity_m_s'],native['signed_reference_component_m_s']):
                    if u is None or v is None:self.assertIsNone(s)
                    else:self.assertAlmostEqual(along_velocity(u,v,bearing),s,places=12)
                self.assertEqual(layer['threshold_m_s'],.05)
                for k in ['upper_depth_m','lower_depth_m','layer_thickness_m']:self.assertEqual(layer[k],a['model_'+k])
    def test_exact_windows_frames_methods_and_branch_geometry(self):
        self.assertEqual(len({c['method_id'] for c in self.cases}),4);self.assertEqual(len({c['comparison_group'] for c in self.cases}),4)
        for c in self.cases:
            w=[500,900] if c['diagnostic_context_id']=='upper' else [900,1500];self.assertEqual(c['selection_depth_interval_m'],w);self.assertEqual(c['core_search_depth_interval_m'],w);self.assertEqual(c['primary_threshold_m_s'],.05);self.assertEqual(c['source_section_geometry'],'longitude' if c['diagnostic_branch_id']=='south-iberian' else 'latitude');self.assertIn(c['diagnostic_branch_id'],c['method_id']);self.assertIsNone(c['source_surface_component_gate_m_s'])
    def test_all_edges_censoring_and_missing_selection_preserved(self):
        for c in self.cases:
            for a in c['anchors']:
                ok=a['source_horizontal_selection_status']==p.INTERIOR and a['model_lower_depth_m'] is not None;self.assertEqual(a['lower_projection_eligible'],ok);self.assertEqual(a['layer_projection_eligible'],ok and a['model_layer_thickness_m'] is not None)
            self.assertEqual(c in self.addendum['projections'],any(a['lower_projection_eligible'] for a in c['anchors']))
    def test_adjacent_only_same_branch_context_and_no_cape_connector(self):
        for c in self.cases:
            self.assertEqual(len(c['anchors']),4)
            for a,b,s in zip(c['anchors'],c['anchors'][1:],c['segments']):
                values,used,status=interpolate(c['anchors'],(a['distance_km']+b['distance_km'])/2);self.assertEqual(used,[a,b]);self.assertEqual(s['source_anchor_ids'],[a['id'],b['id']]);self.assertEqual(a['source_section_definition']['diagnostic_branch_id'],b['source_section_definition']['diagnostic_branch_id'])
                if not(a['lower_projection_eligible'] and b['lower_projection_eligible']):self.assertIsNone(values['model_lower_depth_m']);self.assertEqual(s['projection_status'],'gap_no_projection')
    def test_source_owner_branch_frame_native_default_context_and_flags_mutations_rejected(self):
        for kind in ['owner','branch','frame','native','default','context','additive']:
            chunks=copy.deepcopy(self.chunks);d=chunks[next(iter(chunks))]
            if kind=='owner':d['entity_id']='current:portugal'
            if kind=='branch':d['diagnostic_branch_id']='west-iberian'
            if kind=='frame':d['component_bearing_degrees_true']=90
            if kind=='native':d['columns'][0]['eastward_velocity_m_s'][0]=999
            if kind=='default':d['default_diagnostic_context_id']='lower'
            if kind=='context':d['context_diagnoses']['lower']['diagnosis']['selected_column_index']=9999
            if kind=='additive':d['vertical_contexts_are_additive']=True
            with self.subTest(kind=kind),self.assertRaises((ValueError,IndexError)):p.checked_sources(self.source_manifest,chunks,self.sourceop,self.op)
    def test_missing_duplicate_or_relabelled_manifest_branches_rejected(self):
        for kind in ['missing','duplicate','branch','context']:
            m=copy.deepcopy(self.source_manifest)
            if kind=='missing':m['sections'].pop()
            if kind=='duplicate':m['sections'][-1]=copy.deepcopy(m['sections'][0])
            if kind=='branch':m['sections'][0]['diagnostic_branch_id']='wrong'
            if kind=='context':m['sections'][0]['context_diagnoses']['lower']['context_id']='upper'
            with self.subTest(kind=kind),self.assertRaises(ValueError):p.checked_sources(m,self.chunks,self.sourceop,self.op)
    def test_unselected_branch_context_cannot_borrow_other_context_or_branch(self):
        lookup=copy.deepcopy(self.lookup);stamp=self.sourceop['snapshot_times_utc'][0]
        for identity,row in lookup.items():
            if identity[0]==stamp and row[3]['diagnostic_branch_id']=='south-iberian':row[3]['context_diagnoses']['upper']['diagnosis'].update(selected_column_index=None,horizontal_selection_status='no_qualifying_interval_component_column',selected_column_threshold_layers=[])
        c=p.regional_case(stamp,'south-iberian','upper',lookup,self.sourceop,self.op);self.assertTrue(all(a['model_lower_depth_m'] is None and not a['lower_projection_eligible'] for a in c['anchors']));self.assertTrue(all(s['projection_status']=='gap_no_projection' for s in c['segments']))
    def test_no_physical_annual_independent_volume_or_pressure_layer_promotion(self):
        for c in self.cases:
            self.assertFalse(any(c['eligibility'].values()));self.assertIsNone(c['physical_thickness_m']);self.assertIsNone(c['annual_range_m']);self.assertFalse(c['whole_current_representative'])
            for k in ['vertical_contexts_are_additive','branches_are_additive','contexts_are_independent_observations','water_mass_classification_performed','current_identity_independently_validated']:self.assertFalse(c[k])
            self.assertEqual(c['new_velocity_field_requests'],0)
        self.assertFalse(self.sourceop['pressure_to_depth_conversion_performed']);self.assertEqual(self.view['counts']['whole_route_physical_depth_profiles'],0);self.assertEqual(self.view['counts']['volume_estimates'],0)
    def test_csv_old_cells_preserved_and_new_branch_context_flags_and_methods(self):
        before=list(csv.DictReader(io.StringIO(combined_csv_bytes(self.old,self.read).decode())));after=list(csv.DictReader(io.StringIO(combined_csv_bytes(self.manifest,self.reader).decode())))
        for a,b in zip(before,after):self.assertEqual(a,{k:b[k] for k in a})
        cases={c['id']:c for c in self.addendum['projections']}
        for row in after[len(before):]:
            c=cases[row['projection_id']]
            for k in ['diagnostic_branch_id','diagnostic_context_id','method_id','comparison_group']:self.assertEqual(row[k],c[k])
            for k in ['vertical_contexts_are_additive','branches_are_additive','contexts_are_independent_observations']:self.assertEqual(row[k],'False')
    def test_pins_caps_count_and_piece_corruption(self):
        for f,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256(self.read(f)).hexdigest(),pin,f)
        self.assertTrue(all(len(r)<2500000 for r in self.pieces.values()))
        with self.assertRaises(ValueError):load_inventory(self.manifest,lambda f:self.reader(f)+b' ' if f==p.ADDENDUM else self.reader(f))
        bad=copy.deepcopy(self.manifest);bad['counts']['regional_projection_scenarios']+=1
        with self.assertRaises(ValueError):load_inventory(bad,self.reader)

if __name__=='__main__':unittest.main()
