import copy,csv,io,json,unittest,urllib.request
from pathlib import Path
import build_current_depth_reference_inventory_v26 as build
import load_current_depth_reference_inventory_v26 as loader
import load_current_depth_reference_inventory_v25 as prior
ROOT=Path(__file__).resolve().parents[1]

def no_network(*a,**k):raise RuntimeError('Published admission forbids source/network replay')

class BenguelaMeanPressure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        urllib.request.urlopen=no_network;urllib.request.build_opener=no_network
        cls.inventory,cls.addendum,cls.facts,cls.pieces,cls.view=build.build()
        cls.reader=staticmethod(lambda p:(ROOT/p).read_bytes())
        cls.previous=json.loads(cls.reader('research/current-depth-reference-inventory-v25.json'))
        cls.before=prior.load_inventory(cls.previous,cls.reader);cls.parts=prior.read_parts(cls.previous,cls.reader)

    def test_every_prior_reference_context_base_and_addendum_is_preserved(self):
        self.assertEqual(self.view['evidence'][:-1],self.before['evidence'])
        self.assertEqual(self.inventory['base'],self.previous['base']);self.assertEqual(self.inventory['addenda'][:-1],self.previous['addenda'])
        for k,v in self.before['source_contexts'].items():self.assertEqual(self.view['source_contexts'][k],v)
        self.assertEqual(self.view['counts'],{'identities':111,'depth_references':859,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0})
        self.assertEqual(self.view['coordinate_unit_counts'],{'dbar':2,'m':857})

    def test_pressure_is_not_metres_and_cannot_be_promoted_to_physical_depth(self):
        e=self.addendum['evidence'][0];self.assertEqual(e['approximate_value_dbar'],1270);self.assertEqual(e['unit'],'dbar')
        for k in ['approximate_value_m','thickness_m','lower_boundary_m','upper_boundary_m','uncertainty_m','annual_range_m','observed_period']:self.assertIsNone(e[k])
        for k in ['pressure_to_depth_conversion_applied','direct_current_depth_measurement','physical_depth_ranking_eligible','volume_eligible','physical_state_join_eligible','reference_route_projection_eligible','seasonal_playback_eligible']:self.assertFalse(e[k])
        for k,v in [('unit','m'),('approximate_value_m',1270),('pressure_to_depth_conversion_applied',True),('thickness_m',1270),('volume_eligible',True)]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][k]=v
            with self.assertRaises(ValueError):loader.assemble(*self.parts,[(a,self.facts)])

    def test_model_reference_geostrophic_averaging_and_missing_Ekman_are_preserved(self):
        for k,v in [('time_mean_reference_velocity','direct_current_meter'),('direct_full_column_velocity_observation',True),('wind_driven_Ekman_velocity_included',True),('published_mean_boundary_is_mean_instantaneous_boundary',True)]:
            f=copy.deepcopy(self.facts);f['methods'][k]=v
            with self.assertRaises(ValueError):loader.validate_facts(f)

    def test_source_region_period_and_direction_cannot_be_reassigned(self):
        for k,v in [('entity_id','current:benguela-undercurrent'),('source_latitude_degrees_north',-30),('source_flow_direction','southward'),('branch_scope','whole_system'),('source_statistic','instantaneous')]:
            f=copy.deepcopy(self.facts);f['records'][0][k]=v
            with self.assertRaises(ValueError):loader.validate_facts(f)
        f=copy.deepcopy(self.facts);f['reported_observational_months']=['2013-01','2013-12']
        with self.assertRaises(ValueError):loader.validate_facts(f)

    def test_same_mean_boundary_and_transport_split_count_once(self):
        f=copy.deepcopy(self.facts);f['records']*=2
        with self.assertRaises(ValueError):loader.validate_facts(f)
        with self.assertRaises(ValueError):loader.assemble(*self.parts,[(self.addendum,self.facts)]*2)
        self.assertEqual(len(self.addendum['evidence']),1)

    def test_source_custody_and_precision_not_invented(self):
        for k,v in [('source_html_sha256','invented'),('source_pdf_sha256','invented'),('source_figures_visually_reviewed',True),('raw_velocity_profiles_reanalysed',True),('exact_common_averaging_endpoints_resolved',True),('calendar_annual_or_climatological_mean',True)]:
            f=copy.deepcopy(self.facts);f[k]=v
            with self.assertRaises(ValueError):loader.validate_facts(f)
        self.assertEqual(self.addendum['evidence'][0]['source_reported_record'],self.facts['records'][0])
        self.assertEqual(self.addendum['evidence'][0]['source_pointer'],'/records/0')

    def test_pinned_roundtrip_source_hash_and_csv_corruption_guards(self):
        reader=lambda p:self.pieces[p] if p in self.pieces else self.reader(p)
        self.assertEqual(loader.load_inventory(self.inventory,reader)['evidence'],self.view['evidence'])
        for file in [loader.FACTS,build.CSV]:
            with self.assertRaises(ValueError):loader.load_inventory(self.inventory,lambda p:reader(p)+b' ' if p==file else reader(p))
        table=csv.DictReader(io.StringIO(self.pieces[build.CSV].decode()))
        self.assertEqual(list(table),[{k:loader.base.cell(e.get(k)) for k in table.fieldnames} for e in self.addendum['evidence']])

if __name__=='__main__':unittest.main()
