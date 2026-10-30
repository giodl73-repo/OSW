import copy
import unittest
import current_reference_profile_batch_query_v1 as query


class BatchContract(unittest.TestCase):
    def fixture(self):
        # Explicitly synthetic small parent: never read a runtime packet/index.
        contract=query.build_contract();collections={k:[] for k in ['objects','entities','widths','length_assessments','reference_routes','route_decisions','sources','unrelated']}
        for owner,prior in contract['prior_owners'].items():
            for name in ['objects','entities','widths','length_assessments','reference_routes']:collections[name]+=copy.deepcopy(prior[name])
        collections['route_decisions']=[copy.deepcopy(contract['prior_decision'])]
        collections['sources']=copy.deepcopy(contract['prior_source_inventory']+[contract['prior_publication']])
        collections['unrelated']=[{'id':'synthetic-unchanged-row','nested':{'value':17}}]
        contract['parent_collection_counts']={k:len(v) for k,v in collections.items()}
        return collections,{'input_sha256':{}},contract

    def apply(self,collections,manifest,contract):
        return query.apply_verified(collections,manifest,contract,parent_logical_sha256=query.PARENT,contract_sha256='a'*64)

    def test_complete_source_contract_and_distinct_quantities(self):
        c=query.build_contract();self.assertEqual(sum(c['parent_collection_counts'].values()),110328)
        self.assertEqual((len(c['routes']),len(c['records']),len(c['new_sources'])),(2,24,3))
        self.assertEqual(len({r['id'] for r in c['records']}),24)
        self.assertNotIn(c['prior_publication']['id'],[r['id'] for r in c['new_sources']])
        self.assertTrue(all(r['geometry'] is None and r['uncertainty_degrees'] is None and not r['annual_extrema_eligible'] for r in c['records']))

    def test_atomic_addition_preserves_other_rows_and_caller_data(self):
        collections,manifest,c=self.fixture();original=copy.deepcopy((collections,manifest))
        after,m=self.apply(collections,manifest,c)
        self.assertEqual((collections,manifest),original)
        self.assertEqual(after['unrelated'],collections['unrelated'])
        self.assertEqual(after['widths'],collections['widths'])
        self.assertEqual(len(after[query.COLLECTION]),24)
        self.assertEqual(len(after['sources']),len(collections['sources'])+3)
        self.assertEqual(m[query.KEY]['whole_current_lengths_added'],0)
        with self.assertRaises(ValueError):self.apply(after,m,c)

    def test_prior_dimension_source_or_identifier_collisions_refused(self):
        for mode in ['width','publication','collision']:
            collections,m,c=self.fixture()
            if mode=='width':collections['widths'][0]['changed']=True
            elif mode=='publication':collections['sources'][-1]['title']='changed'
            else:collections['unrelated'].append({'id':c['records'][0]['id']})
            with self.assertRaises(ValueError):self.apply(collections,m,c)

    def test_modified_contract_cannot_pass_frozen_admission(self):
        c=query.build_contract();c['records'][0]['annual_extrema_eligible']=True
        with self.assertRaisesRegex(ValueError,'frozen'):query.prepare({}, {},c,parent_logical_sha256=query.PARENT)


if __name__=='__main__':unittest.main()
