import copy
import csv
import io
import json
import unittest
from pathlib import Path
import build_current_depth_reference_inventory_v21 as build
import load_current_depth_reference_inventory_v21 as loader
import load_current_depth_reference_inventory_v20 as prior

ROOT = Path(__file__).resolve().parents[1]


class BedformDepthAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory, cls.addendum, cls.facts, cls.pieces, cls.view = build.build()
        cls.reader = staticmethod(lambda path: (ROOT / path).read_bytes())
        cls.before_manifest = json.loads(cls.reader('research/current-depth-reference-inventory-v20.json'))
        cls.before = prior.load_inventory(cls.before_manifest, cls.reader)
        cls.parts = prior.read_parts(cls.before_manifest, cls.reader)

    def test_every_prior_row_context_and_part_preserved(self):
        self.assertEqual(self.view['evidence'][:-1], self.before['evidence'])
        self.assertEqual(self.inventory['base'], self.before_manifest['base'])
        self.assertEqual(self.inventory['addenda'][:-1], self.before_manifest['addenda'])
        for key, value in self.before['source_contexts'].items():
            self.assertEqual(self.view['source_contexts'][key], value)

    def test_new_counts_and_native_pressure_preserved(self):
        self.assertEqual(self.view['counts']['depth_references'], 819)
        self.assertEqual(self.view['counts']['identities'], 111)
        self.assertEqual(self.view['coordinate_unit_counts'], {'dbar': 1, 'm': 818})

    def test_indirect_metric_has_no_physical_depth_ranking_or_penetration(self):
        row = self.addendum['evidence'][0]
        self.assertEqual(row['metric'], 'current_associated_bedform_field_water_depth_extent')
        self.assertEqual(row['approximate_value_m'], 70)
        for key in ['physical_depth_ranking_eligible', 'physical_current_bottom_established',
                    'reference_route_projection_eligible', 'volume_eligible',
                    'core_to_seabed_vertical_connectivity_established', 'direct_current_depth_measurement']:
            self.assertFalse(row[key])
        for key in ['thickness_m', 'annual_range_m', 'observed_period', 'source_survey_dates', 'bedform_height_m']:
            self.assertIsNone(row[key])

    def test_no_site_specific_depth_or_date_invention(self):
        for key, value in [('site_specific_depth_extents_separately_reported_in_reviewed_abstract', True),
                           ('exact_survey_dates', ['1993-01-01']), ('depth_datum_independently_resolved', True)]:
            facts = copy.deepcopy(self.facts); facts['reported_context'][key] = value
            with self.assertRaises(ValueError): loader.validate_facts(facts)

    def test_no_velocity_or_connected_layer_substitution(self):
        for key in ['direct_velocity_profile_available', 'core_to_seabed_vertical_connectivity_established']:
            facts = copy.deepcopy(self.facts); facts['reported_context'][key] = True
            with self.assertRaises(ValueError): loader.validate_facts(facts)
        for key, value in [('metric', 'physical_current_depth'), ('approximate_value_m', 100), ('range_m', [10, 70]), ('entity_id', 'current:norwegian-coastal')]:
            facts = copy.deepcopy(self.facts); facts['records'][0][key] = value
            with self.assertRaises(ValueError): loader.validate_facts(facts)

    def test_honest_abstract_access_without_full_paper_or_raw_data(self):
        for key, value in [('full_article_reviewed', True), ('exact_html_bytes_retained', True),
                           ('source_html_sha256', 'invented'), ('raw_survey_data_reanalysed', True),
                           ('physical_current_bottom_established', True)]:
            facts = copy.deepcopy(self.facts); facts[key] = value
            with self.assertRaises(ValueError): loader.validate_facts(facts)

    def test_every_typed_csv_cell_matches_json(self):
        reader = csv.DictReader(io.StringIO(self.pieces[build.CSV].decode()))
        rows = list(reader); self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0], {k: loader.base.cell(self.addendum['evidence'][0].get(k)) for k in reader.fieldnames})

    def test_duplicate_or_physically_promoted_row_rejected(self):
        with self.assertRaises(ValueError): loader.assemble(*self.parts, [(self.addendum, self.facts)] * 2)
        a = copy.deepcopy(self.addendum); a['evidence'][0]['thickness_m'] = 70
        with self.assertRaises(ValueError): loader.assemble(*self.parts, [(a, self.facts)])

    def test_roundtrip_and_changed_source_piece_rejected(self):
        reader = lambda p: self.pieces[p] if p in self.pieces else self.reader(p)
        self.assertEqual(loader.load_inventory(self.inventory, reader)['evidence'], self.view['evidence'])
        bad = lambda p: reader(p) + b' ' if p == loader.FACTS else reader(p)
        with self.assertRaises(ValueError): loader.load_inventory(self.inventory, bad)


if __name__ == '__main__': unittest.main()
