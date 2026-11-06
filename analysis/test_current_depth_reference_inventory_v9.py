import copy,csv,hashlib,io,json,unittest
import build_current_depth_reference_inventory_v9 as p
import load_current_depth_reference_inventory_v8 as prior
import load_current_depth_reference_inventory_v9 as loader


class EpisodicWaterMassTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory,cls.addendum,cls.facts,cls.pieces,cls.view=p.build();cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes());cls.previous=json.loads((p.ROOT/cls.op['previous_inventory_file']).read_bytes());cls.before=prior.load_inventory(cls.previous,lambda f:(p.ROOT/f).read_bytes());cls.parts=prior.read_parts(cls.previous,lambda f:(p.ROOT/f).read_bytes())
    def reader(self,f):return self.pieces[f] if f in self.pieces else (p.ROOT/f).read_bytes()
    def assembled(self,a=None,facts=None):return loader.assemble(*self.parts,[(a or self.addendum,facts or self.facts)])
    def test_751_prior_rows_contexts_and_record_fields_preserved(self):
        self.assertEqual(self.view['evidence'][:751],self.before['evidence']);self.assertEqual(self.inventory['base'],self.previous['base']);self.assertEqual(self.inventory['addenda'][:-1],self.previous['addenda'])
        for k,v in self.before['source_contexts'].items():self.assertEqual(self.view['source_contexts'][k],v)
        for old,new in zip(self.before['records'],self.view['records']):
            self.assertEqual(new['depth_reference_ids'][:len(old['depth_reference_ids'])],old['depth_reference_ids']);self.assertEqual({k:v for k,v in old.items() if k!='depth_reference_ids'},{k:v for k,v in new.items() if k!='depth_reference_ids'})
    def test_one_original_10_15_scale_not_seven_depth_measurements(self):
        self.assertEqual(len(self.addendum['evidence']),1);r=self.addendum['evidence'][0];self.assertEqual(r['entity_id'],'current:jutland');self.assertEqual(r['range_m'],[10,15]);self.assertEqual(r['metric'],'reported_episodic_nutrient_bearing_water_mass_upper_layer_extent');self.assertTrue(r['source_annual_composition_profile_is_supporting_context_only']);self.assertEqual(len(self.facts['source_profile']['rows']),7)
    def test_approximate_range_has_no_midpoint_exact_bottom_or_thickness(self):
        r=self.addendum['evidence'][0]
        for k in ['approximate_value_m','upper_boundary_m','lower_boundary_m','lower_bound_m','upper_bound_m','lower_bound_operator','thickness_m','uncertainty_m']:self.assertIsNone(r[k])
        self.assertEqual(r['range_interpretation'],'approximate_upper_layer_scale_not_confidence_interval_or_annual_extrema')
    def test_atypical_year_context_not_occupation_or_annual_envelope(self):
        r=self.addendum['evidence'][0];self.assertIn('1994',r['temporal_scope']);self.assertIn('1995',r['temporal_scope']);self.assertIn('Atypical',r['temporal_scope']);self.assertIsNone(r['observed_period']);self.assertIsNone(r['calendar_months']);self.assertIsNone(r['annual_range_m']);self.assertNotIn('1980',r['temporal_scope'])
    def test_source_composition_profile_preserved_as_separate_statistic(self):
        profile=self.facts['source_profile'];self.assertEqual([r['source_depth_m'] for r in profile['rows']],[0,-5,-10,-20,-30,-50,-62]);self.assertEqual([r['source_fraction_decimal_comma'] for r in profile['rows']],['0,40','0,37','0,30','0,21','0,17','0,11','0,09']);self.assertIsNone(profile['source_station_id']);self.assertIsNone(profile['exact_occupation_dates']);self.assertFalse(profile['independent_observation_count_claimed'])
    def test_original_page_review_custody_is_not_cloud_pdf_reanalysis(self):
        review=json.loads((p.ROOT/self.op['source_review_file']).read_bytes());r=self.addendum['evidence'][0];self.assertEqual(review['original_pdf_pages_visually_reviewed'],[74,75]);self.assertEqual(r['source_pdf_bytes'],4292648);self.assertEqual(r['source_pdf_sha256'],'29e027afd56877b6acec02382a8a6a2e5b2ecce24572171c2e15c1f1ae071525');self.assertFalse(r['source_pdf_rehashed_in_cloud']);self.assertFalse(self.addendum['source_pdf_rehashed_in_cloud'])
    def test_cannot_promote_to_whole_current_bottom_annual_or_volume(self):
        for key,value in [('metric','physical_current_bottom'),('approximate_value_m',12.5),('thickness_m',15),('lower_boundary_m',15),('annual_range_m',[10,15]),('observed_period',[1994,1995]),('calendar_months',[3,4]),('uncertainty_m',2.5),('whole_current_representative',True),('physical_current_bottom_established',True),('volume_eligible',True),('reference_route_projection_eligible',True),('seasonal_playback_eligible',True)]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.assembled(a)
    def test_cannot_replace_episode_with_composition_endpoint_or_abstract_scale(self):
        for value in [[10,10],[0,62],[20,30],[10,15,62]]:
            a=copy.deepcopy(self.addendum);a['evidence'][0]['range_m']=value
            with self.subTest(value=value),self.assertRaises(ValueError):self.assembled(a)
    def test_context_population_owner_and_episode_cannot_change(self):
        for mode in ['owner','population','context','episode','cloud_provenance']:
            a=copy.deepcopy(self.addendum)
            if mode=='owner':a['evidence'][0]['entity_id']='current:norwegian-coastal'
            elif mode=='population':a['evidence'][0]['source_population']='whole_Jutland_Current'
            elif mode=='context':a['source_contexts'][loader.CONTEXT]['source_scope']='whole route'
            elif mode=='episode':a['evidence'][0]['source_episode']['source_time_context']='annual extrema'
            else:a['evidence'][0]['source_pdf_rehashed_in_cloud']=True
            with self.subTest(mode=mode),self.assertRaises(ValueError):self.assembled(a)
    def test_exact_source_provenance_and_no_width_pairing(self):
        for key,value in [('source_pointer','/source_profile/rows/6'),('source_sha256','wrong'),('source_file','other.json'),('source_pdf_sha256','wrong'),('same_source_width_reference_id','jutland-width')]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.assembled(a)
    def test_missing_duplicate_or_extra_source_rows_rejected(self):
        for mode in ['missing','duplicate']:
            a=copy.deepcopy(self.addendum)
            if mode=='missing':a['evidence']=[]
            else:a['evidence'].append(copy.deepcopy(a['evidence'][0]))
            with self.subTest(mode=mode),self.assertRaises(ValueError):self.assembled(a)
    def test_hash_pinned_facts_and_json_csv_pieces_cannot_change(self):
        for piece in [self.addendum['reviewed_source_facts'],self.inventory['addenda'][-1]['json'],self.inventory['addenda'][-1]['csv']]:
            with self.subTest(file=piece['file']),self.assertRaises(ValueError):loader.load_inventory(self.inventory,lambda f:self.reader(f)+b' ' if f==piece['file'] else self.reader(f))
    def test_all_prior_csv_cells_preserved_and_episode_cells_typed(self):
        old=list(csv.DictReader(io.StringIO(prior.combined_csv_bytes(self.previous,lambda f:(p.ROOT/f).read_bytes()).decode())));new=list(csv.DictReader(io.StringIO(loader.combined_csv_bytes(self.inventory,self.reader).decode())));self.assertEqual(len(new),752)
        for a,b in zip(old,new):self.assertEqual(a,{k:b[k] for k in a})
        r=new[-1];self.assertEqual(r['metric'],loader.METRIC);self.assertEqual(json.loads(r['range_m']),[10,15]);self.assertEqual(r['thickness_m'],'');self.assertEqual(r['volume_eligible'],'False');self.assertEqual(r['source_pdf_rehashed_in_cloud'],'False')
    def test_counts_input_pins_and_fixed_caps(self):
        self.assertEqual(self.view['counts']['depth_references'],752);self.assertEqual(self.view['counts']['identities_with_scoped_depth_reference'],101);self.assertEqual(self.view['counts']['whole_route_depth_profiles'],0);self.assertEqual(self.view['counts']['volume_estimates'],0);self.assertEqual(self.view['metric_counts'][loader.METRIC],1)
        for f,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin,f)
        self.assertTrue(all(len(raw)<2500000 for raw in self.pieces.values()));self.assertLess(sum(map(len,self.pieces.values())),3000000)


if __name__=='__main__':unittest.main()
