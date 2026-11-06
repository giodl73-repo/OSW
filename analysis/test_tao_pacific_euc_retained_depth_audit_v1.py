import copy
import unittest
import audit_tao_pacific_euc_retained_depth_v1 as audit
import test_tao_pacific_euc_daily_depth_v1 as fixtures


class IndependentBoundaryAudit(unittest.TestCase):
    def profile(self):return audit.source.frozen.profiles(fixtures.field_bytes(),fixtures.target())[0][0]

    def test_agrees_for_measured_proxy_but_not_corrupted_boundary(self):
        p=self.profile();audit.verify_profile(p)
        p['threshold_contexts'][1]['lower_depth_m']+=1
        with self.assertRaises(ValueError):audit.verify_profile(p)

    def test_missing_and_depth_gaps_are_independent_censors(self):
        z=[40,50,60,70,80,90,100,110,120];u=[0,0,.2,.5,1,.5,None,0,0]
        self.assertIsNone(audit.independent(z,u,.1)['lower'])
        self.assertIsNone(audit.independent([40,50,60,70,80,120],[0,0,.2,.5,1,0],.1)['lower'])

    def test_quality_and_unit_substitution_rejected(self):
        for key,value in [('accepted_eastward_velocity_m_s',100),('source_u_quality',3)]:
            p=self.profile();p[key][6]=value
            with self.assertRaises(ValueError):audit.verify_profile(p)

    def test_proxy_never_becomes_thickness_or_complete_time_coverage(self):
        for key,value in [('physical_current_thickness_m',70),('annual_range_m',[50,130]),('daily_underlying_sample_coverage_verified',True),('mean_field_depth_is_mean_instantaneous_depth',True)]:
            p=self.profile();p[key]=value
            with self.assertRaises(ValueError):audit.verify_profile(p)

    def test_retained_audit_network_tripwire(self):
        with self.assertRaises(RuntimeError):audit.no_network('https://example.invalid/')


if __name__=='__main__':unittest.main()
