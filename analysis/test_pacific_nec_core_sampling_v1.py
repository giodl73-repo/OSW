import unittest
import pacific_nec_connected_core_v1 as native
import pacific_nec_core_sampling_v1 as sampling


class CoreSampling(unittest.TestCase):
    def test_all_phases_preserve_endpoints_without_duplicates(self):
        for size in (2,8,31,331):
            for stride in (1,2,4):
                for phase in range(stride):
                    selected=sampling.indices(size,stride,phase)
                    self.assertEqual(selected,sorted(set(selected)))
                    self.assertEqual((selected[0],selected[-1]),(0,size-1))

    def test_native_grid_reproduces_original_core(self):
        lat=[10,11,12];lon=[179,180,181,182];u=[[-.1]*4,[-.3]*4,[-.1]*4];v=[[0]*4 for _ in u]
        old=native.core_path(lat,lon,u,v);new=sampling.anchored_path(lat,lon,u,v,list(range(4)),list(range(3)))
        self.assertEqual(new['path'],old['path']);self.assertEqual(new['reason'],old['reason'])

    def test_coarse_leg_cannot_skip_missing_or_eastward_column(self):
        for blocked in (None,.1):
            u=[[-.2,blocked,-.2,-.2],[-.1,blocked,-.1,-.1]];v=[[0]*4 for _ in u]
            self.assertIsNone(sampling.corridor_path([10,11],[130,131,132,133],u,v,0,0,3,0))

    def test_native_witness_not_just_endpoint_vector_check(self):
        u=[[-.2]*4,[-.1]*4];v=[[0,10,0,0],[0,10,0,0]]
        self.assertIsNone(sampling.corridor_path([10,11],[130,131,132,133],u,v,0,0,3,0))

    def test_coarse_score_retains_all_native_step_units(self):
        u=[[-.2]*5,[-.1]*5];v=[[0]*5 for _ in u]
        result=sampling.corridor_path([10,11],list(range(130,135)),u,v,0,0,4,0)
        self.assertAlmostEqual(result['score'],.8)
        self.assertEqual(result['path'],[0]*5)

    def test_tied_routes_are_not_arbitrarily_admitted(self):
        u=[[-.2]*5,[-.2]*5];v=[[0]*5 for _ in u]
        result=sampling.anchored_path([10,11],list(range(130,135)),u,v,[0,4],[0,1])
        self.assertEqual(result['reason'],'ambiguous_score_tie')

    def test_vertex_thinning_is_geometry_only(self):
        path=[0,1,0];lat=[10,11];lon=[130,131,132]
        distance=lambda a,b,c,d:((c-a)**2+(d-b)**2)**.5
        full=sampling.length(lon,lat,path,distance)
        thin=sampling.length(lon,lat,path,distance,[0,2])
        self.assertGreater(full,thin);self.assertEqual(path,[0,1,0])


if __name__=='__main__':unittest.main()
