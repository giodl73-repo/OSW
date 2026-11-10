"""Linked observed depth metrics preserve source cases, censors and prior references."""
import copy,csv,io,json,unittest
from collections import Counter
from unittest.mock import patch
import build_current_depth_reference_inventory_v20 as build
import load_current_depth_reference_inventory_v20 as loader
import load_current_depth_reference_inventory_v19 as prior


class RedsoxObservedReferences(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('urllib.request.urlopen',side_effect=AssertionError('No retrieval')):cls.inventory,cls.addendum,cls.facts,cls.pieces,cls.view=build.build()
        cls.old=json.loads((build.ROOT/'research/current-depth-reference-inventory-v19.json').read_bytes());cls.parts=prior.read_parts(cls.old,lambda f:(build.ROOT/f).read_bytes())
    def fixture(self):
        r=self.facts['records'][0];source=json.loads((build.ROOT/r['source_report_file']).read_bytes());return copy.deepcopy(source['cases'][int(r['source_case_pointer'].split('/')[-1])]),r
    def test_all810_prior_rows_contexts_parts_base_and_units_preserved(self):
        old=prior.load_inventory(self.old,lambda f:(build.ROOT/f).read_bytes());self.assertEqual(self.view['evidence'][:810],old['evidence']);self.assertEqual(self.inventory['base'],self.old['base']);self.assertEqual(self.inventory['addenda'][:-1],self.old['addenda']);self.assertEqual({k:self.view['source_contexts'][k] for k in old['source_contexts']},old['source_contexts']);self.assertEqual(self.view['counts']['depth_references'],818);self.assertEqual(self.view['coordinate_unit_counts'],{'m':817,'dbar':1});self.assertIs(build.prior,prior)
    def test_eight_metric_rows_are_four_linked_source_cases_not_eight_observations(self):
        refs=self.addendum['evidence'];self.assertEqual(len(refs),8);self.assertEqual(Counter(r['metric'] for r in refs),{'core_depth':4,'derived_core_connected_component_penetration_lower_bound':4});self.assertEqual(set(Counter(r['source_case_id'] for r in refs).values()),{2});self.assertEqual(len({r['source_case_id'] for r in refs}),4);self.assertEqual(self.facts['source_profile_cases'],4);self.assertFalse(self.facts['independent_observation_count_claimed'])
        for key in ['identities','identities_with_scoped_depth_reference','identities_not_yet_assessed','whole_route_depth_profiles','volume_estimates']:self.assertEqual(self.view['counts'][key],self.old['counts'][key])
    def test_native_cores_and_inclusive_reaches_are_separate_quantities(self):
        refs=self.addendum['evidence'];self.assertEqual([r['approximate_value_m'] for r in refs[::2]],[665.197,695.317,414.876,424.593]);self.assertEqual([r['lower_bound_m'] for r in refs[1::2]],[711.235,702.097,442.524,453.822])
        for core,reach in zip(refs[::2],refs[1::2]):self.assertIsNone(core['lower_bound_m']);self.assertIsNone(reach['approximate_value_m']);self.assertFalse(reach['lower_bound_exclusive']);self.assertEqual(core['source_case_id'],reach['source_case_id']);self.assertEqual(reach['support_start_depth_m'],core['approximate_value_m']);self.assertFalse(reach['surface_connection_established']);self.assertEqual(reach['source_lower_status'],'censored_at_native_velocity_sampling_end')
    def test_source_positions_pointers_timestamps_and_component_groups_retained(self):
        self.assertEqual(len({r['comparison_group'] for r in self.addendum['evidence']}),2)
        for r in self.addendum['evidence']:
            f=self.facts['records'][int(r['source_pointer'].split('/')[2])];self.assertEqual(r['source_position_lon_lat'],f['position_lon_lat']);self.assertEqual(r['source_velocity_header_time_utc'],f['source_velocity_header_time_utc']);self.assertEqual(r['source_ctd_start_time_utc'],f['source_ctd_start_time_utc']);self.assertEqual(r['source_case_pointer'],f['source_case_pointer']);self.assertEqual(r['source_report_sha256'],f['source_report_sha256']);self.assertEqual(r['section_bearing_degrees_true'],f['section_bearing_degrees_true']);self.assertEqual(r['source_hydrographic_depth_operator'],f['source_hydrographic_depth_operator'])
    def test_source_fact_regeneration_matches_exact_published_source_reports(self):
        op=json.loads((build.ROOT/build.OPERATOR).read_bytes());self.assertEqual(build.facts_from_sources(build.ROOT,op),self.facts)
        for r in self.facts['records']:
            source=json.loads((build.ROOT/r['source_report_file']).read_bytes());c=source['cases'][int(r['source_case_pointer'].split('/')[-1])];self.assertEqual(r['core_depth_m'],c['core_depth_m']);self.assertEqual(r['supported_penetration_lower_bound_m'],c['joint_diagnosis']['lower']['last_connected_depth_m']);self.assertEqual(r['source_report_sha256'],build.sha((build.ROOT/r['source_report_file']).read_bytes()))
    def test_fine_path_missing_salinity_dip_or_unsupported_segment_blocks_admission(self):
        for mutation in ['missing','dip','gap']:
            c,r=self.fixture();g=c['fine_source_union_grid'];i=g['seed_union_index']+1
            if mutation=='missing':g['salinity_psu'][i]=None
            elif mutation=='dip':g['salinity_psu'][i]=37
            else:g['salinity_segment_support'][i]='gap'
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):build.admit_case(c,r['source_report_file'],r['source_report_sha256'],1)
    def test_source_censor_cannot_be_replaced_by_bed_or_a_finite_bottom(self):
        c,r=self.fixture();c['joint_diagnosis']['lower']['boundary_depth_m']=c['joint_diagnosis']['lower']['last_connected_depth_m']
        with self.assertRaises(ValueError):build.admit_case(c,r['source_report_file'],r['source_report_sha256'],1)
        for key,value in [('supported_penetration_lower_bound_exclusive',True),('lower_boundary_depth_m',711.235),('support_start_depth_m',0),('physical_layer_thickness_m',46.038)]:
            f=copy.deepcopy(self.facts);f['records'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):loader.validate_facts(f)
    def test_changed_core_or_source_quality_rejected_without_weaker_replacement(self):
        for key,value in [('core_depth_m',666),('core_component_m_s',.1),('exclusion_reasons',['quality_issue']),('sample_level_synchronization_verified',True)]:
            c,r=self.fixture();c[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):build.admit_case(c,r['source_report_file'],r['source_report_sha256'],1)
    def test_no_physical_identity_clock_tidal_or_independence_promotion(self):
        for key in ['physical_current_bottom_established','surface_connection_established','physical_cast_identity_independently_verified','sample_level_synchronization_verified','source_reference_quality_independently_verified','tidal_correction_applied','independent_observation_count_claimed','reference_route_projection_eligible']:
            f=copy.deepcopy(self.facts);f['records'][0][key]=True
            with self.subTest(key=key),self.assertRaises(ValueError):loader.validate_facts(f)
        for r in self.addendum['evidence']:self.assertFalse(r['physical_current_bottom_established']);self.assertFalse(r['water_mass_identity_established']);self.assertFalse(r['independent_observation_count_claimed'])
    def test_every_typed_json_csv_cell_exact_and_source_facts_round_trip(self):
        incoming=csv.DictReader(io.StringIO(self.pieces[build.CSV].decode()));rows=list(incoming);self.assertEqual(len(rows),8)
        for raw,row in zip(self.addendum['evidence'],rows):self.assertEqual(row,{k:loader.base.cell(raw.get(k)) for k in incoming.fieldnames})
        self.assertEqual(json.loads(self.pieces[loader.FACTS]),self.facts)
    def test_duplicate_context_or_changed_reference_rejected(self):
        with self.assertRaises(ValueError):loader.assemble(*self.parts,[(self.addendum,self.facts),(self.addendum,self.facts)])
        a=copy.deepcopy(self.addendum);a['evidence'][1]['lower_bound_exclusive']=True
        with self.assertRaises(ValueError):loader.assemble(*self.parts,[(a,self.facts)])
    def test_no_thickness_uncertainty_annual_width_volume_or_runtime_promotion(self):
        for r in self.addendum['evidence']:
            for key in ['thickness_m','upper_boundary_m','lower_boundary_m','uncertainty_m','annual_range_m','same_source_width_reference_id','observed_period','calendar_months']:self.assertIsNone(r[key])
            for key in ['whole_current_representative','volume_eligible','annual_extrema_eligible','seasonal_playback_eligible','reference_route_projection_eligible','physical_state_join_eligible']:self.assertFalse(r[key])
        self.assertFalse(self.inventory['runtime_changed']);self.assertFalse(self.inventory['full_goal_complete'])


if __name__=='__main__':unittest.main()
