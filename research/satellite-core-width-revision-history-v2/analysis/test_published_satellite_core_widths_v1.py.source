import copy
import gzip
import json
import unittest
import published_satellite_core_widths_v1 as m
import published_satellite_core_width_index_v1 as index


class SatelliteWidthProjectionTests(unittest.TestCase):
    def parent(self):
        widths=[{'id':identity,'current_id':'agulhas','preserve':'old definition'} for identity in sorted(m.OLD_IDS)]
        widths.extend({'id':f'old-{i}','current_id':'other'} for i in range(170))
        return {'schema':'osw.query-bundle.v1','manifest':{'preserve':True,'input_sha256':{}},'collections':{
            'widths':widths,'width_samples':[{'id':'sample','unchanged':True}],
            'objects':[{'id':m.OWNER,'width_ids':sorted(m.OLD_IDS),'capabilities':{'scoped_width':2,'reference_route':1},'route_ids':['route']},{'id':'current:other','preserve':True}],
            'current_core_velocity_estimates':[{'id':'older','preserve':True}]}}

    def test_only_two_widths_and_agulhas_join_change(self):
        parent=self.parent();original=copy.deepcopy(parent);result=m.prepare(parent,logical_parent_sha256=m.PARENT)
        self.assertEqual(parent,original);self.assertEqual(len(result['collections']['widths']),174)
        self.assertEqual(result['collections']['widths'][:172],original['collections']['widths'])
        for name in ['width_samples','current_core_velocity_estimates']:self.assertEqual(result['collections'][name],original['collections'][name])
        self.assertEqual(result['collections']['objects'][1],original['collections']['objects'][1])
        owner=result['collections']['objects'][0];self.assertEqual(owner['width_ids'][:2],original['collections']['objects'][0]['width_ids'])
        self.assertEqual(owner['capabilities'],{'scoped_width':4,'reference_route':1});self.assertEqual(owner['route_ids'],['route'])
        self.assertEqual([r['approximate_width_km'] for r in result['collections']['widths'][172:]],[64,80])

    def test_wrong_parent_collision_missing_owner_or_old_join_refused(self):
        with self.assertRaises(ValueError):m.prepare(self.parent(),logical_parent_sha256='wrong')
        for change in [lambda p:p['collections']['objects'].pop(0),
                       lambda p:p['collections']['objects'][0]['width_ids'].pop(),
                       lambda p:p['collections']['objects'][0]['capabilities'].update(scoped_width=4),
                       lambda p:p['collections']['widths'].pop(),
                       lambda p:p['manifest'].update(input_sha256={m.SOURCE:'wrong'})]:
            parent=self.parent();change(parent)
            with self.assertRaises(ValueError):m.prepare(parent,logical_parent_sha256=m.PARENT)
        result=m.prepare(self.parent(),logical_parent_sha256=m.PARENT)
        with self.assertRaises(ValueError):m.prepare(result,logical_parent_sha256=m.PARENT)

    def test_exact_pointers_do_not_promote_means_into_seasonal_data(self):
        doc,_=m.document()
        for i,row in enumerate(m.records()):
            self.assertEqual(row['source_pointer'],f'/records/{i}');self.assertEqual(row['id'],doc['records'][i]['id'])
            for key in ['width_range_km','observed_period','fixed_layer_bounds_m','geometry','confidence_interval_km']:self.assertIsNone(row[key])
            self.assertIs(row['seasonal_playback_eligible'],False)
        self.assertEqual(m.records()[0]['satellite_core_context']['source_ambiguities'][0]['resolved'],False)


class SatelliteWidthIndexTests(unittest.TestCase):
    def test_old_string_preserved_and_source_pointers_exact(self):
        old='{ "preserved original spacing": true }\n'
        raw=index.encode({'schema':'osw.almanac-index-bundle.v1','documents':{'research/old.json':old}});compressed=gzip.compress(raw,mtime=0)
        catalog={'schema':'osw.almanac-index-catalog.v1','source_count':1,'source_bytes':len(old.encode()),'bundle_sha256':index.sha(raw),'bundle_bytes':len(raw),'compressed_sha256':index.sha(compressed),'compressed_bytes':len(compressed),'documents':[{'path':'research/old.json','source_sha256':index.sha(old.encode()),'source_bytes':len(old.encode())}]}
        source=(m.ROOT/m.SOURCE).read_bytes();files,audit=index._extend_verified(catalog,compressed,{'schema':'osw.almanac-index-sources.v1','documents':['research/old.json']},source)
        docs=json.loads(gzip.decompress(files['almanac/index-data.json.gz']))['documents']
        self.assertEqual(docs['research/old.json'],old);self.assertEqual(docs[m.SOURCE].encode(),source)
        self.assertEqual([r['reported_mean_width_km'] for r in json.loads(docs[m.SOURCE])['records']],[64,80])
        self.assertEqual(audit['replaced_source_paths'],[])
        with self.assertRaises(ValueError):index.source_index(b'{}',b'not loaded',b'not loaded')


if __name__=='__main__':unittest.main()
