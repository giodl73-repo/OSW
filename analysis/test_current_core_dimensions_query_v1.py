import copy
import unittest
import current_core_dimensions_query_v1 as query
import current_core_dimensions_delivery_rules_v1 as rules

class ContractTests(unittest.TestCase):
    def fixture(self):
        doc=query.build_contract();rows={name:[] for name in doc['parent_collection_counts']}
        rows['sources']=copy.deepcopy(doc['prior_source_inventory'])
        for prior in doc['prior_owners'].values():
            for name in ['objects','entities','widths',query.REACHES]:rows[name]+=copy.deepcopy(prior[name])
        rows['objects'].append({'id':'current:south-equatorial','capabilities':{'scoped_width':0},'published_length_km':None})
        rows['claims']=[{'id':'unrelated','value':130}]
        doc['parent_collection_counts']={n:len(v) for n,v in rows.items()};return doc,rows

    def test_additive_records_owner_fingerprints_and_family_preservation(self):
        doc,rows=self.fixture();before=copy.deepcopy(rows);parent={'collections':rows,'manifest':{'input_sha256':{}},'schema':'fixture'}
        collections,manifest=query.apply_verified(rows,parent['manifest'],doc,parent_logical_sha256=query.PARENT,contract_sha256=query.digest(doc))
        report=rules.verify_extension(parent,{**parent,'collections':collections,'manifest':manifest},doc)
        self.assertEqual(rows,before);self.assertEqual(collections['objects'][-1],before['objects'][-1]);self.assertEqual(report['existing_measurement_rows_changed'],0)
        self.assertEqual(len(collections[query.REACHES]),1);self.assertEqual(len(collections['widths']),1)
        self.assertEqual(collections['objects'][0]['capabilities']['reported_length'],0)
        self.assertEqual(collections['objects'][0]['capabilities']['reported_regional_reaches'],1)

    def test_parent_collision_prior_width_and_immutable_pin_refusals(self):
        for case in range(4):
            doc,rows=self.fixture();parent=query.PARENT;manifest={'input_sha256':{}}
            if case==0:parent='0'*64
            elif case==1:rows['claims'][0]['id']=doc['reach_records'][0]['id']
            elif case==2:rows['widths'].append({'id':'surprise','entity_id':query.OWNERS[1]});doc['parent_collection_counts']['widths']+=1
            else:manifest['input_sha256'][query.FILE]='bad'
            with self.assertRaises(ValueError):query.apply_verified(rows,manifest,doc,parent_logical_sha256=parent,contract_sha256=query.digest(doc))

    def test_pagination_keeps_matching_scene_and_empty_family_stays_empty(self):
        doc,rows=self.fixture();request={'collection':query.REACHES,'filters':[{'field':'current_id','op':'eq','value':'red-sea-saline-overflow'}],'limit':1,'offset':1}
        old={'total':0,'rows':[],'chart_scene':None};value=rules.expected_query(request,old,doc,rows)
        self.assertEqual(value['total'],1);self.assertEqual(value['rows'],[]);self.assertEqual(len(value['chart_scene']['length_records']),1)
        request['collection']='widths';request['filters'][0]['value']='south-equatorial'
        self.assertEqual(rules.expected_query(request,old,doc,rows),old)

    def test_complete_frozen_contract_and_source_classes(self):
        doc=query.build_contract();self.assertEqual(query.encoded(doc),(query.ROOT/query.FILE).read_bytes())
        self.assertIsNone(doc['reach_records'][0]['annual_length_range_km']);self.assertIsNone(doc['width_records'][0]['independent_observation_count'])
        scene=rules.owner_scene(query.OWNERS[1],doc);self.assertEqual(scene['width_records'][0]['source_evidence_kind'],'cruise_report_citing_earlier_width_literature')
        self.assertEqual(scene['length_records'],[])

if __name__=='__main__':unittest.main()
