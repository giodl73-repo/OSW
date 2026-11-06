import copy,unittest
from current_depth_cast_time_view_v29 import corrected,corrections,REMOVE,prior


class CastTimeChecks(unittest.TestCase):
    def fixture(self):
        return {'evidence':[{'id':i,'metric':prior.METRIC,REMOVE:True,'source_cast_datetime_utc':'2021-03-23T16:51:25',
            'approximate_value_m':1790,'source_computed_depth_before_display_rounding_m':1793.38,'source_native_bracketing_depths_m':[1792,1800],
            'temporal_scope':'old'} for i in corrections()['reference_ids']]+[{'id':'unrelated','value':123}],
            'counts':{'depth_references':869,'whole_route_depth_profiles':0,'volume_estimates':0}}

    def test_cast_duration_replaces_instantaneous_claim_without_depth_changes(self):
        old=self.fixture();out=corrected(old,corrections())
        self.assertEqual(old['counts'],out['counts']);self.assertEqual(out['evidence'][-1],old['evidence'][-1])
        for a,b in zip(old['evidence'][:-1],out['evidence'][:-1]):
            self.assertNotIn(REMOVE,b);self.assertIn('finite cast duration',b['temporal_scope'])
            self.assertTrue(b['metric_frame_is_cast_specific_not_climatology']);self.assertFalse(b['source_frame_is_mathematical_instant'])
            for k in ['approximate_value_m','source_computed_depth_before_display_rounding_m','source_native_bracketing_depths_m']:
                self.assertEqual(a[k],b[k])
            self.assertIn(REMOVE,a)

    def test_scope_cannot_expand_or_change_scientific_fields(self):
        c=corrections();c['set_fields']['approximate_value_m']=9999
        with self.assertRaises(ValueError):corrected(self.fixture(),c)
        c=corrections();c['reference_ids'].append('unrelated')
        with self.assertRaises(ValueError):corrected(self.fixture(),c)

    def test_missing_target_and_wrong_metric_fail_closed(self):
        old=self.fixture();old['evidence'].pop(0)
        with self.assertRaises(ValueError):corrected(old,corrections())
        old=self.fixture();old['evidence'][0]['metric']='core_depth'
        with self.assertRaises(ValueError):corrected(old,corrections())


if __name__=='__main__':unittest.main()
