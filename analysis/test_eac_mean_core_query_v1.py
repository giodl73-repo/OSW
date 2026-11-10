import copy
import unittest
import eac_mean_core_query_v1 as m

def fixture(contract):
    prior=contract['prior_records'];counts=contract['parent_collection_counts']
    collections={}
    for name,key in [('objects','owner'),('entities','entity')]:
        collections[name]=[copy.deepcopy(prior[key])]+[{'id':f'fixture:{name}:{i}'} for i in range(counts[name]-1)]
    for name in ['widths','reference_routes']:
        collections[name]=copy.deepcopy(prior[name])+[{'id':f'fixture:{name}:{i}','current_id':'fixture-other'} for i in range(counts[name]-len(prior[name]))]
    collections['sources']=copy.deepcopy(prior['owner_sources'])+[
        {'id':f'fixture:source:{i}','title':f'Unrelated fixture publication {i}'} for i in range(counts['sources']-len(prior['owner_sources']))]
    collections['unrelated_scientific_table']=[{'id':'fixture:unrelated','values':[1,2,3]}]
    return collections,{'input_sha256':{'fixture:historical':'keep'},'historical_marker':{'keep':True}}

class MeanCoreQuery(unittest.TestCase):
    def test_exact_five_rows_have_source_pointers_and_mean_geometry_scope(self):
        contract=m.build_contract();source=m.read(m.facts.FACTS)
        self.assertEqual(len(contract['records']),5)
        self.assertEqual(contract['new_width_records'],0)
        for i,row in enumerate(contract['records']):
            self.assertEqual(row['source_pointer'],f'/records/{i}')
            self.assertEqual(row['source_file_sha256'],m.sha(m.facts.FACTS))
            self.assertEqual(row['offshore_extent_km'],source['records'][i]['offshore_extent_km'])
            self.assertEqual(row['maximum_depth_m'],source['records'][i]['maximum_depth_m'])
            self.assertIsNone(row['geometry']);self.assertIsNone(row['paired_edge_width_km'])
            self.assertIsNone(row['annual_width_range_km']);self.assertIsNone(row['observed_period'])
            self.assertFalse(row['seasonal_playback_eligible']);self.assertFalse(row['new_width_record_admitted'])

    def test_adapter_preserves_all_unaffected_scientific_lists(self):
        contract=m.build_contract();collections,manifest=fixture(contract)
        before={k:v for k,v in collections.items()};sources=copy.deepcopy(collections['sources'])
        m.prepare(collections,manifest,contract,parent_logical_sha256=m.PARENT)
        for key in ['widths','reference_routes','entities','unrelated_scientific_table']:self.assertIs(collections[key],before[key])
        self.assertEqual(collections['sources'],sources+[contract['new_source']])
        self.assertEqual(collections[m.COLLECTION],contract['records'])
        self.assertEqual(manifest['historical_marker'],{'keep':True})
        self.assertEqual(manifest['input_sha256']['fixture:historical'],'keep')
        self.assertEqual(manifest[m.KEY],m.marker(contract))

    def test_owner_keeps_existing_width_routes_geometry_time_and_observations(self):
        contract=m.build_contract();old=contract['prior_records']['owner'];new=contract['final_owner']
        for key in ['width_ids','width_sample_ids','route_ids','map_features','series','latest_observation_date']:
            self.assertEqual(old[key],new[key],key)
        for key,value in old['capabilities'].items():self.assertEqual(new['capabilities'][key],value,key)
        self.assertEqual(new['capabilities']['reported_model_core_sections'],5)
        self.assertEqual(new['linked_source_count'],old['linked_source_count']+1)
        self.assertEqual(new['section_fingerprints']['measurements'],old['section_fingerprints']['measurements'])
        self.assertNotEqual(new['fingerprint'],old['fingerprint'])

    def test_changed_parent_or_prior_width_refused_without_mutation(self):
        contract=m.build_contract()
        collections,manifest=fixture(contract);before=copy.deepcopy(collections)
        with self.assertRaises(ValueError):m.prepare(collections,manifest,contract,parent_logical_sha256='0'*64)
        self.assertEqual(collections,before)
        collections['widths'][0]['unexpected_mutation']=True;before=copy.deepcopy(collections)
        with self.assertRaises(ValueError):m.prepare(collections,manifest,contract,parent_logical_sha256=m.PARENT)
        self.assertEqual(collections,before)

    def test_existing_publication_requires_reconciliation(self):
        contract=m.build_contract()
        for publication in [contract['new_source'],{'id':'existing-by-title','title':contract['new_source']['title']}]:
            collections,manifest=fixture(contract);collections['sources'][-1]=copy.deepcopy(publication)
            before=copy.deepcopy(collections)
            with self.assertRaises(ValueError):m.prepare(collections,manifest,contract,parent_logical_sha256=m.PARENT)
            self.assertEqual(collections,before)

    def test_modified_contract_cannot_promote_geometry_or_ranges(self):
        contract=m.build_contract();collections,manifest=fixture(contract)
        for key,value in [('geometry',{'type':'Point','coordinates':[154,-27.5]}),('annual_width_range_km',[150,200])]:
            changed=copy.deepcopy(contract);changed['records'][0][key]=value
            with self.assertRaises(ValueError):m.prepare(collections,manifest,changed,parent_logical_sha256=m.PARENT)

    def test_duplicate_application_refused(self):
        contract=m.build_contract();collections,manifest=fixture(contract)
        m.prepare(collections,manifest,contract,parent_logical_sha256=m.PARENT)
        with self.assertRaises(ValueError):m.prepare(collections,manifest,contract,parent_logical_sha256=m.PARENT)

if __name__=='__main__':unittest.main()
