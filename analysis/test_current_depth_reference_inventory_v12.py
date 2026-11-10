import copy,csv,hashlib,io,json,unittest
from collections import Counter
import build_current_depth_reference_inventory_v12 as p
import load_current_depth_reference_inventory_v11 as prior
import load_current_depth_reference_inventory_v12 as loader


class CompleteCoastalAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory,cls.addendum,cls.bundle,cls.pieces,cls.view=p.build();cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes());cls.previous=json.loads((p.ROOT/cls.op['previous_inventory_file']).read_bytes());cls.before=prior.load_inventory(cls.previous,lambda f:(p.ROOT/f).read_bytes());cls.parts=prior.read_parts(cls.previous,lambda f:(p.ROOT/f).read_bytes())
    def reader(self,f):return self.pieces[f] if f in self.pieces else (p.ROOT/f).read_bytes()
    def assembled(self,a=None,bundle=None):return loader.assemble(*self.parts,[(a or self.addendum,bundle or self.bundle)])
    def test_all762_prior_evidence_contexts_record_fields_and_pieces_preserved(self):
        self.assertEqual(self.view['evidence'][:762],self.before['evidence']);self.assertEqual(self.inventory['base'],self.previous['base']);self.assertEqual(self.inventory['addenda'][:-1],self.previous['addenda'])
        for k,v in self.before['source_contexts'].items():self.assertEqual(self.view['source_contexts'][k],v)
        for old,new in zip(self.before['records'],self.view['records']):
            self.assertEqual(new['depth_reference_ids'][:len(old['depth_reference_ids'])],old['depth_reference_ids']);self.assertEqual({k:v for k,v in old.items() if k!='depth_reference_ids'},{k:v for k,v in new.items() if k!='depth_reference_ids'})
    def test_all32_native_outcomes_reproduce27_crossings_and5_unclassified(self):
        cases=loader.reproduce(self.bundle);self.assertEqual(len(cases),32);self.assertEqual(Counter(c['classification']['status'] for c in cases),{'conditional_fresh_component_core_supported':27,'original_horizontal_axis_unresolved':2,'original_velocity_core_not_in_declared_fresh_class':3});self.assertEqual(sum((c['classification'].get('lower') or {}).get('status')=='adjacent_native_joint_predicate_crossing' for c in cases),27)
    def test_only22_new_refs_and5_old_refs_reused_unchanged(self):
        audit=self.bundle['admission_report'];self.assertEqual(audit['new_reference_count'],22);self.assertEqual(len(audit['reused_reference_ids']),5);self.assertEqual(len(self.addendum['evidence']),22);self.assertEqual(self.view['metric_counts'][loader.METRIC],27)
        old={r['id']:r for r in self.before['evidence'] if r['metric']==loader.METRIC};self.assertEqual(set(audit['reused_reference_ids']),set(old))
        for key,row in old.items():self.assertEqual(row,next(r for r in self.view['evidence'] if r['id']==key));self.assertNotIn(key,{r['id'] for r in self.addendum['evidence']})
    def test_owner_specific_rules_9_ncc_and13_egcc_new_rows(self):
        self.assertEqual(Counter(r['entity_id'] for r in self.addendum['evidence']),{'current:norwegian-coastal':9,'current:east-greenland-coastal':13})
        for entity,(bearing,salt) in loader.source.RULES.items():
            context=self.addendum['source_contexts'][loader.context_id(entity)];self.assertEqual(context['component_bearing_degrees_true'],bearing);self.assertEqual(context['practical_salinity_exclusive_upper_threshold'],salt);self.assertEqual(context['velocity_threshold_m_s'],.1);self.assertFalse(context['published_coastal_front_foot_definition_reproduced'])
    def test_all32_admission_outcomes_retain_unclassified_cases_without_zero(self):
        cases=self.bundle['admission_report']['cases'];self.assertEqual(len(cases),32);self.assertEqual(Counter(c['admission_status'] for c in cases),{'NEW_CONDITIONAL_DESCRIPTOR_ADMITTED':22,'EXACT_EXISTING_REFERENCE_REUSED_UNCHANGED':5,'UNRESOLVED_OR_UNCLASSIFIED_NO_REFERENCE':5})
        for c in cases:
            if c['admission_status']=='UNRESOLVED_OR_UNCLASSIFIED_NO_REFERENCE':self.assertIsNone(c['reference_id']);self.assertIn(c['classification']['status'],['original_horizontal_axis_unresolved','original_velocity_core_not_in_declared_fresh_class'])
    def test_salinity_and_stored_classification_cannot_change(self):
        for mode in ['salt','classification','frame','threshold']:
            b=copy.deepcopy(self.bundle);profile=b['profiles'][1]
            if mode=='salt':profile['practical_salinity_columns'][profile['original_selected_column_index']][0]=49
            elif mode=='classification':profile['classification']['lower']['boundary_depth_m']=999
            elif mode=='frame':profile['component_bearing_degrees_true']=225
            else:profile['practical_salinity_exclusive_upper_threshold']=34
            with self.subTest(mode=mode),self.assertRaises(ValueError):loader.reproduce(b)
    def test_every_native_coordinate_depth_date_and_selected_core_required(self):
        for mode in ['outer_column','depth','date','timeindex','selection','primary_layer']:
            b=copy.deepcopy(self.bundle);profile=b['profiles'][1]
            if mode=='outer_column':profile['native_longitudes_degrees_east'][0]+=.08
            elif mode=='depth':profile['depth_levels_m'][1]+=.5
            elif mode=='date':profile['source_returned_timestamp_utc']='2022-03-15T03:00:00Z'
            elif mode=='timeindex':profile['source_time_index']+=1
            elif mode=='selection':profile['original_selected_column_index']+=1
            else:profile['original_primary_layer']['core_index']+=1
            with self.subTest(mode=mode),self.assertRaises(ValueError):loader.reproduce(b)
    def test_original_velocity_axis_selection_must_reproduce(self):
        b=copy.deepcopy(self.bundle);file=b['expected_files'][0];b['sections'][file]['diagnosis']['horizontal_selection_status']='fabricated_interior_axis'
        with self.assertRaises(ValueError):loader.reproduce(b)
    def test_old_descriptor_changes_fail_instead_of_replacement_or_duplication(self):
        for key,value in [('approximate_value_m',159),('source_native_bracket_m',[125,150]),('phase_label','2022-03-16T00:00:00Z')]:
            before=copy.deepcopy(self.before);old=next(r for r in before['evidence'] if r['metric']==loader.METRIC);old[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):loader.admission(before,self.bundle,self.addendum)
        before=copy.deepcopy(self.before);old=next(r for r in before['evidence'] if r['metric']==loader.METRIC);before['evidence'].append(copy.deepcopy(old))
        with self.assertRaises(ValueError):loader.admission(before,self.bundle,self.addendum)
    def test_native_bracket_not_physical_bottom_uncertainty_or_annual_range(self):
        for key,value in [('lower_boundary_m',100),('upper_boundary_m',0),('thickness_m',100),('range_m',[8,177]),('annual_range_m',[8,177]),('uncertainty_m',10),('calendar_months',[3]),('observed_period','2022'),('physical_current_bottom_established',True),('volume_eligible',True),('reference_route_projection_eligible',True),('same_source_width_reference_id','width')]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.assembled(a)
    def test_changed_or_missing_admission_roles_and_reused_ids_rejected(self):
        for mode in ['reuse','count','gap']:
            b=copy.deepcopy(self.bundle);audit=b['admission_report']
            if mode=='reuse':audit['reused_reference_ids'][0]='wrong'
            elif mode=='count':audit['new_reference_count']=27
            else:next(c for c in audit['cases'] if c['reference_id'] is None)['reference_id']='false-depth'
            with self.subTest(mode=mode),self.assertRaises(ValueError):self.assembled(bundle=b)
    def test_omitted_duplicate_or_wrong_source_reference_rejected(self):
        for mode in ['omit','duplicate','pointer','owner']:
            a=copy.deepcopy(self.addendum)
            if mode=='omit':a['evidence'].pop()
            elif mode=='duplicate':a['evidence'].append(copy.deepcopy(a['evidence'][0]))
            elif mode=='pointer':a['evidence'][0]['source_pointer']='/classification/upper'
            else:a['evidence'][0]['entity_id']='current:east-greenland'
            with self.subTest(mode=mode),self.assertRaises(ValueError):self.assembled(a)
    def test_source_profiles_controls_operator_ledger_and_admission_hashes_required(self):
        files=[self.addendum['source_operator']['file'],self.addendum['derived_source_report']['file'],self.addendum['original_velocity_audit_report']['file'],loader.DIRECTORY+self.bundle['report']['profiles'][0]['file'],self.bundle['controls'][0][0],loader.DIRECTORY+'transport-ledger.json',p.AUDIT,self.inventory['addenda'][-1]['json']['file'],self.inventory['addenda'][-1]['csv']['file']]
        for file in files:
            with self.subTest(file=file),self.assertRaises(ValueError):loader.load_inventory(self.inventory,lambda f:self.reader(f)+b' ' if f==file else self.reader(f))
    def test_control_mismatch_and_budget_receipt_changes_cannot_pass(self):
        b=copy.deepcopy(self.bundle);b['controls'][0][1]['practical_salinity_columns'][0][0]=49
        with self.assertRaises(ValueError):loader.reproduce(b)
        for key,value in [('additional_retry_scalars_reserved',0),('maximum_joint_native_cell_units',300000),('conservative_retained_velocity_and_reserved_salinity_bytes',0)]:
            b=copy.deepcopy(self.bundle);b['ledger'][key]=value;b['report']['transport'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):loader.reproduce(b)
    def test_all_old_csv_cells_preserved_and_new_case_provenance_typed(self):
        old=list(csv.DictReader(io.StringIO(prior.combined_csv_bytes(self.previous,lambda f:(p.ROOT/f).read_bytes()).decode())));new=list(csv.DictReader(io.StringIO(loader.combined_csv_bytes(self.inventory,self.reader).decode())));self.assertEqual(len(new),784)
        for a,b in zip(old,new):self.assertEqual(a,{k:b[k] for k in a})
        for row in new[762:]:self.assertEqual(row['metric'],loader.METRIC);self.assertEqual(row['thickness_m'],'');self.assertEqual(row['volume_eligible'],'False');self.assertEqual(row['source_native_bracket_is_annual_range'],'False')
    def test_counts_and_fixed_publication_caps_and_pins(self):
        self.assertEqual(self.view['counts']['depth_references'],784);self.assertEqual(self.view['counts']['identities_with_scoped_depth_reference'],101);self.assertEqual(self.view['counts']['whole_route_depth_profiles'],0);self.assertEqual(self.view['counts']['volume_estimates'],0);self.assertEqual(self.view['metric_counts'][loader.METRIC],27)
        for file,pin in self.op['input_sha256'].items():self.assertFalse(file.startswith('.pytest_cache/'));self.assertEqual(hashlib.sha256((p.ROOT/file).read_bytes()).hexdigest(),pin,file)
        self.assertTrue(all(len(raw)<2500000 for raw in self.pieces.values()));self.assertLess(sum(map(len,self.pieces.values())),3000000)


if __name__=='__main__':unittest.main()
