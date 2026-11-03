import copy,csv,io,json,unittest
import build_current_depth_reference_inventory_v16 as build
import load_current_depth_reference_inventory_v16 as loader
import load_current_depth_reference_inventory_v15 as prior


class FilteredCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory,cls.addendum,cls.facts,cls.pieces,cls.view=build.build();cls.old=json.loads((build.ROOT/'research/current-depth-reference-inventory-v15.json').read_bytes());cls.parts=prior.read_parts(cls.old,lambda f:(build.ROOT/f).read_bytes())
    def test_all797_prior_rows_contexts_base_and_parts_unchanged(self):
        old=prior.load_inventory(self.old,lambda f:(build.ROOT/f).read_bytes());self.assertEqual(self.view['evidence'][:797],old['evidence']);self.assertEqual(self.inventory['base'],self.old['base']);self.assertEqual(self.inventory['addenda'][:-1],self.old['addenda']);self.assertEqual({k:self.view['source_contexts'][k] for k in old['source_contexts']},old['source_contexts']);self.assertEqual(self.view['counts']['depth_references'],802)
    def test_exact_five_owners_metrics_and_depths(self):
        self.assertEqual([(r['entity_id'],r['metric'],r['approximate_value_m']) for r in self.addendum['evidence']],[(owner,metric,value) for identity,owner,metric,value,month,interval,velocity in loader.EXPECTED])
    def test_event_months_and_interval_maxima_are_distinct(self):
        rows=self.addendum['evidence'];self.assertIsNone(rows[0]['observed_period']);self.assertEqual(rows[1]['observed_period'],{'event_month':'2017-12'});self.assertEqual(rows[2]['observed_period'],{'event_month':'2021-03'});self.assertEqual(rows[3]['observed_period'],{'start_month':'2016-03','end_month':'2017-04'});self.assertEqual(rows[4]['observed_period'],{'start_month':'2019-06','end_month':'2020-06'})
    def test_year_filter_and_endpoint_exclusions_preserved(self):
        for row in self.addendum['evidence']:self.assertEqual(row['source_temporal_filter'],{'kind':'one_year_moving_average_low_pass','discarded_endpoint_months':[6,5]});self.assertFalse(row['source_reported_record']['instantaneous_observation_claimed']);self.assertIsNone(row['calendar_months'])
    def test_acquisition_window_not_filtered_peak_window(self):
        self.assertEqual(self.facts['source_station_acquisition_dates'],['2015-09-26','2021-12-27']);self.assertNotEqual(self.addendum['evidence'][1]['observed_period'],self.facts['source_station_acquisition_dates'])
    def test_sampling_and_density_partition_not_new_depth_values(self):
        self.assertEqual(self.facts['source_native_ADCP_bin_size_m'],8);self.assertEqual(self.facts['source_vertical_interpolation_spacing_m'],10)
        values=[r['approximate_value_m'] for r in self.addendum['evidence']]
        for excluded in [40,450,900,1000,4000,5500,26.8]:self.assertNotIn(excluded,values)
    def test_exact_HTML_figure_review_without_invented_PDF(self):
        for row in self.addendum['evidence']:self.assertTrue(row['source_figure2_visually_reviewed']);self.assertFalse(row['original_pdf_obtained']);self.assertIsNone(row['source_pdf_sha256']);self.assertFalse(row['source_assets_rehashed_in_admission_cloud'])
    def test_no_extrema_thickness_or_physical_volume_promotions(self):
        for row in self.addendum['evidence']:
            for key in ['range_m','thickness_m','annual_range_m','uncertainty_m','upper_boundary_m','lower_boundary_m']:self.assertIsNone(row[key])
            for key in ['whole_current_representative','physical_current_bottom_established','volume_eligible','annual_extrema_eligible','seasonal_playback_eligible','independent_observation_count_claimed']:self.assertFalse(row[key])
    def test_wrong_owner_direction_or_event_date_rejected(self):
        for index,key,value in [(3,'entity_id','current:pacific-north-equatorial'),(3,'direction','westward'),(1,'event_month','2017-11')]:
            facts=copy.deepcopy(self.facts);facts['records'][index][key]=value
            with self.assertRaises(ValueError):loader.validate_facts(facts)
    def test_filter_relaxation_or_unperformed_analysis_rejected(self):
        for key,value in [('temporal_filter',{'kind':'monthly','discarded_endpoint_months':[0,0]}),('source_assets_rehashed_in_admission_cloud',True),('original_pdf_obtained',True),('raw_mooring_data_reanalysed',True)]:
            facts=copy.deepcopy(self.facts);facts[key]=value
            with self.assertRaises(ValueError):loader.validate_facts(facts)
    def test_every_JSON_CSV_cell_exact(self):
        incoming=csv.DictReader(io.StringIO(self.pieces[build.CSV].decode()));rows=list(incoming);self.assertEqual(len(rows),5)
        for raw,row in zip(self.addendum['evidence'],rows):self.assertEqual(row,{k:loader.base.cell(raw.get(k)) for k in incoming.fieldnames})
    def test_duplicate_context_and_altered_reference_rejected(self):
        with self.assertRaises(ValueError):loader.assemble(*self.parts,[(self.addendum,self.facts),(self.addendum,self.facts)])
        a=copy.deepcopy(self.addendum);a['evidence'][0]['metric']='core_depth'
        with self.assertRaises(ValueError):loader.assemble(*self.parts,[(a,self.facts)])


if __name__=='__main__':unittest.main()
