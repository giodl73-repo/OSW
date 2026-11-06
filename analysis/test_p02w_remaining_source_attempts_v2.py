import copy,unittest
from complete_p02w_remaining_source_attempts_v2 import remaining


class RemainingSourceChecks(unittest.TestCase):
    def fixture(self):
        targets=[{'cast_id':s,'url':'https://example.invalid/'+s+'.nc'} for s in ['00601','00701','00801']]
        prior={'case_operation_cap':3,'case_response_byte_cap':600000,'case_time_cap_seconds':180,
            'operations':[{'url':targets[0]['url'],'status':'failed_or_interrupted_no_retry'}]}
        return prior,targets
    def test_failed00601_never_selected_again(self):
        prior,targets=self.fixture()
        self.assertEqual([r['cast_id'] for r in remaining(prior,targets)],['00701','00801'])
        prior['operations'].append({'url':targets[1]['url'],'status':'failed_once'})
        self.assertEqual([r['cast_id'] for r in remaining(prior,targets)],['00801'])
    def test_duplicate_or_changed_case_cannot_create_fresh_allowance(self):
        prior,targets=self.fixture();prior['operations']*=2
        with self.assertRaises(ValueError):remaining(prior,targets)
        prior,targets=self.fixture();prior['case_operation_cap']=4
        with self.assertRaises(ValueError):remaining(prior,targets)
    def test_all_attempted_means_no_more_source_requests(self):
        prior,targets=self.fixture();prior['operations']=[{'url':r['url']} for r in targets]
        self.assertEqual(remaining(prior,targets),[])


if __name__=='__main__':unittest.main()
