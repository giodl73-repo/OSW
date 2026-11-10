import base64,copy,csv,hashlib,io,json,unittest
import build_current_depth_route_projections_v61 as p
import load_current_depth_projection_inventory_v1 as loader
from build_current_depth_route_projections_v12 import interpolate


class QualifiedMeanFieldProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes());cls.inventory,cls.addendum,cls.pieces,cls.view=p.build();cls.cases=cls.addendum['projections']+cls.addendum['unresolved_reference_cases'];cls.prior=json.loads((p.ROOT/cls.op['previous_inventory_file']).read_bytes());cls.before=loader.load_inventory(cls.prior,lambda f:(p.ROOT/f).read_bytes());cls.sop=json.loads((p.ROOT/cls.op['source_operator_file']).read_bytes());cls.m=json.loads((p.ROOT/cls.op['source_manifest_file']).read_bytes());cls.sections={r['file']:json.loads((p.ROOT/(cls.op['source_directory']+r['file'])).read_bytes()) for r in cls.m['source_files']};cls.ledger=json.loads((p.ROOT/cls.op['source_ledger_file']).read_bytes());cls.header=json.loads((p.ROOT/cls.sop['header_file']).read_bytes());cls.axes=json.loads((p.ROOT/cls.sop['coordinates_file']).read_bytes())['coordinate_arrays'];cls.old_custody=json.loads((p.ROOT/cls.sop['prior_custody_ledger']).read_bytes())
    def reader(self,f):return self.pieces[f] if f in self.pieces else (p.ROOT/f).read_bytes()
    def audit(self,**updates):
        a={'manifest':self.m,'sections':self.sections,'ledger':self.ledger,'sop':self.sop,'header':self.header,'axes':self.axes,'prior':self.old_custody,'source_operator_sha':hashlib.sha256((p.ROOT/self.op['source_operator_file']).read_bytes()).hexdigest()};a.update(updates);return p.audit_mean_fields(**a)
    def test_all_prior_cases_ownership_and_other_currents_preserved(self):
        self.assertEqual(self.view['projections'][:294],self.before['projections']);self.assertEqual(self.view['unresolved_reference_cases'][:27],self.before['unresolved_reference_cases']);self.assertEqual(self.inventory['base'],self.prior['base']);self.assertEqual(self.inventory['addenda'][:46],self.prior['addenda'])
        for row in self.before['records']:
            after=next(r for r in self.view['records'] if r['entity_id']==row['entity_id']);self.assertEqual(row['depth_reference_ids'],after['depth_reference_ids'])
            if row['entity_id']!='current:west-australian':self.assertEqual(row,after)
    def test_four_spatial_mean_cases_all504_actual_native_anchors(self):
        self.assertEqual(len(self.cases),4);self.assertEqual(sum(len(c['anchors']) for c in self.cases),504);self.assertEqual(len({c['id'] for c in self.cases}),4)
        for c in self.cases:
            self.assertEqual(c['entity_id'],'current:west-australian');self.assertIsNone(c['snapshot_time_utc']);self.assertFalse(c['snapshot_is_applicable']);self.assertFalse(c['axis_selection_applied']);self.assertEqual(c['field_geometry_kind'],p.FIELD_KIND);self.assertFalse(c['mean_is_mean_of_instantaneous_depths']);self.assertEqual(c['method_id'],p.METHOD)
            for a in c['anchors']:self.assertFalse(a['reference_geometry_is_unselected_gate_midpoint']);self.assertFalse(a['axis_selection_applied']);self.assertEqual(a['source_component_bearing_degrees_true'],0)
    def test_all320_wire_rows_CF_decoded_columns_and_mean_context_verified(self):
        audit=self.audit();self.assertEqual(audit['exact_source_rows_verified'],320);self.assertEqual(audit['native_profiles_verified'],504);self.assertEqual(audit['packed_bytes_verified'],80640);self.assertEqual(audit['new_field_requests'],0);self.assertTrue(audit['source_representative_diagnoses_unchanged']);self.assertFalse(audit['physical_current_identity_validated'])
    def test_wire_identity_range_order_body_hash_and_budget_mutations_rejected(self):
        for kind in ['identity','range','hash','failed','budget']:
            ledger=copy.deepcopy(self.ledger)
            if kind=='identity':ledger['source_bytes']+=1
            if kind=='range':ledger['requests'][0]['ranges'][0][0]+=2
            if kind=='hash':ledger['requests'][0]['parts'][0]['sha256']='0'*64
            if kind=='failed':ledger['requests'][0]['status']='failed_no_replay'
            if kind=='budget':ledger['maximum_requests']+=1
            with self.subTest(kind=kind),self.assertRaises(ValueError):self.audit(ledger=ledger)
    def test_raw_packing_coordinate_decoded_frame_and_diagnosis_mutations_rejected(self):
        first=self.m['source_files'][0]['file']
        for kind in ['raw','packing','position','component','group','representative']:
            sections=copy.deepcopy(self.sections);s=sections[first]
            if kind=='raw':
                c=s['components']['water_v'];raw=bytearray(base64.b64decode(c['packed_base64']));raw[0]^=1;c['packed_base64']=base64.b64encode(raw).decode();c['packed_sha256']=hashlib.sha256(raw).hexdigest()
            if kind=='packing':s['components']['water_v']['packing']['scale_factor']=.01
            if kind=='position':s['columns'][0]['sampled_lon_lat'][0]+=.01
            if kind=='component':s['columns'][0]['signed_reference_component_m_s'][0]=999
            if kind=='group':s['diagnosis']['qualifying_component_groups']=[]
            if kind=='representative':s['diagnosis']['selected_column_index']=0
            with self.subTest(kind=kind),self.assertRaises(ValueError):self.audit(sections=sections)
    def test_fabricated_snapshot_sampling_coverage_and_physical_promotion_rejected(self):
        first=self.m['source_files'][0]['file']
        for key,value in [('snapshot_time_utc','2005-01-01T00:00:00Z'),('actual_averaging_coverage_verified',True),('fixed_depth_Eulerian_mean_equivalence_verified',True),('seasonal_mean_or_annual_extrema_established',True)]:
            sections=copy.deepcopy(self.sections);sections[first]['source_mean_context'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.audit(sections=sections)
        m=copy.deepcopy(self.m);m['regional_inventory_promotion_authorized']=True
        with self.assertRaises(ValueError):self.audit(manifest=m)
    def test_point_values_actual_positions_and_exact_primary_layer_pointers(self):
        for c in self.cases:
            for a in c['anchors']:
                f,pointer=a['source_model_profile_ref'].split('#');s=self.sections[f.split('/')[-1]];column=s['columns'][int(pointer.split('/')[-1])];self.assertEqual(a['reference_lon_lat'],column['sampled_lon_lat'])
                if a['source_connected_diagnosis_ref']:
                    value=s
                    for key in a['source_connected_diagnosis_ref'].split('#')[1].split('/')[1:]:value=value[int(key)] if isinstance(value,list) else value[key]
                    self.assertEqual(a['source_model_connected_layer'],value);self.assertEqual(value['threshold_m_s'],.01);self.assertEqual(a['model_lower_depth_m'],value['lower_depth_m'])
    def test_native_field_edge_point_does_not_require_or_promote_axis_maximum(self):
        layer={'threshold_m_s':.01,'upper_depth_m':0.,'lower_depth_m':100.,'layer_thickness_m':100.,'upper_status':'surface_bounded_layer','lower_status':'adjacent_isotach_crossing','status':'resolved_connected_model_threshold_layer'}
        columns=[{'native_longitude_index':i,'sampled_lon_lat':[94.+i,-30.]} for i in range(3)];d={'candidate_scores':[{'eligible':True},{'eligible':False},{'eligible':False}],'all_qualifying_column_layers':[{'column_index':0,'layers':[layer]}]};s={'section_index':0,'columns':columns,'diagnosis':d,'source_mean_context':self.m['source_mean_context']};m={'source_files':[{'file':'synthetic.json'}]}
        supported,blocked=p.field_cases(m,{'synthetic.json':s},'synthetic/',self.sop,self.op);self.assertFalse(blocked);case=supported[0];self.assertTrue(case['anchors'][0]['lower_projection_eligible']);self.assertFalse(case['axis_selection_applied']);self.assertFalse(case['representative_axis_proxy_controls_field_point_eligibility']);self.assertTrue(all(seg['projection_status']=='gap_no_projection' for seg in case['segments']))
    def test_all_ineligible_or_censored_points_preserve_gaps_without_sensitivity_fill(self):
        for c in self.cases:
            for a,b,seg in zip(c['anchors'],c['anchors'][1:],c['segments']):
                value,used,status=interpolate(c['anchors'],(a['distance_km']+b['distance_km'])/2);self.assertEqual(used,[a,b])
                if not (a['lower_projection_eligible'] and b['lower_projection_eligible']):self.assertIsNone(value['model_lower_depth_m']);self.assertEqual(seg['projection_status'],'gap_no_projection')
            for a in c['anchors']:
                if a['lower_projection_eligible']:self.assertIsNotNone(a['model_lower_depth_m']);self.assertFalse(a['projection_block_reasons'])
                else:self.assertTrue(a['projection_block_reasons'])
        for c in self.addendum['unresolved_reference_cases']:self.assertFalse(any(a['lower_projection_eligible'] for a in c['anchors']))
    def test_csv_preserves_all_prior_cells_and_mean_field_flags_without_dates(self):
        old=list(csv.DictReader(io.StringIO(loader.combined_csv_bytes(self.prior,lambda f:(p.ROOT/f).read_bytes()).decode())));new=list(csv.DictReader(io.StringIO(loader.combined_csv_bytes(self.inventory,self.reader).decode())))
        for a,b in zip(old,new):self.assertEqual(a,{k:b[k] for k in a})
        self.assertEqual(len(new)-len(old),sum(len(c['samples']) for c in self.addendum['projections']))
        for row in new[len(old):]:self.assertEqual(row['snapshot_time_utc'],'');self.assertEqual(row['snapshot_is_applicable'],'False');self.assertEqual(row['axis_selection_applied'],'False');self.assertEqual(row['field_geometry_kind'],p.FIELD_KIND);self.assertEqual(row['nominal_provider_period'],'1994_01_2015_12');self.assertEqual(row['method_id'],p.METHOD)
    def test_no_physical_depth_volume_annual_range_or_source_field_replay_claim(self):
        for c in self.cases:
            self.assertFalse(any(c['eligibility'].values()));self.assertIsNone(c['physical_thickness_m']);self.assertIsNone(c['annual_range_m']);self.assertFalse(c['whole_current_representative']);self.assertFalse(c['cross_section_is_physical_current_width']);self.assertFalse(c['current_identity_independently_validated'])
            for sample in c['samples']:self.assertFalse(sample['volume_eligible']);self.assertIsNone(sample['physical_thickness_m'])
        self.assertEqual(self.view['counts']['whole_route_physical_depth_profiles'],0);self.assertEqual(self.view['counts']['volume_estimates'],0)
    def test_input_piece_pins_counts_and_publication_caps_fail_closed(self):
        for f,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin,f)
        self.assertEqual(loader.load_inventory(self.inventory,self.reader)['counts'],self.inventory['counts']);self.assertTrue(all(len(raw)<2500000 for raw in self.pieces.values()))
        bad=copy.deepcopy(self.inventory);bad['counts']['regional_projection_scenarios']+=1
        with self.assertRaises(ValueError):loader.load_inventory(bad,self.reader)
        path=self.inventory['addenda'][-1]['json']['file']
        with self.assertRaises(ValueError):loader.load_inventory(self.inventory,lambda f:self.reader(f)+b' ' if f==path else self.reader(f))


if __name__=='__main__':unittest.main()
