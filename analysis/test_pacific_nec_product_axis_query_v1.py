import copy
import unittest
import pacific_nec_product_axis_query_v1 as admission
import pacific_nec_product_axis_records_v1 as data


class AdditiveDiagnosticAdmission(unittest.TestCase):
    def fixture(self):
        collections={'objects':[{'id':data.OWNER,'published_length_km':None},{'id':data.FAMILY,'note':'family evidence stays separate'}],
            'entities':[{'id':data.OWNER},{'id':data.FAMILY}],'sources':[{'id':'source:historical','title':'Existing immutable source'}]}
        manifest={'input_sha256':{'historical':'a'*64},'prior_namespace':{'unchanged':True}}
        contract={'namespace':data.KEY,'parent_logical_sha256':'parent',
            'parent_collection_counts':{k:len(v) for k,v in collections.items()},
            'prior_source_inventory':copy.deepcopy(collections['sources']),
            'prior_identity_rows':{owner:{k:[copy.deepcopy(r) for r in collections[k] if r['id']==owner] for k in ('objects','entities')} for owner in (data.OWNER,data.FAMILY)},
            'new_sources':[{'id':'source:method','kind':'internal'}],
            'collections_added':{'current_axis_series':[{'id':'product_axis_series:pacific-nec:fixture','rank_eligible':False}]},
            'counts_added':{'current_axis_series':1},'input_sha256':{'new_contract_input':'b'*64},'prefixes':list(data.PREFIXES)}
        return collections,manifest,contract

    def apply(self,collections,manifest,contract):
        return admission.apply_verified(collections,manifest,contract,parent_logical_sha256='parent',contract_sha256='c'*64)

    def test_addition_keeps_every_prior_row_source_and_namespace_unchanged(self):
        collections,manifest,contract=self.fixture();before=copy.deepcopy(collections);old_manifest=copy.deepcopy(manifest)
        after,updated=self.apply(collections,manifest,contract)
        self.assertEqual(collections,before);self.assertEqual(manifest,old_manifest)
        for name in ('objects','entities'):self.assertIs(after[name],collections[name]);self.assertEqual(after[name],before[name])
        self.assertEqual(after['sources'][:-1],before['sources'])
        self.assertEqual(updated['prior_namespace'],old_manifest['prior_namespace'])
        self.assertEqual(updated[data.KEY]['reported_lengths_added'],0)
        self.assertEqual(updated[data.KEY]['physical_widths_added'],0)

    def test_partial_parent_altered_sources_identity_and_historical_pins_refused(self):
        for change in ('collection','source','identity','pin','partial_marker','prefix'):
            collections,manifest,contract=self.fixture()
            if change=='collection':collections['unexpected']=[]
            elif change=='source':collections['sources'][0]['title']='Changed'
            elif change=='identity':collections['objects'][0]['published_length_km']=13000
            elif change=='pin':manifest['input_sha256']['new_contract_input']='d'*64
            elif change=='partial_marker':manifest[data.KEY]={}
            else:
                collections['objects'][0]['id']='product_axis_reading:pacific-nec:collision'
                contract['prior_identity_rows'][data.OWNER]['objects']=[]
            with self.subTest(change=change),self.assertRaises(ValueError):self.apply(collections,manifest,contract)

    def test_prior_owner_evidence_cannot_be_relabelled_as_new_diagnostic(self):
        collections,manifest,contract=self.fixture()
        collections['widths']=[{'id':'existing-width','entity_id':data.OWNER,'width_km':100}]
        contract['parent_collection_counts']['widths']=1
        contract['prior_identity_rows'][data.OWNER]['linked_records']={'widths':copy.deepcopy(collections['widths'])}
        collections['widths'][0]['width_km']=200
        with self.assertRaisesRegex(ValueError,'evidence changed'):self.apply(collections,manifest,contract)

    def test_actual_contract_has_complete_source_bound_diagnostics(self):
        contract=admission.build_contract()
        self.assertEqual(contract['counts_added'],{'current_axis_series':3,'current_axis_readings':36,'current_axis_scenarios':1332,'current_axis_section_spans':36})
        self.assertEqual(contract['parent_collection_counts']['sources'],222)
        self.assertEqual(len(contract['new_sources']),3)
        self.assertFalse(contract['owner_and_family_rows_changed'])
        self.assertTrue(all(r['method_source_id']==admission.SOURCE_IDS[2] for rows in contract['collections_added'].values() for r in rows))
        self.assertEqual(next(r for r in contract['new_sources'] if r['id']==admission.SOURCE_IDS[1])['citation_role'],
            'geographic_and_definition_context_only_not_numerical_measurement_source')

    def test_frozen_contract_refuses_boolean_to_number_substitution(self):
        contract=admission.build_contract()
        contract['collections_added']['current_axis_readings'][0]['rank_eligible']=0
        with self.assertRaisesRegex(ValueError,'frozen contract'):
            admission.prepare({}, {}, contract, parent_logical_sha256=admission.PARENT)


if __name__=='__main__':unittest.main()
