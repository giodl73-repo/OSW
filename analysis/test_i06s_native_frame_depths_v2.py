import math,unittest
from sample_i06s_native_frame_depths_v2 import native_frame
from sample_a20_gulf_stream_core_direction_depths_v2 import sample_aligned
from sample_a20_gulf_stream_depth_brackets_v1 import coarse_indices

class NativeBasisChecks(unittest.TestCase):
    def test_projection_does_not_depend_on_common_basis_rotation(self):
        for angle in [0,.7,2.4]:
            c,s=math.cos(angle),math.sin(angle)
            samples=[{'native_index':0,'depth_m':100,'u_m_s':.3*c-.4*s,'v_m_s':.3*s+.4*c}]
            f=native_frame(samples,[0]);u,v=.12*c-.16*s,.12*s+.16*c
            self.assertAlmostEqual(u*f['native_uv_unit_vector'][0]+v*f['native_uv_unit_vector'][1],.2)
            self.assertFalse(f['independent_geographic_direction_or_current_axis_verified'])

    def test_missing_reference_does_not_create_direction(self):
        f=native_frame([{'native_index':0,'depth_m':100,'u_m_s':None,'v_m_s':1}],[0])
        self.assertFalse(f['qualified']);self.assertIsNone(f['native_uv_unit_vector'])

    def test_missing_sample_retains_censoring(self):
        z=list(range(0,1001,10));initial=coarse_indices(z)
        def point(i):return {'u_m_s':.4 if z[i]<200 else None,'v_m_s':0.,'uerr_m_s':.1}
        inherited=[{'native_index':i,'depth_m':z[i],**point(i)} for i in initial]
        report=sample_aligned(z,inherited,point,[1.,0.])
        for case in report['threshold_cases']:
            self.assertIsNone(case['lower_depth_m'])
            self.assertFalse(case['physical_current_bottom_established'])

    def test_local_crossing_preserves_alias_and_bottom_caveats(self):
        z=list(range(0,1001,10));initial=coarse_indices(z)
        def point(i):return {'u_m_s':.4-.0004*z[i],'v_m_s':0.,'uerr_m_s':.1}
        inherited=[{'native_index':i,'depth_m':z[i],**point(i)} for i in initial]
        report=sample_aligned(z,inherited,point,[1.,0.])
        self.assertLessEqual(report['selected_native_levels'],40)
        for case in report['threshold_cases']:
            self.assertIsNotNone(case['lower_depth_m'])
            self.assertFalse(case['local_crossing_is_first_crossing_of_entire_native_profile'])
            self.assertFalse(case['volume_eligible'])

if __name__=='__main__':unittest.main()
