import copy,csv,hashlib,io,json,math,unittest
import build_current_depth_reference_inventory_v5 as p
import load_current_depth_reference_inventory_v4 as prior
import load_current_depth_reference_inventory_v5 as loader
from derive_tsushima_observed_pair_depth_v1 import derive_pair


class ObservedPairDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes());cls.inventory,cls.addendum,cls.report,cls.pieces,cls.view=p.build();read=lambda f:json.loads((p.ROOT/f).read_bytes());cls.previous=read(cls.op['previous_inventory_file']);cls.before=prior.load_inventory(cls.previous,lambda f:(p.ROOT/f).read_bytes());cls.parts=prior.read_parts(cls.previous,lambda f:(p.ROOT/f).read_bytes());cls.facts=read(cls.op['source_facts_file'])
    def reader(self,f):return self.pieces[f] if f in self.pieces else (p.ROOT/f).read_bytes()
    def assembled(self,a=None,report=None):return loader.assemble(*self.parts,[(a or self.addendum,report or self.report)])
    def test_all731_prior_references_contexts_and_other_record_fields_preserved(self):
        self.assertEqual(self.view['evidence'][:731],self.before['evidence']);self.assertEqual(self.inventory['base'],self.previous['base']);self.assertEqual(self.inventory['addenda'][:-1],self.previous['addenda'])
        for k,v in self.before['source_contexts'].items():self.assertEqual(self.view['source_contexts'][k],v)
        for old in self.before['records']:
            new=next(r for r in self.view['records'] if r['entity_id']==old['entity_id']);self.assertEqual(new['depth_reference_ids'][:len(old['depth_reference_ids'])],old['depth_reference_ids']);self.assertEqual({k:v for k,v in old.items() if k!='depth_reference_ids'},{k:v for k,v in new.items() if k!='depth_reference_ids'})
    def test_original_five_station_pairs_four_reversals_no_A_extrapolation(self):
        self.assertEqual([r['source_row']['station'] for r in self.report['records']],['A','C','B','D','E']);self.assertEqual(self.report['eligible_scenario_count'],4);self.assertEqual([r['source_observed_pair']['station'] for r in self.addendum['evidence']],['C','B','D','E']);a=self.report['records'][0];self.assertFalse(a['eligible']);self.assertIsNone(a['linear_scenario_depth_m']);self.assertIsNone(a['open_depth_bracket_m'])
    def test_common19day_means_and_station_E_true_frame_not_modern_model_frame(self):
        self.assertEqual(self.facts['table_mean_period'],{'start_date':'1980-07-26','end_date':'1980-08-14','source_reported_common_days':19})
        for r in self.addendum['evidence']:
            self.assertEqual(r['observed_period'],self.facts['table_mean_period']);pair=r['source_observed_pair'];self.assertEqual(pair['positive_alongshore_bearing_degrees_true'],75 if pair['station']=='E' else 90);self.assertEqual(pair,next(x for x in self.facts['rows'] if x['station']==pair['station']))
    def test_independent_linear_witness_and_dimensionless_velocity_ratio(self):
        row={'shallow_depth_m':10.,'deep_depth_m':70.,'shallow_mean_U_cm_s':20.,'deep_mean_U_cm_s':-10.};result=derive_pair(row);self.assertEqual(result['linear_scenario_depth_m'],50.);self.assertEqual(result['open_depth_bracket_m'],[10.,70.])
        scaled=copy.deepcopy(row);scaled.update(shallow_mean_U_cm_s=.2,deep_mean_U_cm_s=-.1);self.assertAlmostEqual(derive_pair(scaled)['linear_scenario_depth_m'],50.)
    def test_no_nonfinite_reversed_or_nonpositive_sampling_depths(self):
        row={'shallow_depth_m':10,'deep_depth_m':70,'shallow_mean_U_cm_s':20,'deep_mean_U_cm_s':-10}
        for key,value in [('shallow_depth_m',0),('deep_depth_m',5),('shallow_mean_U_cm_s',math.nan),('deep_mean_U_cm_s',math.inf)]:
            bad={**row,key:value}
            with self.subTest(key=key),self.assertRaises(ValueError):derive_pair(bad)
    def test_zero_endpoint_same_sign_and_reverse_polarity_not_admitted(self):
        for ua,ub in [(20,10),(20,0),(0,-10),(-20,10),(-20,-10)]:
            r=derive_pair({'shallow_depth_m':10,'deep_depth_m':70,'shallow_mean_U_cm_s':ua,'deep_mean_U_cm_s':ub});self.assertFalse(r['eligible']);self.assertIsNone(r['linear_scenario_depth_m'])
    def test_each_estimate_strictly_inside_original_open_bracket(self):
        for r in self.addendum['evidence']:
            lo,hi=r['source_open_direction_change_bracket_m'];self.assertTrue(lo<r['approximate_value_m']<hi);self.assertTrue(r['source_bracket_endpoints_excluded']);self.assertIsNone(r['range_m']);self.assertIsNone(r['uncertainty_m']);self.assertIsNone(r['source_sampled_lon_lat'])
    def test_no_exact_bottom_thickness_annual_coordinate_width_or_volume_promotion(self):
        for key,value in [('lower_boundary_m',50),('thickness_m',50),('range_m',[10,70]),('annual_range_m',[10,110]),('uncertainty_m',30),('source_sampled_lon_lat',[134.7,35.7]),('same_source_width_reference_id','modal-width'),('physical_current_bottom_established',True),('source_zero_crossing_uniqueness_established',True),('source_raw_profile_reconstructed',True),('volume_eligible',True),('reference_route_projection_eligible',True),('calendar_months',[7,8])]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.assembled(a)
    def test_original_source_pair_period_frame_and_value_cannot_be_substituted(self):
        for kind in ['value','pair','period','owner','bracket','assumption','source_facts','context']:
            a=copy.deepcopy(self.addendum);r=a['evidence'][0]
            if kind=='value':r['approximate_value_m']=50
            elif kind=='pair':r['source_observed_pair']['positive_alongshore_bearing_degrees_true']=60
            elif kind=='period':r['observed_period']['end_date']='1980-08-25'
            elif kind=='owner':r['entity_id']='current:kuroshio'
            elif kind=='bracket':r['source_open_direction_change_bracket_m']=[0,70]
            elif kind=='assumption':r['source_interpolation_assumption']='measured_exact_contour'
            elif kind=='source_facts':r['source_facts_pointer']='/rows/0'
            elif kind=='context':a['source_contexts'][loader.CONTEXT]['physical_current_bottom_established']=True
            with self.subTest(kind=kind),self.assertRaises(ValueError):self.assembled(a)
    def test_report_cannot_change_formula_or_source_pair_to_same_sign(self):
        report=copy.deepcopy(self.report);report['records'][1]['linear_scenario_depth_m']=50
        with self.assertRaises(ValueError):self.assembled(report=report)
        report=copy.deepcopy(self.report);report['records'][1]['source_row']['deep_mean_U_cm_s']=11.1
        with self.assertRaises(ValueError):self.assembled(report=report)
    def test_exact_nonnegative_report_pointers_and_piece_hashes(self):
        for r in self.addendum['evidence']:
            self.assertEqual(r['source_file'],p.REPORT);self.assertEqual(r['source_sha256'],hashlib.sha256(self.pieces[p.REPORT]).hexdigest())
        a=copy.deepcopy(self.addendum);a['evidence'][0]['source_pointer']='/records/-1'
        with self.assertRaises(ValueError):self.assembled(a)
        for piece in [self.addendum['derived_source_report'],self.inventory['addenda'][-1]['json'],self.inventory['addenda'][-1]['csv']]:
            with self.subTest(file=piece['file']),self.assertRaises(ValueError):loader.load_inventory(self.inventory,lambda f:self.reader(f)+b' ' if f==piece['file'] else self.reader(f))
    def test_old_csv_cells_preserved_and_new_scenarios_not_measured_boundaries(self):
        old=list(csv.DictReader(io.StringIO(prior.combined_csv_bytes(self.previous,lambda f:(p.ROOT/f).read_bytes()).decode())));new=list(csv.DictReader(io.StringIO(loader.combined_csv_bytes(self.inventory,self.reader).decode())));self.assertEqual(len(new),735)
        for a,b in zip(old,new):self.assertEqual(a,{k:b[k] for k in a})
        for r in new[731:]:self.assertEqual(r['metric'],'derived_two_level_mean_direction_change_depth_scenario');self.assertEqual(r['lower_boundary_m'],'');self.assertEqual(r['annual_range_m'],'');self.assertEqual(r['volume_eligible'],'False')
    def test_all_and_only_eligible_report_nodes_required(self):
        a=copy.deepcopy(self.addendum);a['evidence'].pop();raw=(json.dumps(a,separators=(',',':'))+'\n').encode();csv_raw=loader.reference_csv_bytes(a['evidence']);manifest=copy.deepcopy(self.inventory)
        for key,value in [('json',raw),('csv',csv_raw)]:manifest['addenda'][-1][key].update(sha256=hashlib.sha256(value).hexdigest(),bytes=len(value))
        with self.assertRaises(ValueError):loader.load_inventory(manifest,lambda f:raw if f==p.ADDENDUM else csv_raw if f==p.CSV else self.reader(f))
    def test_counts_frozen_primary_custody_and_publication_limits(self):
        self.assertEqual(self.view['counts']['depth_references'],735);self.assertEqual(self.view['counts']['identities_with_scoped_depth_reference'],101);self.assertEqual(self.view['counts']['whole_route_depth_profiles'],0);self.assertEqual(self.view['counts']['volume_estimates'],0);self.assertEqual(self.view['metric_counts']['derived_two_level_mean_direction_change_depth_scenario'],4)
        for f,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin,f)
        self.assertTrue(all(len(raw)<2500000 for raw in self.pieces.values()));self.assertLess(sum(map(len,self.pieces.values())),3000000)


if __name__=='__main__':unittest.main()
