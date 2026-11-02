import copy
import csv
import io
import json
import unittest
import build_current_depth_register_v42 as depth


class MalvinasDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.rows=cls.data['evidence'][-4:]

    def test_prior_evidence_and_identity_scope(self):
        old=json.loads((depth.ROOT/'research/current-depth-register-v41.json').read_bytes())
        self.assertEqual(self.data['evidence'][:350],old['evidence'])
        self.assertEqual(self.data['counts']['depth_references'],354)
        self.assertEqual(self.data['counts']['identities_with_scoped_depth_reference'],101)
        self.assertTrue(all(r['entity_id']=='current:falkland' for r in self.rows))
        self.assertEqual(len(next(r for r in self.data['records'] if r['entity_id']=='current:falkland')['depth_reference_ids']),5)

    def test_distinct_local_maxima_are_not_global_branch_maxima(self):
        self.assertEqual([r['approximate_value_m'] for r in self.rows],[250,400,550,None])
        self.assertEqual(self.rows[1]['source_velocity_maximum_role'],'secondary_subsurface_local_maximum')
        self.assertEqual(self.rows[2]['source_velocity_maximum_role'],'separate_offshore_subsurface_high_velocity_core')
        self.assertEqual(self.rows[1]['source_crossing_number'],self.rows[2]['source_crossing_number'])
        self.assertNotEqual(self.rows[1]['source_case_id'],self.rows[2]['source_case_id'])

    def test_near_surface_band_is_not_an_observed_zero_depth_point(self):
        row=self.rows[3]
        self.assertEqual(row['range_m'],[0,50]);self.assertIsNone(row['approximate_value_m'])
        self.assertIsNone(row['upper_boundary_m']);self.assertIsNone(row['thickness_m'])
        self.assertTrue(row['source_unsampled_surface_not_resolved'])
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes())
        self.assertEqual(source['archive_lead']['metadata_depth_support_m'],[24.44,720.44])
        self.assertFalse(source['archive_lead']['raw_profiles_processed'])

    def test_crossing_periods_and_upstream_context(self):
        self.assertEqual([r['source_crossing_number'] for r in self.rows],[7,14,14,16])
        self.assertEqual(self.rows[0]['source_section_date_bounds'],['2017-12-31','2018-01-02'])
        self.assertEqual(self.rows[3]['source_section_date_bounds'],['2020-01-12','2020-01-13'])
        self.assertTrue(self.rows[0]['source_approach_context_only'])
        for row in self.rows:
            self.assertIsNone(row['observed_period']);self.assertIsNone(row['calendar_months'])
            self.assertEqual(row['source_date_role'],'whole_crossing_not_exact_maximum_occupation')

    def test_sampling_range_bathymetry_and_errors_are_not_flow_depth(self):
        for row in self.rows:
            self.assertEqual(row['source_nominal_ADCP_range_m'],700)
            self.assertEqual(row['source_horizontal_smoothing_km'],25)
            self.assertEqual(row['source_time_averaging_seconds'],120)
            self.assertEqual(row['source_velocity_projection'],'perpendicular_to_nominal_transect_along_slope')
            for field in ['lower_boundary_m','upper_boundary_m','thickness_m','uncertainty_m','annual_range_m']:
                self.assertIsNone(row[field])
            for field in ['volume_eligible','whole_current_representative','physical_state_join_eligible','seasonal_playback_eligible','reference_route_projection_eligible']:
                self.assertFalse(row[field])

    def test_mutations_reject_role_merging_and_unsupported_extent(self):
        for row in self.rows:
            for key,value in [('approximate_value_m',700),('metric','lower_flow_boundary_depth'),('source_velocity_maximum_role','global_branch_maximum'),('source_approach_context_only',not row['source_approach_context_only']),('source_date_role','exact_maximum_occupation'),('uncertainty_m',2),('volume_eligible',True)]:
                changed=copy.deepcopy(row);changed[key]=value
                with self.subTest(reference=row['id'],field=key),self.assertRaises(ValueError):depth.validate_context(changed)

    def test_exact_outputs_and_previous_csv_cells(self):
        self.assertEqual(self.data,json.loads((depth.ROOT/depth.OUTPUT).read_bytes()))
        raw=depth.csv_bytes(self.data);self.assertEqual(raw,(depth.ROOT/depth.CSV).read_bytes())
        rows=list(csv.DictReader(io.StringIO(raw.decode('utf8'))))
        old=list(csv.DictReader(io.StringIO((depth.ROOT/'research/current-depth-register-v41.csv').read_text(encoding='utf8'))))
        for before,after in zip(old,rows):
            for key,value in before.items():self.assertEqual(value,after[key],(before['id'],key))
        self.assertEqual(json.loads(rows[-1]['range_m']),[0,50])
        self.assertEqual(json.loads(rows[-1]['source_section_date_bounds']),['2020-01-12','2020-01-13'])


if __name__=='__main__':unittest.main()
