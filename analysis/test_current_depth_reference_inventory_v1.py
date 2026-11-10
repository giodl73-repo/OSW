import copy,csv,hashlib,io,json,unittest
import build_current_depth_reference_inventory_v1 as p
import load_current_depth_reference_inventory_v1 as loader


class StatisticalDepthReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes());cls.inventory,cls.addendum,cls.pieces,cls.view=p.build();cls.base=json.loads((p.ROOT/cls.op['base_register_file']).read_bytes());cls.facts=json.loads((p.ROOT/cls.op['source_facts_file']).read_bytes())
    def reader(self,f):return self.pieces[f] if f in self.pieces else (p.ROOT/f).read_bytes()
    def test_all701_prior_references_and_all_other_current_records_unchanged(self):
        self.assertEqual(self.view['evidence'][:701],self.base['evidence']);self.assertEqual(self.view['counts']['depth_references'],713);self.assertEqual(self.view['counts']['identities_with_scoped_depth_reference'],101)
        for before in self.base['records']:
            after=next(r for r in self.view['records'] if r['entity_id']==before['entity_id'])
            if before['entity_id']!='current:red-sea-saline-overflow':self.assertEqual(after,before)
            else:
                self.assertEqual(after['depth_reference_ids'][:len(before['depth_reference_ids'])],before['depth_reference_ids']);self.assertEqual(len(after['depth_reference_ids'])-len(before['depth_reference_ids']),12)
                self.assertEqual({k:v for k,v in after.items() if k!='depth_reference_ids'},{k:v for k,v in before.items() if k!='depth_reference_ids'})
    def test_transcription_matches_all_original_table2_channel_layer_cruise_statistics(self):
        expected={('northern','bottom'):([59,34,119,21],[42,25,88,12]),('northern','interfacial'):([102,36,286,21],[69,40,116,12]),('northern','whole_plume'):([161,76,344,21],[111,65,186,12]),('southern','bottom'):([45,16,119,16],[36,16,81,10]),('southern','interfacial'):([63,19,146,16],[64,21,139,10]),('southern','whole_plume'):([108,49,184,16],[100,38,186,10])}
        self.assertEqual(len(self.addendum['evidence']),12)
        for row in self.addendum['evidence']:
            values=expected[row['source_channel'],row['source_layer_component']][0 if row['source_cruise']=='REDSOX-1' else 1]
            self.assertEqual([row['approximate_value_m'],*row['range_m'],row['source_cast_count']],values);self.assertEqual(row['metric'],'reported_vertical_thickness');self.assertEqual(row['vertical_datum'],'not_applicable_thickness_distance')
    def test_cruise_specific_boundaries_and_active_cast_selection_preserved(self):
        for row in self.addendum['evidence']:
            winter=row['source_cruise']=='REDSOX-1';self.assertEqual(row['source_top_boundary_speed_threshold_m_s'],.075 if winter else .05);self.assertEqual(row['source_top_boundary_salinity_threshold_psu'],36.5 if winter else 35.7);self.assertEqual(row['source_top_boundary_direction_departure_degrees'],45);self.assertTrue(row['source_active_flow_cast_selection']);self.assertTrue(row['source_layer_cast_sets_overlap']);self.assertFalse(row['seasonal_common_operator_comparison_eligible']);self.assertFalse(row['independent_observation_count_claimed']);self.assertEqual(row['source_bottom_layer_detection_limit_approximately_m'],15)
    def test_original_source_provenance_and_exact_fact_pointers(self):
        acquisition=json.loads((p.ROOT/self.op['source_acquisition_file']).read_bytes());self.assertEqual(self.facts['source_pdf_sha256'],acquisition['sha256']);self.assertEqual(self.facts['source_pdf_bytes'],1432988);self.assertTrue(self.facts['original_page_visually_reviewed'])
        for row in self.addendum['evidence']:
            fact=self.facts['data'][int(row['source_pointer'].split('/')[-1])];self.assertEqual(row['source_reported_mean_thickness_m'],fact['mean_thickness_m']);self.assertEqual(row['source_sha256'],hashlib.sha256((p.ROOT/row['source_file']).read_bytes()).hexdigest())
    def test_duplicate_reference_unknown_owner_context_overwrite_and_bad_source_rule_rejected(self):
        for kind in ['duplicate','owner','context','rule','selection','operator']:
            a=copy.deepcopy(self.addendum)
            if kind=='duplicate':a['evidence'].append(a['evidence'][0])
            if kind=='owner':a['evidence'][0]['entity_id']='current:unknown'
            if kind=='context':a['source_contexts']=copy.deepcopy(self.base['source_contexts'])
            if kind=='rule':a['evidence'][0]['source_top_boundary_speed_threshold_m_s']=.05
            if kind=='selection':a['evidence'][0]['source_active_flow_cast_selection']=False
            if kind=='operator':a['evidence'][0]['source_top_boundary_operator']='all_three_conditions_required'
            with self.subTest(kind=kind),self.assertRaises(ValueError):loader.assemble(self.base,[a])
    def test_false_whole_current_annual_confidence_width_or_volume_promotion_rejected(self):
        for key,value in [('annual_range_m',[38,344]),('range_is_confidence_interval',True),('whole_current_representative',True),('volume_eligible',True),('same_source_width_reference_id','bathymetric-channel-width'),('thickness_m',161),('calendar_months',[2]),('seasonal_common_operator_comparison_eligible',True)]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):loader.assemble(self.base,[a])
    def test_invalid_or_inconsistent_reported_statistics_rejected(self):
        for key,value in [('approximate_value_m',999),('range_m',[120,34]),('source_cast_count',0),('source_reported_minimum_thickness_m',33)]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):loader.assemble(self.base,[a])
    def test_base_or_addendum_integrity_and_duplicate_manifest_parts_rejected(self):
        for piece in [self.inventory['base']['json'],self.inventory['base']['csv'],self.inventory['addenda'][0]['json'],self.inventory['addenda'][0]['csv']]:
            with self.subTest(piece=piece['file']),self.assertRaises(ValueError):loader.load_inventory(self.inventory,lambda f:self.reader(f)+b' ' if f==piece['file'] else self.reader(f))
        bad=copy.deepcopy(self.inventory);bad['addenda']*=2
        with self.assertRaises(ValueError):loader.load_inventory(bad,self.reader)
    def test_repinned_csv_wrong_values_still_rejected_by_json_semantics(self):
        bad=copy.deepcopy(self.inventory);piece=bad['addenda'][0]['csv'];rows=list(csv.DictReader(io.StringIO(self.reader(piece['file']).decode())));columns=list(rows[0]);rows[0]['approximate_value_m']='999';out=io.StringIO(newline='');w=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');w.writeheader();w.writerows(rows);raw=out.getvalue().encode();piece.update(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
        with self.assertRaises(ValueError):loader.load_inventory(bad,lambda f:raw if f==piece['file'] else self.reader(f))
    def test_all_old_csv_cells_and_order_survive_combined_query_view(self):
        old=list(csv.DictReader(io.StringIO((p.ROOT/self.op['base_csv_file']).read_text(encoding='utf8'))));new=list(csv.DictReader(io.StringIO(loader.combined_csv_bytes(self.inventory,self.reader).decode())))
        self.assertEqual(len(new),713)
        for a,b in zip(old,new):self.assertEqual(a,{k:b[k] for k in a})
        self.assertEqual([r['id'] for r in new[701:]],[r['id'] for r in self.addendum['evidence']])
        for r in new[701:]:self.assertEqual(r['annual_range_m'],'');self.assertEqual(r['volume_eligible'],'False');self.assertEqual(r['source_active_flow_cast_selection'],'True')
    def test_inventory_counts_and_view_collection_overrides_rejected(self):
        for kind in ['counts','metrics','collections','completion']:
            bad=copy.deepcopy(self.inventory)
            if kind=='counts':bad['counts']['depth_references']+=1
            if kind=='metrics':bad['metric_counts']['reported_vertical_thickness']+=1
            if kind=='collections':bad['view_metadata']['evidence']=[]
            if kind=='completion':bad['view_metadata']['full_goal_complete']=True
            with self.subTest(kind=kind),self.assertRaises(ValueError):loader.load_inventory(bad,self.reader)
    def test_source_contexts_and_all_global_physical_values_preserved(self):
        for key,value in self.base['source_contexts'].items():self.assertEqual(self.view['source_contexts'][key],value)
        self.assertEqual(self.view['metric_counts']['reported_vertical_thickness'],self.base['metric_counts']['reported_vertical_thickness']+12);self.assertEqual(self.view['counts']['whole_route_depth_profiles'],0);self.assertEqual(self.view['counts']['volume_estimates'],0)
        for row in self.view['records']:self.assertIsNone(row['whole_route_depth_m']);self.assertIsNone(row['annual_depth_range_m']);self.assertIsNone(row['volume_km3'])
    def test_input_hashes_and_publication_caps_without_expanded_register(self):
        for f,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin,f)
        self.assertEqual(set(self.pieces),{p.INVENTORY,p.ADDENDUM,p.CSV});self.assertTrue(all(len(raw)<2500000 for raw in self.pieces.values()));self.assertLess(sum(map(len,self.pieces.values())),3000000);self.assertFalse(self.inventory['view_metadata']['runtime_changed']);self.assertFalse(self.inventory['view_metadata']['query_ui_integration_performed'])


if __name__=='__main__':unittest.main()
