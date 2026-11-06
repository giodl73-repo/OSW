import copy,csv,io,json,unittest,urllib.request
from pathlib import Path
import build_current_depth_reference_inventory_v24 as build
import load_current_depth_reference_inventory_v24 as loader
import load_current_depth_reference_inventory_v23 as prior
ROOT=Path(__file__).resolve().parents[1]

def no_network(*args,**kwargs):raise RuntimeError('Published factual admission forbids field/network acquisition')

class PublishedEventCores(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        urllib.request.urlopen=no_network;urllib.request.build_opener=no_network
        cls.inventory,cls.addendum,cls.facts,cls.pieces,cls.view=build.build()
        cls.reader=staticmethod(lambda p:(ROOT/p).read_bytes())
        cls.previous=json.loads(cls.reader('research/current-depth-reference-inventory-v23.json'))
        cls.before=prior.load_inventory(cls.previous,cls.reader);cls.parts=prior.read_parts(cls.previous,cls.reader)

    def test_all_old_rows_contexts_and_pieces_preserved(self):
        self.assertEqual(self.view['evidence'][:-11],self.before['evidence'])
        self.assertEqual(self.inventory['base'],self.previous['base'])
        self.assertEqual(self.inventory['addenda'][:-1],self.previous['addenda'])
        for k,v in self.before['source_contexts'].items():self.assertEqual(self.view['source_contexts'][k],v)
        self.assertEqual(self.view['counts'],{'identities':111,'depth_references':853,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0})
        self.assertEqual(self.view['coordinate_unit_counts'],{'dbar':1,'m':852})

    def test_all_eleven_dated_pairs_and_source_pointer_resolution(self):
        self.assertEqual(len(self.addendum['evidence']),11)
        for i,row in enumerate(self.addendum['evidence']):
            self.assertEqual(row['entity_id'],'current:indian-equatorial-undercurrent')
            self.assertEqual(row['source_file'],loader.FACTS)
            self.assertEqual(row['source_pointer'],'/records/'+str(i))
            self.assertEqual(json.loads(self.reader(row['source_file']))['records'][i],row['source_reported_record'])
            self.assertEqual(row['source_reported_record']['approximate_value_m'],row['approximate_value_m'])
            self.assertEqual(row['metric'],'core_depth')
            self.assertEqual(row['source_nominal_lon_lat'],[90,0])

    def test_dates_speeds_depths_author_seasons_and_IOD_footnote_cannot_change(self):
        for index,k,v in [(0,'event_date','2001-04-27'),(4,'approximate_value_m',141),(6,'reported_eastward_speed_cm_s',35),(7,'source_season_label','boreal_autumn'),(10,'source_IOD_footnote',False),(0,'statistic','instantaneous_profile_core')]:
            f=copy.deepcopy(self.facts);f['records'][index][k]=v
            with self.assertRaises(ValueError):loader.validate_facts(f)

    def test_qualitative_absence_is_not_zero_or_new_reference(self):
        f=copy.deepcopy(self.facts);f['non_numeric_source_outcomes'][0]['depth_m']=0
        with self.assertRaises(ValueError):loader.validate_facts(f)
        f=copy.deepcopy(self.facts);f['records'].append(copy.deepcopy(f['records'][0]))
        with self.assertRaises(ValueError):loader.validate_facts(f)
        self.assertFalse(self.facts['non_numeric_source_outcomes'][0]['independently_reproduced'])

    def test_filter_resolution_and_raw_quality_context_stay_explicit(self):
        for k,v in [('figure6_running_mean_days',1),('table_specific_filter_separately_explicit',True),('reported_quality_flags',[1,2]),('within_window_numeric_coverage_independently_verified',True),('original_vertical_interval_is_depth_uncertainty',True)]:
            f=copy.deepcopy(self.facts);f['reported_methods'][k]=v
            with self.assertRaises(ValueError):loader.validate_facts(f)
        for k,v in [('source_html_sha256','invented'),('exact_html_bytes_retained',True),('raw_adcp_records_obtained',True),('actual_deployment_coordinates_independently_resolved',True)]:
            f=copy.deepcopy(self.facts);f[k]=v
            with self.assertRaises(ValueError):loader.validate_facts(f)

    def test_no_thickness_annual_range_volume_daily_or_full_column_promotion(self):
        for r in self.addendum['evidence']:
            for k in ['thickness_m','lower_boundary_m','upper_boundary_m','uncertainty_m','annual_range_m','observed_period','source_sampled_lon_lat','source_snapshot_time_utc']:self.assertIsNone(r[k])
            for k in ['full_water_column_core_established','physical_current_bottom_established','reference_route_projection_eligible','volume_eligible','physical_depth_ranking_eligible','seasonal_playback_eligible','independent_observation_count_claimed','operational_NOAA_daily_context_gate_applied']:self.assertFalse(r[k])
        for k,v in [('metric','physical_current_depth'),('thickness_m',110),('annual_range_m',[70,160]),('source_statistic','daily_mean'),('source_table_specific_filter_separately_explicit',True),('volume_eligible',True)]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][k]=v
            with self.assertRaises(ValueError):loader.assemble(*self.parts,[(a,self.facts)])
        with self.assertRaises(ValueError):loader.assemble(*self.parts,[(self.addendum,self.facts)]*2)

    def test_every_typed_csv_cell_preserved(self):
        table=csv.DictReader(io.StringIO(self.pieces[build.CSV].decode()))
        self.assertEqual(list(table),[{k:loader.base.cell(r.get(k)) for k in table.fieldnames} for r in self.addendum['evidence']])

    def test_roundtrip_and_changed_source_hash_rejected(self):
        reader=lambda p:self.pieces[p] if p in self.pieces else self.reader(p)
        self.assertEqual(loader.load_inventory(self.inventory,reader)['evidence'],self.view['evidence'])
        with self.assertRaises(ValueError):loader.load_inventory(self.inventory,lambda p:reader(p)+b' ' if p==loader.FACTS else reader(p))

if __name__=='__main__':unittest.main()
