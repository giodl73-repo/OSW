import copy,hashlib,json,unittest
from unittest.mock import patch
import coastal_fresh_depth_curtains_v1 as p

NCC='current:norwegian-coastal'
EGCC='current:east-greenland-coastal'


class NativeConnectivityTests(unittest.TestCase):
    def nodes(self,v,s=None,seed=(0,0),entity=NCC):
        return p.connected_nodes(list(range(len(v[0]))),v,s if s is not None else [[33]*len(a) for a in v],*seed,entity)
    def test_four_neighbors_connect_without_diagonals(self):
        self.assertEqual(self.nodes([[.2,0],[0,.2]]),{(0,0)})
        self.assertEqual(self.nodes([[.2,.2],[0,.2]]),{(0,0),(0,1),(1,1)})
    def test_missing_velocity_blocks_direct_connection(self):
        self.assertEqual(self.nodes([[.2,None,.2]]),{(0,0)})
    def test_missing_salinity_blocks_direct_connection(self):
        self.assertEqual(self.nodes([[.2,.2,.2]],[[33,None,33]]),{(0,0)})
    def test_missing_hole_can_only_be_traversed_by_real_native_detour(self):
        self.assertEqual(self.nodes([[.2,None,.2],[.2,.2,.2]]),{(0,0),(0,2),(1,0),(1,1),(1,2)})
    def test_velocity_equality_is_excluded(self):
        self.assertEqual(self.nodes([[.2,.1,.2]]),{(0,0)})
    def test_source_specific_salinity_thresholds_and_equality(self):
        self.assertEqual(self.nodes([[.2,.2,.2]],[[33,34,35]]),{(0,0),(0,1)})
        self.assertEqual(self.nodes([[.2,.2,.2]],[[33,34,35]],entity=EGCC),{(0,0)})
    def test_unqualified_original_seed_never_reselected(self):
        self.assertEqual(self.nodes([[.1,.3]]),set())
        self.assertEqual(self.nodes([[.2,.3]],[[35,33]]),set())
    def test_disconnected_fresh_lens_never_joined(self):
        self.assertEqual(self.nodes([[.2,0,.2],[.2,0,.2]]),{(0,0),(1,0)})
    def test_multiple_vertical_runs_are_not_collapsed(self):
        nodes=self.nodes([[.2,0,.2],[.2,.2,.2]])
        self.assertEqual(p.runs_for_column(nodes,0),[[0,0],[2,2]])
        self.assertEqual(p.runs_for_column(nodes,1),[[0,2]])
        self.assertEqual(p.runs_for_column(nodes,2),[])
    def test_invalid_dimensions_indices_and_owner_rejected(self):
        for args in [([0,1],[[.2]],[[33]],0,0,NCC),([0,1],[[.2,.2]],[[33,33]],True,0,NCC),([0,1],[[.2,.2]],[[33,33]],0,2,NCC),([0,1],[[.2,.2]],[[33,33]],0,0,'current:unknown')]:
            with self.assertRaises(ValueError):p.connected_nodes(*args)
    def test_nonfinite_and_out_of_range_inputs_rejected(self):
        for field,value in [('v',float('nan')),('v',float('inf')),('s',51),('s',True)]:
            v=[[.2,.2]];s=[[33,33]];(v if field=='v' else s)[0][1]=value
            with self.assertRaises(ValueError):self.nodes(v,s)
    def test_native_depth_order_and_caps_rejected(self):
        for z,v,s in [([1,0],[[.2,.2]],[[33,33]]),(list(range(41)),[[.2]*41],[[33]*41]),([0,1],[[.2,.2]]*151,[[33,33]]*151)]:
            with self.assertRaises(ValueError):p.connected_nodes(z,v,s,0,0,NCC)
    def test_original_seed_can_be_subsurface_without_surface_inheritance(self):
        self.assertEqual(self.nodes([[0,.2,.2]],seed=(0,1)),{(0,1),(0,2)})
    def test_iteration_is_deterministic_and_input_arrays_unchanged(self):
        v=[[.2,0,.2],[.2,.2,.2]];before=copy.deepcopy(v)
        self.assertEqual(self.nodes(v),self.nodes(v));self.assertEqual(v,before)


class RetainedCurtainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report,cls.raw=p.build();cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes());cls.manifest=json.loads((p.ROOT/cls.op['reference_inventory_file']).read_bytes());cls.parts=p.inventory.read_parts(cls.manifest,lambda f:(p.ROOT/f).read_bytes());cls.bundle=cls.parts[-1][0][1];cls.cases=p.inventory.reproduce(cls.bundle)
    def test_complete32_case_cohort_and27_curtains(self):
        self.assertEqual(self.report['counts']['original_cases'],32);self.assertEqual(self.report['counts']['curtains'],27);self.assertEqual(self.report['counts']['unclassified_cases'],5);self.assertEqual(len(self.report['records']),32)
        for case,row in zip(self.cases,self.report['records']):
            self.assertEqual(row,p.curtain(case,self.bundle));self.assertEqual(row['original_classification'],case['classification']);self.assertEqual(row['original_velocity_source_file'],case['original']['source_section_file'])
    def test_exact_original_core_boundaries_retained_without_duplicate_reference(self):
        for row in self.report['records']:
            runs=[run for column in row['columns'] for run in column['connected_depth_runs'] if run['contains_original_core']]
            if row['columns']:
                self.assertEqual(len(runs),1);self.assertEqual(runs[0]['upper'],row['original_classification']['upper']);self.assertEqual(runs[0]['lower'],row['original_classification']['lower'])
            else:self.assertEqual(runs,[])
        self.assertEqual(self.report['new_reference_inventory_rows_admitted'],0)
    def test_all_native_columns_and_vertical_memberships_reproducible(self):
        for case,row in zip(self.cases,self.report['records']):
            if not row['columns']:continue
            source=self.bundle['sections'][row['original_velocity_source_file']];velocity=[c['signed_reference_component_m_s'] for c in source['columns']];nodes=p.connected_nodes(row['depth_levels_m'],velocity,case['profile']['practical_salinity_columns'],row['original_selected_column_index'],row['original_core_index'],row['entity_id'])
            self.assertEqual(len(row['columns']),len(source['columns']));self.assertEqual(row['connected_native_node_count'],len(nodes))
            for index,column in enumerate(row['columns']):
                self.assertEqual(column['native_column_index'],index);self.assertEqual(column['native_longitude_index'],source['columns'][index]['global_longitude_index']);self.assertEqual([r['native_depth_indices_inclusive'] for r in column['connected_depth_runs']],p.runs_for_column(nodes,index))
    def test_unclassified_missing_domain_and_lateral_support_not_promoted(self):
        for row in self.report['records']:
            self.assertFalse(row['core_reselected']);self.assertFalse(row['physical_current_bottom_established']);self.assertIsNone(row['physical_layer_thickness_m']);self.assertIsNone(row['width_m']);self.assertIsNone(row['volume_m3']);self.assertIsNone(row['cross_section_area_m2'])
            for index,column in enumerate(row['columns']):
                self.assertEqual(column['touches_lateral_sampling_edge'],bool(column['connected_depth_runs']) and index in (0,len(row['columns'])-1))
                for run in column['connected_depth_runs']:
                    for side in ['upper','lower']:
                        if run[side]['status']!='adjacent_native_joint_predicate_crossing':self.assertIsNone(run[side]['boundary_depth_m'])
            if not row['columns']:self.assertEqual(row['connected_native_node_count'],0);self.assertNotEqual(row['original_classification']['status'],'conditional_fresh_component_core_supported')
        self.assertEqual(self.report['new_ocean_field_requests'],0);self.assertFalse(self.report['runtime_changed'])
    def test_synthetic_surface_missing_domain_and_multi_run_boundaries(self):
        case=copy.deepcopy(next(c for c in self.cases if c['classification']['status']=='conditional_fresh_component_core_supported'));bundle=copy.deepcopy(self.bundle);source=bundle['sections'][case['original']['source_section_file']];entity=case['original']['entity_id'];diag=p.inventory.source.ncc_diagnose if entity==NCC else p.inventory.source.egcc_diagnose
        source['depth_levels_m']=[0,10,20,30];velocity=[[.2,0,.2,None],[.2,.2,.2,.2]]
        source['columns']=[{**source['columns'][i],'signed_reference_component_m_s':v} for i,v in enumerate(velocity)];source['diagnosis']['selected_column_index']=0;case['profile']['practical_salinity_columns']=[[33]*4,[33]*4];case['classification']=diag(source['depth_levels_m'],velocity[0],[33]*4,0)
        row=p.curtain(case,bundle);self.assertEqual(len(row['columns'][0]['connected_depth_runs']),2);self.assertEqual(row['columns'][0]['connected_depth_runs'][0]['upper']['status'],'surface_sample_supported');self.assertEqual(row['columns'][0]['connected_depth_runs'][1]['lower']['status'],'censored_before_missing_native_input');self.assertEqual(row['columns'][1]['deepest_run_lower_status'],'censored_at_native_domain_end');self.assertIsNone(row['columns'][1]['deepest_run_lower_boundary_depth_m'])
    def test_pins_caps_counts_and_frozen_rules(self):
        self.assertLess(len(self.raw),2400000);self.assertEqual(json.loads(self.raw),self.report)
        for f,pin in self.op['input_sha256'].items():self.assertFalse(f.startswith('.pytest_cache/'));self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin,f)
        counts=self.report['counts'];columns=[c for r in self.report['records'] for c in r['columns']];self.assertEqual(counts['seed_connected_columns'],sum(bool(c['connected_depth_runs']) for c in columns));self.assertEqual(counts['connected_vertical_runs'],sum(len(c['connected_depth_runs']) for c in columns))
        for mutation in ['connectivity','classifiers','eligibility']:
            bad=copy.deepcopy(self.op)
            if mutation=='connectivity':bad[mutation]='diagonal'
            elif mutation=='classifiers':bad[mutation][NCC]['salinity_threshold_exclusive']=34
            else:bad[mutation]['volume']=True
            original=p.Path.read_bytes
            def reader(path):return json.dumps(bad).encode() if str(path).replace('\\','/').endswith(p.OPERATOR) else original(path)
            with patch.object(p.Path,'read_bytes',reader),self.assertRaises(ValueError):p.build()


if __name__=='__main__':unittest.main()
