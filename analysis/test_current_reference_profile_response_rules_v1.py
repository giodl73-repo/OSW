import copy
import unittest
import current_reference_profile_batch_query_v1 as query
import current_reference_profile_response_rules_v1 as rules
import test_current_reference_profile_batch_query_v1 as fixtures


class CompletePreservation(unittest.TestCase):
    def test_independent_packet_expectations_refuse_changed_old_measurement(self):
        collections,manifest,c=fixtures.BatchContract().fixture()
        after,m=query.apply_verified(collections,manifest,c,parent_logical_sha256=query.PARENT,contract_sha256=query.sha(query.FILE))
        parent={'schema':'synthetic-test-packet','collections':collections,'manifest':manifest}
        child={**parent,'collections':after,'manifest':m}
        self.assertEqual(rules.verify_extension(parent,child,c)['existing_measurement_rows_changed'],0)
        child=copy.deepcopy(child);child['collections']['widths'][0]['changed']=True
        with self.assertRaises(ValueError):rules.verify_extension(parent,child,c)

    def test_filtered_zero_touching_profile_and_empty_page_keep_distinct_scopes(self):
        c=query.read(query.FILE)
        request={'collection':query.COLLECTION,'filters':[{'field':'section_longitude_degrees_east','op':'eq','value':-160},{'field':'sampling_depth_m','op':'eq','value':500}],'limit':1}
        response=rules.expected_profile_query(request,c)
        self.assertEqual(response['total'],1);self.assertIsNone(response['map_scene'])
        self.assertTrue(response['rows'][0]['interval_includes_zero'])
        page=rules.expected_profile_query({**request,'offset':1},c)
        self.assertEqual(page['rows'],[])
        self.assertEqual(len(page['chart_scene']['records']),1,'chart scope is full matching set, separate from table pagination')
        empty=rules.expected_profile_query({**request,'filters':[{'field':'sampling_depth_m','op':'gt','value':600}]},c)
        self.assertEqual(empty['total'],0);self.assertIsNone(empty['chart_scene'])
        family=rules.expected_profile_query({**request,'filters':[{'field':'entity_id','op':'eq','value':'current:south-equatorial'}]},c)
        self.assertEqual(family['total'],0)


if __name__=='__main__':unittest.main()
