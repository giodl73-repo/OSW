import copy,csv,hashlib,io,json,unittest
import build_current_depth_reference_inventory_v4 as p
import load_current_depth_reference_inventory_v3 as prior
import load_current_depth_reference_inventory_v4 as loader
from derive_native_primary_penetration_bounds_v2 import bound_at_original_node,INTERIOR
from latitude_depth_section_geometry_v1 import validate_retained,canonical_hash


class NativePrimaryReachTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes());cls.inventory,cls.addendum,cls.report,cls.pieces,cls.view=p.build();read=lambda f:json.loads((p.ROOT/f).read_bytes());cls.previous=read(cls.op['previous_inventory_file']);cls.before=prior.load_inventory(cls.previous,lambda f:(p.ROOT/f).read_bytes());cls.parts=prior.read_parts(cls.previous,lambda f:(p.ROOT/f).read_bytes());cls.sop=read(cls.op['source_operator_file'])
    def reader(self,f):return self.pieces[f] if f in self.pieces else (p.ROOT/f).read_bytes()
    def assembled(self,a=None,report=None):return loader.assemble(*self.parts,[(a or self.addendum,report or self.report)])
    def fixture(self,domain=False):
        z=[0.,100.,200.,300.];v=[.2,.3,.2,.15 if domain else None]
        layer={'threshold_m_s':.1,'upper_depth_m':0.,'upper_status':'surface_bounded_layer','lower_depth_m':None,'layer_thickness_m':None,'lower_status':'censored_at_sample_domain_edge' if domain else 'censored_before_missing_or_dry_level','lower_last_connected_depth_m':300. if domain else 200.}
        return {'depth_levels_m':z,'columns':[{'signed_reference_component_m_s':v}],'diagnosis':{'selected_column_index':0,'horizontal_selection_status':INTERIOR,'selected_column_threshold_layers':[layer]}},{'primary_threshold_m_s':.1}
    def test_723_prior_refs_all_other_record_fields_and_pieces_preserved(self):
        self.assertEqual(self.view['evidence'][:723],self.before['evidence']);self.assertEqual(self.inventory['base'],self.previous['base']);self.assertEqual(self.inventory['addenda'][:-1],self.previous['addenda'])
        for old in self.before['records']:
            new=next(r for r in self.view['records'] if r['entity_id']==old['entity_id']);self.assertEqual(new['depth_reference_ids'][:len(old['depth_reference_ids'])],old['depth_reference_ids']);self.assertEqual({k:v for k,v in old.items() if k!='depth_reference_ids'},{k:v for k,v in new.items() if k!='depth_reference_ids'})
    def test_whole_original_study_and_v29_cases_audited(self):
        a=self.report['source_audit'];self.assertEqual((a['sections_verified'],a['native_profiles_verified'],a['native_cell_pairs_verified'],a['original_component_requests_verified'],a['decoded_velocity_array_bytes']),(20,1500,60000,40,480000));self.assertTrue(a['original_region_cases_and_gaps_unchanged']);self.assertEqual(a['new_field_requests'],0);self.assertEqual(len(self.report['records']),20);self.assertEqual(set(r['entity_id'] for r in self.report['records']),set(self.op['target_entities']))
    def test_all_and_only_eligible_records_and_excluded_edge_remain(self):
        self.assertEqual(len(self.addendum['evidence']),self.report['admitted_supported_reach_bounds']);self.assertGreater(self.report['admitted_supported_reach_bounds'],0)
        pointers=[int(r['source_pointer'].split('/')[-1]) for r in self.addendum['evidence']];self.assertEqual(pointers,[i for i,r in enumerate(self.report['records']) if r['reach_eligible']])
        edge=[r for r in self.report['records'] if r['horizontal_selection_status']!=INTERIOR];self.assertTrue(edge);self.assertTrue(all(not r['reach_eligible'] for r in edge));self.assertTrue(any(not r['reach_eligible'] and r['primary_layer'] and r['primary_layer']['lower_depth_m'] is not None for r in self.report['records']))
    def test_real_bound_profiles_contiguous_and_censoring_distinct(self):
        for r in self.report['records']:
            if not r['reach_eligible']:continue
            s=json.loads((p.ROOT/r['source_section_file']).read_bytes());v=s['columns'][r['selected_column_index']]['signed_reference_component_m_s'];i=r['last_connected_native_index'];self.assertEqual(s['depth_levels_m'][i],r['lower_bound_m']);self.assertTrue(all(x is not None and x>r['primary_threshold_m_s'] for x in v[:i+1]));self.assertIsNone(r['primary_layer']['lower_depth_m']);self.assertIsNone(r['primary_layer']['layer_thickness_m'])
            if r['censoring_kind']=='native_vertical_domain_limit':self.assertEqual(i,len(v)-1);self.assertIsNone(r['next_native_index']);self.assertEqual(r['lower_bound_m'],s['depth_levels_m'][-1])
            else:self.assertEqual(r['censoring_kind'],'missing_signed_component_level');self.assertIsNone(v[i+1]);self.assertEqual(r['next_native_depth_m'],s['depth_levels_m'][i+1])
    def test_synthetic_missing_and_domain_bounds_have_distinct_next_level(self):
        for domain in [False,True]:
            s,c=self.fixture(domain);r=bound_at_original_node(s,c);self.assertTrue(r['reach_eligible']);self.assertEqual(r['lower_bound_m'],300. if domain else 200.);self.assertEqual(r['censoring_kind'],'native_vertical_domain_limit' if domain else 'missing_signed_component_level');self.assertEqual(r['next_native_index'],None if domain else 3)
    def test_no_interior_missing_cutoff_bridge_or_false_domain_endpoint(self):
        for domain in [False,True]:
            for value in [None,.1,.05,float('nan')]:
                s,c=self.fixture(domain);s['columns'][0]['signed_reference_component_m_s'][1]=value
                with self.subTest(domain=domain,value=value),self.assertRaises(ValueError):bound_at_original_node(s,c)
        s,c=self.fixture(True);s['diagnosis']['selected_column_threshold_layers'][0]['lower_last_connected_depth_m']=200.
        with self.assertRaises(ValueError):bound_at_original_node(s,c)
    def test_original_axis_detachment_and_no_weaker_layer_replacement(self):
        for domain in [False,True]:
            s,c=self.fixture(domain);s['diagnosis']['horizontal_selection_status']='section_gate_edge_maximum_axis_unresolved';self.assertFalse(bound_at_original_node(s,c)['reach_eligible']);s,c=self.fixture(domain);s['diagnosis']['selected_column_threshold_layers'][0].update(upper_status='adjacent_isotach_crossing',upper_depth_m=50.);self.assertFalse(bound_at_original_node(s,c)['reach_eligible'])
            s,c=self.fixture(domain);s['diagnosis']['selected_column_threshold_layers'].append({'threshold_m_s':.05,'lower_depth_m':250.});self.assertEqual(bound_at_original_node(s,c)['lower_bound_m'],300. if domain else 200.)
    def test_owner_context_frame_and_original_cutoff_cannot_be_substituted(self):
        for key,value in [('entity_id','current:florida'),('source_primary_threshold_m_s',.05),('source_surface_component_gate_m_s',.01),('source_component_bearing_degrees_true',90),('source_core_search_depth_interval_m',[0,500]),('source_context_id','wrong')]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.assembled(a)
        a=copy.deepcopy(self.addendum);first=a['evidence'][0];first['source_context_id']=next(k for k,v in a['source_contexts'].items() if v['entity_id']!=first['entity_id'])
        with self.assertRaises(ValueError):self.assembled(a)
    def test_no_exact_depth_domain_bottom_thickness_annual_or_volume_promotion(self):
        for key,value in [('approximate_value_m',5000),('range_m',[400,5000]),('upper_bound_m',5000),('lower_bound_operator','>'),('lower_boundary_m',5000),('thickness_m',5000),('annual_range_m',[100,5000]),('source_native_endpoint_is_current_bottom',True),('source_missing_values_interpreted_as_bed',True),('source_bathymetry_used',True),('volume_eligible',True),('reference_route_projection_eligible',True)]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.assembled(a)
    def test_native_censoring_class_next_level_and_provenance_mutations_rejected(self):
        for key,value in [('source_censoring_kind','resolved'),('source_next_native_level_exists','false'),('source_next_native_depth_m',9999),('source_native_level_count',39),('source_native_domain_deep_limit_m',4000),('source_last_connected_velocity_m_s',999),('source_selected_column_index',999),('source_raw_profile_ref','wrong'),('source_raw_section_sha256','bad')]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.assembled(a)
    def test_exact_report_pointers_hashes_and_values(self):
        for r in self.addendum['evidence']:
            record=self.report['records'][int(r['source_pointer'].split('/')[-1])];self.assertEqual(r['entity_id'],record['entity_id']);self.assertEqual(r['lower_bound_m'],record['lower_bound_m']);self.assertEqual(r['source_file'],p.REPORT);self.assertEqual(r['source_sha256'],hashlib.sha256(self.pieces[p.REPORT]).hexdigest())
        a=copy.deepcopy(self.addendum);a['evidence'][0]['source_pointer']='/records/-1'
        with self.assertRaises(ValueError):self.assembled(a)
    def test_source_frame_component_and_position_mutations_rejected(self):
        r=next(r for r in self.report['records'] if r['reach_eligible']);s=json.loads((p.ROOT/r['source_section_file']).read_bytes());config={**self.sop,**self.sop['currents'][r['entity_id']]}
        for kind in ['frame','component','position']:
            bad=copy.deepcopy(s)
            if kind=='frame':bad['component_bearing_degrees_true']=90
            if kind=='component':bad['columns'][0]['signed_reference_component_m_s'][0]=999.;bad['decoded_columns_sha256']=canonical_hash(bad['columns'])
            if kind=='position':bad['columns'][0]['sampled_lon_lat'][1]+=.1;bad['decoded_columns_sha256']=canonical_hash(bad['columns'])
            with self.subTest(kind=kind),self.assertRaises(ValueError):validate_retained(bad,config)
    def test_old_csv_cells_and_new_bound_types_preserved(self):
        old=list(csv.DictReader(io.StringIO(prior.combined_csv_bytes(self.previous,lambda f:(p.ROOT/f).read_bytes()).decode())));new=list(csv.DictReader(io.StringIO(loader.combined_csv_bytes(self.inventory,self.reader).decode())));self.assertEqual(len(new),723+len(self.addendum['evidence']))
        for a,b in zip(old,new):self.assertEqual(a,{k:b[k] for k in a})
        for r in new[723:]:self.assertEqual(r['approximate_value_m'],'');self.assertEqual(r['lower_bound_operator'],'>=');self.assertEqual(r['annual_range_m'],'');self.assertEqual(r['source_native_endpoint_is_current_bottom'],'False')
    def test_report_and_addendum_piece_hash_changes_rejected(self):
        for piece in [self.addendum['derived_source_report'],self.inventory['addenda'][-1]['json'],self.inventory['addenda'][-1]['csv']]:
            with self.subTest(file=piece['file']),self.assertRaises(ValueError):loader.load_inventory(self.inventory,lambda f:self.reader(f)+b' ' if f==piece['file'] else self.reader(f))
    def test_counts_no_global_profiles_no_volume_and_fixed_input_caps(self):
        n=len(self.addendum['evidence']);self.assertEqual(self.view['counts']['depth_references'],723+n);self.assertEqual(self.view['counts']['identities_with_scoped_depth_reference'],101);self.assertEqual(self.view['counts']['whole_route_depth_profiles'],0);self.assertEqual(self.view['counts']['volume_estimates'],0);self.assertEqual(self.view['metric_counts']['derived_supported_component_penetration_lower_bound'],self.before['metric_counts']['derived_supported_component_penetration_lower_bound']+n)
        for f,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin,f)
        self.assertTrue(all(len(raw)<2500000 for raw in self.pieces.values()));self.assertLess(sum(map(len,self.pieces.values())),3000000)


if __name__=='__main__':unittest.main()
