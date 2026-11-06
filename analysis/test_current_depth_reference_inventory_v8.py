import copy,csv,hashlib,io,json,unittest
from collections import Counter
import build_current_depth_reference_inventory_v8 as p
import load_current_depth_reference_inventory_v7 as prior
import load_current_depth_reference_inventory_v8 as loader


class IntervalCoreReachTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory,cls.addendum,cls.report,cls.pieces,cls.view=p.build();cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes());cls.previous=json.loads((p.ROOT/cls.op['previous_inventory_file']).read_bytes());cls.before=prior.load_inventory(cls.previous,lambda f:(p.ROOT/f).read_bytes());cls.parts=prior.read_parts(cls.previous,lambda f:(p.ROOT/f).read_bytes())
    def reader(self,f):return self.pieces[f] if f in self.pieces else (p.ROOT/f).read_bytes()
    def assembled(self,a=None,report=None):return loader.assemble(*self.parts,[(a or self.addendum,report or self.report)])
    def test_738_prior_rows_contexts_and_record_fields_preserved(self):
        self.assertEqual(self.view['evidence'][:738],self.before['evidence']);self.assertEqual(self.inventory['base'],self.previous['base']);self.assertEqual(self.inventory['addenda'][:-1],self.previous['addenda'])
        for k,v in self.before['source_contexts'].items():self.assertEqual(self.view['source_contexts'][k],v)
        for old,new in zip(self.before['records'],self.view['records']):
            self.assertEqual(new['depth_reference_ids'][:len(old['depth_reference_ids'])],old['depth_reference_ids']);self.assertEqual({k:v for k,v in old.items() if k!='depth_reference_ids'},{k:v for k,v in new.items() if k!='depth_reference_ids'})
    def test_expected_owner_counts_and_depths(self):
        rows=self.addendum['evidence'];self.assertEqual(Counter(r['entity_id'] for r in rows),{'current:north-cape':1,'current:norwegian-coastal':5,'current:east-greenland-coastal':7});self.assertEqual(sorted(r['lower_bound_m'] for r in rows),[150,200,200,200,200,250,250,250,250,250,300,300,350])
    def test_north_cape_detached_upper_crossing_preserved(self):
        r=next(x for x in self.addendum['evidence'] if x['entity_id']=='current:north-cape')['source_audit_record'];self.assertFalse(r['source_surface_connection_established']);self.assertEqual(r['primary_layer']['upper_status'],'adjacent_isotach_crossing');self.assertGreater(r['primary_layer']['upper_depth_m'],90);self.assertEqual(r['core_depth_m'],125);self.assertEqual(r['lower_bound_m'],350)
        self.assertEqual(sum(x['source_audit_record']['source_surface_connection_established'] for x in self.addendum['evidence']),12)
    def test_frames_windows_and_null_surface_gate(self):
        expected={'current:north-cape':(90,[50,350]),'current:norwegian-coastal':(0,[0,100]),'current:east-greenland-coastal':(225,[0,100])}
        for row in self.addendum['evidence']:
            r=row['source_audit_record'];frame,window=expected[r['entity_id']];self.assertEqual(r['component_bearing_degrees_true'],frame);self.assertEqual(r['selection_depth_interval_m'],window);self.assertEqual(r['core_search_depth_interval_m'],window);self.assertIsNone(r['surface_component_gate_m_s']);self.assertEqual(r['primary_threshold_m_s'],.1)
    def test_all_96_cases_retained_only_13_eligible_admitted(self):
        self.assertEqual(sum(len(s['records']) for s in self.report['studies']),96);self.assertEqual(len(self.addendum['evidence']),13);pointers={r['source_pointer'] for r in self.addendum['evidence']};self.assertEqual(len(pointers),13)
        for si,s in enumerate(self.report['studies']):
            for ri,r in enumerate(s['records']):self.assertEqual('/studies/'+str(si)+'/records/'+str(ri) in pointers,r['reach_eligible'])
    def test_omitted_duplicate_or_excluded_records_rejected(self):
        for mode in ['omit','duplicate','excluded']:
            a=copy.deepcopy(self.addendum)
            if mode=='omit':a['evidence'].pop()
            elif mode=='duplicate':a['evidence'].append(copy.deepcopy(a['evidence'][0]))
            else:a['evidence'][0]['source_pointer']='/studies/0/records/0'
            with self.subTest(mode=mode),self.assertRaises(ValueError):self.assembled(a)
    def test_exact_report_pointer_hash_and_native_provenance_required(self):
        for key,value in [('source_pointer','/studies/00/records/0'),('source_sha256','bad'),('source_file','other.json'),('source_locator','other-profile')]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.assembled(a)
        for key,value in [('source_section_sha256','bad'),('selected_column_index',-1),('core_native_index',0),('next_native_depth_m',999),('branch_scope','whole route')]:
            a=copy.deepcopy(self.addendum);a['evidence'][0]['source_audit_record'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.assembled(a)
    def test_no_exact_depth_span_annual_geometry_or_volume_promotion(self):
        for key,value in [('approximate_value_m',350),('thickness_m',350),('upper_boundary_m',0),('lower_boundary_m',350),('range_m',[150,350]),('annual_range_m',[150,350]),('calendar_months',[12]),('observed_period','2022'),('lower_bound_operator','>'),('volume_eligible',True),('physical_current_bottom_established',True),('reference_route_projection_eligible',True),('independently_validated_axis',True)]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.assembled(a)
    def test_owner_context_and_surface_assumptions_cannot_change(self):
        for mode in ['owner','context','surface']:
            a=copy.deepcopy(self.addendum)
            if mode=='owner':a['evidence'][0]['entity_id']='current:norwegian'
            elif mode=='context':next(iter(a['source_contexts'].values()))['core_search_depth_interval_m']=[0,100]
            else:a['evidence'][0]['source_audit_record']['source_surface_connection_established']=True
            with self.subTest(mode=mode),self.assertRaises(ValueError):self.assembled(a)
    def test_missing_native_next_sample_is_not_zero_or_domain_end(self):
        for mode in ['zero','index','domain','core','threshold']:
            report=copy.deepcopy(self.report);r=next(r for s in report['studies'] for r in s['records'] if r['reach_eligible'])
            if mode=='zero':r['next_signed_component_m_s']=0
            elif mode=='index':r['next_native_index']=r['last_connected_native_index']
            elif mode=='domain':r['censoring_kind']='native_vertical_domain_limit'
            elif mode=='core':r['core_depth_m']=0
            else:r['primary_threshold_m_s']=.01
            with self.subTest(mode=mode),self.assertRaises(ValueError):loader.eligible_records(report)
    def test_snapshot_dates_are_not_observations_or_seasonal_means(self):
        for row in self.addendum['evidence']:
            r=row['source_audit_record'];self.assertIn(r['snapshot_time_utc'],['2022-03-15T00:00:00Z','2022-06-15T00:00:00Z','2022-09-15T00:00:00Z','2022-12-15T00:00:00Z']);self.assertEqual(row['phase_label'],r['snapshot_time_utc']);self.assertIsNone(row['calendar_months']);self.assertIsNone(row['annual_range_m']);self.assertFalse(row['independent_observation_count_claimed'])
    def test_hash_pinned_report_and_addendum_json_csv_cannot_change(self):
        for piece in [self.addendum['derived_source_report'],self.inventory['addenda'][-1]['json'],self.inventory['addenda'][-1]['csv']]:
            with self.subTest(file=piece['file']),self.assertRaises(ValueError):loader.load_inventory(self.inventory,lambda f:self.reader(f)+b' ' if f==piece['file'] else self.reader(f))
    def test_all_old_csv_cells_preserved_and_new_cells_typed(self):
        old=list(csv.DictReader(io.StringIO(prior.combined_csv_bytes(self.previous,lambda f:(p.ROOT/f).read_bytes()).decode())));new=list(csv.DictReader(io.StringIO(loader.combined_csv_bytes(self.inventory,self.reader).decode())));self.assertEqual(len(new),751)
        for a,b in zip(old,new):self.assertEqual(a,{k:b[k] for k in a})
        for r in new[738:]:self.assertEqual(r['metric'],loader.METRIC);self.assertEqual(r['lower_bound_operator'],'>=');self.assertEqual(r['thickness_m'],'');self.assertEqual(r['volume_eligible'],'False');self.assertEqual(r['source_contiguous_support_start'],'original_primary_core')
    def test_counts_pins_and_fixed_caps(self):
        self.assertEqual(self.view['counts']['depth_references'],751);self.assertEqual(self.view['counts']['identities_with_scoped_depth_reference'],101);self.assertEqual(self.view['counts']['whole_route_depth_profiles'],0);self.assertEqual(self.view['counts']['volume_estimates'],0);self.assertEqual(self.view['metric_counts'][loader.METRIC],13)
        for f,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin,f)
        self.assertTrue(all(len(raw)<2500000 for raw in self.pieces.values()));self.assertLess(sum(map(len,self.pieces.values())),3000000)


if __name__=='__main__':unittest.main()
