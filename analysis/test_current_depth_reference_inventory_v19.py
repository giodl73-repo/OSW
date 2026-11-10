"""Source-named core progression preserves prior references and unknown geometry."""
import copy,csv,io,json,unittest
from unittest.mock import patch
import build_current_depth_reference_inventory_v19 as build
import load_current_depth_reference_inventory_v19 as loader
import load_current_depth_reference_inventory_v18 as prior


class PgwCoreDepthRegimes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('urllib.request.urlopen',side_effect=AssertionError('No retrieval')):cls.inventory,cls.addendum,cls.facts,cls.pieces,cls.view=build.build()
        cls.old=json.loads((build.ROOT/'research/current-depth-reference-inventory-v18.json').read_bytes());cls.parts=prior.read_parts(cls.old,lambda f:(build.ROOT/f).read_bytes())
    def test_all808_prior_rows_contexts_parts_and_base_preserved(self):
        old=prior.load_inventory(self.old,lambda f:(build.ROOT/f).read_bytes());self.assertEqual(self.view['evidence'][:808],old['evidence']);self.assertEqual(self.inventory['base'],self.old['base']);self.assertEqual(self.inventory['addenda'][:-1],self.old['addenda']);self.assertEqual({k:self.view['source_contexts'][k] for k in old['source_contexts']},old['source_contexts']);self.assertEqual(self.view['counts']['depth_references'],810);self.assertIs(build.prior,prior)
    def test_units_and_identity_coverage_unchanged_except_two_metre_refs(self):
        self.assertEqual(self.view['coordinate_unit_counts'],{'dbar':1,'m':809})
        for key in ['identities','identities_with_scoped_depth_reference','identities_not_yet_assessed','whole_route_depth_profiles','volume_estimates']:self.assertEqual(self.view['counts'][key],self.old['counts'][key])
    def test_core_depth_span_not_a_midpoint_or_layer_thickness(self):
        a,b=self.addendum['evidence'];self.assertIsNone(a['approximate_value_m']);self.assertEqual(a['range_m'],[70,120]);self.assertEqual(b['approximate_value_m'],200);self.assertIsNone(b['range_m'])
        for r in [a,b]:self.assertEqual(r['metric'],'core_depth');self.assertIsNone(r['thickness_m']);self.assertIsNone(r['upper_boundary_m']);self.assertIsNone(r['lower_boundary_m']);self.assertFalse(r['physical_current_bottom_established'])
    def test_existing220m_core_kept_separate_without_averaging(self):
        existing=next(r for r in self.view['evidence'] if r['id']=='pgw-pous-2004-gogp99-thermohaline-core');self.assertEqual(existing['approximate_value_m'],220);self.assertNotIn(existing['id'],{r['id'] for r in self.addendum['evidence']});self.assertEqual(len(self.addendum['evidence']),2)
    def test_relative_shoaling_and_r15_exception_are_context_not_absolute_endpoints(self):
        p=self.view['source_contexts'][loader.CONTEXT]['downstream_profile_context'];self.assertEqual(p,self.facts['downstream_profile_context']);self.assertEqual(p['R14_to_R02']['reported_core_shoaling_exclusive_upper_bound_m'],30);self.assertIsNone(p['R14_to_R02']['absolute_endpoint_depths_m']);self.assertTrue(p['R12_excluded_by_authors']);self.assertTrue(p['post_R17']['R15_exception'])
    def test_source_named_regimes_keep_campaign_distinct_from_exact_cast_dates(self):
        for r in self.addendum['evidence']:self.assertIsNone(r['observed_period']);self.assertIsNone(r['calendar_months']);self.assertEqual(r['campaign_window'],{'start':'1999-10-08','end':'1999-11-10'});self.assertEqual(r['window_role'],'whole_campaign_not_exact_core_occupation');self.assertEqual(r['entity_id'],loader.OWNER)
    def test_midpoint_wrong_owner_or_depth_substitution_rejected(self):
        for key,value in [('approximate_value_m',95),('range_m',[0,120]),('entity_id','current:other'),('reference_route_projection_eligible',True)]:
            f=copy.deepcopy(self.facts);f['records'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):loader.validate_facts(f)
    def test_absolute_endpoints_interpolation_symmetric_thickness_or_independence_rejected(self):
        for key,value in [('mapped_section_positions',[[57,25]]),('interpolation_performed',True),('top_bottom_inferred_by_centering_thickness_on_core',True),('thickness_or_width_values_joined',True),('new_independent_observations_claimed',True)]:
            f=copy.deepcopy(self.facts);f['downstream_profile_context'][key]=value
            with self.assertRaises(ValueError):loader.validate_facts(f)
        f=copy.deepcopy(self.facts);f['downstream_profile_context']['R14_to_R02']['absolute_endpoint_depths_m']=[200,170]
        with self.assertRaises(ValueError):loader.validate_facts(f)
    def test_no_invented_article_custody_digitization_or_exact_common_occupation(self):
        for key,value in [('source_html_sha256','invented'),('source_figure_digitized',True),('raw_casts_reanalysed',True),('author_version_reacquired_in_this_admission',True),('campaign_window_is_exact_common_occupation',True)]:
            f=copy.deepcopy(self.facts);f[key]=value
            with self.assertRaises(ValueError):loader.validate_facts(f)
    def test_every_typed_json_csv_cell_exact(self):
        incoming=csv.DictReader(io.StringIO(self.pieces[build.CSV].decode()));rows=list(incoming);self.assertEqual(len(rows),2)
        for raw,row in zip(self.addendum['evidence'],rows):self.assertEqual(row,{k:loader.base.cell(raw.get(k)) for k in incoming.fieldnames})
    def test_duplicate_source_context_or_changed_reference_rejected(self):
        with self.assertRaises(ValueError):loader.assemble(*self.parts,[(self.addendum,self.facts),(self.addendum,self.facts)])
        a=copy.deepcopy(self.addendum);a['evidence'][0]['thickness_m']=50
        with self.assertRaises(ValueError):loader.assemble(*self.parts,[(a,self.facts)])
    def test_no_whole_route_annual_width_volume_or_runtime_promotion(self):
        for r in self.addendum['evidence']:
            for key in ['whole_current_representative','volume_eligible','annual_extrema_eligible','seasonal_playback_eligible','reference_route_projection_eligible','physical_state_join_eligible']:self.assertFalse(r[key])
            for key in ['annual_range_m','uncertainty_m','same_source_width_reference_id']:self.assertIsNone(r[key])
        self.assertFalse(self.inventory['runtime_changed']);self.assertFalse(self.inventory['full_goal_complete'])


if __name__=='__main__':unittest.main()
