import copy
import unittest
import atlantic_nsec_reference_query_v1 as query
import atlantic_nsec_reference_delivery_rules_v1 as rules


class DeliveryTests(unittest.TestCase):
    def fixture(self):
        doc=query.build_contract()
        c={'objects':[copy.deepcopy(doc['prior_owner'])],'entities':[copy.deepcopy(doc['prior_entity'])],
            'route_decisions':[copy.deepcopy(doc['prior_decision'])],'reference_routes':[],
            'sources':copy.deepcopy(doc['prior_owner_sources']),'widths':copy.deepcopy(doc['prior_widths']),
            'length_assessments':copy.deepcopy(doc['prior_length_assessments']),
            'unrelated':[{'id':'retained','nested':{'value':42}}]}
        doc['parent_collection_counts']={name:len(rows) for name,rows in c.items()}
        return c,{'input_sha256':{'prior.json':'a'*64},'unrelated_namespace':{'v':3}},doc

    def apply(self,c,m,doc):return rules.apply_verified(c,m,doc,parent_logical_sha256=query.PARENT,contract_sha256='b'*64)

    def test_atomic_patch_preserves_all_prior_physical_evidence(self):
        c,m,doc=self.fixture();before=copy.deepcopy((c,m));after,manifest=self.apply(c,m,doc)
        self.assertEqual((c,m),before)
        for name in ['widths','length_assessments','entities','unrelated']:self.assertEqual(after[name],c[name])
        self.assertEqual(after['sources'][:len(c['sources'])],c['sources'])
        self.assertEqual(len(after['reference_routes']),2)
        self.assertEqual(manifest['unrelated_namespace'],m['unrelated_namespace'])
        self.assertEqual(manifest[query.KEY]['reported_whole_current_lengths_added'],0)

    def test_changed_parent_or_id_collision_refuses_without_mutation(self):
        for kind in ['width','decision','collision','source_pin','partial_parent','reapplication']:
            c,m,doc=self.fixture()
            if kind=='width':c['widths'][0]['approximate_width_km']=99
            elif kind=='decision':c['route_decisions'][0]['candidate_count']=99
            elif kind=='collision':c['unrelated'][0]['id']=doc['routes'][0]['id']
            elif kind=='source_pin':m['input_sha256'][next(iter(doc['input_sha256']))]='c'*64
            elif kind=='partial_parent':c['entities']=[]
            else:m[query.KEY]={}
            before=copy.deepcopy((c,m))
            with self.assertRaises(ValueError,msg=kind):self.apply(c,m,doc)
            self.assertEqual((c,m),before)


if __name__=='__main__':unittest.main()
