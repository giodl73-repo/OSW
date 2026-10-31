import copy,unittest
from unittest.mock import patch
import atlantic_nec_band_spans_query_v1 as query

class AdmissionTests(unittest.TestCase):
    def fixture(self):
        doc=query.build_contract();rows={n:[] for n in doc['parent_collection_counts']}
        rows['sources']=copy.deepcopy(doc['prior_source_inventory'])
        for owner,prior in doc['prior_owners'].items():
            for name in ('objects','entities','widths'):rows[name].extend(copy.deepcopy(prior[name]))
        rows['claims']=[{'id':'unrelated-science','value':123}]
        doc['parent_collection_counts']={n:len(r) for n,r in rows.items()}
        return doc,rows
    def test_additive_scope_and_family_preservation(self):
        doc,rows=self.fixture();before=copy.deepcopy(rows);manifest={'input_sha256':{},'unchanged':{'a':1}}
        after,updated=query.apply_verified(rows,manifest,doc,parent_logical_sha256=query.PARENT,contract_sha256=query.digest(doc))
        self.assertEqual(rows,before);self.assertEqual(manifest,{'input_sha256':{},'unchanged':{'a':1}})
        for name in rows:
            if name not in ('widths','sources','objects'):self.assertEqual(after[name],rows[name])
        self.assertEqual(len(after['widths']),2);self.assertEqual(len(after['sources']),len(rows['sources'])+1)
        self.assertEqual([r for r in after['objects'] if r['id']==query.FAMILY],[r for r in rows['objects'] if r['id']==query.FAMILY])
    def test_moved_parent_changed_identity_and_colliding_id_refused(self):
        for case in range(3):
            doc,rows=self.fixture();parent=query.PARENT
            if case==0:parent='0'*64
            elif case==1:rows['objects'][0]['fingerprint']='changed'
            else:rows['claims'][0]['id']=doc['width_records'][0]['id']
            with self.assertRaises(ValueError):query.apply_verified(rows,{},doc,parent_logical_sha256=parent,contract_sha256=query.digest(doc))
    def test_source_scope_cannot_become_annual_or_fixed_edge_width(self):
        original=query.read
        for field,value in [('annual_width_range_km',[664,700]),('boundary_rule','zero crossing'),('seasonal_playback_eligible',True)]:
            def changed(path):
                v=original(path)
                if path==query.PREPARED:v['width_records'][0][field]=value
                return v
            with patch.object(query,'read',side_effect=changed),self.assertRaises(ValueError):query.build_contract()
    def test_exact_frozen_contract(self):
        self.assertEqual(query.encoded(query.build_contract()),(query.ROOT/query.FILE).read_bytes())

if __name__=='__main__':unittest.main()
