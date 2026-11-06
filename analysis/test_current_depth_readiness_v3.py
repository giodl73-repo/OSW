import copy,unittest
from build_current_depth_readiness_v3 import join,metric_family,CATALOG
from test_current_depth_readiness_v2 import fixture,ReadinessSemantics,CompiledV40Semantics

class MetricGapTests(unittest.TestCase):
    def test_metric_families_do_not_collapse_core_censor_or_model(self):
        cases={'core_depth':'core_structure','derived_relative_core_component_decay_depth':'processed_velocity_descriptor','derived_core_connected_component_penetration_lower_bound':'censored_reach','reported_censored_flow_pressure_reach':'censored_reach','transport_selected_depth_extent':'transport_operator','reported_model_mean_current_vertical_extent':'published_model_extent','reported_vertical_extent':'reported_extent_or_boundary_metric','reported_vertical_thickness':'reported_layer_or_plume_thickness','sampled_water_mass_depth_band':'hydrographic_or_habitat_proxy','reported_regional_ladcp_flow_pressure_band':'regional_pressure_domain','invented-new-metric':'unclassified_metric_retained'}
        for metric,expected in cases.items():
            with self.subTest(metric=metric):self.assertEqual(metric_family(metric),expected)
    def test_core_only_reference_is_not_an_extent_and_parent_needs_no_scalar(self):
        view,priority=fixture();report=join(view,priority,[]);family,leaf=report['records']
        self.assertEqual(leaf['collection_gap_kind'],'reported_extent_or_boundary_metric_not_in_canonical_references');self.assertEqual(leaf['metric_family_counts'],{'core_structure':1});self.assertIsNone(leaf['suggested_whole_current_depth_m'])
        self.assertFalse(family['family_requires_single_depth']);self.assertEqual(family['collection_gap_kind'],'component_identity_scope_before_parent_depth');self.assertEqual(report['collection_queue'][0]['entity_id'],'current:leaf')
    def test_extent_metric_changes_collection_target_without_proving_route_or_volume(self):
        view,priority=fixture();view['evidence'][0]['metric']='reported_vertical_extent';report=join(view,priority,[]);leaf=report['records'][1]
        self.assertEqual(leaf['collection_gap_kind'],'extend_regional_extent_evidence_to_aligned_route_and_time');self.assertIsNone(leaf['whole_route_physical_depth_m']);self.assertIsNone(leaf['volume_km3']);self.assertFalse(report['full_goal_complete'])
    def test_pressure_and_unknown_flags_remain_explicit(self):
        view,priority=fixture();view['evidence'][0].update(unit='dbar',metric='unknown-pressure-method');report=join(view,priority,[]);leaf=report['records'][1]
        self.assertEqual(leaf['pressure_reference_ids'],['ref']);self.assertEqual(leaf['unclassified_metric_names'],['unknown-pressure-method']);self.assertEqual(leaf['missing_reference_volume_eligibility_flag_count'],1);self.assertEqual(leaf['declared_reference_volume_eligible_count'],0);self.assertFalse(leaf['eligibility_flag_counts_are_physical_validation']);self.assertEqual(report['canonical_reference_inventory'],CATALOG)
    def test_every_reference_retained_once_and_inputs_unchanged(self):
        view,priority=fixture();view['evidence'] += [{'id':'pressure','entity_id':'current:leaf','unit':'dbar','metric':'reported_regional_bottom_intensified_flow_pressure_band'},{'id':'model','entity_id':'current:leaf','unit':'m','metric':'reported_model_snapshot_current_vertical_extent'}];saved=copy.deepcopy((view,priority));report=join(view,priority,[])
        self.assertEqual((view,priority),saved);self.assertEqual(sum(report['counts']['metric_family_references'].values()),3);self.assertEqual(sorted(x for ids in report['records'][1]['metric_family_reference_ids'].values() for x in ids),['model','pressure','ref'])
    def test_unknown_owner_and_identity_mismatch_rejected(self):
        view,priority=fixture();view['evidence'][0]['entity_id']='current:unknown'
        with self.assertRaises(ValueError):join(view,priority,[])
        view,priority=fixture();priority['records'].pop()
        with self.assertRaises(ValueError):join(view,priority,[])

if __name__=='__main__':unittest.main()
