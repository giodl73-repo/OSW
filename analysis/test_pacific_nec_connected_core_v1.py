import unittest
import pacific_nec_connected_core_v1 as core


class ConnectedCore(unittest.TestCase):
    def test_directed_westward_core_and_component(self):
        u=[[-.1]*4,[-.3]*4,[-.1]*4];v=[[0]*4 for _ in u]
        value=core.core_path([10,11,12],[179,180,181,182],u,v)
        self.assertIsNone(value['reason']);self.assertEqual(value['path'],[1]*4)
        labels,groups=core.components(core.eligible(u,v,.025))
        self.assertEqual(len(groups),1);self.assertTrue(groups[0]['touches_west_gate'] and groups[0]['touches_east_gate'])

    def test_eastward_and_missing_barriers_not_bridged(self):
        for missing in (None,.1):
            u=[[-.3,missing,-.3],[-.2,missing,-.2]];v=[[0]*3 for _ in u]
            self.assertEqual(core.core_path([10,11],[130,131,132],u,v)['reason'],'no_directed_connection')

    def test_diagonal_corner_touch_is_not_connection(self):
        u=[[-.3,.1],[.1,-.3]];v=[[0]*2 for _ in u]
        self.assertEqual(core.core_path([10,11],[130,131],u,v,angle=90)['reason'],'no_directed_connection')
        self.assertEqual(len(core.components(core.eligible(u,v,.025))[1]),2)

    def test_score_ties_are_withheld(self):
        u=[[-.2]*3,[-.2]*3];v=[[0]*3 for _ in u]
        result=core.core_path([10,11],[130,131,132],u,v)
        self.assertTrue(result['ambiguous']);self.assertEqual(result['reason'],'ambiguous_score_tie')

    def test_vectors_must_align_at_both_endpoints(self):
        u=[[-.1]*3,[-.1]*3];v=[[10]*3,[-10]*3]
        self.assertEqual(core.core_path([10,11],[130,131,132],u,v,angle=45)['reason'],'no_directed_connection')

    def test_anchor_stays_in_own_component_not_fastest_peak(self):
        lat=list(range(7));u=[.1,-.1,.1,-.9,-.5,.1,.1]
        result=core.anchored_span(lat,u,1)
        self.assertEqual((result['south_latitude'],result['north_latitude']),(.5,1.5))
        self.assertEqual(result['source_cell_interval'],[1,1])

    def test_censored_anchor_span_stays_null(self):
        result=core.anchored_span([8,9,10],[-.1,-.2,-.1],1)
        self.assertEqual(result['reason'],'south_halo_censored;north_halo_censored')
        self.assertIsNone(result['south_latitude']);self.assertIsNone(result['north_latitude'])

    def test_split_and_merge_do_not_become_unique_continuations(self):
        previous=[{'id':0,'cells':set(range(10))}]
        following=[{'id':0,'cells':set(range(5))},{'id':1,'cells':set(range(5,10))}]
        self.assertFalse(any(e['unique_one_to_one'] for e in core.component_links(previous,following)))
        self.assertFalse(any(e['unique_one_to_one'] for e in core.component_links(following,previous)))

    def test_component_and_local_overlap_have_explicit_bounds(self):
        a=[{'id':1,'cells':{1,2,3,4}}];b=[{'id':2,'cells':{3,4,5,6}}]
        self.assertTrue(core.component_links(a,b)[0]['unique_one_to_one'])
        self.assertTrue(core.interval_continuation((8,12),(10,14))['continues'])
        self.assertFalse(core.interval_continuation((8,12),(13,17))['continues'])
        self.assertFalse(core.interval_continuation(None,(13,17))['continues'])


if __name__=='__main__':unittest.main()
