import copy,hashlib,json,unittest
import audit_interval_core_connected_reach_v1 as p
from mixed_interval_section_geometry_v1 import validate_retained
from sample_eac_hycom_route_depth_v1 import canonical_hash


class IntervalReachAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes());cls.report=p.build()
    def fixture(self,domain=False):
        layer={'threshold_m_s':.1,'core_index':3,'core_depth_m':200,'upper_depth_m':75,'upper_status':'adjacent_isotach_crossing','lower_depth_m':None,'lower_status':'censored_at_sample_domain_edge' if domain else 'censored_before_missing_or_dry_level','lower_last_connected_depth_m':400 if domain else 300}
        s={'depth_levels_m':[0,50,100,200,300,400],'columns':[{'signed_reference_component_m_s':[.01,.02,.2,.3,.2,.15 if domain else None]}],'diagnosis':{'selected_column_index':0,'horizontal_selection_status':p.INTERIOR,'selected_column_threshold_layers':[layer]}}
        return s,{'primary_threshold_m_s':.1,'core_search_depth_interval_m':[50,300]}
    def test_all96_original_cases_and_six_owners_audited(self):
        self.assertEqual([s['study_id'] for s in self.report['studies']],['barents-makassar','coastal-upper-layer','guiana-egcc']);self.assertEqual([s['source_sections_verified'] for s in self.report['studies']],[32,32,32]);self.assertEqual(sum(len(s['records']) for s in self.report['studies']),96);self.assertEqual({r['entity_id'] for s in self.report['studies'] for r in s['records']},{'current:north-cape','current:indonesian-throughflow','current:norwegian-coastal','current:tsushima','current:guiana','current:east-greenland-coastal'})
    def test_original_projection_cases_and_every_gap_preserved(self):
        self.assertTrue(all(s['original_projections_and_gaps_unchanged'] for s in self.report['studies']));self.assertTrue(all(s['original_component_requests_verified']==64 for s in self.report['studies']));self.assertLessEqual(sum(s['native_cell_pairs_verified'] for s in self.report['studies']),250000)
    def test_actual_bounds_start_at_original_core_not_assumed_surface(self):
        eligible=[r for s in self.report['studies'] for r in s['records'] if r['reach_eligible']];self.assertEqual(len(eligible),self.report['eligible_core_connected_reach_bounds']);self.assertGreater(len(eligible),0)
        for r in eligible:
            source=json.loads((p.ROOT/r['source_section_file']).read_bytes());v=source['columns'][r['selected_column_index']]['signed_reference_component_m_s'];a=r['core_native_index'];b=r['last_connected_native_index'];self.assertTrue(all(x is not None and x>r['primary_threshold_m_s'] for x in v[a:b+1]));self.assertEqual(source['depth_levels_m'][b],r['lower_bound_m']);self.assertEqual(r['lower_bound_operator'],'>=');self.assertIsNone(r['primary_layer']['lower_depth_m']);self.assertFalse(r['physical_current_bottom_established']);self.assertIsNone(r['physical_layer_thickness_m'])
    def test_detached_layer_yields_core_reach_without_surface_claim(self):
        s,c=self.fixture();r=p.bound_at_original_node(s,c);self.assertEqual(r['lower_bound_m'],300);self.assertFalse(r['source_surface_connection_established']);self.assertEqual(r['primary_layer']['upper_depth_m'],75);self.assertEqual(r['core_depth_m'],200)
    def test_missing_and_domain_censoring_distinct(self):
        for domain in [False,True]:
            s,c=self.fixture(domain);r=p.bound_at_original_node(s,c);self.assertTrue(r['reach_eligible']);self.assertEqual(r['lower_bound_m'],400 if domain else 300);self.assertEqual(r['censoring_kind'],'native_vertical_domain_limit' if domain else 'missing_signed_component_level');self.assertEqual(r['next_native_index'],None if domain else 5)
    def test_no_missing_or_cutoff_bridge_below_original_core(self):
        for value in [None,.1,.05,float('nan')]:
            s,c=self.fixture();s['columns'][0]['signed_reference_component_m_s'][4]=value
            with self.subTest(value=value),self.assertRaises(ValueError):p.bound_at_original_node(s,c)
    def test_no_false_core_or_domain_endpoint(self):
        s,c=self.fixture();s['diagnosis']['selected_column_threshold_layers'][0]['core_depth_m']=100
        with self.assertRaises(ValueError):p.bound_at_original_node(s,c)
        s,c=self.fixture(True);s['diagnosis']['selected_column_threshold_layers'][0]['lower_last_connected_depth_m']=300
        with self.assertRaises(ValueError):p.bound_at_original_node(s,c)
    def test_resolved_edge_support_edge_and_absent_axes_stay_excluded(self):
        for status in ['section_gate_edge_maximum_axis_unresolved','selection_interval_support_edge_maximum_axis_unresolved','no_qualifying_interval_component_column']:
            s,c=self.fixture();s['diagnosis']['horizontal_selection_status']=status;self.assertFalse(p.bound_at_original_node(s,c)['reach_eligible'])
        s,c=self.fixture();s['diagnosis']['selected_column_index']=None;self.assertFalse(p.bound_at_original_node(s,c)['reach_eligible']);s,c=self.fixture();s['diagnosis']['selected_column_threshold_layers'][0]['lower_depth_m']=350;self.assertFalse(p.bound_at_original_node(s,c)['reach_eligible'])
    def test_no_weaker_sensitivity_substitution(self):
        s,c=self.fixture();s['diagnosis']['selected_column_threshold_layers'].append({'threshold_m_s':.05,'lower_depth_m':390});self.assertEqual(p.bound_at_original_node(s,c)['lower_bound_m'],300)
    def test_frozen_source_frame_diagnosis_and_coordinate_guards(self):
        study=self.op['studies'][0];record=next(r for r in self.report['studies'][0]['records'] if r['selected_column_index'] is not None);source=json.loads((p.ROOT/record['source_section_file']).read_bytes());sop=json.loads((p.ROOT/study['source_operator_file']).read_bytes());config={**sop,**sop['currents'][source['entity_id']]}
        for kind in ['frame','diagnosis','component','position']:
            bad=copy.deepcopy(source)
            if kind=='frame':bad['component_bearing_degrees_true']+=90
            elif kind=='diagnosis':bad['diagnosis']['selected_column_index']=None
            elif kind=='component':bad['columns'][0]['signed_reference_component_m_s'][0]=999.;bad['decoded_columns_sha256']=canonical_hash(bad['columns'])
            else:bad['columns'][0]['sampled_lon_lat'][0]+=.1;bad['decoded_columns_sha256']=canonical_hash(bad['columns'])
            with self.subTest(kind=kind),self.assertRaises(ValueError):validate_retained(bad,config)
    def test_no_field_retrieval_or_inventory_physical_promotion(self):
        self.assertEqual(self.report['new_ocean_field_requests'],0);self.assertEqual(self.report['new_reference_inventory_rows_admitted'],0);self.assertFalse(self.report['reference_inventory_updated']);self.assertFalse(self.report['physical_current_bottom_established']);self.assertFalse(self.report['runtime_changed']);self.assertFalse(self.report['full_goal_complete'])
    def test_all_input_pins_and_fixed_report_cap(self):
        for f,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin,f)
        self.assertLess(len((json.dumps(self.report,separators=(',',':'))+'\n').encode()),2500000)


if __name__=='__main__':unittest.main()
