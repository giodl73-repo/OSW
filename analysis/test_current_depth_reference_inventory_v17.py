import copy,csv,io,json,unittest
import build_current_depth_reference_inventory_v17 as build
import load_current_depth_reference_inventory_v17 as loader
import load_current_depth_reference_inventory_v16 as prior


class NativeCoordinates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory,cls.addendum,cls.facts,cls.pieces,cls.view=build.build();cls.old=json.loads((build.ROOT/'research/current-depth-reference-inventory-v16.json').read_bytes());cls.parts=prior.read_parts(cls.old,lambda f:(build.ROOT/f).read_bytes())
    def test_all802_prior_rows_contexts_base_and_parts_unchanged(self):
        old=prior.load_inventory(self.old,lambda f:(build.ROOT/f).read_bytes());self.assertEqual(self.view['evidence'][:802],old['evidence']);self.assertEqual(self.inventory['base'],self.old['base']);self.assertEqual(self.inventory['addenda'][:-1],self.old['addenda']);self.assertEqual({k:self.view['source_contexts'][k] for k in old['source_contexts']},old['source_contexts']);self.assertEqual(self.view['counts']['depth_references'],804)
    def test_coordinate_unit_counts_prevent_blended_rankings(self):
        self.assertEqual(self.view['coordinate_unit_counts'],{'dbar':1,'m':803});self.assertEqual(self.inventory['coordinate_unit_counts'],self.view['coordinate_unit_counts'])
    def test_native_transition_metres_and_pressure_remain_distinct(self):
        transition,pressure=self.addendum['evidence'];self.assertEqual(transition['unit'],'m');self.assertEqual(transition['range_m'],[100,200]);self.assertIsNone(transition['approximate_value_dbar']);self.assertEqual(pressure['unit'],'dbar');self.assertEqual(pressure['approximate_value_dbar'],350);self.assertIsNone(pressure['approximate_value_m']);self.assertIsNone(pressure['range_m'])
    def test_pressure_sampling_limit_not_current_bottom(self):
        row=self.addendum['evidence'][1];self.assertTrue(row['source_reported_record']['sampling_limit_censors_unknown_flow_bottom']);self.assertFalse(row['physical_current_bottom_established']);self.assertFalse(row['pressure_to_depth_conversion_performed']);self.assertFalse(row['pressure_datum_independently_verified'])
    def test_no_invented_fulltext_PDF_or_figure_review(self):
        for row in self.addendum['evidence']:self.assertFalse(row['full_article_obtained']);self.assertFalse(row['original_pdf_obtained']);self.assertIsNone(row['source_pdf_sha256']);self.assertIn('ABSTRACT',row['source_review_tier'])
    def test_observation_month_is_not_publication_year_or_season(self):
        for row in self.addendum['evidence']:self.assertEqual(row['observed_period'],{'survey_month':'1993-04'});self.assertIsNone(row['calendar_months'])
    def test_no_thickness_uncertainty_annual_or_volume_promotion(self):
        for row in self.addendum['evidence']:
            for key in ['thickness_m','annual_range_m','uncertainty_m','upper_boundary_m','lower_boundary_m']:self.assertIsNone(row[key])
            for key in ['whole_current_representative','physical_current_bottom_established','volume_eligible','annual_extrema_eligible','seasonal_playback_eligible','independent_observation_count_claimed']:self.assertFalse(row[key])
    def test_pressure_relabelled_or_assigned_metres_rejected(self):
        for key,value in [('unit','m'),('approximate_value_m',350),('range_m',[300,350])]:
            facts=copy.deepcopy(self.facts);facts['records'][1][key]=value
            with self.assertRaises(ValueError):loader.validate_facts(facts)
    def test_invented_datum_latitude_conversion_or_review_rejected(self):
        for key,value in [('pressure_datum_independently_verified',True),('assumed_latitude_degrees_north',42),('pressure_to_depth_conversion_performed',True),('full_article_obtained',True),('source_figures_visually_reviewed',True)]:
            facts=copy.deepcopy(self.facts);facts[key]=value
            with self.assertRaises(ValueError):loader.validate_facts(facts)
    def test_changed_survey_or_transition_band_rejected(self):
        facts=copy.deepcopy(self.facts);facts['survey_month']='1999-04'
        with self.assertRaises(ValueError):loader.validate_facts(facts)
        facts=copy.deepcopy(self.facts);facts['records'][0]['range_m']=[250,300]
        with self.assertRaises(ValueError):loader.validate_facts(facts)
    def test_every_JSON_CSV_cell_exact_including_native_units(self):
        incoming=csv.DictReader(io.StringIO(self.pieces[build.CSV].decode()));rows=list(incoming);self.assertEqual(len(rows),2)
        for raw,row in zip(self.addendum['evidence'],rows):self.assertEqual(row,{k:loader.base.cell(raw.get(k)) for k in incoming.fieldnames})
        self.assertEqual(rows[1]['approximate_value_m'],'');self.assertEqual(rows[1]['approximate_value_dbar'],'350');self.assertEqual(rows[1]['unit'],'dbar')
    def test_duplicate_context_and_altered_unit_rejected(self):
        with self.assertRaises(ValueError):loader.assemble(*self.parts,[(self.addendum,self.facts),(self.addendum,self.facts)])
        a=copy.deepcopy(self.addendum);a['evidence'][1]['unit']='m'
        with self.assertRaises(ValueError):loader.assemble(*self.parts,[(a,self.facts)])


if __name__=='__main__':unittest.main()
