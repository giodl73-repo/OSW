import gzip
import json
import unittest
import published_current_speed_source_index_v1 as m


class SourceIndexTests(unittest.TestCase):
    def fixture(self):
        text='{ "schema": "old", "rows": [1, 2] }\n'
        raw=m.encode({'schema':'osw.almanac-index-bundle.v1','documents':{'research/old.json':text}})
        compressed=gzip.compress(raw,mtime=0)
        catalog={'schema':'osw.almanac-index-catalog.v1','source_count':1,'source_bytes':len(text.encode()),
                 'bundle_sha256':m.digest(raw),'bundle_bytes':len(raw),
                 'compressed_sha256':m.digest(compressed),'compressed_bytes':len(compressed),
                 'documents':[{'path':'research/old.json','source_sha256':m.digest(text.encode()),'source_bytes':len(text.encode())}]}
        registry={'schema':'osw.almanac-index-sources.v1','documents':['research/old.json']}
        return catalog,compressed,registry,text

    def test_preserve_original_strings_and_add_exact_source_bytes(self):
        catalog,compressed,registry,text=self.fixture()
        source=b'{"schema":"speed-fixture","records":[1]}\n'
        files,audit=m._extend_verified_index(catalog,compressed,registry,source)
        docs=json.loads(gzip.decompress(files['almanac/index-data.json.gz']))['documents']
        self.assertEqual(docs['research/old.json'],text)
        self.assertEqual(docs[m.speed.SOURCE].encode(),source)
        self.assertEqual(audit['original_source_strings_preserved'],1)
        self.assertEqual(audit['replaced_source_paths'],[])
        self.assertEqual(catalog['source_count'],1)
        self.assertEqual(json.loads(files['almanac/index-catalog.json'])['source_count'],2)

    def test_reject_corrupt_compression_and_wrong_installed_catalog(self):
        catalog,compressed,registry,_=self.fixture()
        with self.assertRaisesRegex(ValueError,'Compressed'):
            m._extend_verified_index(catalog,compressed+b'x',registry,b'{}')
        with self.assertRaisesRegex(ValueError,'Exact installed'):
            m.source_index(b'{}',b'not-opened',b'not-opened')

    def test_reject_a_repeated_source_addition(self):
        catalog,compressed,registry,_=self.fixture()
        source=b'{"schema":"new"}\n'
        files,_=m._extend_verified_index(catalog,compressed,registry,source)
        with self.assertRaisesRegex(ValueError,'Only one new'):
            m._extend_verified_index(json.loads(files['almanac/index-catalog.json']),files['almanac/index-data.json.gz'],json.loads(files['almanac/index-sources.json']),source)


if __name__=='__main__':unittest.main()
