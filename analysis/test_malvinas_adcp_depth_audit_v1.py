import unittest
import audit_malvinas_adcp_depth_v1 as audit


def row(depth,v,quality=100):return {'depth':depth,'v':v,'quality':quality,'lat':-46,'lon':-59}


class NativeProfileAuditTests(unittest.TestCase):
    def test_maximum_ties_and_unsampled_surface(self):
        d=audit.summarize_profile([row(24,40),row(32,40),row(40,20)],70)
        self.assertEqual(d['sampled_maximum_depths_m'],[24,32]);self.assertTrue(d['maximum_at_shallowest_valid_level'])
        self.assertIsNone(d['flow_boundary_depth_m']);self.assertIsNone(d['physical_thickness_m'])

    def test_quality_threshold_sensitivity_and_missing_values(self):
        rows=[row(24,60,60),row(32,30,90),row(40,None,100),row(48,100,None)]
        self.assertEqual(audit.summarize_profile(rows,50)['sampled_maximum_depths_m'],[24])
        d=audit.summarize_profile(rows,70);self.assertEqual(d['sampled_maximum_depths_m'],[32]);self.assertEqual(d['valid_velocity_levels'],1)

    def test_no_northward_flow_is_unknown_maximum_not_zero_depth(self):
        d=audit.summarize_profile([row(24,-10),row(32,0)],50)
        self.assertEqual(d['sampled_maximum_depths_m'],[]);self.assertIsNone(d['positive_northward_velocity_max_cm_s'])
        self.assertIsNone(d['deepest_valid_northward_sample_m'])

    def test_depth_gaps_are_preserved_without_interpolation(self):
        d=audit.summarize_profile([row(24,10),row(32,None),row(40,20)],50)
        self.assertEqual(d['valid_sample_depth_gaps_m'],[16]);self.assertTrue(d['maximum_at_deepest_valid_level'])
        with self.assertRaises(ValueError):audit.summarize_profile([row(24,10),row(24,20)],50)

    def test_native_units_required_and_quality_not_silently_coerced(self):
        text='/* metadata */\nDate/Time\tID\tLatitude\tLongitude\tDepth water [m]\tCur vel V [cm/s]\tQuality [%]\n2020-01-12T16:00:57\t1\t-46\t-59\t24.44\t40\t90\n'
        names,groups,count=audit.parse(text.encode());self.assertEqual(count,1);self.assertEqual(len(groups),1)
        with self.assertRaises(ValueError):audit.parse(text.replace('[cm/s]','[m/s]').encode())
        with self.assertRaises(ValueError):audit.parse(text.replace('\t90\n','\t101\n').encode())
        self.assertIsNone(audit.number('NaN'));self.assertIsNone(audit.number('?40'))

    def test_audit_cannot_promote_profile_maxima(self):
        raw=b'/* metadata */\nDate/Time\tID\tLatitude\tLongitude\tDepth water [m]\tCur vel V [cm/s]\tQuality [%]\n2020-01-12T16:00:57\t1\t-46\t-59\t24.44\t40\t90\n'
        d=audit.audit(raw,{'data_url':'example','dataset_doi':'example','quality_pg_scenarios_percent':[50,70,90]})
        self.assertFalse(d['branch_assignment_performed']);self.assertFalse(d['paper_processing_reproduced'])
        self.assertEqual(d['canonical_depth_references_added'],0);self.assertFalse(d['physical_boundary_inference_performed'])


if __name__=='__main__':unittest.main()
