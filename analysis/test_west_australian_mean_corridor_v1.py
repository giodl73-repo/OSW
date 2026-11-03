import copy,hashlib,json,struct,unittest
import west_australian_mean_corridor_v1 as p


class WestAustralianMeanCorridorTests(unittest.TestCase):
    def fixture(self):
        op=json.loads((p.ROOT/p.OPERATOR).read_bytes());axes={'depth':[float(i*100) for i in range(39)]+[5000.],'lat':[-30.,-28.,-26.,-24.,-22.],'lon':[94.,96.,100.,104.],'time':[42.]}
        h=json.loads((p.ROOT/op['header_file']).read_bytes());h=copy.deepcopy(h)
        for d in h['dimensions']:
            if d['name'] in axes:d['declared_length']=len(axes[d['name']])
        size=40*5*4*2
        for name,begin in [('water_u',100000),('water_v',100000+size)]:
            next(v for v in h['variables'] if v['name']==name).update(begin=begin,vsize=size)
        h['source_content_length']=100000+size*2
        prior={'source_url':h['source_object_url'],'source_bytes':h['source_content_length'],'source_last_modified':h['source_last_modified'],'requests':[]}
        return axes,h,op,prior
    def test_exact_fixed_latitude_row_offsets_shape_and_all_target_counts(self):
        axes,h,op,prior=self.fixture();sections,c=p.plan_sections(axes,h,op,prior)
        self.assertEqual(c['cell_pairs'],640);self.assertEqual(c['packed_component_bytes'],2560);self.assertEqual(c['planned_http_requests'],320);self.assertEqual(c['conservative_decoded_float64_component_bytes'],10240)
        for s in sections:
            iy=s['native_latitude_index'];self.assertEqual(s['native_longitude_indices'],[0,1,2,3]);self.assertEqual(s['nearest_axis_distance_km'],0)
            for component in s['components'].values():
                self.assertEqual(component['ranges'][0],(component['variable_begin']+iy*8,8));self.assertEqual(component['ranges'][-1],(component['variable_begin']+2*((39*5+iy)*4),8))
    def test_global_field_patch_request_and_whole_plan_body_caps(self):
        axes,h,op,prior=self.fixture()
        for key,value in [('maximum_total_cell_pairs',639),('maximum_total_decoded_bytes',10239),('maximum_cell_pairs_per_section',159),('maximum_http_requests',319),('maximum_requested_bytes',2559),('maximum_response_body_bytes',7),('maximum_total_response_body_bytes',1000),('maximum_profiles_per_section',3)]:
            bad=copy.deepcopy(op);bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):p.plan_sections(axes,h,bad,prior)
    def test_cf_record_packing_storage_and_component_frame_fail_closed(self):
        axes,h,op,prior=self.fixture()
        for mutate in [lambda v:v.update(nc_type=4),lambda v:v.update(dimension_names=['time','lat','depth','lon']),lambda v:v.update(vsize=v['vsize']-2),lambda v:v['attributes']['scale_factor'].update(values=[.01]),lambda v:v['attributes']['standard_name'].update(values='grid_northward_velocity')]:
            bad=copy.deepcopy(h);mutate(next(v for v in bad['variables'] if v['name']=='water_v'))
            with self.assertRaises(ValueError):p.plan_sections(axes,bad,op,prior)
        for key,value in [('format','CDF1'),('record_count',2),('source_content_length',100001)]:
            bad=copy.deepcopy(h);bad[key]=value
            with self.assertRaises(ValueError):p.plan_sections(axes,bad,op,prior)
        bad=copy.deepcopy(op);bad['component_bearing_degrees_true']=90
        with self.assertRaises(ValueError):p.plan_sections(axes,h,bad,prior)
    def test_native_axis_tolerance_duplicate_latitude_and_endpoint_guards(self):
        axes,h,op,prior=self.fixture()
        for targets in [[-30.,-30.001],[0.]]:
            bad=copy.deepcopy(op);bad['section_latitudes_deg_n']=targets
            with self.assertRaises(ValueError):p.plan_sections(axes,h,bad,prior)
        for key,value in [('lon',[94.,100.,96.,104.]),('time',[]),('depth',[float(i*101) for i in range(39)]+[5000.])]:
            bad=copy.deepcopy(axes);bad[key]=value
            with self.assertRaises(ValueError):p.plan_sections(bad,h,op,prior)
    def test_prior_successful_custody_ranges_are_never_replayed(self):
        axes,h,op,prior=self.fixture();sections,c=p.plan_sections(axes,h,op,prior);r=sections[0]['components']['water_u']['ranges'][0]
        prior['requests']=[{'status':'success','ranges':[list(r)]}]
        with self.assertRaises(ValueError):p.plan_sections(axes,h,op,prior)
        prior['requests']=[];prior['source_last_modified']='changed'
        with self.assertRaises(ValueError):p.plan_sections(axes,h,op,prior)
    def test_signed_fill_removed_before_scaling_and_native_transpose(self):
        raw=struct.pack('>6h',-30000,-2,3,4,-5,6);packing={'missing_packed':-30000,'scale_factor':.001,'add_offset':0.}
        self.assertEqual(p.decode_component(raw,3,2,packing),[[None,.003,-.005],[-.002,.004,.006]])
        with self.assertRaises(ValueError):p.decode_component(raw[:-1],3,2,packing)
    def test_broad_components_partition_without_bridging_gaps_or_axis_claim(self):
        axes,h,op,prior=self.fixture();z=[0,250,500,1000];a=[.02,.02,.02,0];b=[.03,.04,.03,0];negative=[-.01]*4
        r=p.corridor_diagnosis(z,[a,b,negative,negative,a],op)
        self.assertEqual(r['qualifying_column_indices'],[0,1,4]);self.assertEqual([g['column_indices'] for g in r['qualifying_component_groups']],[[0,1],[4]]);self.assertEqual(r['selected_column_index'],1)
        self.assertFalse(r['physical_current_axis_validated']);self.assertTrue(all(not g['is_named_current_or_physical_width'] for g in r['qualifying_component_groups']))
    def test_full_depth_tracing_and_no_deep_or_sensitivity_fill(self):
        axes,h,op,prior=self.fixture();z=[0,250,500,1000];strong=[.02,.03,.02,0];weak=[.007,.007,.007,.4]
        r=p.corridor_diagnosis(z,[[0.]*4,strong,[0.]*4],op);layer=next(x for x in r['selected_column_threshold_layers'] if x['threshold_m_s']==.01);self.assertGreater(layer['lower_depth_m'],500)
        r=p.corridor_diagnosis(z,[weak]*3,op);self.assertIsNone(r['selected_column_index']);self.assertEqual(r['qualifying_column_indices'],[])
    def test_missing_support_and_deepest_positive_flow_remain_unknown(self):
        axes,h,op,prior=self.fixture();z=[0,250,500,1000];missing=[.02,None,.02,0]
        r=p.corridor_diagnosis(z,[[0.]*4,missing,[0.]*4],op);self.assertEqual(r['qualifying_column_indices'],[])
        r=p.corridor_diagnosis(z,[[.02]*4]*3,op);layer=next(x for x in r['selected_column_threshold_layers'] if x['threshold_m_s']==.01);self.assertIsNone(layer['lower_depth_m']);self.assertEqual(layer['lower_status'],'censored_at_sample_domain_edge');self.assertFalse(r['regional_inventory_promotion_authorized'])
    def test_qualified_mean_has_no_fabricated_snapshot_or_seasonal_range_and_pins(self):
        axes,h,op,prior=self.fixture();c=p.mean_context(op,axes);self.assertIsNone(c['snapshot_time_utc']);self.assertFalse(c['time_coordinate_is_averaging_interval']);self.assertFalse(c['fixed_depth_Eulerian_mean_equivalence_verified']);self.assertFalse(c['seasonal_mean_or_annual_extrema_established'])
        self.assertEqual(op['section_latitudes_deg_n'],[-30.,-28.,-26.,-24.]);self.assertEqual(op['longitude_gate_deg_e'],[94.,104.]);self.assertEqual(op['primary_threshold_m_s'],.01);self.assertEqual(op['selection_depth_interval_m'],[0,500])
        for f,pin in op['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin,f)


if __name__=='__main__':unittest.main()
