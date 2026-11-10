import copy,csv,io,json,unittest,urllib.request
from pathlib import Path
import build_current_depth_reference_inventory_v25 as build
import load_current_depth_reference_inventory_v25 as loader
import load_current_depth_reference_inventory_v24 as prior
ROOT=Path(__file__).resolve().parents[1]
def no_network(*a,**k):raise RuntimeError('Published reference admission forbids acquisition')

class RegionalMeanBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        urllib.request.urlopen=no_network;urllib.request.build_opener=no_network
        cls.inventory,cls.addendum,cls.facts,cls.pieces,cls.view=build.build()
        cls.reader=staticmethod(lambda p:(ROOT/p).read_bytes())
        cls.previous=json.loads(cls.reader('research/current-depth-reference-inventory-v24.json'))
        cls.before=prior.load_inventory(cls.previous,cls.reader);cls.parts=prior.read_parts(cls.previous,cls.reader)

    def test_all853_old_references_contexts_and_pressure_coordinate_survive(self):
        self.assertEqual(self.view['evidence'][:-5],self.before['evidence'])
        self.assertEqual(self.inventory['base'],self.previous['base'])
        self.assertEqual(self.inventory['addenda'][:-1],self.previous['addenda'])
        for k,v in self.before['source_contexts'].items():self.assertEqual(self.view['source_contexts'][k],v)
        self.assertEqual(self.view['counts'],{'identities':111,'depth_references':858,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0})
        self.assertEqual(self.view['coordinate_unit_counts'],{'dbar':1,'m':857})

    def test_exact_five_depths_four_owners_and_actual_source_pointers(self):
        expected=[('current:pacific-south-equatorial','lower_flow_boundary_depth',90),('current:pacific-equatorial-undercurrent','upper_flow_boundary_depth',100),('current:pacific-equatorial-undercurrent','lower_flow_boundary_depth',300),('current:pacific-north-equatorial-countercurrent','reported_vertical_extent',150),('current:pacific-north-equatorial-undercurrent','upper_flow_boundary_depth',350)]
        self.assertEqual([(r['entity_id'],r['metric'],r['approximate_value_m']) for r in self.addendum['evidence']],expected)
        for i,r in enumerate(self.addendum['evidence']):
            self.assertEqual(r['source_file'],loader.FACTS);self.assertEqual(r['source_pointer'],'/records/'+str(i))
            self.assertEqual(json.loads(self.reader(r['source_file']))['records'][i],r['source_reported_record'])
            self.assertEqual(r['source_context_id'],loader.context_id(r['entity_id']))
            self.assertEqual(r['source_review_tier'],loader.TIER)

    def test_branch_and_unmapped_identity_substitution_rejected(self):
        for i,k,v in [(4,'entity_id','current:pacific-north-subsurface-countercurrent'),(4,'source_branch_scope','all_NEUC_jets'),(0,'source_zonal_flow_direction','eastward'),(3,'reported_latitude_band_degrees_north',[8,21])]:
            f=copy.deepcopy(self.facts);f['records'][i][k]=v
            with self.assertRaises(ValueError):loader.validate_facts(f)
        with self.assertRaises(ValueError):loader.context_id('current:subtropical-countercurrent')

    def test_uncertain3000m_claim_is_context_only(self):
        f=copy.deepcopy(self.facts);f['unadmitted_candidates'][0]['numeric_reference_admitted']=True
        with self.assertRaises(ValueError):loader.validate_facts(f)
        f=copy.deepcopy(self.facts);f['records'][4]['approximate_value_m']=3000
        with self.assertRaises(ValueError):loader.validate_facts(f)
        self.assertTrue(all(r['approximate_value_m']!=3000 for r in self.addendum['evidence']))

    def test_native_resolution_altimeter_fill_filter_and_mean_operator_cannot_change(self):
        for k,v in [('ADCP_native_bin_interval_m',5),('interpolated_vertical_spacing_m',16),('upper_layer_filled_using','direct_ADCP'),('latitude_dependent_lowpass_cutoff_hours',[{'latitude_interval':[0,22],'hours':96}]),('native_point_coverage_or_source_QC_independently_verified',True)]:
            f=copy.deepcopy(self.facts);f['methods'][k]=v
            with self.assertRaises(ValueError):loader.validate_facts(f)
        for k,v in [('reported_observational_months',['2016-01','2016-12']),('calendar_annual_or_climatological_mean',True),('exact_common_averaging_endpoints_resolved',True)]:
            f=copy.deepcopy(self.facts);f[k]=v
            with self.assertRaises(ValueError):loader.validate_facts(f)

    def test_provisional_tier_and_original_custody_cannot_be_promoted(self):
        for k,v in [('source_review_tier','ORIGINAL_VERIFIED'),('full_article_obtained',True),('source_html_sha256','invented'),('source_pdf_sha256','invented'),('source_figures_visually_reviewed',True),('raw_velocity_profiles_reanalysed',True)]:
            f=copy.deepcopy(self.facts);f[k]=v
            with self.assertRaises(ValueError):loader.validate_facts(f)

    def test_paired_mean_boundaries_are_not_physical_thickness_or_route_volume(self):
        for r in self.addendum['evidence']:
            for k in ['upper_boundary_m','lower_boundary_m','thickness_m','uncertainty_m','annual_range_m','observed_period','source_sampled_lon_lat']:self.assertIsNone(r[k])
            for k in ['source_upper_to_lower_pair_is_physical_thickness','source_mean_field_boundary_is_mean_instantaneous_boundary','source_interpolated_grid_is_native_resolution','physical_current_bottom_established','physical_depth_ranking_eligible','reference_route_projection_eligible','volume_eligible','physical_state_join_eligible','seasonal_playback_eligible']:self.assertFalse(r[k])
        for k,v in [('thickness_m',200),('annual_range_m',[100,300]),('source_review_tier','VERIFIED'),('source_statistic','instantaneous'),('source_methods',{}),('source_upper_to_lower_pair_is_physical_thickness',True)]:
            a=copy.deepcopy(self.addendum);a['evidence'][1][k]=v
            with self.assertRaises(ValueError):loader.assemble(*self.parts,[(a,self.facts)])
        with self.assertRaises(ValueError):loader.assemble(*self.parts,[(self.addendum,self.facts)]*2)

    def test_typed_csv_cells_and_roundtrip(self):
        table=csv.DictReader(io.StringIO(self.pieces[build.CSV].decode()))
        self.assertEqual(list(table),[{k:loader.base.cell(r.get(k)) for k in table.fieldnames} for r in self.addendum['evidence']])
        reader=lambda p:self.pieces[p] if p in self.pieces else self.reader(p)
        self.assertEqual(loader.load_inventory(self.inventory,reader)['evidence'],self.view['evidence'])

    def test_source_hash_corruption_rejected(self):
        reader=lambda p:self.pieces[p] if p in self.pieces else self.reader(p)
        with self.assertRaises(ValueError):loader.load_inventory(self.inventory,lambda p:reader(p)+b' ' if p==loader.FACTS else reader(p))

if __name__=='__main__':unittest.main()
