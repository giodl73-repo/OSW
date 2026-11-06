import unittest
from derive_malvinas_branch_core_scenarios_v1 import choose_branches,smooth,summarize_branch,spatial_select


def cell(z,v,q=100):return {'depth':z,'v':v,'quality':q}


class BranchScenarioTests(unittest.TestCase):
    def test_two_peaks_split_at_intervening_minimum(self):
        d=choose_branches([0,10,50,20,5,15,40,10,0],list(range(0,90,10)),30)
        self.assertEqual(d,{'offshore_surface_peak_index':2,'inshore_surface_peak_index':6,'separator_index':4})

    def test_single_peak_and_close_peaks_remain_unknown(self):
        self.assertIsNone(choose_branches([0,10,5,2,1],[0,10,20,30,40],30))
        self.assertIsNone(choose_branches([0,10,0,10,0],[0,1,2,3,4],30))

    def test_smoothing_averages_signed_values_and_rejects_edges(self):
        samples=[[cell(24,v)] for v in [10,10,-10,-10,10,10,10,10,10]]
        profiles=smooth(samples,list(range(9)),50,4,min_count=5)
        self.assertEqual(profiles[0],{});self.assertEqual(profiles[-1],{})
        self.assertEqual(profiles[4][24]['v_cm_s'],2)

    def test_missing_and_low_quality_do_not_become_zeros(self):
        samples=[[cell(24,v,q)] for v,q in [(10,100),(10,100),(100,0),(10,100),(10,100),(10,100),(10,100)]]
        profiles=smooth(samples,list(range(7)),70,4,min_count=5)
        self.assertNotIn(24,profiles[3])

    def test_vertical_gaps_and_unsampled_surface_not_filled(self):
        samples=[[cell(24,20),cell(40,10)] for _ in range(9)]
        profile=smooth(samples,list(range(9)),70,4)[4]
        self.assertEqual(sorted(profile),[24,40]);self.assertNotIn(0,profile);self.assertNotIn(32,profile)

    def test_core_preserves_edge_status_and_unknown_bottom(self):
        profiles=[{24:{'v_cm_s':40,'contributors':5,'possible_ensembles':5},40:{'v_cm_s':30,'contributors':5,'possible_ensembles':5}}]
        d=summarize_branch([0],profiles,[0],[{'lon':-59,'lat':-46,'date':'2020-01-12'}])
        self.assertEqual(d['sampled_maximum_depths_m'],[24]);self.assertTrue(d['maximum_at_shallowest_supported_level'])
        self.assertIsNone(d['flow_bottom_m']);self.assertIsNone(d['physical_thickness_m']);self.assertIsNone(d['uncertainty_m'])

    def test_all_maximum_ties_retained(self):
        p={'v_cm_s':40,'contributors':5,'possible_ensembles':5}
        d=summarize_branch([0],[{24:p,40:p}],[0],[{'lon':-59,'lat':-46,'date':'2020-01-12'}])
        self.assertEqual(d['sampled_maximum_depths_m'],[24,40])

    def test_station_revisits_do_not_gain_spatial_weight(self):
        samples=[[{'lon':lon,'lat':-46,'date':str(i),'depth':24,'v':20,'quality':100}]
                 for i,lon in enumerate([-58,-58.006,-58.005,-58.0061,-58.03,-58.05])]
        selected,positions,metadata,review=spatial_select(samples)
        self.assertLess(review['occupied_1km_cells'],len(samples))
        self.assertEqual(review['eastward_steps'],1)
        self.assertTrue(any(not group for group in selected))
        self.assertEqual(len(selected),len(positions))

    def test_empty_spatial_center_cannot_become_synthetic_maximum(self):
        samples=[[cell(24,20)] for _ in range(9)];samples[4]=[]
        self.assertEqual(smooth(samples,list(range(9)),70,4)[4],{})


if __name__=='__main__':unittest.main()
