import copy,csv,io,json,math,socket,unittest
from unittest.mock import patch
import audit_eac_mooring_local_depth_sensitivity_v1 as audit

class EACEndpointSensitivity(unittest.TestCase):
    def test_two_independent_interpolants_reproduce_analytic_cases(self):
        self.assertAlmostEqual(audit.crossing([100,200],[0.3,-0.1],0.1),150)
        self.assertAlmostEqual(audit.crossing([100,200],[0.3,0.1],0.1),200)
        self.assertIsNone(audit.crossing([100,200],[0.3,0.2],0.1))
        with self.assertRaises(ValueError):audit.crossing([100,100],[0.3,-0.1],0.1)
        with self.assertRaises(ValueError):audit.crossing([100,200],[float('nan'),0],0.1)

    def test_complete_rectangle_bounds_all_interior_responses(self):
        r=audit.sensitivity([100,200],[0.3,-0.1],[0.02,0.03],0.1)
        low,high=r['complete_endpoint_rectangle_depth_sensitivity_range_m']
        for a in [-1,-0.5,0,0.5,1]:
            for b in [-1,-0.5,0,0.5,1]:
                depth=audit.crossing([100,200],[0.3+a*0.02,-0.1+b*0.03],0.1)
                self.assertLessEqual(low,depth);self.assertLessEqual(depth,high)
        self.assertEqual(len(r['corners']),4);self.assertFalse(r['confidence_interval_established'])
        self.assertFalse(r['endpoint_errors_assumed_independent']);self.assertFalse(r['full_profile_or_core_connection_reassessed'])

    def test_invalid_one_corner_suppresses_complete_range_and_never_relocates(self):
        r=audit.sensitivity([100,200],[0.2,0],[0.15,0.01],0.1)
        self.assertEqual(r['status'],'ENDPOINT_ERROR_RECTANGLE_INVALIDATES_LOCAL_BRACKET')
        self.assertIsNone(r['complete_endpoint_rectangle_depth_sensitivity_range_m'])
        self.assertTrue(any(not c['bracket_survives'] for c in r['corners']))
        self.assertTrue(any(c['bracket_survives'] for c in r['corners']))
        self.assertEqual(r['source_endpoint_depths_m'],[100,200])

    def test_missing_error_is_unknown_not_zero_and_negative_invalid(self):
        r=audit.sensitivity([100,200],[0.3,0],[None,0.01],0.1)
        self.assertEqual(r['status'],'SOURCE_ENDPOINT_STANDARD_ERROR_MISSING');self.assertEqual(r['corners'],[])
        self.assertIsNone(r['complete_endpoint_rectangle_depth_sensitivity_range_m'])
        for se in [[-0.01,0.01],[float('nan'),0.01],[True,0.01]]:
            with self.assertRaises(ValueError):audit.sensitivity([100,200],[0.3,0],se,0.1)

    def test_zero_errors_are_valid_degenerate_response_not_accuracy(self):
        r=audit.sensitivity([100,200],[0.3,-0.1],[0,0],0.1)
        self.assertEqual(r['complete_endpoint_rectangle_depth_sensitivity_range_m'],[150,150])
        self.assertIsNone(r['physical_depth_uncertainty_m']);self.assertFalse(r['confidence_interval_established'])
        for k in ['volume_eligible','physical_state_join_eligible','reference_route_projection_eligible','seasonal_playback_eligible','physical_current_bottom_established']:self.assertFalse(r[k])

    def test_retained_actual_all42_outcomes_reproduce_nominal_and_original_bytes(self):
        source=(audit.ROOT/audit.SOURCE).read_bytes();report=audit.build()
        self.assertEqual((audit.ROOT/audit.SOURCE).read_bytes(),source)
        self.assertEqual(report['counts']['source_profiles'],14);self.assertEqual(report['counts']['station_date_threshold_outcomes'],42)
        self.assertEqual(report['counts']['nominal_resolved_lower_boundaries'],16)
        self.assertEqual(report['counts']['nominal_lower_boundary_unresolved'],26)
        self.assertEqual(report['counts']['retained_typed_velocity_scalars'],8768)
        self.assertLessEqual(report['counts']['local_bracket_scalar_touches'],252)
        for r in report['outcomes']:
            if r['sensitivity']:
                self.assertAlmostEqual(r['sensitivity']['nominal_crossing_depth_m'],r['original_nominal_layer']['lower_depth_m'],places=8)
            self.assertFalse(r['fixed_station_is_current_axis']);self.assertFalse(r['new_native_measurement'])
        missing=[r for r in report['outcomes'] if r['station']=='NRSNSI' and r['source_date']=='2022-07-15']
        self.assertEqual(len(missing),3);self.assertTrue(all(r['sensitivity'] is None for r in missing))

    def test_csv_empty_missing_ranges_and_network_tripwire(self):
        def denied(*a,**k):raise RuntimeError('Source replay prohibited')
        with patch.object(socket,'socket',denied),patch.object(socket,'create_connection',denied):r=audit.build()
        table=list(csv.DictReader(io.StringIO(audit.csv_bytes(r['outcomes']).decode())))
        self.assertEqual(len(table),42)
        for row,original in zip(table,r['outcomes']):
            if original['sensitivity'] is None or original['sensitivity']['complete_endpoint_rectangle_depth_sensitivity_range_m'] is None:
                self.assertEqual(row['complete_local_sensitivity_min_m'],'');self.assertEqual(row['complete_local_sensitivity_max_m'],'')

if __name__=='__main__':unittest.main()
