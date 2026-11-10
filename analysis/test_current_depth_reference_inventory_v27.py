import copy
import json
import socket
import unittest
from pathlib import Path
import build_current_depth_reference_inventory_v27 as build
import load_current_depth_reference_inventory_v27 as loader
import load_current_depth_reference_inventory_v26 as prior

ROOT = Path(__file__).resolve().parents[1]


class LabradorMeanExtent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        socket.socket = lambda *a, **k: (_ for _ in ()).throw(RuntimeError('Offline only'))
        cls.inventory, cls.addendum, cls.facts, cls.pieces, cls.view = build.build()
        cls.reader = staticmethod(lambda p: (ROOT / p).read_bytes())
        cls.previous = json.loads(cls.reader('research/current-depth-reference-inventory-v26.json'))
        cls.parts = prior.read_parts(cls.previous, cls.reader)
        cls.before = prior.load_inventory(cls.previous, cls.reader)

    def test_all_prior_references_and_contexts_preserved(self):
        self.assertEqual(self.view['evidence'][:-1], self.before['evidence'])
        self.assertEqual(self.inventory['base'], self.previous['base'])
        self.assertEqual(self.inventory['addenda'][:-1], self.previous['addenda'])
        for k, v in self.before['source_contexts'].items():
            self.assertEqual(self.view['source_contexts'][k], v)
        self.assertEqual(self.view['counts'], {'identities': 111, 'depth_references': 860,
            'identities_with_scoped_depth_reference': 101, 'identities_not_yet_assessed': 10,
            'whole_route_depth_profiles': 0, 'volume_estimates': 0})
        self.assertEqual(self.view['coordinate_unit_counts'], {'dbar': 2, 'm': 858})

    def test_regional_mean_extent_cannot_be_physical_or_seasonal_depth(self):
        row = self.addendum['evidence'][0]
        self.assertEqual(row['approximate_value_m'], 500)
        self.assertEqual(row['metric'], 'reported_vertical_extent')
        for k in ['thickness_m', 'annual_range_m', 'uncertainty_m', 'upper_boundary_m',
                  'lower_boundary_m', 'source_fixed_velocity_threshold_m_s']:
            self.assertIsNone(row[k])
        for k, v in [('thickness_m', 500), ('volume_eligible', True),
                     ('physical_current_bottom_established', True),
                     ('seasonal_playback_eligible', True), ('physical_depth_ranking_eligible', True)]:
            a = copy.deepcopy(self.addendum); a['evidence'][0][k] = v
            with self.assertRaises(ValueError): loader.assemble(*self.parts, [(a, self.facts)])

    def test_shallow_current_owner_and_observational_period_cannot_change(self):
        for k, v in [('entity_id', 'current:deep-western-boundary'),
                     ('source_period_years', [1958, 2009]),
                     ('source_section_latitude_degrees_north', 60),
                     ('metric', 'velocity_layer_lower_boundary_depth')]:
            facts = copy.deepcopy(self.facts); facts['records'][0][k] = v
            with self.assertRaises(ValueError): loader.validate_facts(facts)

    def test_model_agreement_is_not_independent_observation(self):
        for k in ['VIKING20_model_value_admitted_as_second_observation',
                  'deep_DWBC_assigned_to_Labrador_Current',
                  'source_statistic_is_mean_individual_boundary_depth',
                  'fixed_velocity_threshold_specified_for_500m_extent']:
            facts = copy.deepcopy(self.facts); facts['methods'][k] = True
            with self.assertRaises(ValueError): loader.validate_facts(facts)
        with self.assertRaises(ValueError):
            loader.assemble(*self.parts, [(self.addendum, self.facts)] * 2)

    def test_custody_and_source_provenance_cannot_be_upgraded(self):
        for k, v in [('source_html_sha256', 'invented'), ('source_figures_visually_reviewed', True),
                     ('raw_velocity_profiles_reanalysed', True), ('new_ocean_field_requests', 1)]:
            facts = copy.deepcopy(self.facts); facts[k] = v
            with self.assertRaises(ValueError): loader.validate_facts(facts)

    def test_artifact_roundtrip_detects_changed_reference_bytes(self):
        reader = lambda p: self.pieces[p] if p in self.pieces else self.reader(p)
        self.assertEqual(loader.load_inventory(self.inventory, reader)['evidence'], self.view['evidence'])
        broken = dict(self.pieces); broken[build.CSV] += b'changed'
        with self.assertRaises(ValueError):
            loader.load_inventory(self.inventory, lambda p: broken[p] if p in broken else self.reader(p))
        self.assertLess(sum(map(len, self.pieces.values())), 2400000)


if __name__ == '__main__':
    unittest.main()
