import copy,unittest
import load_current_depth_reference_inventory_v39 as m

class JutlandBoundSemantics(unittest.TestCase):
    def setUp(self):
        rows=[]
        dates=['2024-03-15','2024-06-15','2024-09-15','2024-12-15'];sections=['hanstholm-search-cut','north-jutland-midcoast-search-cut','hirtshals-search-cut']
        for i in range(12):
            edge=i==8;bound=100 if edge else [25,65,50][i%3]
            layer={'threshold_m_s':.1,'upper_depth_m':0.,'lower_depth_m':None,'layer_thickness_m':None,'upper_status':'surface_bounded_layer','lower_status':'censored_before_missing_or_dry_level','status':'unresolved_connected_layer_boundary','core_index':0,'core_depth_m':0,'core_velocity_m_s':.5,'lower_last_connected_depth_m':bound}
            rows.append({'case_index':i,'entity_id':'current:jutland','date':dates[i//3],'time_utc':dates[i//3]+'T12:00:00Z','section_id':sections[i%3],
                'component_bearing_degrees_true':45,'primary_threshold_m_s':.1,'selection_interval_m':[0,25],
                'source_vertical_sampling':'provider_interpolated_fixed_z_not_native_ROMS_s_layers','salinity_gate_applied':False,'physical_current_identity_independently_verified':False,
                'primary_component_layer':layer,'primary_connected_depth_lower_bound_m':bound,'primary_lower_component_contour_depth_m':None,'conditional_component_span_m':None,
                'regional_axis_proxy_lower_contour_anchor_eligible':False,'physical_current_bottom_established':False,'physical_thickness_m':None,'volume_m3':None,'annual_range_m':None,
                'whole_current_representative':False,'width_join_eligible':False,'volume_eligible':False,'horizontal_axis_proxy_interior':not edge,
                'horizontal_selection_status':'section_gate_edge_maximum_axis_unresolved' if edge else 'interior_section_integral_maximum_with_finite_neighbors_not_independently_validated_axis',
                'selected_position_lon_lat':[8.,57.],'source_raw_file':'synthetic-test-not-provider-data','source_raw_sha256':'0'*64})
        self.source={'schema':'osw.norkyst-jutland-dated-regional-depth-anchors.v1','entity_id':'current:jutland','rows':rows}
    def test_inclusive_censor_support_does_not_become_a_boundary_or_thickness(self):
        rows=m.references(self.source);self.assertEqual(len(rows),11)
        for r in rows:
            self.assertEqual(r['lower_bound_m'],r['source_descriptor']['primary_component_layer']['lower_last_connected_depth_m'])
            self.assertFalse(r['lower_bound_exclusive']);self.assertIsNone(r['lower_boundary_m']);self.assertIsNone(r['thickness_m']);self.assertIsNone(r['approximate_value_m']);self.assertIsNone(r['annual_range_m']);self.assertFalse(r['physical_current_bottom_established']);self.assertFalse(r['reference_route_projection_eligible'])
    def test_gate_edge_case_never_enters_the_reference_list(self):
        selected,excluded=m.qualified(self.source);ids={r['source_case_id'] for r in m.references(self.source)}
        self.assertEqual(len(excluded),1);self.assertNotIn(excluded[0][1]['case_index'],ids)
        self.assertEqual(m.context(self.source)['unadmitted_edge_cases'][0]['source_descriptor'],excluded[0][1])
    def test_source_frame_threshold_censor_or_physical_promotion_rejected(self):
        for key,v in [('component_bearing_degrees_true',0),('primary_threshold_m_s',.05),('primary_lower_component_contour_depth_m',25),('physical_current_identity_independently_verified',True),('regional_axis_proxy_lower_contour_anchor_eligible',True),('physical_thickness_m',25)]:
            source=copy.deepcopy(self.source);source['rows'][0][key]=v
            with self.assertRaises(ValueError):m.references(source)
    def test_bound_disagreement_and_duplicate_source_case_rejected(self):
        source=copy.deepcopy(self.source);source['rows'][0]['primary_connected_depth_lower_bound_m']=50
        with self.assertRaises(ValueError):m.references(source)
        source=copy.deepcopy(self.source);source['rows'][1]['case_index']=source['rows'][0]['case_index']
        with self.assertRaises(ValueError):m.references(source)
    def test_exact_source_row_and_prior_owner_fields_preserved(self):
        before={'records':[{'entity_id':'current:jutland','depth_reference_ids':['old'],'status':'scoped_depth_reference','volume_km3':None}],'evidence':[{'id':'old','entity_id':'current:jutland','metric':'old','unit':'m'}],'source_contexts':{'old':{'x':None}}}
        saved=copy.deepcopy((before,self.source));a={'schema':m.SCHEMA,'id':m.ADDENDUM_ID,'evidence':m.references(self.source),'source_contexts':{m.CONTEXT:m.context(self.source)},'runtime_changed':False,'full_goal_complete':False}
        out=m.assemble(before,a,self.source);self.assertEqual(out['evidence'][0],before['evidence'][0]);self.assertEqual(out['source_contexts']['old'],before['source_contexts']['old']);self.assertEqual((before,self.source),saved)
        for e,(i,r) in zip(out['evidence'][1:],m.qualified(self.source)[0]):self.assertEqual(e['source_descriptor'],r);self.assertEqual(e['source_pointer'],'/rows/'+str(i))

if __name__=='__main__':unittest.main()
