import copy,csv,hashlib,io,json,unittest
import build_current_depth_reference_inventory_v10 as p
import load_current_depth_reference_inventory_v9 as prior
import load_current_depth_reference_inventory_v10 as loader


class FreshComponentAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory,cls.addendum,cls.bundle,cls.pieces,cls.view=p.build();cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes());cls.previous=json.loads((p.ROOT/cls.op['previous_inventory_file']).read_bytes());cls.before=prior.load_inventory(cls.previous,lambda f:(p.ROOT/f).read_bytes());cls.parts=prior.read_parts(cls.previous,lambda f:(p.ROOT/f).read_bytes())
    def reader(self,f):return self.pieces[f] if f in self.pieces else (p.ROOT/f).read_bytes()
    def assembled(self,a=None,bundle=None):return loader.assemble(*self.parts,[(a or self.addendum,bundle or self.bundle)])
    def test_752_prior_rows_contexts_and_record_fields_preserved(self):
        self.assertEqual(self.view['evidence'][:752],self.before['evidence']);self.assertEqual(self.inventory['base'],self.previous['base']);self.assertEqual(self.inventory['addenda'][:-1],self.previous['addenda'])
        for k,v in self.before['source_contexts'].items():self.assertEqual(self.view['source_contexts'][k],v)
        for old,new in zip(self.before['records'],self.view['records']):
            self.assertEqual(new['depth_reference_ids'][:len(old['depth_reference_ids'])],old['depth_reference_ids']);self.assertEqual({k:v for k,v in old.items() if k!='depth_reference_ids'},{k:v for k,v in new.items() if k!='depth_reference_ids'})
    def test_all_five_native_results_reproduce_and_keep_original_core_depths(self):
        records=loader.reproduce(self.bundle);self.assertEqual(len(records),5);self.assertEqual([r['classification']['original_core_depth_m'] for r in records],[0,0,25,20,0]);self.assertTrue(all(r['classification']['core_reselected'] is False for r in records))
        for row,expected in zip(self.addendum['evidence'],[158.21967915556252,128.33347461218955,166.66666666666666,97.02122478795503,96.84184108818953]):self.assertAlmostEqual(row['approximate_value_m'],expected)
    def test_exact_native_brackets_are_not_confidence_or_annual_ranges(self):
        self.assertEqual([r['source_native_bracket_m'] for r in self.addendum['evidence']],[[150,200],[125,150],[150,200],[90,100],[90,100]])
        for r in self.addendum['evidence']:
            self.assertFalse(r['source_native_bracket_is_confidence_interval']);self.assertFalse(r['source_native_bracket_is_annual_range']);self.assertIsNone(r['uncertainty_m']);self.assertIsNone(r['range_m']);self.assertIsNone(r['annual_range_m'])
    def test_old_component_minimum_reaches_remain_distinct(self):
        old=[r for r in self.before['evidence'] if r['metric']=='derived_core_connected_component_penetration_lower_bound' and r['entity_id']=='current:norwegian-coastal'];self.assertEqual(len(old),5)
        for r in old:self.assertEqual(r,next(e for e in self.view['evidence'] if e['id']==r['id']));self.assertIn(r['lower_bound_m'],[250,300])
        self.assertTrue(all(r['metric']=='derived_conditional_fresh_component_lower_boundary_depth' for r in self.addendum['evidence']))
    def test_salinity_frame_core_and_classification_cannot_be_changed(self):
        for mode in ['salinity','velocity','core','result','time','stencil','units']:
            b=copy.deepcopy(self.bundle);profile=b['profiles'][0]
            if mode=='salinity':profile['practical_salinity_columns'][1][0]=36
            elif mode=='velocity':profile['selected_original_component_m_s'][0]=.05
            elif mode=='core':profile['original_audit_record']['core_native_index']=1
            elif mode=='result':profile['classification']['lower']['boundary_depth_m']=250
            elif mode=='time':profile['source_returned_timestamp_utc']='2022-03-15T03:00:00Z'
            elif mode=='stencil':profile['native_longitude_indices_inclusive'][0]+=1
            else:b['report']['source_variable_attributes']['units']='g/kg'
            with self.subTest(mode=mode),self.assertRaises(ValueError):loader.reproduce(b)
    def test_source_report_or_original_audit_linkage_cannot_be_changed(self):
        for mode in ['owner','pointer','record','profile','missing']:
            b=copy.deepcopy(self.bundle)
            if mode=='owner':b['report']['records'][0]['original_audit_record']['entity_id']='current:norwegian'
            elif mode=='pointer':b['report']['records'][0]['source_audit_pointer']='/studies/1/records/-1'
            elif mode=='record':b['report']['records'][0]['classification']['lower']['boundary_depth_m']=250
            elif mode=='profile':b['report']['records'][0]['profile']['sha256']='wrong'
            else:b['profiles'].pop()
            with self.subTest(mode=mode),self.assertRaises(ValueError):loader.reproduce(b)
    def test_no_physical_bottom_span_volume_or_axis_validation_promotion(self):
        for key,value in [('lower_boundary_m',158),('upper_boundary_m',0),('thickness_m',158),('lower_bound_m',158),('lower_bound_operator','>='),('volume_eligible',True),('physical_current_bottom_established',True),('independently_validated_axis',True),('reference_route_projection_eligible',True),('same_source_width_reference_id','width')]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.assembled(a)
    def test_date_and_population_not_annual_envelope_or_observed_series(self):
        r=self.addendum['evidence'][0];self.assertEqual(r['phase_label'],'2022-03-15T00:00:00Z');self.assertEqual(r['source_classification']['practical_salinity_exclusive_upper_threshold'],35);self.assertEqual(r['source_classification']['velocity_threshold_m_s'],.1)
        for k in ['observed_period','calendar_months','annual_range_m']:self.assertIsNone(r[k])
        for key,value in [('calendar_months',[3]),('annual_range_m',[97,167]),('observed_period','2022'),('whole_current_representative',True),('seasonal_playback_eligible',True),('independent_observation_count_claimed',True)]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.assembled(a)
    def test_native_resolution_and_exact_source_provenance_cannot_change(self):
        for key,value in [('source_native_bracket_m',[97,167]),('source_native_bracket_is_confidence_interval',True),('source_pointer','/classification/upper'),('source_sha256','wrong'),('source_report_pointer','/records/-1'),('source_report_sha256','wrong')]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.assembled(a)
    def test_missing_duplicate_or_extra_reference_rejected(self):
        for mode in ['omit','duplicate']:
            a=copy.deepcopy(self.addendum)
            if mode=='omit':a['evidence'].pop()
            else:a['evidence'].append(copy.deepcopy(a['evidence'][0]))
            with self.subTest(mode=mode),self.assertRaises(ValueError):self.assembled(a)
    def test_context_ownership_threshold_and_support_start_cannot_change(self):
        for key,value in [('entity_id','current:norwegian'),('practical_salinity_exclusive_upper_threshold',35.16),('velocity_threshold_m_s',.05),('support_start','surface_reselected_core')]:
            a=copy.deepcopy(self.addendum);a['source_contexts'][loader.CONTEXT][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.assembled(a)
    def test_source_profile_report_velocity_and_json_csv_hashes_required(self):
        files=[self.addendum['derived_source_report']['file'],self.addendum['original_velocity_audit_report']['file'],loader.DIRECTORY+'target-1.json',self.bundle['report']['records'][0]['original_audit_record']['source_section_file'],self.inventory['addenda'][-1]['json']['file'],self.inventory['addenda'][-1]['csv']['file']]
        for path in files:
            with self.subTest(file=path),self.assertRaises(ValueError):loader.load_inventory(self.inventory,lambda f:self.reader(f)+b' ' if f==path else self.reader(f))
    def test_all_prior_csv_cells_preserved_and_new_classification_typed(self):
        old=list(csv.DictReader(io.StringIO(prior.combined_csv_bytes(self.previous,lambda f:(p.ROOT/f).read_bytes()).decode())));new=list(csv.DictReader(io.StringIO(loader.combined_csv_bytes(self.inventory,self.reader).decode())));self.assertEqual(len(new),757)
        for a,b in zip(old,new):self.assertEqual(a,{k:b[k] for k in a})
        for r in new[752:]:self.assertEqual(r['metric'],loader.METRIC);self.assertEqual(r['thickness_m'],'');self.assertEqual(r['volume_eligible'],'False');self.assertIn('salinity',r['source_classification'])
    def test_counts_input_pins_and_fixed_caps(self):
        self.assertEqual(self.view['counts']['depth_references'],757);self.assertEqual(self.view['counts']['identities_with_scoped_depth_reference'],101);self.assertEqual(self.view['counts']['whole_route_depth_profiles'],0);self.assertEqual(self.view['counts']['volume_estimates'],0);self.assertEqual(self.view['metric_counts'][loader.METRIC],5)
        for f,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin,f)
        self.assertTrue(all(len(raw)<2500000 for raw in self.pieces.values()));self.assertLess(sum(map(len,self.pieces.values())),3000000)


if __name__=='__main__':unittest.main()
