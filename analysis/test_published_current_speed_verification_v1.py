import unittest
from unittest.mock import patch
import check_published_current_speeds_v1 as v


class VerificationTests(unittest.TestCase):
    def test_local_execution_refused_before_packet_access(self):
        with patch.dict(v.os.environ, {'GITHUB_ACTIONS':'false'}):
            with self.assertRaisesRegex(ValueError, 'Exact cloud'):
                v.controls()

    def test_verifier_rejects_bad_published_statistic_and_truncated_scene(self):
        case={'name':'one','expected_total':1,'expected_median':1.13,'expected_scene_records':1}
        response={'ok':True,'total':1,'rows':[{'median':1.13}],'chart_scene':{'records':[{}]}}
        v.verify_case(case,response)
        response['rows'][0]['median']=1.1
        with self.assertRaisesRegex(ValueError,'statistic'):
            v.verify_case(case,response)
        response['rows'][0]['median']=1.13
        response['chart_scene']['records']=[]
        with self.assertRaisesRegex(ValueError,'support'):
            v.verify_case(case,response)

    def test_verifier_rejects_chart_routed_to_map_output(self):
        case={'name':'dispatch','expected_total':1,'expected_scene_kind':'published_current_speed_statistics'}
        response={'ok':True,'total':1,'rows':[{}],'chart_scene':None,'map_scene':{'kind':'published_current_speed_statistics'}}
        with self.assertRaisesRegex(ValueError,'map geometry'):
            v.verify_case(case,response)
        response['map_scene']=None
        with self.assertRaisesRegex(ValueError,'dispatch missing'):
            v.verify_case(case,response)


if __name__=='__main__':unittest.main()
