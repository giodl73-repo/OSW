import copy
import json
import os
import unittest
from unittest.mock import patch
import pacific_nec_nominal_width_index_v1 as m


def tiny_parent():
    docs={f'research/fixture-{i}.json':'{ "fixture": '+str(i)+' }\n' for i in range(639)}
    catalog={'schema':'osw.almanac-index-catalog.v1','source_count':639,'documents':[
        {'path':p,'source_sha256':m.sha(t.encode()),'source_bytes':len(t.encode()),'optional':False} for p,t in docs.items()]}
    return catalog,{'schema':'osw.almanac-index-bundle.v1','documents':docs},{'schema':'osw.almanac-index-sources.v1','documents':list(docs)}


class SourceIndex(unittest.TestCase):
    def audit(self):return m.extend(*tiny_parent(),{p:(m.query.ROOT/p).read_bytes() for p in m.DOCUMENTS})[-1]

    def test_local_access_refused_before_decompression(self):
        with patch.dict(os.environ,{},clear=True),patch.object(m.gzip,'decompress',side_effect=AssertionError('early read')):
            with self.assertRaises(ValueError):m.source_index(None,None,None)

    def test_three_actual_documents_append_without_changing_639_fixture_strings(self):
        parent=tiny_parent();before=copy.deepcopy(parent)
        catalog,corpus,registry,audit=m.extend(*parent,{p:(m.query.ROOT/p).read_bytes() for p in m.DOCUMENTS});m.verify_audit(audit)
        self.assertEqual(parent,before);self.assertEqual(catalog['source_count'],642);self.assertEqual(len(registry['documents']),642)
        for p,t in parent[1]['documents'].items():self.assertEqual(corpus['documents'][p],t)
        facts=json.loads(corpus['documents'][m.query.nominal.FACTS]);self.assertEqual(facts['nominal_surface_width']['latitude_bounds_deg_north'],[8,17])
        self.assertIsNone(facts['nominal_surface_width']['numerical_width_uncertainty_km'])

    def test_corrupt_or_replaced_historical_sources_refused(self):
        bad=tiny_parent();bad[1]['documents']['research/fixture-0.json']='{}'
        with self.assertRaises(ValueError):m.extend(*bad,{})
        with self.assertRaises(ValueError):m.extend(*tiny_parent(),{'research/fixture-0.json':b'{}'})

    def test_changed_audit_inventory_or_replacement_refused(self):
        for key,value in [('original_sources_verified',638),('original_source_strings_preserved',638),('replaced_source_paths',['research/fixture-0.json']),('added_source_paths',m.DOCUMENTS+['research/extra.json'])]:
            audit=self.audit();audit[key]=value
            with self.assertRaises(ValueError):m.verify_audit(audit)

    def test_attach_preserves_packet_rows_and_rejects_duplicate_or_wrong_totals(self):
        c=m.query.build_contract();bundle={'manifest':{m.query.KEY:m.query.marker(c),'historical':{'keep':True},'input_sha256':{'old':'keep'}},
            'collections':{'sources':[{} for _ in range(219)],'widths':[{'id':f'fixture:{i}'} for i in range(178)]+[c['width_record']]}}
        before=copy.deepcopy(bundle);generated={p:b'{}' for p in m.INDEX};generated['almanac/index-catalog.json']=b'{"source_count":642}'
        child=m.attach(bundle,generated,self.audit());self.assertEqual(bundle,before);self.assertIs(child['collections'],bundle['collections'])
        self.assertEqual(child['manifest']['historical'],{'keep':True});self.assertEqual(child['manifest']['input_sha256']['old'],'keep')
        with self.assertRaises(ValueError):m.attach(child,generated,self.audit())
        generated['almanac/index-catalog.json']=b'{"source_count":641}'
        with self.assertRaises(ValueError):m.attach(bundle,generated,self.audit())


if __name__=='__main__':unittest.main()
