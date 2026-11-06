import copy,csv,hashlib,io,json,unittest
import build_current_depth_reference_inventory_v13 as p
import load_current_depth_reference_inventory_v12 as prior
import load_current_depth_reference_inventory_v13 as loader


class NorthwardAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory,cls.addendum,cls.bundle,cls.pieces,cls.view=p.build();cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes());cls.previous=json.loads((p.ROOT/cls.op['previous_inventory_file']).read_bytes());cls.before=prior.load_inventory(cls.previous,lambda f:(p.ROOT/f).read_bytes());cls.parts=prior.read_parts(cls.previous,lambda f:(p.ROOT/f).read_bytes())
    def reader(self,file):return self.pieces[file] if file in self.pieces else (p.ROOT/file).read_bytes()
    def assembled(self,a=None,b=None):return loader.assemble(*self.parts,[(a or self.addendum,b or self.bundle)])
    def test_all784_prior_evidence_contexts_record_fields_and_pieces_preserved(self):
        self.assertEqual(self.view['evidence'][:784],self.before['evidence']);self.assertEqual(self.inventory['base'],self.previous['base']);self.assertEqual(self.inventory['addenda'][:-1],self.previous['addenda'])
        for k,v in self.before['source_contexts'].items():self.assertEqual(self.view['source_contexts'][k],v)
        for a,b in zip(self.before['records'],self.view['records']):self.assertEqual(b['depth_reference_ids'][:len(a['depth_reference_ids'])],a['depth_reference_ids']);self.assertEqual({k:v for k,v in a.items() if k!='depth_reference_ids'},{k:v for k,v in b.items() if k!='depth_reference_ids'})
    def test_all_eight_original_diagnoses_reproduce_and_only_seven_refs(self):
        cases=loader.native.reproduce(self.bundle);self.assertEqual(len(cases),8);self.assertEqual(len(self.addendum['evidence']),7);self.assertEqual(self.view['counts']['depth_references'],791);self.assertEqual(self.view['metric_counts'][loader.METRIC],34)
        for row in self.addendum['evidence']:self.assertEqual(row['entity_id'],'current:norwegian-coastal');self.assertEqual(row['source_context_id'],loader.CONTEXT);self.assertEqual(row['source_native_bracket_m'],row['source_classification']['lower']['bracket_m']);self.assertEqual(row['approximate_value_m'],row['source_classification']['lower']['boundary_depth_m'])
    def test_march62p25_axis_unresolved_retained_without_reference_or_zero(self):
        gaps=[r for r in self.bundle['spatial_admission_report']['records'] if r['reference_id'] is None];self.assertEqual(len(gaps),1);gap=gaps[0];self.assertEqual(gap['source_case']['section_id'],'section-62p25n');self.assertEqual(gap['source_case']['snapshot_time_utc'],'2022-03-15T00:00:00Z');self.assertEqual(gap['curtain']['columns'],[]);self.assertEqual(gap['classification']['status'],'original_horizontal_axis_unresolved');self.assertNotIn('lower',gap['classification'])
    def test_original_selected_core_boundaries_equal_admitted_and_spatial(self):
        rows={r['id']:r for r in self.addendum['evidence']}
        for record in self.bundle['spatial_admission_report']['records']:
            if record['reference_id'] is None:continue
            runs=[r for col in record['curtain']['columns'] for r in col['connected_depth_runs'] if r['contains_original_core']];self.assertEqual(len(runs),1);self.assertEqual(runs[0]['upper'],record['classification']['upper']);self.assertEqual(runs[0]['lower'],record['classification']['lower']);self.assertEqual(runs[0]['lower']['boundary_depth_m'],rows[record['reference_id']]['approximate_value_m'])
    def test_curtains_reuse_frozen_topology_for_all_native_columns(self):
        cases=loader.native.reproduce(self.bundle);expected=loader.native.curtains(cases,self.bundle)
        for record,curtain in zip(self.bundle['spatial_admission_report']['records'],expected):self.assertEqual(record['curtain'],curtain)
        counts=self.bundle['spatial_admission_report']['counts'];self.assertEqual(counts['original_cases_reproduced'],8);self.assertEqual(counts['depth_curtains'],7);self.assertEqual(counts['unclassified_cases'],1);self.assertGreater(counts['seed_connected_columns'],7)
    def test_both_components_must_reproduce_northward_signed_field(self):
        b=copy.deepcopy(self.bundle);s=next(iter(b['sections'].values()));s['columns'][0]['northward_velocity_m_s'][0]=9
        with self.assertRaises(ValueError):loader.native.reproduce(b)
    def test_original_velocity_selection_and_fresh_boundary_cannot_change(self):
        for mode in ['selection','boundary','salt']:
            b=copy.deepcopy(self.bundle);s=next(iter(b['sections'].values()))
            if mode=='selection':s['diagnosis']['selected_column_index']+=1
            elif mode=='boundary':s['fresh_component_classification']['lower']['boundary_depth_m']=999
            else:s['practical_salinity_columns'][s['diagnosis']['selected_column_index']][0]=49
            with self.subTest(mode=mode),self.assertRaises(ValueError):loader.native.reproduce(b)
    def test_all_native_coordinate_date_index_and_depth_metadata_required(self):
        for mode in ['longitude','latitude','index','time','date','depth','pairing']:
            b=copy.deepcopy(self.bundle);s=next(iter(b['sections'].values()))
            if mode=='longitude':s['columns'][0]['native_source_longitude_degrees_east']+=.1
            elif mode=='latitude':s['native_latitude_degrees_north']+=.1
            elif mode=='index':s['columns'][0]['global_longitude_index']+=1
            elif mode=='time':s['source_time_index']+=1
            elif mode=='date':s['source_returned_timestamp_utc']='2022-03-15T03:00:00Z'
            elif mode=='depth':s['depth_levels_m'][3]+=.1
            else:s['native_coordinates_exactly_paired']=False
            with self.subTest(mode=mode),self.assertRaises(ValueError):loader.native.reproduce(b)
    def test_source_metadata_units_frame_and_physical_limits_required(self):
        for mode in ['unit','frame','physical']:
            b=copy.deepcopy(self.bundle);s=next(iter(b['sections'].values()))
            if mode=='unit':s['source_metadata']['variables']['salinity']['units']='g/kg'
            elif mode=='frame':s['source_metadata']['variables']['water_v']['standard_name']='eastward_sea_water_velocity'
            else:s['physical_current_bottom_established']=True
            with self.subTest(mode=mode),self.assertRaises(ValueError):loader.native.reproduce(b)
    def test_ordered_unique_three_field_ledger_patches_and_attempts_required(self):
        for mode in ['duplicate','patch','attempt','status']:
            b=copy.deepcopy(self.bundle);ledger=b['ledger']
            if mode=='duplicate':ledger['requests'].append(copy.deepcopy(ledger['requests'][0]))
            elif mode=='patch':ledger['requests'][0]['latitude_index']+=1
            elif mode=='attempt':ledger['requests'][0]['attempt']=2
            else:ledger['requests'][0]['status']='provider_io_failure'
            b['report']['transport']=copy.deepcopy(ledger)
            with self.subTest(mode=mode),self.assertRaises(ValueError):loader.native.reproduce(b)
    def test_joint_reservations_requested_returned_and_caps_cannot_change(self):
        for key in ['planned_velocity_cell_pairs','additional_retry_scalar_values_reserved','joint_reserved_native_cell_units','conservative_joint_decoded_bytes','actual_requested_scalar_values','successful_returned_scalar_values','maximum_joint_native_cell_units','maximum_decoded_bytes']:
            b=copy.deepcopy(self.bundle);b['ledger'][key]+=1;b['report']['transport']=copy.deepcopy(b['ledger'])
            with self.subTest(key=key),self.assertRaises(ValueError):loader.native.reproduce(b)
    def test_existing_native_case_cannot_be_duplicated(self):
        before=copy.deepcopy(self.before);before['evidence'].append(copy.deepcopy(self.addendum['evidence'][0]))
        with self.assertRaises(ValueError):loader.admission(before,self.bundle,self.addendum)
    def test_all_and_only_seven_source_refs_and_new_context(self):
        for mode in ['omit','duplicate','pointer','context']:
            a=copy.deepcopy(self.addendum)
            if mode=='omit':a['evidence'].pop()
            elif mode=='duplicate':a['evidence'].append(copy.deepcopy(a['evidence'][0]))
            elif mode=='pointer':a['evidence'][0]['source_pointer']='/fresh_component_classification/upper'
            else:a['source_contexts'][loader.CONTEXT]['practical_salinity_exclusive_upper_threshold']=34
            with self.subTest(mode=mode),self.assertRaises(ValueError):self.assembled(a)
    def test_brackets_not_uncertainty_annual_range_thickness_width_or_volume(self):
        for key,value in [('thickness_m',50),('lower_boundary_m',50),('uncertainty_m',5),('annual_range_m',[37,186]),('source_native_bracket_is_annual_range',True),('physical_current_bottom_established',True),('volume_eligible',True),('same_source_width_reference_id','width'),('calendar_months',[3])]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.assembled(a)
    def test_spatial_report_gap_boundary_and_physical_promotions_rejected(self):
        for mode in ['gap','boundary','width','count']:
            b=copy.deepcopy(self.bundle);report=b['spatial_admission_report']
            if mode=='gap':next(r for r in report['records'] if r['reference_id'] is None)['reference_id']='fake'
            elif mode=='boundary':report['records'][0]['curtain']['columns'][0]['deepest_run_lower_boundary_depth_m']=0
            elif mode=='width':report['physical_width_established']=True
            else:report['counts']['depth_curtains']=8
            with self.subTest(mode=mode),self.assertRaises(ValueError):self.assembled(b=b)
    def test_every_source_piece_hash_and_new_output_csv_hash_required(self):
        files=[loader.native.OPERATOR,loader.native.REPORT,loader.native.DIRECTORY+'transport-ledger.json',*self.bundle['sections'],p.SPATIAL,self.inventory['addenda'][-1]['json']['file'],self.inventory['addenda'][-1]['csv']['file']]
        for file in files:
            with self.subTest(file=file),self.assertRaises(ValueError):loader.load_inventory(self.inventory,lambda f:self.reader(f)+b' ' if f==file else self.reader(f))
    def test_all_old_csv_cells_and_new_typed_native_provenance(self):
        old=list(csv.DictReader(io.StringIO(prior.combined_csv_bytes(self.previous,lambda f:(p.ROOT/f).read_bytes()).decode())));new=list(csv.DictReader(io.StringIO(loader.combined_csv_bytes(self.inventory,self.reader).decode())));self.assertEqual(len(new),791)
        for a,b in zip(old,new):self.assertEqual(a,{k:b[k] for k in a})
        for row in new[784:]:self.assertEqual(row['thickness_m'],'');self.assertEqual(row['volume_eligible'],'False');self.assertEqual(row['source_context_id'],loader.CONTEXT)
    def test_public_pins_fixed_caps_and_no_new_ocean_or_runtime_claims(self):
        for file,pin in self.op['input_sha256'].items():self.assertFalse(file.startswith('.pytest_cache/'));self.assertEqual(hashlib.sha256((p.ROOT/file).read_bytes()).hexdigest(),pin,file)
        self.assertTrue(all(len(raw)<2500000 for raw in self.pieces.values()));self.assertLess(sum(map(len,self.pieces.values())),3000000);self.assertEqual(self.view['counts']['identities_with_scoped_depth_reference'],101);self.assertEqual(self.view['counts']['whole_route_depth_profiles'],0);self.assertEqual(self.view['counts']['volume_estimates'],0)
        report=self.bundle['spatial_admission_report'];self.assertEqual(report['new_ocean_field_requests'],0);self.assertFalse(report['source_coordinate_pairing_rechecked_against_remote_grid']);self.assertFalse(report['runtime_changed']);self.assertFalse(report['full_goal_complete'])


if __name__=='__main__':unittest.main()
