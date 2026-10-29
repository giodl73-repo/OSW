import copy
import unittest
import pacific_nec_product_axis_delivery_contract_v1 as rules

class CompleteAdditiveExpectations(unittest.TestCase):
    def contract(self):
        collections={'current_axis_series':[{'id':'series:a'}],'current_axis_readings':[{'id':'reading:a','series_id':'series:a'}],'current_axis_scenarios':[{'id':'scenario:a','series_id':'series:a','length_km':None}],'current_axis_section_spans':[]}
        return {'namespace':'diagnostic_namespace','parent_logical_sha256':'parent','input_sha256':{},'counts_added':{k:len(v) for k,v in collections.items()},'collections_added':collections,'new_sources':[{'id':'source:new'}]}
    def test_unrelated_query_values_are_preserved_recursively(self):
        parent={'ok':True,'rows':[{'nested':{'unknown':None,'false':False}}],'map_scene':{'features':[1,2]},'chart_scene':None}
        result=rules.expected_query({'collection':'widths'},parent,self.contract(),[])
        self.assertEqual(result,parent);result['rows'][0]['nested']['false']=0;self.assertIs(parent['rows'][0]['nested']['false'],False)
    def test_complete_object_sources_are_additive_and_family_has_no_member_scene(self):
        for owner in [rules.OWNER,'current:north-equatorial','current:indian-south-equatorial']:
            parent={'ok':True,'id':owner,'collections':{'sources':[{'id':'old'}],'widths':[{'width':100}]},'bundle_sha256':'parent','unknown':{'retained':True}}
            result=rules.expected_object(owner,parent,self.contract(),'child')
            self.assertEqual(result['collections']['widths'],parent['collections']['widths']);self.assertEqual(result['collections']['sources'],[{'id':'old'},{'id':'source:new'}]);self.assertEqual('surface_product_axis_scene' in result,owner==rules.OWNER)
    def test_source_pagination_reorders_only_new_sources_and_rejects_a_forged_parent(self):
        contract=self.contract();contract['new_sources']=[{'id':'b'}];old=[{'id':'a'},{'id':'c'}]
        request={'collection':'sources','limit':1,'offset':1};parent={'ok':True,'total':2,'rows':[{'id':'c'}],'map_scene':None}
        result=rules.expected_query(request,parent,contract,old);self.assertEqual(result['rows'],[{'id':'b'}]);self.assertEqual(result['total'],3)
        parent['rows']=[]
        with self.assertRaises(ValueError):rules.expected_query(request,parent,contract,old)
    def test_only_matching_native_readings_can_supply_map_scene_paths(self):
        c=self.contract()
        for name in ['current_axis_scenarios','current_axis_section_spans']:
            self.assertEqual(rules.query_scene(name,c['collections_added'][name],c)['readings'],[])
        self.assertEqual(rules.query_scene('current_axis_readings',[],c)['readings'],[])
        scene=rules.query_scene('current_axis_series',c['collections_added']['current_axis_series'],c);self.assertEqual(scene['readings'],c['collections_added']['current_axis_readings'])
    def test_unchanged_historical_rows_are_required_before_extension_is_accepted(self):
        c=self.contract();parent={'schema':'packet','manifest':{},'collections':{'sources':[{'id':'old'}],'widths':[{'width':100}]}}
        child=copy.deepcopy(parent);child['collections'].update(copy.deepcopy(c['collections_added']));child['collections']['sources']+=c['new_sources'];child['manifest']={c['namespace']:rules.admission_marker(c),'input_sha256':{rules.FILE:rules.admission_marker(c)['contract_sha256']}};rules.verify_extension(parent,child,c)
        child['collections']['widths'][0]['width']=101
        with self.assertRaises(ValueError):rules.verify_extension(parent,child,c)
    def test_complete_response_check_rejects_added_missing_and_boolean_numeric_changes(self):
        expected={'ok':True,'rows':[{'physical_current_axis_qualified':False,'value':None}],'map_scene':None}
        for changed in [{'ok':True,'rows':[{'physical_current_axis_qualified':0,'value':None}],'map_scene':None},{'ok':True,'rows':expected['rows']},{**expected,'extra':True}]:
            with self.assertRaises(ValueError):rules.verify_response(expected,changed)
        rules.verify_response(expected,copy.deepcopy(expected))

if __name__=='__main__':unittest.main()
