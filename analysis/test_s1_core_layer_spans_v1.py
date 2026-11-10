import copy,unittest
from measure_s1_core_layer_spans_v1 import layer,profiles_from_csv

def profile():
    return {'time_utc':'2023-07-10T00:00:00Z','levels':[{'native_vertical_coordinate_m':z,'provider_u_m_s':u,'provider_v_m_s':0.,'provider_current_qc':1} for z,u in [(-200,.05),(-192,.15),(-184,.3),(-176,.2),(-168,.02)]]}

class LocalSpanSemantics(unittest.TestCase):
    def test_rotation_and_vertical_sign_invariance_without_claiming_a_depth(self):
        p=profile();r=layer(p,.1);rotated=copy.deepcopy(p)
        for row in rotated['levels']:row['provider_v_m_s']=row['provider_u_m_s'];row['provider_u_m_s']=0.;row['native_vertical_coordinate_m']*=-1
        rotated['levels'].sort(key=lambda x:x['native_vertical_coordinate_m'])
        s=layer(rotated,.1)
        self.assertEqual(r['span_m'],16);self.assertEqual(s['span_m'],r['span_m'])
        self.assertIsNone(r['absolute_current_depth_m']);self.assertIsNone(r['physical_current_thickness_m']);self.assertIsNone(r['current_owner']);self.assertIsNone(r['annual_range_m']);self.assertIsNone(r['volume_m3'])

    def test_qc_and_missing_bins_break_connectivity_instead_of_being_bridged(self):
        p=profile();p['levels'][1]['provider_current_qc']=4;r=layer(p,.1)
        self.assertEqual(r['span_m'],8);self.assertEqual(r['numeric_minimum_end_stop'],'QC_OR_MISSING_VELOCITY')
        p=profile();p['levels'][1]['provider_u_m_s']=None;self.assertEqual(layer(p,.1)['span_m'],8)

    def test_missing_large_gap_and_threshold_are_not_zero_depths(self):
        p=profile()
        for r in p['levels']:r['provider_current_qc']=4
        self.assertIsNone(layer(p,.1)['span_m']);self.assertEqual(layer(p,.1)['status'],'NO_GOOD_FINITE_CURRENT_BINS')
        self.assertIsNone(layer(profile(),.4)['span_m'])
        p=profile();p['levels'][0]['native_vertical_coordinate_m']=-300;p['levels'][1]['native_vertical_coordinate_m']=-290
        r=layer(p,.1);self.assertEqual(r['span_m'],8);self.assertEqual(r['numeric_minimum_end_stop'],'VERTICAL_SAMPLING_GAP')

    def test_sample_edge_is_censored_and_counterflow_is_excluded(self):
        p=profile()
        for row in p['levels']:row['provider_u_m_s']=.2
        r=layer(p,.1);self.assertEqual(r['span_m'],32);self.assertTrue(r['sampling_censored_at_either_numeric_end']);self.assertFalse(r['physical_bottom_established'])
        p=profile();p['levels'][1]['provider_u_m_s']=-.15;self.assertEqual(layer(p,.1)['span_m'],8)

    def test_oversized_profile_selection_rejected_before_float_parsing(self):
        header='time,depth,CurrVelE_ADCP,CurrVelN_ADCP,Curr_QC,latitude,longitude\nUTC,m,meters for seconds,meters for seconds,,degrees_north,degrees_east\n'
        rows=''.join(f'2023-07-10T{i:02}:00:00Z,not-a-float,0,0,1,76,13\n' for i in range(151))
        with self.assertRaisesRegex(ValueError,'profile/level bounds before numeric decoding'):profiles_from_csv((header+rows).encode())

if __name__=='__main__':unittest.main()
