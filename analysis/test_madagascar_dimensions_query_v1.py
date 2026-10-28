import copy
import unittest
import madagascar_dimensions_query_v1 as m

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

class MadagascarQuery(unittest.TestCase):
    def test_width_and_event_scope(self):
        c=m.build_contract();width=c['width_record']
        self.assertEqual(width['width_range_km'],[60,100]);self.assertIsNone(width['approximate_width_km'])
        self.assertEqual(c['new_width_samples'],0);self.assertEqual(c['new_length_records'],0)
        self.assertFalse(width['annual_extrema_eligible']);self.assertFalse(width['seasonal_playback_eligible'])
        for i,row in enumerate(c['event_records']):
            self.assertEqual(row['source_pointer'],f'/event_index/{i}')
            self.assertEqual(row['source_file_sha256'],m.sha(m.source.FACTS))
            for key in ['width_km','geometry','annual_width_range_km','uncertainty_km','inferred_eddy_id']:self.assertIsNone(row[key])
            self.assertFalse(row['independent_new_observation']);self.assertFalse(row['seasonal_playback_eligible'])

    def test_preserves_prior_collections_rows_and_manifest(self):
        c=m.build_contract();collections,manifest=fixture(c);before=dict(collections)
        sources=copy.deepcopy(collections['sources']);widths=copy.deepcopy(collections['widths'])
        m.prepare(collections,manifest,c,parent_logical_sha256=m.PARENT)
        for key in ['entities','reference_routes','unrelated_scientific_table']:self.assertIs(collections[key],before[key])
        self.assertEqual(collections['widths'],widths+[c['width_record']])
        self.assertEqual(collections['sources'],sources+[c['new_source']])
        for old,new in zip(before['objects'][1:],collections['objects'][1:]):self.assertIs(old,new)
        self.assertEqual(manifest['historical_marker'],{'keep':True})
        self.assertEqual(manifest['input_sha256']['fixture:historical'],'keep')
        self.assertEqual(manifest[m.KEY],m.marker(c))

    def test_owner_preserves_lengths_routes_geometry_samples_and_time(self):
        c=m.build_contract();old=c['prior_records']['owner'];new=c['final_owner']
        for key in ['published_length_km','measurement_ids','route_ids','map_features','series','latest_observation_date','width_sample_ids']:
            self.assertEqual(new[key],old[key],key)
        for key,value in old['capabilities'].items():
            self.assertEqual(new['capabilities'][key],value+(key=='scoped_width'),key)
        self.assertEqual(new['capabilities']['reported_flow_events'],8)
        self.assertEqual(new['width_ids'],old['width_ids']+[c['width_record']['id']])
        self.assertEqual(new['linked_source_count'],old['linked_source_count']+1)
        for key in ['identity','routes_geometry','time_evidence','claims','media']:
            self.assertEqual(new['section_fingerprints'][key],old['section_fingerprints'][key])

    def test_parent_and_prior_row_changes_refused_atomically(self):
        c=m.build_contract()
        for name in ['objects','entities','widths','reference_routes','sources']:
            collections,manifest=fixture(c);collections[name][0]['unexpected']=True
            before=copy.deepcopy(collections);old_manifest=copy.deepcopy(manifest)
            with self.assertRaises(ValueError):m.prepare(collections,manifest,c,parent_logical_sha256=m.PARENT)
            self.assertEqual(collections,before);self.assertEqual(manifest,old_manifest)
        collections,manifest=fixture(c);before=copy.deepcopy(collections)
        with self.assertRaises(ValueError):m.prepare(collections,manifest,c,parent_logical_sha256='0'*64)
        self.assertEqual(collections,before)

    def test_existing_publication_by_id_doi_or_title_refused(self):
        c=m.build_contract()
        for row in [c['new_source'],{'id':'by-doi','doi':'https://doi.org/10.1175/JPO-D-15-0154.1'},
                    {'id':'by-title','title':c['new_source']['title']}]:
            collections,manifest=fixture(c);collections['sources'][-1]=copy.deepcopy(row);before=copy.deepcopy(collections)
            with self.assertRaises(ValueError):m.prepare(collections,manifest,c,parent_logical_sha256=m.PARENT)
            self.assertEqual(collections,before)

    def test_duplicate_width_id_even_under_other_owner_refused(self):
        c=m.build_contract();collections,manifest=fixture(c)
        collections['widths'][-1]['id']=c['width_record']['id'];before=copy.deepcopy(collections)
        with self.assertRaises(ValueError):m.prepare(collections,manifest,c,parent_logical_sha256=m.PARENT)
        self.assertEqual(collections,before)

    def test_modified_contract_refused(self):
        c=m.build_contract();collections,manifest=fixture(c);before=copy.deepcopy(collections)
        changed=copy.deepcopy(c);changed['event_records'][0]['width_km']=80
        with self.assertRaises(ValueError):m.prepare(collections,manifest,changed,parent_logical_sha256=m.PARENT)
        self.assertEqual(collections,before)

    def test_duplicate_application_refused(self):
        c=m.build_contract();collections,manifest=fixture(c)
        m.prepare(collections,manifest,c,parent_logical_sha256=m.PARENT);before=copy.deepcopy(collections)
        with self.assertRaises(ValueError):m.prepare(collections,manifest,c,parent_logical_sha256=m.PARENT)
        self.assertEqual(collections,before)

if __name__=='__main__':unittest.main()
