"""Small synthetic index tests; never load the installed runtime index."""
import copy
import json
import unittest

import current_reference_profile_index_v1 as index
import current_reference_profile_batch_query_v1 as query
from current_gap_index_extension import extend


class SourceRegistration(unittest.TestCase):
    def fixture(self):
        originals={f'research/synthetic-source-{i}.json':json.dumps({'synthetic':i}) for i in range(685)}
        catalog={'schema':'osw.almanac-index-catalog.v1','source_count':685,
            'documents':[{'path':p,'source_sha256':index.sha(raw.encode()),'source_bytes':len(raw.encode())} for p,raw in originals.items()]}
        corpus={'schema':'osw.almanac-index-bundle.v1','documents':originals}
        registry={'schema':'osw.almanac-index-sources.v1','documents':list(originals)}
        additions={p:(index.ROOT/p).read_bytes() for p in index.DOCUMENTS}
        return catalog,corpus,registry,additions

    def test_all_original_strings_preserved_and_exact_eleven_appended(self):
        catalog,corpus,registry,additions=self.fixture()
        before=copy.deepcopy((catalog,corpus,registry))
        next_catalog,next_corpus,next_registry,audit=extend(catalog,corpus,registry,additions)
        index.verify_audit(audit)
        self.assertEqual((catalog,corpus,registry),before)
        self.assertEqual(next_catalog['source_count'],696)
        for p,text in corpus['documents'].items():self.assertEqual(next_corpus['documents'][p],text)
        for p,raw in additions.items():self.assertEqual(next_corpus['documents'][p].encode(),raw)
        self.assertEqual(len(next_registry['documents']),696)

    def test_changed_original_and_existing_new_path_refused(self):
        catalog,corpus,registry,additions=self.fixture()
        corpus['documents'][next(iter(corpus['documents']))]='{}'
        with self.assertRaises(ValueError):extend(catalog,corpus,registry,additions)
        catalog,corpus,registry,additions=self.fixture()
        p=next(iter(additions));old=next(iter(corpus['documents']))
        additions[old]=b'{"replacement":true}'
        with self.assertRaises(ValueError):extend(catalog,corpus,registry,additions)
        catalog,corpus,registry,additions=self.fixture()
        catalog['documents'][0]['path']=p
        corpus['documents'][p]=corpus['documents'].pop(old)
        registry['documents'][0]=p
        # Even a coincidentally identical pre-existing source cannot count as new.
        additions[p]=corpus['documents'][p].encode()
        *_,audit=extend(catalog,corpus,registry,additions)
        with self.assertRaises(ValueError):index.verify_audit(audit)

    def test_source_registration_requires_complete_batch_and_exact_descriptors(self):
        import gzip
        catalog,corpus,registry,additions=self.fixture()
        catalog,corpus,registry,audit=extend(catalog,corpus,registry,additions)
        body=index.encode(corpus);packed=gzip.compress(body,mtime=0)
        registry_raw=index.encode(registry)
        catalog.update(bundle_sha256=index.sha(body),bundle_bytes=len(body),compressed_sha256=index.sha(packed),compressed_bytes=len(packed),input_sha256={'almanac/index-sources.json':index.sha(registry_raw)})
        generated={'almanac/index-catalog.json':index.encode(catalog),'almanac/index-data.json.gz':packed,'almanac/index-sources.json':registry_raw}
        contract=query.read(query.FILE)
        bundle={'manifest':{'input_sha256':{},query.KEY:query.marker(contract,index.sha((index.ROOT/query.FILE).read_bytes()))}}
        before=copy.deepcopy(bundle)
        result=index.attach(bundle,generated,audit,contract)
        self.assertEqual(bundle,before)
        self.assertEqual(result['manifest'][index.KEY]['source_count'],696)
        del bundle['manifest'][query.KEY]
        with self.assertRaises(ValueError):index.attach(bundle,generated,audit,contract)
        bad=copy.deepcopy(catalog);bad['documents'][-1]['source_sha256']='0'*64
        # Change an admitted descriptor, not one of the synthetic originals.
        row=next(r for r in bad['documents'] if r['path']==query.FILE);row['source_sha256']='0'*64
        with self.assertRaises(ValueError):index.attach(before,{**generated,'almanac/index-catalog.json':index.encode(bad)},audit,contract)


if __name__=='__main__':unittest.main()
