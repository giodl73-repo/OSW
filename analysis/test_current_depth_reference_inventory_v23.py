import copy
import csv
import io
import hashlib
import json
import unittest
from pathlib import Path
import build_current_depth_reference_inventory_v23 as build
import load_current_depth_reference_inventory_v23 as loader
import load_current_depth_reference_inventory_v22 as prior

ROOT=Path(__file__).resolve().parents[1]


class ObservedDailyLowerAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory,cls.addendum,cls.facts,cls.pieces,cls.view=build.build()
        cls.reader=staticmethod(lambda p:(ROOT/p).read_bytes())
        cls.previous=json.loads(cls.reader('research/current-depth-reference-inventory-v22.json'))
        cls.before=prior.load_inventory(cls.previous,cls.reader)
        cls.parts=prior.read_parts(cls.previous,cls.reader)

    def test_every_prior_row_context_and_piece_preserved(self):
        self.assertEqual(self.view['evidence'][:-18],self.before['evidence'])
        self.assertEqual(self.inventory['base'],self.previous['base'])
        self.assertEqual(self.inventory['addenda'][:-1],self.previous['addenda'])
        for k,v in self.before['source_contexts'].items():self.assertEqual(self.view['source_contexts'][k],v)
        self.assertEqual(self.view['counts'],{'identities':111,'depth_references':842,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0})
        self.assertEqual(self.view['coordinate_unit_counts'],{'dbar':1,'m':841})

    def test_lower_proxy_is_not_physical_thickness_or_error_interval(self):
        for row in self.addendum['evidence']:
            self.assertEqual(row['metric'],loader.METRIC)
            self.assertEqual(row['source_primary_threshold_m_s'],.1)
            for k in ['thickness_m','lower_boundary_m','upper_boundary_m','uncertainty_m','range_m','annual_range_m','source_sampled_lon_lat','source_snapshot_time_utc']:
                self.assertIsNone(row[k])
            for k in ['physical_current_bottom_established','physical_depth_ranking_eligible','reference_route_projection_eligible','volume_eligible','current_identity_independently_verified','source_daily_underlying_sample_coverage_verified','source_mean_field_depth_is_mean_instantaneous_depth']:
                self.assertFalse(row[k])
        self.assertEqual(sum(r['source_threshold_layer_span_m'] is not None for r in self.addendum['evidence']),15)

    def test_all48_outcomes_still_linked_with_nominal_geometry_and_daily_operator(self):
        context=self.addendum['source_contexts'][loader.CONTEXT]
        self.assertEqual(context['all_source_profiles_retained'],48)
        self.assertEqual(context['all_case_csv_piece']['file'],'research/tao-pacific-euc-daily-depth-profiles-v1.csv')
        for r in self.addendum['evidence']:
            self.assertEqual(r['source_position_role'],'nominal_station_not_actual_deployment_or_current_axis')
            self.assertEqual(r['source_daily_average_interval_utc']['start'][:10],r['source_time_label_utc'][:10])
            self.assertTrue(r['source_data_url'].startswith('https://coastwatch.pfeg.noaa.gov/erddap/tabledap/pmelTaoDyAdcp.csv?'))

    def test_wrong_metric_frame_threshold_quality_or_sampling_rejected(self):
        for k,v in [('metric','physical_current_depth'),('component_bearing_degrees_true',270),('primary_threshold_m_s',.05),('quality_flags_accepted',[1,2,3]),('core_search_depth_interval_m',[0,350]),('source_coordinate_role','measured_current_axis'),('source_temporal_operator','instantaneous_snapshot')]:
            f=copy.deepcopy(self.facts);f[k]=v
            with self.assertRaises(ValueError):loader.validate_facts(f)

    def test_candidate_date_station_and_depth_mutations_rejected(self):
        for k,v in [('source_daily_average_date','2005-01-01'),('approximate_value_m',1),('source_station',{'station':'other','longitude':165,'latitude':0}),('threshold_m_s',.2),('source_raw_sha256','0'*64)]:
            f=copy.deepcopy(self.facts);f['records'][0][k]=v
            with self.assertRaises(ValueError):loader.validate_facts(f)

    def test_source_piece_and_independent_audit_binding_cannot_be_replaced(self):
        wrapper=json.loads(self.reader(loader.FACTS))
        for piece in ['candidate_piece','profile_piece','audit_piece','journal_piece','all_case_csv_piece','all_case_geojson_piece']:
            file=wrapper[piece]['file']
            with self.assertRaises(ValueError):loader.read_facts(wrapper,lambda p:self.reader(p)+b' ' if p==file else self.reader(p))
        f=copy.deepcopy(self.facts);f['admitted_finite_primary_lower_estimates']=17
        with self.assertRaises(ValueError):loader.validate_facts(f)

    def test_proxy_span_or_bracket_cannot_be_promoted(self):
        for k,v in [('thickness_m',100),('lower_boundary_m',200),('uncertainty_m',[10,20]),('annual_range_m',[100,300]),('source_statistic','mean_instantaneous_current_depth'),('reference_route_projection_eligible',True)]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][k]=v
            with self.assertRaises(ValueError):loader.assemble(*self.parts,[(a,self.facts)])
        with self.assertRaises(ValueError):loader.assemble(*self.parts,[(self.addendum,self.facts)]*2)

    def test_every_typed_csv_cell_and_roundtrip(self):
        table=csv.DictReader(io.StringIO(self.pieces[build.CSV].decode()));rows=list(table)
        self.assertEqual(rows,[{k:loader.base.cell(r.get(k)) for k in table.fieldnames} for r in self.addendum['evidence']])
        reader=lambda p:self.pieces[p] if p in self.pieces else self.reader(p)
        self.assertEqual(loader.load_inventory(self.inventory,reader)['evidence'],self.view['evidence'])

    def test_every_reference_source_pointer_resolves_to_the_exact_retained_record(self):
        for row in self.addendum['evidence']:
            raw=self.reader(row['source_file']);target=json.loads(raw)
            self.assertEqual(hashlib.sha256(raw).hexdigest(),row['source_sha256'])
            for key in row['source_pointer'].split('/')[1:]:target=target[int(key)] if isinstance(target,list) else target[key]
            self.assertEqual(target,row['source_audit_record'])


if __name__=='__main__':unittest.main()
