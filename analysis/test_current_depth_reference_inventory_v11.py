import copy,csv,hashlib,io,json,unittest
import build_current_depth_reference_inventory_v11 as p
import load_current_depth_reference_inventory_v10 as prior
import load_current_depth_reference_inventory_v11 as loader


class CoastalFrontFootTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory,cls.addendum,cls.facts,cls.pieces,cls.view=p.build();cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes());cls.previous=json.loads((p.ROOT/cls.op['previous_inventory_file']).read_bytes());cls.before=prior.load_inventory(cls.previous,lambda f:(p.ROOT/f).read_bytes());cls.parts=prior.read_parts(cls.previous,lambda f:(p.ROOT/f).read_bytes())
    def reader(self,f):return self.pieces[f] if f in self.pieces else (p.ROOT/f).read_bytes()
    def assembled(self,a=None,facts=None):return loader.assemble(*self.parts,[(a or self.addendum,facts or self.facts)])
    def test_757_prior_rows_contexts_and_record_fields_preserved(self):
        self.assertEqual(self.view['evidence'][:757],self.before['evidence']);self.assertEqual(self.inventory['base'],self.previous['base']);self.assertEqual(self.inventory['addenda'][:-1],self.previous['addenda'])
        for k,v in self.before['source_contexts'].items():self.assertEqual(self.view['source_contexts'][k],v)
        for old,new in zip(self.before['records'],self.view['records']):
            self.assertEqual(new['depth_reference_ids'][:len(old['depth_reference_ids'])],old['depth_reference_ids']);self.assertEqual({k:v for k,v in old.items() if k!='depth_reference_ids'},{k:v for k,v in new.items() if k!='depth_reference_ids'})
    def test_five_reported_values_and_cruise_year_section_pairs(self):
        rows=self.addendum['evidence'];self.assertEqual([r['approximate_value_m'] for r in rows],[75,200,110,140,65]);self.assertEqual([(r['source_reported_record']['source_survey_year'],r['source_reported_record']['cruise'],r['source_reported_record']['source_section_label']) for r in rows],[(2004,'JR105','1'),(2004,'JR105','2'),(2001,'OC369','Cape Farewell'),(2002,'OC380','Cape Farewell'),(2003,'OC395','Cape Farewell')]);self.assertTrue(all(r['metric']=='reported_coastal_front_foot_depth_scale' for r in rows))
    def test_original_34_isohaline_bottom_intersection_not_velocity_cutoff(self):
        for r in self.addendum['evidence']:
            original=r['source_reported_record'];self.assertEqual(original['source_depth_rule'],'34_isohaline_intersection_with_nearshore_seabed');self.assertEqual(original['source_salinity_contour_psu'],34);self.assertEqual(original['source_depth_scale_symbol'],'h_obs');self.assertIn('15percent',r['source_original_definition']['lateral_rule_context'])
        for contour in [34.5,34.8,34.956,35]:
            facts=copy.deepcopy(self.facts);facts['records'][0]['source_salinity_contour_psu']=contour
            with self.subTest(contour=contour),self.assertRaises(ValueError):loader.validate_facts(facts)
    def test_2003_not_full_velocity_and_regression_exclusion_retained(self):
        row=self.addendum['evidence'][-1];r=row['source_reported_record'];self.assertEqual(row['approximate_value_m'],65);self.assertTrue(r['source_2003_salinity_scale_does_not_contain_full_velocity_current']);self.assertTrue(r['source_excluded_from_depth_wind_correlation'])
        for key in ['source_2003_salinity_scale_does_not_contain_full_velocity_current','source_excluded_from_depth_wind_correlation']:
            facts=copy.deepcopy(self.facts);facts['records'][-1][key]=False
            with self.subTest(key=key),self.assertRaises(ValueError):loader.validate_facts(facts)
    def test_2001_cited_comparison_reanalysis_not_independent_observation(self):
        r=self.addendum['evidence'][2]['source_reported_record'];self.assertIn('Pickart2005',r['source_evidence_role']);self.assertIn('OC369_reanalysis',r['source_evidence_role']);self.assertFalse(r['independent_observation_count_claimed']);self.assertFalse(self.addendum['evidence'][2]['independent_observation_count_claimed'])
    def test_original_page_review_and_cloud_pdf_limitations(self):
        review=json.loads((p.ROOT/self.op['source_review_file']).read_bytes());self.assertEqual(review['original_pdf_pages_visually_reviewed'],[3,4,5,12,15]);self.assertEqual([r['source_reported_record']['source_pdf_page'] for r in self.addendum['evidence']],[4,5,4,12,12]);self.assertFalse(self.addendum['source_PDF_rehashed_in_cloud'])
        for r in self.addendum['evidence']:self.assertFalse(r['source_PDF_rehashed_in_cloud']);self.assertFalse(r['source_raw_CTD_or_ADCP_reanalysed']);self.assertFalse(r['source_contours_digitized']);self.assertEqual(r['source_pdf_bytes'],1491354);self.assertEqual(r['source_pdf_sha256'],'a1046dc95677464134afe8c7720a23fd2a536147b04af570a41ce550254e3bda')
    def test_no_current_bottom_thickness_volume_or_width_pairing(self):
        for key,value in [('lower_boundary_m',75),('upper_boundary_m',0),('thickness_m',75),('lower_bound_m',75),('lower_bound_operator','>='),('physical_current_bottom_established',True),('volume_eligible',True),('reference_route_projection_eligible',True),('same_source_width_reference_id','source-width-30km'),('source_PDF_rehashed_in_cloud',True),('source_contours_digitized',True)]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.assembled(a)
    def test_summer_years_not_annual_ranges_exact_dates_or_uncertainty(self):
        for r in self.addendum['evidence']:
            for k in ['range_m','annual_range_m','calendar_months','observed_period','uncertainty_m','thickness_m']:self.assertIsNone(r[k])
            self.assertFalse(r['seasonal_playback_eligible']);self.assertFalse(r['annual_extrema_eligible'])
        for key,value in [('range_m',[65,200]),('annual_range_m',[65,140]),('calendar_months',[7,8]),('observed_period','2004-07-01'),('uncertainty_m',10),('whole_current_representative',True)]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.assembled(a)
    def test_no_other_owner_old_1997_depth_or_theoretical_ratio_substitution(self):
        for key,value in [('entity_id','current:east-greenland'),('metric','derived_conditional_fresh_component_lower_boundary_depth'),('approximate_value_m',100),('approximate_value_m',1.4)]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):self.assembled(a)
    def test_complete_ordered_source_set_no_drop_duplicate_or_new_weak_section(self):
        for mode in ['omit','duplicate','weak_section']:
            a=copy.deepcopy(self.addendum)
            if mode=='omit':a['evidence'].pop()
            elif mode=='duplicate':a['evidence'].append(copy.deepcopy(a['evidence'][0]))
            else:a['evidence'][0]['source_reported_record']['source_section_label']='5'
            with self.subTest(mode=mode),self.assertRaises(ValueError):self.assembled(a)
        facts=copy.deepcopy(self.facts);facts['records'].pop()
        with self.assertRaises(ValueError):loader.validate_facts(facts)
    def test_exact_source_context_record_pointer_and_page_provenance(self):
        for key,value in [('source_pointer','/records/-1'),('source_sha256','wrong'),('source_file','other.json'),('source_locator','Figure13digitization')]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.assembled(a)
        a=copy.deepcopy(self.addendum);a['source_contexts'][loader.CONTEXT]['source_salinity_contour_psu']=35
        with self.assertRaises(ValueError):self.assembled(a)
    def test_fact_json_and_csv_piece_hashes_required(self):
        for piece in [self.addendum['reviewed_source_facts'],self.inventory['addenda'][-1]['json'],self.inventory['addenda'][-1]['csv']]:
            with self.subTest(file=piece['file']),self.assertRaises(ValueError):loader.load_inventory(self.inventory,lambda f:self.reader(f)+b' ' if f==piece['file'] else self.reader(f))
    def test_all_old_csv_cells_preserved_and_original_record_typed(self):
        old=list(csv.DictReader(io.StringIO(prior.combined_csv_bytes(self.previous,lambda f:(p.ROOT/f).read_bytes()).decode())));new=list(csv.DictReader(io.StringIO(loader.combined_csv_bytes(self.inventory,self.reader).decode())));self.assertEqual(len(new),762)
        for a,b in zip(old,new):self.assertEqual(a,{k:b[k] for k in a})
        for r in new[757:]:self.assertEqual(r['metric'],loader.METRIC);self.assertEqual(r['thickness_m'],'');self.assertEqual(r['volume_eligible'],'False');self.assertEqual(r['source_PDF_rehashed_in_cloud'],'False')
        self.assertTrue(json.loads(new[-1]['source_reported_record'])['source_excluded_from_depth_wind_correlation'])
    def test_counts_public_input_pins_and_fixed_caps(self):
        self.assertEqual(self.view['counts']['depth_references'],762);self.assertEqual(self.view['counts']['identities_with_scoped_depth_reference'],101);self.assertEqual(self.view['counts']['whole_route_depth_profiles'],0);self.assertEqual(self.view['counts']['volume_estimates'],0);self.assertEqual(self.view['metric_counts'][loader.METRIC],5)
        for f,pin in self.op['input_sha256'].items():self.assertFalse(f.startswith('.pytest_cache/'));self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin,f)
        self.assertTrue(all(len(raw)<2500000 for raw in self.pieces.values()));self.assertLess(sum(map(len,self.pieces.values())),3000000)


if __name__=='__main__':unittest.main()
