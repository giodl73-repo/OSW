import copy
import csv
import io
import json
import unittest
import build_current_depth_register_v41 as depth


class CanaryConvertedDepthRegisterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.rows=cls.data['evidence'][-3:]
        cls.rules=json.loads((depth.ROOT/depth.RULES).read_bytes())

    def test_previous_evidence_and_identity_coverage(self):
        old=json.loads((depth.ROOT/'research/current-depth-register-v40.json').read_bytes())
        self.assertEqual(self.data['evidence'][:347],old['evidence'])
        self.assertEqual(self.data['counts']['depth_references'],350)
        self.assertEqual(self.data['counts']['identities_with_scoped_depth_reference'],101)
        self.assertEqual(self.data['counts']['whole_route_depth_profiles'],0)
        self.assertEqual(self.data['counts']['volume_estimates'],0)
        self.assertEqual(self.data['member_depth_index_file'],'research/current-depth-member-index-v6.json')

    def test_native_values_and_conversion_provenance(self):
        converted=json.loads((depth.ROOT/'research/canary-pies-converted-depths-v1.json').read_bytes())
        for row,result in zip(self.rows,converted['records']):
            self.assertEqual(row['approximate_value_m'],result['display_approximate_depth_m'])
            self.assertEqual(row['source_pressure_dbar'],result['source_pressure_dbar'])
            self.assertEqual(row['computed_depth_before_display_rounding_m'],result['computed_depth_m'])
            self.assertEqual(row['pressure_conversion_gsw_version'],'3.6.23')
            self.assertEqual(row['metric'],'converted_mean_section_velocity_reversal_depth')
            self.assertEqual(row['evidence_kind'],'derived_standard_ocean_pressure_conversion')
            self.assertEqual(row['pressure_conversion_latitude_degrees_north'],result['conversion_latitude_degrees_north'])

    def test_region_and_conditional_selection_are_not_seasonal_range(self):
        self.assertEqual([r['approximate_value_m'] for r in self.rows],[800,480,680])
        self.assertEqual(self.rows[0]['source_pies_endpoints'],['C','E'])
        self.assertEqual(self.rows[1]['source_pies_endpoints'],['A','B'])
        self.assertEqual(self.rows[1]['source_mean_velocity_condition'],'all_times_time_mean')
        self.assertIn('excluding_recirculation',self.rows[2]['source_mean_velocity_condition'])
        for row in self.rows:
            self.assertIsNone(row['range_m']);self.assertIsNone(row['calendar_months']);self.assertIsNone(row['observed_period'])

    def test_no_physical_boundary_or_uncertainty_promotion(self):
        for row in self.rows:
            for field in ['upper_boundary_m','lower_boundary_m','thickness_m','annual_range_m','uncertainty_m']:
                self.assertIsNone(row[field])
            for field in ['volume_eligible','whole_current_representative','physical_state_join_eligible','seasonal_playback_eligible','reference_route_projection_eligible','sensitivity_is_uncertainty_interval']:
                self.assertFalse(row[field])

    def test_mutations_reject_pressure_relabeling_and_scope_loss(self):
        for row in self.rows:
            for key,value in [('approximate_value_m',row['source_pressure_dbar']),('metric','lower_flow_boundary_depth'),('pressure_conversion_latitude_degrees_north',0),('source_mean_velocity_condition','annual_climatology'),('uncertainty_m',0.02),('volume_eligible',True)]:
                changed=copy.deepcopy(row);changed[key]=value
                with self.subTest(reference=row['id'],field=key),self.assertRaises(ValueError):
                    depth.validate_context(changed)

    def test_json_and_csv_preserve_old_quantity_cells(self):
        self.assertEqual(self.data,json.loads((depth.ROOT/depth.OUTPUT).read_bytes()))
        raw=depth.csv_bytes(self.data);self.assertEqual(raw,(depth.ROOT/depth.CSV).read_bytes())
        rows=list(csv.DictReader(io.StringIO(raw.decode('utf8'))))
        old=list(csv.DictReader(io.StringIO((depth.ROOT/'research/current-depth-register-v40.csv').read_text(encoding='utf8'))))
        for before,after in zip(old,rows):
            for key,value in before.items():self.assertEqual(value,after[key],(before['id'],key))
        for source,out in zip(self.rows,rows[-3:]):
            self.assertEqual(float(out['source_pressure_dbar']),source['source_pressure_dbar'])
            self.assertEqual(json.loads(out['source_pies_endpoints']),source['source_pies_endpoints'])

    def test_rules_and_all_direct_input_hashes_are_retained(self):
        self.assertIn('converted_mean_section_velocity_reversal_depth',self.rules['metric_types'])
        import hashlib
        for path,digest in self.data['input_sha256'].items():
            self.assertEqual(hashlib.sha256((depth.ROOT/path).read_bytes()).hexdigest(),digest)
        self.assertIn('research/canary-pies-converted-depths-v1.json',self.data['input_sha256'])


if __name__=='__main__':unittest.main()
