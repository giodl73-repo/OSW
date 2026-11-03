import base64,copy,csv,hashlib,io,json,unittest
import build_current_depth_route_projections_v62 as p
import load_current_depth_projection_inventory_v1 as loader
from build_current_depth_route_projections_v12 import interpolate


class MeridionalMeanDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes());cls.inventory,cls.addendum,cls.pieces,cls.view=p.build();cls.cases=cls.addendum['projections']+cls.addendum['unresolved_reference_cases'];cls.prior=json.loads((p.ROOT/cls.op['previous_inventory_file']).read_bytes());cls.before=loader.load_inventory(cls.prior,lambda f:(p.ROOT/f).read_bytes())
        read=lambda f:json.loads((p.ROOT/f).read_bytes());cls.sop=read(cls.op['source_operator_file']);cls.geometry=read(cls.sop['geometry_operator_file']);d=cls.op['source_directory']
        cls.args={'manifest':read(cls.op['source_manifest_file']),'sections':{'section-%02d.json'%i:read(d+'section-%02d.json'%i) for i in range(4)},'rectangles':{n:read(d+'rectangle-'+n+'.json') for n in ['water_u','water_v']},'ledger':read(cls.op['source_ledger_file']),'sop':cls.sop,'geometry':cls.geometry,'header':read(cls.geometry['header_file']),'axes':read(cls.geometry['coordinates_file'])['coordinate_arrays'],'prior_ledger':read(cls.sop['prior_ledger_files'][0]),'seed':read(cls.sop['prior_checkpoint_file']),'bundle':read(cls.sop['prior_checkpoint_bundle_file']),'imported':read(d+'imported-custody.json'),'source_operator_sha':hashlib.sha256((p.ROOT/cls.op['source_operator_file']).read_bytes()).hexdigest()}
        cls.report=json.loads(cls.pieces[p.REPORT])
    def reader(self,f):return self.pieces[f] if f in self.pieces else (p.ROOT/f).read_bytes()
    def audit(self,**updates):
        args={**self.args,**updates};return p.audit_fields(**args)
    def test_prior_298_supported_27_unresolved_47_addenda_and_other_currents_preserved(self):
        self.assertEqual(self.view['projections'][:298],self.before['projections']);self.assertEqual(self.view['unresolved_reference_cases'][:27],self.before['unresolved_reference_cases']);self.assertEqual(self.inventory['base'],self.prior['base']);self.assertEqual(self.inventory['addenda'][:47],self.prior['addenda'])
        for row in self.before['records']:
            after=next(r for r in self.view['records'] if r['entity_id']==row['entity_id']);self.assertEqual(row['depth_reference_ids'],after['depth_reference_ids'])
            if row['entity_id']!='current:pacific-north-equatorial-undercurrent':self.assertEqual(row,after)
    def test_four_meridional_spatial_mean_cases_all204_native_points(self):
        self.assertEqual(len(self.cases),4);self.assertEqual(sum(len(c['anchors']) for c in self.cases),204);self.assertEqual(len({c['id'] for c in self.cases}),4)
        for case in self.cases:
            self.assertEqual(case['entity_id'],'current:pacific-north-equatorial-undercurrent');self.assertEqual(case['field_geometry_kind'],p.FIELD_KIND);self.assertEqual(case['source_section_geometry'],'longitude');self.assertEqual(case['selection_depth_interval_m'],[300.,1500.]);self.assertEqual(case['primary_threshold_m_s'],.02);self.assertIsNone(case['snapshot_time_utc']);self.assertFalse(case['axis_selection_applied']);self.assertTrue(case['primary_detached_layer_required']);self.assertTrue(case['independent_latitude_context_required'])
            for a in case['anchors']:self.assertEqual(a['source_component_bearing_degrees_true'],90);self.assertFalse(a['reference_geometry_is_unselected_gate_midpoint'])
    def test_full_source_rows_decoding_and_all_historical_attempts_verified(self):
        audit,derived=self.audit();self.assertEqual(audit,self.addendum['source_field_audit']);self.assertEqual(derived,self.report['sections']);self.assertEqual((audit['exact_source_rows_verified'],audit['historical_attempts_preserved'],audit['aggregate_http_attempts'],audit['packed_bytes_verified'],audit['native_rectangle_profiles_verified'],audit['native_profiles_verified']),(4080,465,820,522240,3264,204));self.assertEqual(audit['new_field_requests'],0)
    def test_reset_history_replayed_row_changed_hash_source_or_budget_rejected(self):
        for kind in ['history','replay','hash','source','budget','body','failed']:
            ledger=copy.deepcopy(self.args['ledger'])
            if kind=='history':ledger['requests'][0]['status']='success'
            if kind=='replay':ledger['requests'][465]['ranges'][0]=ledger['requests'][1]['ranges'][0]
            if kind=='hash':ledger['requests'][465]['parts'][0]['sha256']='0'*64
            if kind=='source':ledger['source_bytes']+=1
            if kind=='budget':ledger['maximum_requests']+=1
            if kind=='body':ledger['response_body_bytes']-=1
            if kind=='failed':ledger['requests'][465]['status']='failed_no_replay'
            with self.subTest(kind=kind),self.assertRaises(ValueError):self.audit(ledger=ledger)
    def test_corrupt_imported_checkpoint_or_import_receipt_rejected(self):
        bundle=copy.deepcopy(self.args['bundle']);bundle['members'][0]['sha256']='0'*64
        with self.assertRaises(ValueError):self.audit(bundle=bundle)
        receipt=copy.deepcopy(self.args['imported']);receipt['prior_http_requests']=0
        with self.assertRaises(ValueError):self.audit(imported=receipt)
    def test_rectangle_bytes_packing_and_native_coordinates_rejected(self):
        for kind in ['raw','packing','coordinate','shape']:
            rectangles=copy.deepcopy(self.args['rectangles']);value=rectangles['water_u']
            if kind=='raw':
                raw=bytearray(base64.b64decode(value['packed_base64']));raw[0]^=1;value['packed_base64']=base64.b64encode(raw).decode();value['packed_sha256']=hashlib.sha256(raw).hexdigest()
            if kind=='packing':value['packing']['scale_factor']=.01
            if kind=='coordinate':value['native_latitudes_deg_n'][0]+=.01
            if kind=='shape':value['packed_shape'][0]-=1
            with self.subTest(kind=kind),self.assertRaises(ValueError):self.audit(rectangles=rectangles)
    def test_section_raw_extraction_CF_frame_position_and_source_diagnosis_rejected(self):
        for kind in ['raw','packing','decoded','longitude','diagnosis','snapshot']:
            sections=copy.deepcopy(self.args['sections']);s=sections['section-00.json']
            if kind=='raw':s['components']['water_u']['packed_base64']='AAAA'
            if kind=='packing':s['components']['water_u']['packing']['scale_factor']=.01
            if kind=='decoded':s['components']['water_u']['profiles_m_s'][0][0]=999
            if kind=='longitude':s['sampled_longitude_deg_e']+=.01
            if kind=='diagnosis':s['diagnostic']['selected_column_index']=None
            if kind=='snapshot':s['snapshot_time_utc']='2022-01-01T00:00:00Z'
            with self.subTest(kind=kind),self.assertRaises(ValueError):self.audit(sections=sections)
    def test_false_mean_semantics_and_physical_claims_rejected(self):
        for key,value in [('snapshot_time_utc','2005-01-01'),('averaging_semantics_validated',True),('provider_regional_bias_assessed',True),('current_identity_validated',True),('regional_inventory_promotion_authorized',True)]:
            m=copy.deepcopy(self.args['manifest']);m[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.audit(manifest=m)
    def test_native_positions_primary_report_pointers_and_eligibility_rules(self):
        for case in self.cases:
            for a in case['anchors']:
                f,pointer=a['source_model_profile_ref'].split('#');source=self.args['sections'][f.split('/')[-1]];j=a['source_profile_index'];self.assertEqual(a['reference_lon_lat'],[source['sampled_longitude_deg_e'],source['native_latitudes_deg_n'][j]])
                if a['source_connected_diagnosis_ref']:
                    file,pointer=a['source_connected_diagnosis_ref'].split('#');self.assertEqual(file,p.REPORT);v=self.report
                    for key in pointer.split('/')[1:]:v=v[int(key)] if isinstance(v,list) else v[key]
                    self.assertEqual(a['source_model_connected_layer'],v);self.assertEqual(v['threshold_m_s'],.02)
                if a['lower_projection_eligible']:
                    self.assertTrue(6.5<=a['reference_lon_lat'][1]<=9.5);self.assertEqual(a['source_model_connected_layer']['upper_status'],'adjacent_isotach_crossing');self.assertGreater(a['model_upper_depth_m'],0);self.assertIsNotNone(a['model_lower_depth_m']);self.assertFalse(a['projection_block_reasons'])
                else:self.assertTrue(a['projection_block_reasons'])
    def synthetic(self,layers):
        section={'section_index':0,'sampled_longitude_deg_e':135.,'native_latitudes_deg_n':[6.4,7.,8.],'native_latitude_indices':[1,2,3]}
        derived=[{'candidate_scores':[{'eligible':True}]*3,'all_qualifying_column_layers':[{'column_index':i,'layers':copy.deepcopy(layers[i])} for i in range(3)]}]
        return p.field_cases({'section-00.json':section},derived,'synthetic/',self.geometry,self.op)
    def test_surface_connected_and_outside_context_rejected_without_axis_reselection(self):
        layer={'threshold_m_s':.02,'upper_depth_m':100.,'lower_depth_m':1000.,'layer_thickness_m':900.,'upper_status':'adjacent_isotach_crossing','lower_status':'adjacent_isotach_crossing','status':'resolved_connected_model_threshold_layer'}
        surface={**layer,'upper_depth_m':0.,'upper_status':'surface_bounded_layer','layer_thickness_m':1000.}
        supported,blocked=self.synthetic([[layer],[layer],[surface]]);self.assertFalse(blocked);anchors=supported[0]['anchors'];self.assertEqual([a['lower_projection_eligible'] for a in anchors],[False,True,False]);self.assertIn('outside_independent_southern_jet_latitude_context',anchors[0]['projection_block_reasons']);self.assertIn('primary_layer_not_resolved_detached_below_surface',anchors[2]['projection_block_reasons']);self.assertTrue(all(s['projection_status']=='gap_no_projection' for s in supported[0]['segments']))
    def test_censored_primary_not_filled_by_resolved_sensitivity(self):
        layer={'threshold_m_s':.02,'upper_depth_m':100.,'lower_depth_m':None,'layer_thickness_m':None,'upper_status':'adjacent_isotach_crossing','lower_status':'censored_at_native_domain','status':'unresolved_connected_model_threshold_layer'};weak={**layer,'threshold_m_s':.01,'lower_depth_m':1200.,'layer_thickness_m':1100.}
        supported,blocked=self.synthetic([[weak,layer]]*3);self.assertFalse(supported);self.assertEqual(len(blocked),1);self.assertTrue(all(a['model_lower_depth_m'] is None for a in blocked[0]['anchors']))
    def test_all_unsupported_adjacent_pairs_are_gaps(self):
        for c in self.cases:
            for a,b,s in zip(c['anchors'],c['anchors'][1:],c['segments']):
                value,used,status=interpolate(c['anchors'],(a['distance_km']+b['distance_km'])/2);self.assertEqual(used,[a,b])
                if not (a['lower_projection_eligible'] and b['lower_projection_eligible']):self.assertIsNone(value['model_lower_depth_m']);self.assertEqual(s['projection_status'],'gap_no_projection')
    def test_old_csv_cells_and_new_mean_geometry_detachment_flags_preserved(self):
        old=list(csv.DictReader(io.StringIO(loader.combined_csv_bytes(self.prior,lambda f:(p.ROOT/f).read_bytes()).decode())));new=list(csv.DictReader(io.StringIO(loader.combined_csv_bytes(self.inventory,self.reader).decode())))
        for a,b in zip(old,new):self.assertEqual(a,{k:b[k] for k in a})
        self.assertEqual(len(new)-len(old),sum(len(c['samples']) for c in self.addendum['projections']))
        for r in new[len(old):]:
            self.assertEqual(r['snapshot_time_utc'],'');self.assertEqual(r['snapshot_is_applicable'],'False');self.assertEqual(r['source_section_geometry'],'longitude');self.assertEqual(r['field_geometry_kind'],p.FIELD_KIND);self.assertEqual(r['method_id'],p.METHOD);self.assertEqual(r['primary_detached_layer_required'],'True');self.assertEqual(r['independent_latitude_context_required'],'True')
    def test_all_physical_annual_volume_claims_remain_unknown(self):
        for c in self.cases:
            self.assertFalse(any(c['eligibility'].values()));self.assertIsNone(c['physical_thickness_m']);self.assertIsNone(c['annual_range_m']);self.assertFalse(c['whole_current_representative']);self.assertFalse(c['mean_is_mean_of_instantaneous_depths']);self.assertFalse(c['cross_section_is_physical_current_width']);self.assertFalse(c['current_identity_independently_validated'])
            for s in c['samples']:self.assertFalse(s['volume_eligible']);self.assertIsNone(s['physical_thickness_m'])
        self.assertEqual(self.view['counts']['whole_route_physical_depth_profiles'],0);self.assertEqual(self.view['counts']['volume_estimates'],0)
    def test_report_input_pins_piece_caps_and_counts_verified(self):
        for f,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin,f)
        report=self.addendum['derived_source_report'];self.assertEqual(report['sha256'],hashlib.sha256(self.pieces[p.REPORT]).hexdigest());self.assertEqual(report['bytes'],len(self.pieces[p.REPORT]));self.assertTrue(all(len(raw)<2500000 for raw in self.pieces.values()));self.assertEqual(loader.load_inventory(self.inventory,self.reader)['counts'],self.inventory['counts'])
        bad=copy.deepcopy(self.inventory);bad['counts']['regional_projection_scenarios']+=1
        with self.assertRaises(ValueError):loader.load_inventory(bad,self.reader)


if __name__=='__main__':unittest.main()
