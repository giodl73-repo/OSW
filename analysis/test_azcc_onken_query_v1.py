import copy
import unittest
import azcc_onken_query_v1 as m


def fixture(contract):
    prior=contract['prior_records'];counts=contract['parent_collection_counts'];collections={}
    for name,key in [('objects','owner'),('entities','entity')]:
        collections[name]=[copy.deepcopy(prior[key])]+[{'id':f'fixture:{name}:{i}'} for i in range(counts[name]-1)]
    for name in ['widths','reference_routes']:
        collections[name]=copy.deepcopy(prior[name])+[{'id':f'fixture:{name}:{i}','current_id':'fixture-other'} for i in range(counts[name]-len(prior[name]))]
    collections['sources']=copy.deepcopy(prior['owner_sources'])+[
        {'id':f'fixture:source:{i}','title':f'Unrelated fixture publication {i}'} for i in range(counts['sources']-len(prior['owner_sources']))]
    collections['unrelated_scientific_table']=[{'id':'fixture:unrelated','values':[1,2,3]}]
    return collections,{'input_sha256':{'fixture:historical':'keep'},'historical_marker':{'keep':True}}


class AzccQuery(unittest.TestCase):
    def assert_refused_without_mutation(self,collections,manifest,contract,parent=m.PARENT):
        before=copy.deepcopy(collections);old=copy.deepcopy(manifest)
        with self.assertRaises(ValueError):m.prepare(collections,manifest,contract,parent_logical_sha256=parent)
        self.assertEqual(collections,before);self.assertEqual(manifest,old)

    def test_cited_width_keeps_missing_dates_layer_edges_ranges_and_uncertainty(self):
        c=m.build_contract();w=c['width_record']
        self.assertEqual(w['approximate_width_km'],200)
        for key in ['width_range_km','annual_width_range_km','numerical_width_uncertainty_km','observed_period',
                    'sampling_dates','calendar_months','boundary_rule','edge_operator','paired_edge_coordinates','section_geometry']:
            self.assertIsNone(w[key],key)
        for key in ['whole_current_representative','width_rank_eligible','annual_extrema_eligible','seasonal_playback_eligible',
                    'is_annual_mean','is_climatology','independent_new_observation','source_figure_digitized','cited_originals_reviewed']:
            self.assertIs(w[key],False,key)
        self.assertEqual(w['source_pointer'],'/cited_width_summary')
        self.assertEqual(w['source_file_sha256'],m.sha(m.FACTS))
        self.assertEqual(c['new_length_records'],0);self.assertEqual(c['new_width_samples'],0)

    def test_exact_addition_preserves_all_prior_rows_collections_and_manifest(self):
        c=m.build_contract();collections,manifest=fixture(c);before=dict(collections)
        old_widths=copy.deepcopy(collections['widths']);old_sources=copy.deepcopy(collections['sources'])
        m.prepare(collections,manifest,c,parent_logical_sha256=m.PARENT)
        self.assertEqual(set(collections),set(before))
        for name in ['entities','reference_routes','unrelated_scientific_table']:self.assertIs(collections[name],before[name])
        self.assertEqual(collections['widths'],old_widths+[c['width_record']])
        self.assertEqual(collections['sources'],old_sources+[c['new_source']])
        for old,new in zip(before['objects'][1:],collections['objects'][1:]):self.assertIs(old,new)
        self.assertEqual(manifest['historical_marker'],{'keep':True})
        self.assertEqual(manifest['input_sha256']['fixture:historical'],'keep')
        self.assertEqual(manifest[m.KEY],m.marker(c))

    def test_owner_changes_only_declared_fields_and_preserves_dated_section(self):
        c=m.build_contract();old=c['prior_records']['owner'];new=c['final_owner']
        allowed={'width_ids','capabilities','source_ids','linked_source_count','section_fingerprints','fingerprint','evidence_links'}
        self.assertEqual(set(old),set(new))
        for key in set(old)-allowed:self.assertEqual(new[key],old[key],key)
        for key,value in old['capabilities'].items():self.assertEqual(new['capabilities'][key],value+(key=='scoped_width'),key)
        self.assertEqual(new['latest_observation_date'],'2009-11-01')
        self.assertIsNone(new['published_length_km']);self.assertEqual(new['route_ids'],[])
        for key in set(old['section_fingerprints'])-{'measurements','sources'}:
            self.assertEqual(new['section_fingerprints'][key],old['section_fingerprints'][key])
        self.assertEqual(new['width_ids'],old['width_ids']+[m.WIDTH_ID]);self.assertEqual(new['linked_source_count'],7)

    def test_changed_audited_records_and_wrong_parent_refused_atomically(self):
        c=m.build_contract()
        for name in ['objects','entities','widths','sources']:
            collections,manifest=fixture(c);collections[name][0]['unexpected']=True
            self.assert_refused_without_mutation(collections,manifest,c)
        collections,manifest=fixture(c)
        self.assert_refused_without_mutation(collections,manifest,c,parent='0'*64)
        collections['reference_routes'][0]['current_id']=m.CURRENT
        self.assert_refused_without_mutation(collections,manifest,c)

    def test_existing_source_by_identity_title_or_encoded_doi_refused(self):
        c=m.build_contract()
        for row in [c['new_source'],{'id':'by-title','title':c['new_source']['title']},
                    {'id':'by-doi','doi':'https://doi.org/10.1175/1520-0485%281993%29023%3C1638%3ATAC%3E2.0.CO%3B2'}]:
            collections,manifest=fixture(c);collections['sources'][-1]=copy.deepcopy(row)
            self.assert_refused_without_mutation(collections,manifest,c)

    def test_duplicate_ids_and_unexpected_inventory_refused(self):
        c=m.build_contract()
        for name in ['objects','entities','widths','reference_routes','sources']:
            collections,manifest=fixture(c);collections[name][-1]=copy.deepcopy(collections[name][0])
            self.assert_refused_without_mutation(collections,manifest,c)
        collections,manifest=fixture(c);collections['widths'][-1]['id']=m.WIDTH_ID
        self.assert_refused_without_mutation(collections,manifest,c)
        collections,manifest=fixture(c);collections['widths'].pop()
        self.assert_refused_without_mutation(collections,manifest,c)

    def test_changed_scope_or_repeated_application_refused(self):
        c=m.build_contract();collections,manifest=fixture(c);bad=copy.deepcopy(c)
        bad['width_record']['annual_width_range_km']=[110,200]
        self.assert_refused_without_mutation(collections,manifest,bad)
        m.prepare(collections,manifest,c,parent_logical_sha256=m.PARENT)
        self.assert_refused_without_mutation(collections,manifest,c)

    def test_historical_input_rebinding_refused_atomically(self):
        c=m.build_contract();collections,manifest=fixture(c)
        manifest['input_sha256'][m.FACTS]='old-unrelated-pin'
        self.assert_refused_without_mutation(collections,manifest,c)


if __name__=='__main__':unittest.main()
