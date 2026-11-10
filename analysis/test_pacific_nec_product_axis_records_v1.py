import copy
import hashlib
import json
from pathlib import Path
import unittest
import pacific_nec_product_axis_records_v1 as records

ROOT=Path(__file__).resolve().parents[1]


class ProductAxisRecords(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paths=['research/pacific-nec-connected-core-run-v1/diagnostic.json','research/pacific-nec-core-sampling-run-v1/diagnostic.json']
        cls.raw=[(ROOT/p).read_bytes() for p in cls.paths]
        cls.reports=[json.loads(b) for b in cls.raw]
        cls.pins={p:hashlib.sha256(b).hexdigest() for p,b in zip(cls.paths,cls.raw)}
        cls.acquisition=json.loads((ROOT/'research/pacific-nec-monthly-dimensions-run-v1/acquisition.json').read_bytes())
        cls.rows=records.records(*cls.reports,cls.acquisition,['source:provider-fixture','source:method-fixture'],cls.pins)

    def test_complete_retained_diagnostics_have_explicit_noncanonical_scope(self):
        self.assertEqual([len(self.rows[k]) for k in records.COLLECTIONS],[3,36,1332,36])
        for rows in self.rows.values():
            for row in rows:
                for field in ('rank_eligible','physical_state_join_eligible','is_independent_observation',
                              'physical_current_axis_qualified','is_annual_physical_range'):
                    self.assertIs(row[field],False)
                self.assertEqual(row['entity_id'],records.OWNER)
        reasons=[r for r in self.rows['current_axis_scenarios'] if r['length_km'] is None]
        self.assertEqual(len(reasons),85)  #12 earlier method failures plus73 anchor failures.
        self.assertTrue(all(r['reason'] for r in reasons))

    def test_exact_native_points_and_shared_baselines_preserved(self):
        readings={r['id']:r for r in self.rows['current_axis_readings']}
        for original in self.reports[1]['native_window_paths']:
            row=readings[records.reading_id(original['window_deg_north'],original['month'])]
            self.assertEqual(row['native_vector_points'],original['points'])
            self.assertEqual(row['length_km'],original['native_witness_length_km'])
            self.assertEqual(row['native_point_count'],331)
            self.assertEqual(sum(len(part) for part in row['geometry']['coordinates']),332)
        self.assertTrue(all(r['reading_id'] in readings and r['shared_measurement_claim_id']==r['reading_id'] for r in self.rows['current_axis_scenarios']))

    def test_dateline_split_duplicates_existing_vertex_without_world_spanning_leg(self):
        geometry=records.split_native_geometry([[181,12],[180,12.5],[179,13]])
        self.assertEqual(geometry,{'type':'MultiLineString','coordinates':[[[-179,12],[-180,12.5]],[[180,12.5],[179,13]]]})
        with self.assertRaisesRegex(ValueError,'existing180E'):records.split_native_geometry([[181,12],[179,13]])

    def test_section_unknowns_and_representation_quantity_stay_distinct(self):
        spans=self.rows['current_axis_section_spans']
        self.assertEqual(sum(r['width_km'] is None for r in spans),1)
        self.assertTrue(all(r['annual_physical_width_range_km'] is None and not r['physical_width_qualified'] for r in spans))
        thinned=[r for r in self.rows['current_axis_scenarios'] if r['scenario_kind']=='vertex_thinning']
        self.assertEqual(len(thinned),252)
        self.assertTrue(all(r['quantity']=='fixed_path_thinned_geodesic_representation_length' and not r['new_route_selected'] for r in thinned))

    def test_changed_nominal_and_missing_hashes_refused(self):
        sampling=copy.deepcopy(self.reports[1]);sampling['native_window_paths'][0]['native_witness_length_km']+=1
        with self.assertRaises(ValueError):records.records(self.reports[0],sampling,self.acquisition,['source:x'],self.pins)
        with self.assertRaises(ValueError):records.records(*self.reports,self.acquisition,['source:x'],{})


if __name__=='__main__':unittest.main()
