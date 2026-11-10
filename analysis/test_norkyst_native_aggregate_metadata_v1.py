import copy
import json
import unittest
import probe_norkyst_native_aggregate_metadata_v1 as m


class AggregateMetadata(unittest.TestCase):
    def setUp(self):
        self.discovery=json.loads((m.ROOT/m.FOLDER/'discovery.json').read_bytes())
        self.root=(m.ROOT/m.FOLDER/'catalogue-01.xml').read_bytes()

    def test_observed_aggregate_uses_one_remaining_request(self):
        p=m.plan(self.discovery,self.root)
        self.assertTrue(p['url'].endswith('/norkyst_v3_sdepth_aggr.ncml.dds'))
        self.assertEqual(p['prior_requests']+p['new_requests_reserved'],p['cumulative_request_cap'])
        self.assertNotIn(p['url'],[r['url'] for r in self.discovery['transport_receipts']])

    def test_missing_observed_dataset_is_not_guessed(self):
        with self.assertRaises(ValueError):m.plan(self.discovery,self.root.replace(b'norkyst_v3_sdepth_aggr.ncml',b'different.ncml'))

    def test_spent_budget_or_field_reads_refused(self):
        for key,value in [('requests_attempted',6),('ocean_field_requests',1)]:
            d=copy.deepcopy(self.discovery);d[key]=value
            with self.assertRaises(ValueError):m.plan(d,self.root)

    def test_no_prior_success_or_failure_replay(self):
        d=copy.deepcopy(self.discovery);d['transport_receipts'][0]['url']=m.plan(d,self.root)['url']
        with self.assertRaises(ValueError):m.plan(d,self.root)


if __name__=='__main__':unittest.main()
