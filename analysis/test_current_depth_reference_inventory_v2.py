import copy,csv,hashlib,io,json,unittest
import build_current_depth_reference_inventory_v2 as p
import load_current_depth_reference_inventory_v2 as loader
import load_current_depth_reference_inventory_v1 as prior


class RegionalHydrographicThicknessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes());cls.inventory,cls.addendum,cls.pieces,cls.view=p.build();cls.previous=json.loads((p.ROOT/cls.op['previous_inventory_file']).read_bytes());cls.before=prior.load_inventory(cls.previous,lambda f:(p.ROOT/f).read_bytes());cls.base,cls.statistical=prior.read_parts(cls.previous,lambda f:(p.ROOT/f).read_bytes());cls.facts=json.loads((p.ROOT/cls.op['source_facts_file']).read_bytes())
    def reader(self,f):return self.pieces[f] if f in self.pieces else (p.ROOT/f).read_bytes()
    def test_all713_prior_references_immutable_pieces_and_other_currents_preserved(self):
        self.assertEqual(self.view['evidence'][:713],self.before['evidence']);self.assertEqual(self.inventory['base'],self.previous['base']);self.assertEqual(self.inventory['addenda'][:1],self.previous['addenda']);self.assertEqual(len(self.inventory['addenda']),2)
        for before in self.before['records']:
            after=next(r for r in self.view['records'] if r['entity_id']==before['entity_id'])
            if before['entity_id']!='current:persian-gulf-saline-overflow':self.assertEqual(after,before)
            else:
                self.assertEqual(after['depth_reference_ids'][:-2],before['depth_reference_ids']);self.assertEqual({k:v for k,v in after.items() if k!='depth_reference_ids'},{k:v for k,v in before.items() if k!='depth_reference_ids'})
    def test_original_prose_values_are_approximate_span_and_single_value_not_cast_means(self):
        first,second=self.addendum['evidence'];self.assertEqual(first['range_m'],[30,40]);self.assertIsNone(first['approximate_value_m']);self.assertEqual(first['source_value_qualifier'],'on_order_of');self.assertEqual(first['source_section_ids'],['R18']);self.assertEqual(second['approximate_value_m'],100);self.assertIsNone(second['range_m']);self.assertEqual(second['source_section_ids'],['R17'])
        for r in [first,second]:self.assertIsNone(r['source_cast_count']);self.assertEqual(r['source_statistic'],'source_approximate_regional_description');self.assertEqual(r['metric'],'reported_vertical_thickness');self.assertEqual(r['vertical_datum'],'not_applicable_thickness_distance')
    def test_hydrographic_definition_source_locator_and_exact_fact_pointers(self):
        a=json.loads((p.ROOT/self.op['source_acquisition_file']).read_bytes());self.assertEqual(self.facts['source_pdf_sha256'],a['sha256']);self.assertEqual(self.facts['source_pdf_bytes'],16308690);self.assertEqual(self.facts['original_pages_visually_reviewed'],[7,23])
        for r in self.addendum['evidence']:
            fact=self.facts['data'][int(r['source_pointer'].split('/')[-1])];self.assertEqual(r['source_core_boundary_equation'],'(S_max+S_env)/2');self.assertEqual(r['source_layer_identity'],'half_salinity_contrast_PGW_core');self.assertIsNone(r['source_velocity_boundary_m_s']);self.assertEqual(r['approximate_value_m'],fact['approximate_thickness_m']);self.assertEqual(r['range_m'],fact['approximate_thickness_range_m']);self.assertEqual(r['source_sha256'],hashlib.sha256((p.ROOT/r['source_file']).read_bytes()).hexdigest())
    def test_regional_descriptions_cannot_be_relabelled_as_cast_means_or_velocity_boundaries(self):
        for key,value in [('source_cast_count',21),('source_statistic','source_reported_mean_over_selected_active_channel_axis_casts'),('source_core_boundary_equation','speed>0.02m/s'),('source_velocity_boundary_m_s',.02),('source_reported_mean_thickness_m',35),('source_section_positions_reconstructed',True),('source_layer_identity','velocity_envelope')]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):loader.assemble(self.base,self.statistical,[a])
    def test_no_midpoint_uncertainty_annual_bounds_or_width_volume_promotion(self):
        for key,value in [('approximate_value_m',35),('uncertainty_m',5),('annual_range_m',[30,100]),('upper_boundary_m',150),('lower_boundary_m',250),('thickness_m',100),('same_source_width_reference_id','pgw-width'),('volume_eligible',True),('range_is_confidence_interval',True),('calendar_months',[10])]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):loader.assemble(self.base,self.statistical,[a])
    def test_invalid_spans_values_and_source_qualifiers_rejected(self):
        for key,value in [('range_m',[40,30]),('range_m',[30,float('nan')]),('range_kind','sampled_minimum_and_maximum'),('source_value_qualifier','exact')]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):loader.assemble(self.base,self.statistical,[a])
    def test_duplicate_owner_context_and_cross_class_mutations_rejected(self):
        for kind in ['duplicate','owner','context']:
            a=copy.deepcopy(self.addendum)
            if kind=='duplicate':a['evidence'].append(a['evidence'][0])
            if kind=='owner':a['evidence'][0]['entity_id']='current:unknown'
            if kind=='context':a['source_contexts']=copy.deepcopy(self.base['source_contexts'])
            with self.subTest(kind=kind),self.assertRaises(ValueError):loader.assemble(self.base,self.statistical,[a])
        r=copy.deepcopy(self.statistical[0]);r['evidence'][0]['source_statistic']='source_approximate_regional_description'
        with self.assertRaises(ValueError):loader.assemble(self.base,[r],[self.addendum])
    def test_all_prior_csv_cells_and_append_order_preserved_in_combined_query(self):
        old=list(csv.DictReader(io.StringIO(prior.combined_csv_bytes(self.previous,lambda f:(p.ROOT/f).read_bytes()).decode())));new=list(csv.DictReader(io.StringIO(loader.combined_csv_bytes(self.inventory,self.reader).decode())))
        self.assertEqual(len(old),713);self.assertEqual(len(new),715)
        for a,b in zip(old,new):self.assertEqual(a,{k:b[k] for k in a})
        self.assertEqual([r['id'] for r in new[713:]],[r['id'] for r in self.addendum['evidence']])
        for r in new[713:]:self.assertEqual(r['source_cast_count'],'');self.assertEqual(r['annual_range_m'],'');self.assertEqual(r['volume_eligible'],'False')
    def test_repeated_or_reordered_manifest_parts_and_changed_piece_hashes_rejected(self):
        bad=copy.deepcopy(self.inventory);bad['addenda'].append(bad['addenda'][-1])
        with self.assertRaises(ValueError):loader.load_inventory(bad,self.reader)
        bad=copy.deepcopy(self.inventory);bad['addenda'].reverse()
        with self.assertRaises(ValueError):loader.load_inventory(bad,self.reader)
        piece=self.inventory['addenda'][-1]['json']
        with self.assertRaises(ValueError):loader.load_inventory(self.inventory,lambda f:self.reader(f)+b' ' if f==piece['file'] else self.reader(f))
    def test_repinned_csv_wrong_cells_and_schema_still_rejected(self):
        bad=copy.deepcopy(self.inventory);piece=bad['addenda'][-1]['csv'];rows=list(csv.DictReader(io.StringIO(self.reader(piece['file']).decode())));columns=list(rows[0]);rows[0]['approximate_value_m']='35';out=io.StringIO(newline='');w=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');w.writeheader();w.writerows(rows);raw=out.getvalue().encode();piece.update(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
        with self.assertRaises(ValueError):loader.load_inventory(bad,lambda f:raw if f==piece['file'] else self.reader(f))
        bad=copy.deepcopy(self.inventory);bad['schema']='unknown'
        with self.assertRaises(ValueError):loader.load_inventory(bad,self.reader)
    def test_source_contexts_old_redsox_thresholds_and_base_member_index_scope_preserved(self):
        for key,value in self.before['source_contexts'].items():self.assertEqual(self.view['source_contexts'][key],value)
        self.assertEqual(self.view['evidence'][701:713],self.before['evidence'][701:713]);self.assertEqual(self.view['member_depth_index_scope'],'base_only_not_updated_for_addenda')
    def test_counts_no_physical_profiles_and_view_collection_overrides(self):
        self.assertEqual(self.view['counts'],{'identities':111,'depth_references':715,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0})
        for row in self.view['records']:self.assertIsNone(row['whole_route_depth_m']);self.assertIsNone(row['annual_depth_range_m']);self.assertIsNone(row['volume_km3'])
        for kind in ['counts','override','completion']:
            bad=copy.deepcopy(self.inventory)
            if kind=='counts':bad['counts']['depth_references']+=1
            if kind=='override':bad['view_metadata']['evidence']=[]
            if kind=='completion':bad['view_metadata']['full_goal_complete']=True
            with self.subTest(kind=kind),self.assertRaises(ValueError):loader.load_inventory(bad,self.reader)
    def test_all_input_pins_and_fixed_publication_caps(self):
        for f,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin,f)
        self.assertEqual(set(self.pieces),{p.INVENTORY,p.ADDENDUM,p.CSV});self.assertTrue(all(len(raw)<2500000 for raw in self.pieces.values()));self.assertLess(sum(map(len,self.pieces.values())),3000000)


if __name__=='__main__':unittest.main()
