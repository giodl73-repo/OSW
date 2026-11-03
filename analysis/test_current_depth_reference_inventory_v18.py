import copy,csv,io,json,unittest
import build_current_depth_reference_inventory_v18 as build
import load_current_depth_reference_inventory_v18 as loader
import load_current_depth_reference_inventory_v17 as prior


class WinterMeanReach(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory,cls.addendum,cls.facts,cls.pieces,cls.view=build.build();cls.old=json.loads((build.ROOT/'research/current-depth-reference-inventory-v17.json').read_bytes());cls.parts=prior.read_parts(cls.old,lambda f:(build.ROOT/f).read_bytes())
    def test_all804_prior_rows_contexts_parts_and_base_preserved(self):
        old=prior.load_inventory(self.old,lambda f:(build.ROOT/f).read_bytes());self.assertEqual(self.view['evidence'][:804],old['evidence']);self.assertEqual(self.inventory['base'],self.old['base']);self.assertEqual(self.inventory['addenda'][:-1],self.old['addenda']);self.assertEqual({k:self.view['source_contexts'][k] for k in old['source_contexts']},old['source_contexts']);self.assertEqual(self.view['counts']['depth_references'],808)
    def test_units_recomputed_with_old_pressure_unchanged(self):
        self.assertEqual(self.view['coordinate_unit_counts'],{'dbar':1,'m':807});self.assertEqual(self.inventory['coordinate_unit_counts'],self.view['coordinate_unit_counts']);pressure=[r for r in self.view['evidence'] if r['unit']=='dbar'];self.assertEqual(len(pressure),1);self.assertIsNone(pressure[0]['approximate_value_m'])
    def test_station_reaches_not_bed_depths_or_thicknesses(self):
        self.assertEqual([r['lower_bound_m'] for r in self.addendum['evidence']],[60,62,70,93]);self.assertEqual([r['site_water_depth_m'] for r in self.addendum['evidence']],[62.9,65.8,73.2,96.9])
        for r in self.addendum['evidence']:self.assertTrue(r['sampling_limit_censors_unknown_flow_bottom']);self.assertFalse(r['lower_bound_exclusive']);self.assertIsNone(r['approximate_value_m']);self.assertIsNone(r['thickness_m'])
    def test_provisional_tier_no_false_article_or_visual_review(self):
        for r in self.addendum['evidence']:self.assertEqual(r['source_review_tier'],loader.TIER);self.assertFalse(r['full_article_obtained']);self.assertFalse(r['source_figures_visually_reviewed']);self.assertIsNone(r['source_html_sha256']);self.assertFalse(r['original_pdf_obtained'])
    def test_actual_station_dates_and_deployment_mean_not_monthly(self):
        for r,(_,_,_,start,end) in zip(self.addendum['evidence'],loader.EXPECTED):self.assertEqual(r['observed_period'],{'start':start,'end':end});self.assertIsNone(r['calendar_months']);self.assertEqual(r['temporal_statistic'],'deployment_mean_not_continuous_instantaneous_flow')
    def test_sampling_alone_or_silent_reversal_omission_rejected(self):
        for key in ['flow_attribution_reviewed','mean_flow_through_sampled_column_reviewed','temporary_full_and_partial_flow_reversals_reported']:
            f=copy.deepcopy(self.facts);f[key]=False
            with self.assertRaises(ValueError):loader.validate_facts(f)
    def test_bed_substitution_or_changed_support_rejected(self):
        for key,value in [('observed_reach_m',62.9),('sampled_depth_range_m',[0,62.9]),('site_water_depth_m',60),('temporal_statistic','instantaneous'),('sampling_limit_censors_unknown_flow_bottom',False)]:
            f=copy.deepcopy(self.facts);f['records'][0][key]=value
            with self.assertRaises(ValueError):loader.validate_facts(f)
    def test_review_or_wrong_current_promotion_rejected(self):
        for key,value in [('source_review_tier','FULL_PRIMARY_REVIEWED'),('entity_id','current:alaska'),('source_html_sha256','challenge-page-hash'),('source_figures_visually_reviewed',True),('full_article_obtained',True)]:
            f=copy.deepcopy(self.facts);f[key]=value
            with self.assertRaises(ValueError):loader.validate_facts(f)
    def test_no_annual_volume_whole_route_or_seasonal_promotion(self):
        for r in self.addendum['evidence']:
            for key in ['thickness_m','annual_range_m','uncertainty_m','upper_boundary_m','lower_boundary_m']:self.assertIsNone(r[key])
            for key in ['whole_current_representative','physical_current_bottom_established','volume_eligible','annual_extrema_eligible','seasonal_playback_eligible','reference_route_projection_eligible','physical_state_join_eligible']:self.assertFalse(r[key])
    def test_no_invented_raw_reanalysis_or_annual_replicates(self):
        f=copy.deepcopy(self.facts);f['raw_velocity_profiles_reanalysed']=True
        with self.assertRaises(ValueError):loader.validate_facts(f)
        f=copy.deepcopy(self.facts);f['records'][0]['independent_seasonal_replicate_claimed']=True
        with self.assertRaises(ValueError):loader.validate_facts(f)
    def test_every_JSON_CSV_cell_exact(self):
        incoming=csv.DictReader(io.StringIO(self.pieces[build.CSV].decode()));rows=list(incoming);self.assertEqual(len(rows),4)
        for raw,row in zip(self.addendum['evidence'],rows):self.assertEqual(row,{k:loader.base.cell(raw.get(k)) for k in incoming.fieldnames})
    def test_duplicate_context_or_changed_row_rejected(self):
        with self.assertRaises(ValueError):loader.assemble(*self.parts,[(self.addendum,self.facts),(self.addendum,self.facts)])
        a=copy.deepcopy(self.addendum);a['evidence'][0]['lower_bound_m']=62.9
        with self.assertRaises(ValueError):loader.assemble(*self.parts,[(a,self.facts)])


if __name__=='__main__':unittest.main()
