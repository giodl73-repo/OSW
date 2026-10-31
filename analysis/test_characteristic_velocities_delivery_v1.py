import copy,unittest
import characteristic_velocities_query_v1 as query
import characteristic_velocities_delivery_rules_v1 as rules

class DeliveryTests(unittest.TestCase):
    def setUp(self):self.contract=query.build_contract()
    def test_existing_core_operator_stays_separate(self):
        prior={'atlantic-north-equatorial-countercurrent':{'kind':'published_seasonal_core_velocities','records':[{'id':'prior-fit','value':.2}]}}
        before=copy.deepcopy(prior);after=rules.speed_scenes(prior,self.contract)
        self.assertEqual(prior,before);self.assertEqual(after['atlantic-north-equatorial-countercurrent']['scenes'][0],before['atlantic-north-equatorial-countercurrent'])
        self.assertEqual(after['atlantic-north-equatorial-countercurrent']['scenes'][1]['kind'],'published_characteristic_current_velocities')
        self.assertEqual(len(after['atlantic-south-equatorial']['records']),3)
        self.assertNotIn('north-equatorial',after)
    def test_paginated_rows_and_full_matching_scientific_context(self):
        request={'collection':query.COLLECTION,'filters':[{'field':'current_id','op':'eq','value':'atlantic-south-equatorial'}],'limit':1,'offset':1}
        value=rules.expected_new_query(request,self.contract)
        self.assertEqual(value['total'],3);self.assertEqual(len(value['rows']),1);self.assertEqual(len(value['chart_scene']['records']),3);self.assertIsNone(value['map_scene'])
        request['filters'][0]['value']='north-equatorial';value=rules.expected_new_query(request,self.contract)
        self.assertEqual(value['total'],0);self.assertIsNone(value['chart_scene'])
    def test_dashboard_projection_preserves_families_and_old_counts(self):
        entries=[copy.deepcopy(v['objects'][0]) for v in self.contract['prior_owners'].values()]
        old={'entries':entries,'snapshot_fingerprint':'parent'};result=rules.dashboard_document(old,self.contract)
        self.assertEqual(sum(r['capabilities'].get('characteristic_velocity',0) for r in result['entries']),10)
        for family in query.FAMILIES:self.assertEqual([r for r in result['entries'] if r['id']==family],[r for r in entries if r['id']==family])
        for prior,final in zip(entries,result['entries']):self.assertEqual(final['capabilities'].get('scoped_width'),prior['capabilities'].get('scoped_width'))
    def test_complete_extension_rejects_changed_older_measurement(self):
        doc=copy.deepcopy(self.contract);rows={n:[] for n in doc['parent_collection_counts']};rows['sources']=copy.deepcopy(doc['prior_source_inventory'])
        for v in doc['prior_owners'].values():
            for name in ('objects','entities','widths'):rows[name].extend(copy.deepcopy(v[name]))
        rows['current_speed_statistics']=[{'id':'pooled','mean':.83}];doc['parent_collection_counts']={n:len(v) for n,v in rows.items()}
        parent={'schema':'osw.query-bundle.v1','collections':rows,'manifest':{'input_sha256':{}}}
        collections,manifest=query.apply_verified(rows,parent['manifest'],doc,parent_logical_sha256=query.PARENT,contract_sha256=query.digest(doc))
        child={'schema':parent['schema'],'collections':collections,'manifest':manifest};rules.verify_extension(parent,child,doc)
        child=copy.deepcopy(child);child['collections']['current_speed_statistics'][0]['mean']=99
        with self.assertRaises(ValueError):rules.verify_extension(parent,child,doc)

if __name__=='__main__':unittest.main()
