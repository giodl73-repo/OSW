import copy,hashlib,json,struct,unittest
import pacific_neuc_mean_sections_v1 as p


class MeanSectionTests(unittest.TestCase):
    def fixture(self):
        op=json.loads((p.ROOT/p.OPERATOR).read_bytes());axes={'depth':[float(i*100) for i in range(40)],'lat':[6.,7.,8.,9.,10.],'lon':[135.,136.5,138.,140.]}
        h=json.loads((p.ROOT/op['header_file']).read_bytes());h=copy.deepcopy(h)
        for d in h['dimensions']:
            if d['name'] in axes:d['declared_length']=len(axes[d['name']])
        size=40*5*4*2
        for name,begin in [('water_u',1000),('water_v',1000+size)]:
            v=next(v for v in h['variables'] if v['name']==name);v.update(begin=begin,vsize=size)
        h['source_content_length']=1000+size*2
        return axes,h,op
    def test_exact_native_indices_and_cdf_offsets_for_both_components(self):
        axes,h,op=self.fixture();sections,counts=p.section_plan(axes,h,op)
        self.assertEqual(counts['cell_pairs'],800);self.assertEqual(counts['packed_component_bytes'],3200);self.assertEqual(counts['decoded_float32_component_bytes'],6400)
        for s in sections:
            ix=s['native_longitude_index'];self.assertEqual(s['native_latitude_indices'],[0,1,2,3,4]);self.assertEqual(s['nearest_axis_distance_km'],0)
            for c in s['components'].values():
                self.assertEqual(c['ranges'][0],(c['variable_begin']+ix*2,2));self.assertEqual(c['ranges'][-1],(c['variable_begin']+2*((39*5+4)*4+ix),2))
    def test_shared_field_caps_and_section_caps_reject_before_io(self):
        axes,h,op=self.fixture()
        for key,value in [('maximum_total_cell_pairs',799),('maximum_total_decoded_bytes',6399),('maximum_cell_pairs_per_section',199),('maximum_profiles_per_section',4)]:
            bad=copy.deepcopy(op);bad[key]=value
            with self.assertRaises(ValueError):p.section_plan(axes,h,bad)
    def test_cf_packing_dimension_storage_record_and_source_length_guards(self):
        axes,h,op=self.fixture()
        for mutate in [lambda v:v.update(nc_type=4),lambda v:v.update(dimension_names=['time','lat','depth','lon']),lambda v:v.update(vsize=v['vsize']-2),lambda v:v['attributes']['scale_factor'].update(values=[.01]),lambda v:v['attributes']['standard_name'].update(values='grid_eastward_velocity')]:
            bad=copy.deepcopy(h);mutate(next(v for v in bad['variables'] if v['name']=='water_u'))
            with self.assertRaises(ValueError):p.section_plan(axes,bad,op)
        for key,value in [('format','CDF1'),('record_count',2),('source_content_length',1001)]:
            bad=copy.deepcopy(h);bad[key]=value
            with self.assertRaises(ValueError):p.section_plan(axes,bad,op)
    def test_axis_distance_duplicate_native_axis_nonmonotonic_and_depth_support(self):
        axes,h,op=self.fixture()
        for targets in [[135,135.001],[0.]]:
            bad=copy.deepcopy(op);bad['section_longitudes_deg_e']=targets
            with self.assertRaises(ValueError):p.section_plan(axes,h,bad)
        for key,values in [('lon',[135,138,136.5,140]),('lat',[6,7,float('nan'),9,10]),('depth',[float(i*101) for i in range(40)])]:
            bad=copy.deepcopy(axes);bad[key]=values
            with self.assertRaises(ValueError):p.section_plan(bad,h,op)
    def test_signed_big_endian_fill_before_scaling_and_depth_major_order(self):
        packing={'missing_packed':-30000,'scale_factor':.001,'add_offset':0.};raw=struct.pack('>6h',-30000,-2,3,4,-5,6)
        self.assertEqual(p.decode_component(raw,3,2,packing),[[None,.003,-.005],[-.002,.004,.006]])
        for bad in [raw[:-1],raw+b'\0\0']:
            with self.assertRaises(ValueError):p.decode_component(bad,3,2,packing)
    def test_detached_interior_weak_jet_preserves_model_only_status(self):
        axes,h,op=self.fixture();z=axes['depth'];core=[0.]*40
        for i,v in [(3,.03),(4,.04),(5,.03)]:core[i]=v
        result=p.section_diagnostic(z,[[0.]*40,core,[0.]*40],[7.,8.,9.],op)
        self.assertEqual(result['selected_column_index'],1);self.assertTrue(result['horizontal_interior_selection']);self.assertTrue(result['primary_layer_detached_from_surface']);self.assertTrue(result['selected_node_in_independent_latitude_context'])
        self.assertFalse(result['current_identity_validated']);self.assertFalse(result['regional_inventory_promotion_authorized']);self.assertIsNone(result['physical_current_depth_m'])
    def test_edge_maximum_not_replaced_by_weaker_interior_and_missing_not_zero(self):
        axes,h,op=self.fixture();z=axes['depth'];core=[0.]*40;core[4]=.04;strong=[v*2 for v in core]
        result=p.section_diagnostic(z,[strong,core,[0.]*40],[6.,8.,10.],op);self.assertEqual(result['selected_column_index'],0);self.assertFalse(result['horizontal_interior_selection']);self.assertFalse(result['selected_node_in_independent_latitude_context'])
        missing=core.copy();missing[10]=None;result=p.section_diagnostic(z,[[0.]*40,missing,[0.]*40],[7.,8.,9.],op);self.assertIsNone(result['selected_column_index'])
    def test_exact_input_pins_fixed_scope_and_no_physical_promotion(self):
        op=json.loads((p.ROOT/p.OPERATOR).read_bytes())
        for f,pin in op['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin,f)
        self.assertEqual(op['section_longitudes_deg_e'],[135.,136.5,138.,140.]);self.assertEqual(op['selection_depth_interval_m'],[300.,1500.]);self.assertEqual(op['primary_threshold_m_s'],.02);self.assertIsNone(op['surface_component_gate_m_s']);self.assertFalse(op['regional_inventory_promotion_authorized']);self.assertEqual(op['maximum_total_cell_pairs'],250000)


if __name__=='__main__':unittest.main()
