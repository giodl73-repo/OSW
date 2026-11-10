import copy
import json
import unittest
import madagascar_dimensions_runtime_v4 as m
import test_madagascar_dimensions_query_v1 as fixtures

def audit():return {'added_source_paths':[m.query.source.FACTS],'replaced_source_paths':[],
    'original_sources_verified':634,'original_source_strings_preserved':634,'scientific_source_documents_replaced':0}

class RuntimePreservation(unittest.TestCase):
    def pair(self):
        contract=m.query.build_contract();collections,manifest=fixtures.fixture(contract)
        parent={'schema':'osw.query-bundle.v1','collections':copy.deepcopy(collections),'manifest':copy.deepcopy(manifest)}
        m.query.prepare(collections,manifest,contract,parent_logical_sha256=m.query.PARENT)
        manifest[m.index.KEY]=audit()
        manifest['input_sha256'].update({p:'fixture-index-pin' for p in m.index.INDEX})
        return parent,{'schema':parent['schema'],'collections':collections,'manifest':manifest}

    def test_only_declared_collections_can_change(self):
        parent,child=self.pair();m.verify_collections(parent,child)
        for name in ['widths','reference_routes','sources','unrelated_scientific_table']:
            changed=copy.deepcopy(child);changed['collections'][name][0]['unexpected']=True
            with self.assertRaises(ValueError):m.verify_collections(parent,changed)
        changed=copy.deepcopy(child);changed['collections'][m.query.COLLECTION][0]['width_km']=80
        with self.assertRaises(ValueError):m.verify_collections(parent,changed)

    def test_historical_manifest_and_source_text_replacement_refused(self):
        parent,child=self.pair();child['manifest']['historical_marker']['keep']=False
        with self.assertRaises(ValueError):m.verify_collections(parent,child)
        parent,child=self.pair();child['manifest'][m.index.KEY]['replaced_source_paths']=['old.json']
        with self.assertRaises(ValueError):m.verify_collections(parent,child)

    def test_dashboard_changes_only_current_and_projection(self):
        c=m.query.build_contract();old={'entries':[c['dashboard_before'],{'id':'other','keep':[1,2]}],
            'snapshot_fingerprint':'old','earlier_projection':{'keep':True}}
        new=m.dashboard_document(old)
        self.assertEqual(new['entries'][1],old['entries'][1]);self.assertEqual(new['earlier_projection'],old['earlier_projection'])
        before={'bundle_sha256':'a'*64,'snapshot_json':json.dumps(old),'untouched':[1,2]}
        after={'bundle_sha256':'b'*64,'snapshot_json':json.dumps(new),'untouched':[1,2]}
        m.verify_snapshot('dashboard',before,after)
        after['untouched'].append(3)
        with self.assertRaises(ValueError):m.verify_snapshot('dashboard',before,after)

    def test_full_atlas_seasons_science_and_prior_scenes_preserved(self):
        c=m.query.build_contract();scene={'kind':'published_current_dimension_evidence','entity_id':m.query.OWNER,
            'width_records':c['prior_records']['widths']+[c['width_record']],'event_records':c['event_records'],
            'source_file':m.query.source.FACTS,'source_url':c['new_source']['url'],'figure':m.query.source.FIGURE,
            'scope':'Regional only','definition':'No seasonal range'}
        old={'bundle_sha256':'a'*64,'mean_core_section_scenes':{'east-australian':{'untouched':[1,2]}},'existing':{'keep':True},'supplemental_widths':[]}
        new=copy.deepcopy(old);new['bundle_sha256']='b'*64;new['current_dimension_evidence_scenes']={m.query.CURRENT:scene}
        new['supplemental_widths']=[c['width_record']]
        m.verify_snapshot('seasons',old,new)
        changed=copy.deepcopy(new);changed['mean_core_section_scenes']['east-australian']['untouched'].append(3)
        with self.assertRaises(ValueError):m.verify_snapshot('seasons',old,changed)
        path='research/ocean-motion-dashboard.json';doc={'entries':[c['dashboard_before']],'snapshot_fingerprint':'old'}
        old['sources_json']={path:json.dumps(doc),'other':'preserve exact string'}
        new['sources_json']={path:json.dumps(m.dashboard_document(doc)),'other':'preserve exact string'}
        m.verify_snapshot('atlas',old,new)
        new['sources_json']['other']='changed'
        with self.assertRaises(ValueError):m.verify_snapshot('atlas',old,new)

if __name__=='__main__':unittest.main()
