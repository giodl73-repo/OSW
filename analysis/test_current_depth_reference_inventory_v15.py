"""Exact observed depth bands,seasonal operators and immutable reference history."""
import copy,csv,io,json,unittest
import build_current_depth_reference_inventory_v15 as build
import load_current_depth_reference_inventory_v15 as loader
import load_current_depth_reference_inventory_v14 as prior


class ObservedBands(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory,cls.addendum,cls.facts,cls.pieces,cls.view=build.build();cls.old=json.loads((build.ROOT/'research/current-depth-reference-inventory-v14.json').read_bytes());cls.parts=prior.read_parts(cls.old,lambda f:(build.ROOT/f).read_bytes())
    def test_all793_prior_rows_contexts_parts_and_base_unchanged(self):
        old=prior.load_inventory(self.old,lambda f:(build.ROOT/f).read_bytes());self.assertEqual(self.view['evidence'][:793],old['evidence']);self.assertEqual(self.inventory['base'],self.old['base']);self.assertEqual(self.inventory['addenda'][:-1],self.old['addenda']);self.assertEqual({k:self.view['source_contexts'][k] for k in old['source_contexts']},old['source_contexts']);self.assertEqual(self.view['counts']['depth_references'],797)
    def test_four_exact_owner_metric_band_combinations(self):
        self.assertEqual([(r['entity_id'],r['metric'],r['range_m']) for r in self.addendum['evidence']],[(owner,metric,band) for identity,owner,metric,band,station,months in loader.EXPECTED])
    def test_seasons_and_temporal_operators_distinct(self):
        rows=self.addendum['evidence'];self.assertIsNone(rows[0]['calendar_months']);self.assertEqual(rows[1]['calendar_months'],[6,7,8,9]);self.assertEqual(rows[2]['calendar_months'],[12,1,2,3]);self.assertEqual(rows[3]['calendar_months'],[12,1,2,3]);self.assertIn('full_time_series',rows[0]['temporal_scope']);self.assertIn('harmonic',rows[1]['temporal_scope'])
    def test_source_body_and_abstract_discrepancy_not_averaged(self):
        self.assertEqual(self.facts['source_body_sem_core_band_m'],[40,100]);self.assertEqual(self.facts['source_abstract_and_discussion_sem_core_band_m'],[50,100]);self.assertFalse(self.facts['alternative_core_band_is_uncertainty']);self.assertEqual(len(self.addendum['evidence']),4)
    def test_different_upper_extent_descriptions_not_duplicate_reference(self):
        self.assertEqual(self.facts['seasonal_upper_eastward_flow_extent_band_m'],[100,120]);self.assertEqual(self.addendum['evidence'][0]['range_m'],[100,150])
    def test_exact_reviewed_PDF_metadata_without_cloud_rehash_claim(self):
        for row in self.addendum['evidence']:
            self.assertEqual(row['source_pdf_sha256'],self.facts['source_pdf_sha256']);self.assertEqual(row['source_pdf_pages_visually_reviewed'],[2,3,4,5,6,7,15]);self.assertFalse(row['source_PDF_rehashed_in_admission_cloud'])
    def test_no_midpoint_thickness_annual_uncertainty_or_volume(self):
        for row in self.addendum['evidence']:
            for key in ['approximate_value_m','thickness_m','annual_range_m','uncertainty_m','upper_boundary_m','lower_boundary_m']:self.assertIsNone(row[key])
            for key in ['whole_current_representative','physical_current_bottom_established','volume_eligible','annual_extrema_eligible','seasonal_playback_eligible','independent_observation_count_claimed']:self.assertFalse(row[key])
    def test_opposing_directions_and_owners_rejected_if_conflated(self):
        for key,value in [('direction','eastward'),('entity_id','current:south-java')]:
            facts=copy.deepcopy(self.facts);facts['records'][2][key]=value
            with self.assertRaises(ValueError):loader.validate_facts(facts)
    def test_altered_depth_or_season_rejected(self):
        for key,value in [('range_m',[50,100]),('calendar_months',[5,6,7,8])]:
            facts=copy.deepcopy(self.facts);facts['records'][1][key]=value
            with self.assertRaises(ValueError):loader.validate_facts(facts)
    def test_raw_or_physical_promotion_rejected(self):
        for key in ['source_contours_digitized','raw_mooring_data_reanalysed','source_pdf_redistributed','source_PDF_rehashed_in_admission_cloud','physical_current_bottom_established']:
            facts=copy.deepcopy(self.facts);facts[key]=True
            with self.assertRaises(ValueError):loader.validate_facts(facts)
    def test_every_JSON_CSV_cell_exact(self):
        incoming=csv.DictReader(io.StringIO(self.pieces[build.CSV].decode()));rows=list(incoming);self.assertEqual(len(rows),4)
        for raw,row in zip(self.addendum['evidence'],rows):self.assertEqual(row,{k:loader.base.cell(raw.get(k)) for k in incoming.fieldnames})
    def test_duplicate_context_or_altered_reference_rejected(self):
        with self.assertRaises(ValueError):loader.assemble(*self.parts,[(self.addendum,self.facts),(self.addendum,self.facts)])
        a=copy.deepcopy(self.addendum);a['evidence'][0]['metric']='core_depth'
        with self.assertRaises(ValueError):loader.assemble(*self.parts,[(a,self.facts)])


if __name__=='__main__':unittest.main()
