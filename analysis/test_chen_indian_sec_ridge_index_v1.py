import copy
import gzip
import json
import os
import unittest
from unittest.mock import patch
import chen_indian_sec_ridge_index_v1 as m

def tiny_parent():
    docs={f'research/fixture-{i}.json':'{ "fixture": '+str(i)+' }\n' for i in range(642)}
    catalog={'schema':'osw.almanac-index-catalog.v1','source_count':642,'documents':[
        {'path':p,'source_sha256':m.sha(t.encode()),'source_bytes':len(t.encode()),'optional':False} for p,t in docs.items()]}
    return catalog,{'schema':'osw.almanac-index-bundle.v1','documents':docs},{'schema':'osw.almanac-index-sources.v1','documents':list(docs)}

class SourceRegistration(unittest.TestCase):
    def generated(self):
        added={p:(m.query.ROOT/p).read_bytes() for p in m.DOCUMENTS}
        catalog,corpus,registry,audit=m.extend(*tiny_parent(),added);m.verify_audit(audit)
        body=m.encode(corpus);packed=gzip.compress(body,mtime=0);reg=m.encode(registry)
        catalog.update(bundle_sha256=m.sha(body),bundle_bytes=len(body),compressed_sha256=m.sha(packed),compressed_bytes=len(packed),input_sha256={'almanac/index-sources.json':m.sha(reg)})
        return {'almanac/index-catalog.json':m.encode(catalog),'almanac/index-data.json.gz':packed,'almanac/index-sources.json':reg},audit
    def bundle(self):
        c={'series_record':{'id':m.query.SERIES_ID},'reading_records':[{'id':'reading','series_id':m.query.SERIES_ID,'length_km':None}],
           'sensitivity_records':[{'id':'choice','series_id':m.query.SERIES_ID}],
           'new_sources':[{'id':i} for i in m.query.SOURCE_IDS],'final_owner':{'id':m.query.ENTITY,'published_length_km':None},
           'final_length_assessment':{'id':'assessment','entity_id':m.query.ENTITY,'published_length_km':None}}
        rows={m.query.SERIES:[c['series_record']],m.query.READINGS:c['reading_records'],m.query.SENSITIVITIES:c['sensitivity_records'],
              'sources':c['new_sources'],'objects':[c['final_owner']], 'length_assessments':[c['final_length_assessment']], 'widths':[{'id':'unrelated','width_km':None}]}
        c['expected_totals']={k:len(v) for k,v in rows.items()}
        marker={'schema':'osw.indian-sec-model-grid-length-runtime.v1','contract_file':m.query.FILE,'contract_sha256':m.query.CANONICAL[m.query.FILE],
                'parent_logical_sha256':m.query.PARENT,'series_added':1,'readings_added':75,'sensitivities_added':120,'qualified_model_grid_lengths':8,
                'withheld_readings':67,'reported_lengths_added':0,'reference_routes_added':0,'widths_added':0,'physical_state_joins_added':0}
        return {'schema':'osw.query-bundle.v1','collections':rows,'manifest':{m.query.KEY:marker,'untouched':{'value':1},'input_sha256':{'historical':'a'*64}}},c
    def test_local_refusal_precedes_decompression(self):
        with patch.dict(os.environ,{},clear=True),patch.object(m.gzip,'decompress',side_effect=AssertionError('early decompression')):
            with self.assertRaises(ValueError):m.source_index(None,None,None)
    def test_seven_actual_documents_preserve_every_source_string(self):
        before=tiny_parent();saved=copy.deepcopy(before)
        additions={p:(m.query.ROOT/p).read_bytes() for p in m.DOCUMENTS}
        catalog,corpus,registry,audit=m.extend(*before,additions);m.verify_audit(audit)
        self.assertEqual(before,saved);self.assertEqual(catalog['source_count'],649)
        for p,t in before[1]['documents'].items():self.assertEqual(corpus['documents'][p],t)
        for p,raw in additions.items():self.assertEqual(corpus['documents'][p].encode(),raw)
        self.assertEqual(len(registry['documents']),649)
        rules=json.loads(corpus['documents'][m.RULES]);self.assertFalse(rules['eligibility']['whole_current_length_ranking']);self.assertIsNone(rules['unknown_dimensions']['physical_width_km'])
    def test_changed_original_or_overwrite_refused(self):
        bad=tiny_parent();bad[1]['documents']['research/fixture-0.json']='{}'
        with self.assertRaises(ValueError):m.extend(*bad,{})
        with self.assertRaises(ValueError):m.extend(*tiny_parent(),{'research/fixture-0.json':b'{}'})
    def test_audit_mutations_refused(self):
        _,audit=self.generated()
        for key,value in [('original_sources_verified',641),('original_source_strings_preserved',641),('replaced_source_paths',['old']),('added_source_paths',m.DOCUMENTS[:-1]),('scientific_source_documents_replaced',1)]:
            bad=copy.deepcopy(audit);bad[key]=value
            with self.assertRaises(ValueError):m.verify_audit(bad)
    def test_attach_changes_only_manifest_index_namespace_and_pins(self):
        generated,audit=self.generated();bundle,c=self.bundle();saved=copy.deepcopy(bundle)
        with patch.object(m.query,'build_contract',return_value=c):
            result=m.attach(bundle,generated,audit)
            self.assertEqual(bundle,saved);self.assertIs(result['collections'],bundle['collections'])
            expected=copy.deepcopy(bundle['manifest']);expected['input_sha256'].update({p:m.sha(v) for p,v in generated.items()});expected[m.KEY]=result['manifest'][m.KEY]
            self.assertEqual(result['manifest'],expected)
            with self.assertRaises(ValueError):m.attach(result,generated,audit)
    def test_changed_receipt_candidate_descriptor_registry_or_hash_refused(self):
        generated,audit=self.generated()
        for mutation in ['marker','row','descriptor','registry','compressed']:
            bundle,c=self.bundle();data=copy.deepcopy(generated)
            if mutation=='marker':bundle['manifest'][m.query.KEY]['reported_lengths_added']=1
            elif mutation=='row':bundle['collections'][m.query.READINGS]=[{'id':'changed'}]
            elif mutation=='descriptor':
                catalog=json.loads(data['almanac/index-catalog.json']);next(r for r in catalog['documents'] if r['path']==m.RULES)['source_sha256']='0'*64;data['almanac/index-catalog.json']=m.encode(catalog)
            elif mutation=='registry':data['almanac/index-sources.json']=m.encode({'schema':'osw.almanac-index-sources.v1','documents':[]})
            else:data['almanac/index-data.json.gz']=b'changed'
            with patch.object(m.query,'build_contract',return_value=c),self.assertRaises(ValueError):m.attach(bundle,data,audit)

if __name__=='__main__':unittest.main()
