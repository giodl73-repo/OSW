import copy
import hashlib
import gzip
import json
import unittest
from unittest.mock import patch
import published_eacc_cited_width_constraint_v1 as m
import published_eacc_cited_width_constraint_index_v1 as index

class EaccConstraintProjectionTests(unittest.TestCase):
    def parent(self):
        owner={'id':m.OWNER,'width_ids':[],'capabilities':{'scoped_width':0,'time_samples':0},'fingerprint':'a'*64,'section_fingerprints':{'measurements':'b'*64,'identity':'c'*64}}
        doc={'snapshot_fingerprint':'d'*64,'entries':[copy.deepcopy(owner),{'id':'current:agulhas','preserve':True}]};raw=json.dumps(doc)
        pin=hashlib.sha256(raw.encode()).hexdigest()
        return {'schema':'osw.query-bundle.v1','manifest':{'input_sha256':{m.DASHBOARD:pin},'dashboard_receipt':{'source_file':m.DASHBOARD,'source_sha256':pin,'source_json':raw}},'collections':{'widths':[{'id':f'old-{i}','current_id':'other'} for i in range(175)],'objects':[owner,{'id':'current:agulhas','preserve':True}],'width_samples':[{'id':'old-sample'}]}}

    def test_exact_append_and_only_declared_owner_fields_change(self):
        parent=self.parent();child=m.prepare(parent,logical_parent_sha256=m.PARENT)
        self.assertEqual(child['collections']['widths'][:175],parent['collections']['widths']);self.assertEqual(child['collections']['widths'][-1],m.record())
        self.assertEqual(child['collections']['objects'][1],parent['collections']['objects'][1]);self.assertEqual(child['collections']['width_samples'],parent['collections']['width_samples'])
        self.assertEqual(child['manifest']['dashboard_receipt'],parent['manifest']['dashboard_receipt'])
        owner=child['collections']['objects'][0];self.assertEqual(owner['capabilities'],{'scoped_width':1,'time_samples':0});self.assertEqual(owner['width_ids'],[m.ID])
        self.assertNotEqual(owner['fingerprint'],parent['collections']['objects'][0]['fingerprint']);self.assertEqual(owner['section_fingerprints']['identity'],'c'*64)

    def test_exact_dashboard_change_preserves_other_owner_and_historical_receipt(self):
        parent=self.parent();raw=parent['manifest']['dashboard_receipt']['source_json'];old=json.loads(raw)
        projected=m.dashboard_document(old,hashlib.sha256(raw.encode()).hexdigest())
        self.assertEqual(projected['entries'][0]['capabilities']['scoped_width'],1);self.assertEqual(projected['entries'][1],old['entries'][1]);self.assertNotEqual(projected['snapshot_fingerprint'],old['snapshot_fingerprint'])
        bad=copy.deepcopy(old['entries'][0]);bad['capabilities']['scoped_width']=1
        with self.assertRaises(ValueError):m.dashboard_row(bad,'a'*64,'b'*64)

    def test_wrong_parent_duplicate_existing_width_and_source_rebinding_refused(self):
        with self.assertRaises(ValueError):m.prepare(self.parent(),logical_parent_sha256='0'*64)
        for mutation in ['width','join','source']:
            parent=self.parent()
            if mutation=='width':parent['collections']['widths'][0]['current_id']='east-african-coastal'
            elif mutation=='join':parent['collections']['objects'][0]['width_ids']=['invented']
            else:parent['manifest']['dashboard_receipt']['source_sha256']='0'*64
            with self.assertRaises(ValueError):m.prepare(parent,logical_parent_sha256=m.PARENT)

    def test_bound_and_all_unknown_support_survive_with_existing_seasonal_states(self):
        row=m.record();self.assertEqual(row['reported_operator'],'gt');self.assertEqual(row['lower_bound_km'],160)
        self.assertTrue(row['lower_bound_exclusive']);self.assertFalse(row['independent_observational_sample'])
        self.assertFalse(row['cited_width_constraint_context']['underlying_cited_work']['original_full_text_reviewed'])
        for key in ['upper_bound_km','reported_width_km','approximate_width_km','width_range_km','geometry','observed_period','fixed_layer_bounds_m','annual_width_range_km','reported_width_uncertainty_km']:
            self.assertIsNone(row[key],key)
        prior={'current_id':'east-african-coastal','phases':[{'id':'old-season','preserve':True}],
            'can_play':True,'eligible_indices':[0],'range_note':'old scope','playback_scope':'old playback'}
        plan=m.phase_plan(prior);self.assertEqual(plan['phases'][:-1],prior['phases'])
        self.assertEqual({k:v for k,v in plan.items() if k!='phases'},{k:v for k,v in prior.items() if k!='phases'})
        self.assertEqual(plan['phases'][-1]['width_id'],m.ID);self.assertFalse(plan['phases'][-1]['playback_step_eligible'])
        for bad in [{}, {**prior,'eligible_indices':[1]},plan]:
            with self.assertRaises(ValueError):m.phase_plan(bad)

    def test_all631_synthetic_source_strings_survive_the_one_document_append(self):
        docs={f'research/old-{i}.json':'{ "preserve original whitespace": '+str(i)+' }\n' for i in range(631)}
        raw=index.encode({'schema':'osw.almanac-index-bundle.v1','documents':docs});packed=gzip.compress(raw,mtime=0)
        catalog={'schema':'osw.almanac-index-catalog.v1','source_count':631,'source_bytes':sum(len(v.encode()) for v in docs.values()),'bundle_sha256':index.sha(raw),'bundle_bytes':len(raw),'compressed_sha256':index.sha(packed),'compressed_bytes':len(packed),'documents':[{'path':p,'source_sha256':index.sha(v.encode()),'source_bytes':len(v.encode())} for p,v in docs.items()]}
        catalog_raw=index.encode(catalog);registry=index.encode({'schema':'osw.almanac-index-sources.v1','documents':list(docs)})
        with patch.object(index,'PARENT_CATALOG_SHA',index.sha(catalog_raw)):
            generated,audit=index.source_index(catalog_raw,packed,registry)
        updated=json.loads(gzip.decompress(generated['almanac/index-data.json.gz']))['documents']
        self.assertEqual({p:updated[p] for p in docs},docs);self.assertEqual(updated[m.SOURCE].encode(),(m.ROOT/m.SOURCE).read_bytes());self.assertEqual(len(updated),632)
        self.assertEqual(audit['original_source_strings_preserved'],631);self.assertEqual(audit['replaced_source_paths'],[])

    def test_wrong_index_catalog_refused_before_payload_or_source_access(self):
        with self.assertRaises(ValueError):index.source_index(b'{}',b'not loaded',b'not loaded')

if __name__=='__main__':unittest.main()
