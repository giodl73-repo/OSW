import copy
import csv
import io
import json
import unittest
from pathlib import Path
import build_current_depth_reference_inventory_v22 as build
import load_current_depth_reference_inventory_v22 as loader
import load_current_depth_reference_inventory_v21 as prior

ROOT=Path(__file__).resolve().parents[1]


class ObservedCoreAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory,cls.addendum,cls.facts,cls.pieces,cls.view=build.build()
        cls.reader=staticmethod(lambda p:(ROOT/p).read_bytes())
        cls.previous=json.loads(cls.reader('research/current-depth-reference-inventory-v21.json'))
        cls.before=prior.load_inventory(cls.previous,cls.reader)
        cls.parts=prior.read_parts(cls.previous,cls.reader)

    def test_old_references_contexts_and_piece_bytes_preserved(self):
        self.assertEqual(self.view['evidence'][:-5],self.before['evidence'])
        self.assertEqual(self.inventory['base'],self.previous['base'])
        self.assertEqual(self.inventory['addenda'][:-1],self.previous['addenda'])
        for k,v in self.before['source_contexts'].items():self.assertEqual(self.view['source_contexts'][k],v)
        self.assertEqual(self.view['counts']['identities_with_scoped_depth_reference'],self.before['counts']['identities_with_scoped_depth_reference'])
        self.assertEqual(self.view['coordinate_unit_counts']['dbar'],self.before['coordinate_unit_counts']['dbar'])

    def test_no_surface_gap_thickness_or_error_promotion(self):
        for row in self.addendum['evidence']:
            self.assertEqual(row['metric'],'core_depth')
            self.assertEqual(row['source_near_surface_unsampled_depth_m'],16)
            for k in ['thickness_m','lower_boundary_m','upper_boundary_m','uncertainty_m','annual_range_m','observed_period','source_sampled_lon_lat']:
                self.assertIsNone(row[k])
            for k in ['full_water_column_core_established','physical_current_bottom_established','reference_route_projection_eligible','volume_eligible','physical_depth_ranking_eligible','seasonal_playback_eligible','independent_observation_count_claimed']:
                self.assertFalse(row[k])

    def test_snapshot_and_mean_operator_substitution_rejected(self):
        for index,key,value in [(0,'observation_date','2014-07-22'),(3,'observation_date','2014-06-17'),(4,'statistic','mean_instantaneous_core_depth'),(0,'station','C3')]:
            f=copy.deepcopy(self.facts);f['records'][index][key]=value
            with self.assertRaises(ValueError):loader.validate_facts(f)

    def test_weak_interbranch_flow_is_not_added_as_a_core(self):
        f=copy.deepcopy(self.facts);f['records'][0].update(station='C3',approximate_value_m=37,reported_current_speed_cm_s=9.1)
        with self.assertRaises(ValueError):loader.validate_facts(f)
        f=copy.deepcopy(self.facts);f['records'].append(copy.deepcopy(f['records'][0]))
        with self.assertRaises(ValueError):loader.validate_facts(f)

    def test_no_raw_source_coordinate_or_date_custody_invention(self):
        for k,v in [('raw_adcp_records_obtained',True),('figures_digitized',True),('station_coordinates_independently_resolved',True),('exact_html_bytes_retained',True),('source_html_sha256','invented')]:
            f=copy.deepcopy(self.facts);f[k]=v
            with self.assertRaises(ValueError):loader.validate_facts(f)
        for k in ['exact_station_deployment_dates_resolved','velocity_error_index_is_depth_error']:
            f=copy.deepcopy(self.facts);f['reported_methods'][k]=True
            with self.assertRaises(ValueError):loader.validate_facts(f)

    def test_csv_preserves_every_typed_statistic_and_date(self):
        table=csv.DictReader(io.StringIO(self.pieces[build.CSV].decode()))
        rows=list(table)
        self.assertEqual(rows,[{k:loader.base.cell(r.get(k)) for k in table.fieldnames} for r in self.addendum['evidence']])

    def test_changed_context_and_physical_row_are_rejected(self):
        for k,v in [('metric','physical_current_depth'),('thickness_m',41),('annual_range_m',[27,61]),('source_statistic','monthly_climatology'),('full_water_column_core_established',True)]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][k]=v
            with self.assertRaises(ValueError):loader.assemble(*self.parts,[(a,self.facts)])
        with self.assertRaises(ValueError):loader.assemble(*self.parts,[(self.addendum,self.facts)]*2)

    def test_exact_roundtrip_and_source_hash_mutation(self):
        reader=lambda p:self.pieces[p] if p in self.pieces else self.reader(p)
        self.assertEqual(loader.load_inventory(self.inventory,reader)['evidence'],self.view['evidence'])
        with self.assertRaises(ValueError):loader.load_inventory(self.inventory,lambda p:reader(p)+b' ' if p==loader.FACTS else reader(p))


if __name__=='__main__':unittest.main()
