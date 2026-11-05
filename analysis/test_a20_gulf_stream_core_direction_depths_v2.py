import json
import unittest
from sample_a20_gulf_stream_core_direction_depths_v2 import sample_aligned, fixed_frame, build, ROOT, SOURCE
from sample_a20_gulf_stream_depth_brackets_v1 import coarse_indices


class FixedDirectionChecks(unittest.TestCase):
    def fixture(self, direction):
        z=[float(i*8) for i in range(801)]
        def point(i):
            speed=.8-z[i]/2000
            return {'native_index':i,'depth_m':z[i],'u_m_s':direction[0]*speed,'v_m_s':direction[1]*speed,'uerr_m_s':.02}
        inherited=[point(i) for i in coarse_indices(z)]
        return z,point,inherited

    def test_northward_jet_is_not_lost_by_eastward_only_cutoff(self):
        z,point,inherited=self.fixture([0.,1.])
        r=sample_aligned(z,inherited,lambda i:{k:v for k,v in point(i).items() if k in ['u_m_s','v_m_s','uerr_m_s']},[0.,1.])
        for c in r['threshold_cases']:
            self.assertAlmostEqual(c['lower_depth_m'],(.8-c['threshold_m_s'])*2000)
            self.assertFalse(c['first_native_downcrossing_below_core_verified'])
        self.assertTrue(all(p['u_m_s']==0 for p in r['selected_native_samples']))

    def test_oblique_rotation_preserves_native_components_and_fixed_metric(self):
        z,point,inherited=self.fixture([.6,.8])
        r=sample_aligned(z,inherited,lambda i:{k:v for k,v in point(i).items() if k in ['u_m_s','v_m_s','uerr_m_s']},[.6,.8])
        for p in r['selected_native_samples']:
            original=point(p['native_index'])
            self.assertEqual(p['u_m_s'],original['u_m_s']);self.assertEqual(p['v_m_s'],original['v_m_s'])
            self.assertAlmostEqual(p['aligned_component_m_s'],.6*p['u_m_s']+.8*p['v_m_s'])

    def test_inherited40levels_leave_no_new_native_reads(self):
        z,point,inherited=self.fixture([1.,0.]);indices={p['native_index'] for p in inherited}
        for i in range(len(z)):
            if len(indices)==40:break
            indices.add(i)
        inherited=[point(i) for i in sorted(indices)]
        r=sample_aligned(z,inherited,lambda i:self.fail('Cumulative40level budget must prevent read'),[1.,0.])
        self.assertEqual(r['selected_native_levels'],40)
        self.assertTrue(all(c['lower_depth_m'] is None for c in r['threshold_cases']))

    def test_missing_or_weak_fixed100m_reference_has_no_direction_fallback(self):
        z,point,inherited=self.fixture([1.,0.]);profile={'selected_native_samples':inherited,'coarse_native_indices':coarse_indices(z)}
        reference=min(inherited,key=lambda p:(abs(p['depth_m']-100),p['native_index']))
        reference['u_m_s']=None
        self.assertFalse(fixed_frame(profile)['qualified'])
        reference['u_m_s']=.01;reference['v_m_s']=.01
        self.assertFalse(fixed_frame(profile)['qualified'])

    def test_nonunit_and_missing_component_direction_rejected(self):
        z,point,inherited=self.fixture([1.,0.])
        with self.assertRaises(ValueError):sample_aligned(z,inherited,point,[1.,1.])
        with self.assertRaises(ValueError):sample_aligned(z,inherited,point,[None,1.])

    def test_actual_same_three_casts_keep_original_samples_and_resource_ledgers(self):
        old=json.loads((ROOT/SOURCE).read_bytes());r=build() # One actual build only.
        self.assertEqual(r['counts']['source_cast_profiles'],3)
        self.assertEqual(r['counts']['new_independent_cast_profiles'],0)
        self.assertLessEqual(r['counts']['case_metadata_touch_bound'],10000)
        self.assertLessEqual(r['counts']['case_scalar_bound_including_prior_phases_one_actual_test_and_producer'],250000)
        for a,b in zip(old['profiles'],r['profiles']):
            old_samples={p['native_index']:p for p in a['selected_native_samples']}
            new_samples={p['native_index']:p for p in b['selected_native_samples']}
            self.assertTrue(set(old_samples)<=set(new_samples));self.assertLessEqual(len(new_samples),40)
            for i,p in old_samples.items():
                for k,v in p.items():self.assertEqual(new_samples[i][k],v)
            self.assertFalse(b['fixed_reference_frame']['reference_direction_is_independently_validated_current_axis'])
        self.assertFalse(r['first_native_crossing_verified']);self.assertFalse(r['whole_route_physical_depth_profile_established'])


if __name__=='__main__':unittest.main()
