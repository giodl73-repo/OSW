import copy,csv,hashlib,io,json,unittest
import build_current_depth_reference_inventory_v3 as p
import load_current_depth_reference_inventory_v2 as prior
import load_current_depth_reference_inventory_v3 as loader
from derive_florida_primary_penetration_bounds_v1 import bound_at_original_node,INTERIOR
from latitude_depth_section_geometry_v1 import validate_retained,canonical_hash


class PrimaryPenetrationBoundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes());cls.inventory,cls.addendum,cls.report,cls.pieces,cls.view=p.build();read=lambda f:json.loads((p.ROOT/f).read_bytes());cls.previous=read(cls.op['previous_inventory_file']);cls.before=prior.load_inventory(cls.previous,lambda f:(p.ROOT/f).read_bytes());cls.base,cls.statistical,cls.regional=prior.read_parts(cls.previous,lambda f:(p.ROOT/f).read_bytes());cls.sop=read(cls.op['source_operator_file'])
    def reader(self,f):return self.pieces[f] if f in self.pieces else (p.ROOT/f).read_bytes()
    def assembled(self,a=None,report=None):return loader.assemble(self.base,self.statistical,self.regional,[(a or self.addendum,report or self.report)])
    def test_all715_prior_references_and_other_current_records_preserved(self):
        self.assertEqual(self.view['evidence'][:715],self.before['evidence']);self.assertEqual(self.inventory['base'],self.previous['base']);self.assertEqual(self.inventory['addenda'][:2],self.previous['addenda'])
        for before in self.before['records']:
            after=next(r for r in self.view['records'] if r['entity_id']==before['entity_id'])
            if before['entity_id']!='current:florida':self.assertEqual(after,before)
            else:self.assertEqual(after['depth_reference_ids'][:-8],before['depth_reference_ids']);self.assertEqual({k:v for k,v in after.items() if k!='depth_reference_ids'},{k:v for k,v in before.items() if k!='depth_reference_ids'})
    def test_complete20section_source_audit_and_original_projections_reproduced(self):
        audit=self.report['source_audit'];self.assertEqual((audit['sections_verified'],audit['native_profiles_verified'],audit['native_cell_pairs_verified'],audit['original_component_requests_verified'],audit['decoded_velocity_array_bytes']),(20,1330,53200,40,425600));self.assertTrue(audit['original_region_cases_and_gaps_unchanged']);self.assertEqual(audit['new_field_requests'],0)
    def test_eight_censored_primary_reaches_and_two_resolved_profiles_remain_distinct(self):
        self.assertEqual(len(self.report['records']),10);self.assertEqual(self.report['admitted_supported_reach_bounds'],8);self.assertEqual(len(self.addendum['evidence']),8);self.assertEqual(sum(r['reason']=='resolved_primary_isotach_not_a_censored_reach_reference' for r in self.report['records']),2)
        for r in self.addendum['evidence']:self.assertIsNone(r['approximate_value_m']);self.assertEqual(r['lower_bound_operator'],'>=');self.assertFalse(r['lower_bound_exclusive']);self.assertEqual(r['source_primary_threshold_m_s'],.1);self.assertEqual(r['source_component_bearing_degrees_true'],0)
    def test_native_reach_allows_no_missing_below_threshold_or_unknown_bed_bridge(self):
        for r in self.report['records']:
            if not r['reach_eligible']:continue
            s=json.loads((p.ROOT/r['source_section_file']).read_bytes());v=s['columns'][r['selected_column_index']]['signed_reference_component_m_s'];i=r['last_connected_native_index'];self.assertTrue(all(x is not None and x>.1 for x in v[:i+1]));self.assertIsNone(v[i+1]);self.assertEqual(r['lower_bound_m'],s['depth_levels_m'][i]);self.assertIsNone(r['primary_layer']['lower_depth_m']);self.assertIsNone(r['primary_layer']['layer_thickness_m'])
    def fixture(self):
        layer={'threshold_m_s':.1,'upper_depth_m':0.,'upper_status':'surface_bounded_layer','lower_depth_m':None,'lower_status':'censored_before_missing_or_dry_level','lower_last_connected_depth_m':200.}
        section={'depth_levels_m':[0.,100.,200.,300.],'columns':[{'signed_reference_component_m_s':[.2,.3,.2,None]}],'diagnosis':{'selected_column_index':0,'horizontal_selection_status':INTERIOR,'selected_column_threshold_layers':[layer]}}
        return section,{'primary_threshold_m_s':.1}
    def test_synthetic_first_missing_stop_and_original_axis_selection_are_preserved(self):
        s,config=self.fixture();self.assertEqual(bound_at_original_node(s,config)['lower_bound_m'],200.)
        bad=copy.deepcopy(s);bad['columns'][0]['signed_reference_component_m_s'][1]=None
        with self.assertRaises(ValueError):bound_at_original_node(bad,config)
        bad=copy.deepcopy(s);bad['columns'][0]['signed_reference_component_m_s'][2]=.1
        with self.assertRaises(ValueError):bound_at_original_node(bad,config)
        bad=copy.deepcopy(s);bad['diagnosis']['horizontal_selection_status']='section_gate_edge_maximum_axis_unresolved';self.assertFalse(bound_at_original_node(bad,config)['reach_eligible'])
    def test_resolved_or_detached_primary_not_relabelled_and_no_sensitivity_fill(self):
        s,config=self.fixture();resolved=copy.deepcopy(s);resolved['diagnosis']['selected_column_threshold_layers'][0]['lower_depth_m']=250.;self.assertFalse(bound_at_original_node(resolved,config)['reach_eligible'])
        detached=copy.deepcopy(s);detached['diagnosis']['selected_column_threshold_layers'][0].update(upper_status='adjacent_isotach_crossing',upper_depth_m=50.);self.assertFalse(bound_at_original_node(detached,config)['reach_eligible'])
        stronger=copy.deepcopy(s);stronger['diagnosis']['selected_column_threshold_layers'].append({'threshold_m_s':.2,'lower_depth_m':150.});self.assertEqual(bound_at_original_node(stronger,config)['lower_bound_m'],200.)
    def test_source_profile_frame_and_diagnosis_mutations_rejected_by_frozen_validator(self):
        r=next(r for r in self.report['records'] if r['reach_eligible']);s=json.loads((p.ROOT/r['source_section_file']).read_bytes());config={**self.sop,**self.sop['currents']['current:florida']}
        for kind in ['frame','diagnosis','component','position']:
            bad=copy.deepcopy(s)
            if kind=='frame':bad['component_bearing_degrees_true']=90
            if kind=='diagnosis':bad['diagnosis']['selected_column_index']=0
            if kind=='component':bad['columns'][0]['signed_reference_component_m_s'][0]=999.;bad['decoded_columns_sha256']=canonical_hash(bad['columns'])
            if kind=='position':bad['columns'][0]['sampled_lon_lat'][1]+=.1;bad['decoded_columns_sha256']=canonical_hash(bad['columns'])
            with self.subTest(kind=kind),self.assertRaises(ValueError):validate_retained(bad,config)
    def test_no_exact_depth_span_bed_annual_or_volume_promotion(self):
        for key,value in [('approximate_value_m',600),('upper_bound_m',1000),('lower_bound_operator','>'),('lower_boundary_m',600),('thickness_m',600),('annual_range_m',[500,800]),('source_missing_values_interpreted_as_bed',True),('source_bathymetry_used',True),('volume_eligible',True),('reference_route_projection_eligible',True)]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.assembled(a)
    def test_weaker_threshold_wrong_frame_or_unmatched_native_metadata_rejected(self):
        for key,value in [('source_primary_threshold_m_s',.05),('source_component_bearing_degrees_true',90),('source_core_search_depth_interval_m',[0,500]),('source_last_connected_velocity_m_s',999),('source_next_native_depth_m',9999),('source_selected_column_index',999),('source_raw_profile_ref','wrong')]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.assembled(a)
    def test_exact_report_pointer_hash_and_all_reported_values_retained(self):
        for row in self.addendum['evidence']:
            i=int(row['source_pointer'].split('/')[-1]);r=self.report['records'][i];self.assertEqual(row['source_file'],p.REPORT);self.assertEqual(row['source_sha256'],hashlib.sha256(self.pieces[p.REPORT]).hexdigest());self.assertEqual(row['lower_bound_m'],r['lower_bound_m']);self.assertEqual(row['source_snapshot_time_utc'],r['snapshot_time_utc'])
        a=copy.deepcopy(self.addendum);a['evidence'][0]['source_pointer']='/records/0'
        with self.assertRaises(ValueError):self.assembled(a)
    def test_old_csv_cells_and_bound_types_preserved_in_full_query_view(self):
        old=list(csv.DictReader(io.StringIO(prior.combined_csv_bytes(self.previous,lambda f:(p.ROOT/f).read_bytes()).decode())));new=list(csv.DictReader(io.StringIO(loader.combined_csv_bytes(self.inventory,self.reader).decode())));self.assertEqual(len(new),723)
        for a,b in zip(old,new):self.assertEqual(a,{k:b[k] for k in a})
        for r in new[715:]:self.assertEqual(r['approximate_value_m'],'');self.assertEqual(r['lower_bound_operator'],'>=');self.assertEqual(r['lower_bound_exclusive'],'False');self.assertEqual(r['annual_range_m'],'');self.assertEqual(r['volume_eligible'],'False')
    def test_report_and_reference_piece_hashes_cannot_be_changed(self):
        for piece in [self.addendum['derived_source_report'],self.inventory['addenda'][-1]['json'],self.inventory['addenda'][-1]['csv']]:
            with self.subTest(file=piece['file']),self.assertRaises(ValueError):loader.load_inventory(self.inventory,lambda f:self.reader(f)+b' ' if f==piece['file'] else self.reader(f))
    def test_counts_and_no_whole_current_or_volume_changes(self):
        self.assertEqual(self.view['counts']['depth_references'],723);self.assertEqual(self.view['counts']['identities_with_scoped_depth_reference'],101);self.assertEqual(self.view['counts']['whole_route_depth_profiles'],0);self.assertEqual(self.view['counts']['volume_estimates'],0);self.assertEqual(self.view['metric_counts']['derived_supported_component_penetration_lower_bound'],self.before['metric_counts']['derived_supported_component_penetration_lower_bound']+8)
        self.assertFalse(self.report['physical_current_bottom_established']);self.assertFalse(self.report['source_missing_values_interpreted_as_bed']);self.assertFalse(self.report['interpolation_performed'])
    def test_all_input_pins_and_fixed_publication_caps(self):
        for f,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin,f)
        self.assertTrue(all(len(raw)<2500000 for raw in self.pieces.values()));self.assertLess(sum(map(len,self.pieces.values())),3000000)


if __name__=='__main__':unittest.main()
